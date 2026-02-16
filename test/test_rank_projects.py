import os
import sqlite3
import sys
import unittest
import tempfile
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import rank_projects


class TestRankProjects(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite DB and create the scans table
        self.conn = sqlite3.connect(':memory:')
        # Make rows behave like sqlite3.Row so code can use dict access
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute(
            '''
            CREATE TABLE scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scanned_at TEXT DEFAULT CURRENT_TIMESTAMP,
                project TEXT,
                notes TEXT
            )
            '''
        )
        # Create a minimal projects table so ranking SQL can left-join against it
        cur.execute(
            '''
            CREATE TABLE projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                repo_url TEXT,
                created_at TEXT
            )
            '''
        )
        self.conn.commit()

    def tearDown(self):
        try:
            self.conn.close()
        except Exception:
            pass

    def insert_scan(self, project: str, scanned_at: str):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO scans (scanned_at, project) VALUES (?, ?)", (scanned_at, project))
        self.conn.commit()

    def test_rank_projects_descending(self):
        # Insert sample data: project A has most recent scan
        self.insert_scan('project-a', '2025-11-01 10:00:00')
        self.insert_scan('project-b', '2025-11-02 12:00:00')
        self.insert_scan('project-a', '2025-11-03 00:22:55')

        with patch('rank_projects.get_connection', return_value=self.conn):
            results = rank_projects.rank_projects(order='desc')

        # Ordering is by project created_at (earliest scan) desc when no project row.
        # project-a has earliest scan 2025-11-01, project-b 2025-11-02, so project-b should come first.
        self.assertGreaterEqual(len(results), 2)
        self.assertEqual(results[0]['project'], 'project-b')
        self.assertEqual(results[0]['scans_count'], 1)
        self.assertEqual(results[1]['project'], 'project-a')

    def test_limit_and_ascending(self):
        # Insert multiple projects with different timestamps
        self.insert_scan('alpha', '2025-01-01 00:00:00')
        self.insert_scan('beta', '2025-06-01 00:00:00')
        self.insert_scan('gamma', '2025-12-01 00:00:00')

        with patch('rank_projects.get_connection', return_value=self.conn):
            results_asc = rank_projects.rank_projects(order='asc', limit=2)

        # Ascending order -> alpha then beta (limited to 2)
        self.assertEqual(len(results_asc), 2)
        self.assertEqual(results_asc[0]['project'], 'alpha')
        self.assertEqual(results_asc[1]['project'], 'beta')

    def test_print_projects_output(self):
        # Prepare a simple projects list and capture printed table
        projects = [
            {'project': 'x', 'first_scan': '2025-01-01 01:00:00', 'last_scan': '2025-01-02 01:00:00', 'scans_count': 1},
            {'project': 'long-project-name', 'first_scan': '2025-02-01 01:00:00', 'last_scan': '2025-02-02 01:00:00', 'scans_count': 2},
        ]
        buf = StringIO()
        # Mock the collaboration status function to avoid database calls
        with patch('rank_projects._get_project_collaboration_status', return_value='Individual'):
            with redirect_stdout(buf):
                rank_projects.print_projects(projects)
        out = buf.getvalue()

        # Basic checks for header and project names
        self.assertIn('Project', out)
        self.assertIn('First Scan', out)
        self.assertIn('Last Scan', out)
        self.assertIn('Scans', out)
        self.assertIn('long-project-name', out)


if __name__ == '__main__':
    unittest.main()


def _make_custom_db():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    conn = sqlite3.connect(tmp.name)
    conn.row_factory = sqlite3.Row
    rank_projects._ensure_custom_ranking_tables(conn)
    conn.close()
    return tmp.name


def _conn_factory(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def test_custom_ranking_save_load_and_list():
    db_path = _make_custom_db()
    try:
        with patch('rank_projects.get_connection', lambda: _conn_factory(db_path)):
            rank_projects.save_custom_ranking("Favorites", ["project-a", "project-b"])
            assert rank_projects.get_custom_ranking("Favorites") == ["project-a", "project-b"]
            names = [r["name"] for r in rank_projects.list_custom_rankings()]
            assert "Favorites" in names
    finally:
        os.remove(db_path)


def test_custom_ranking_rename_and_delete():
    db_path = _make_custom_db()
    try:
        with patch('rank_projects.get_connection', lambda: _conn_factory(db_path)):
            rank_projects.save_custom_ranking("OldName", ["project-a"])
            assert rank_projects.rename_custom_ranking("OldName", "NewName") is True
            assert rank_projects.get_custom_ranking("NewName") == ["project-a"]
            assert rank_projects.delete_custom_ranking("NewName") is True
            assert rank_projects.get_custom_ranking("NewName") == []
    finally:
        os.remove(db_path)
