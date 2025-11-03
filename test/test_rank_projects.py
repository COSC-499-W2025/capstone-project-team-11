import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import sqlite3
from io import StringIO
from contextlib import redirect_stdout
from unittest.mock import patch

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

        # Expect project-a first because its last_scan is newest
        self.assertGreaterEqual(len(results), 2)
        self.assertEqual(results[0]['project'], 'project-a')
        self.assertEqual(results[0]['scans_count'], 2)
        self.assertEqual(results[1]['project'], 'project-b')

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
