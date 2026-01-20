import os
import sqlite3
import sys
import unittest
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import rank_projects


class TestRankByContributor(unittest.TestCase):
    def setUp(self):
        # create in-memory DB and required tables
        self.conn = sqlite3.connect(':memory:')
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
        cur.execute(
            '''
            CREATE TABLE files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL
            )
            '''
        )
        cur.execute(
            '''
            CREATE TABLE contributors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
            '''
        )
        cur.execute(
            '''
            CREATE TABLE file_contributors (
                file_id INTEGER NOT NULL,
                contributor_id INTEGER NOT NULL,
                PRIMARY KEY (file_id, contributor_id)
            )
            '''
        )
        self.conn.commit()

    def tearDown(self):
        try:
            self.conn.close()
        except Exception:
            pass

    def test_rank_by_alice(self):
        cur = self.conn.cursor()
        # scans: proj-a (id 1), proj-b (id 2)
        cur.execute("INSERT INTO scans (project) VALUES (?)", ('proj-a',))
        cur.execute("INSERT INTO scans (project) VALUES (?)", ('proj-b',))
        # files: two files for proj-a, one file for proj-b
        cur.execute("INSERT INTO files (scan_id, file_name, file_path) VALUES (?,?,?)", (1, 'f1', 'f1'))
        cur.execute("INSERT INTO files (scan_id, file_name, file_path) VALUES (?,?,?)", (1, 'f2', 'f2'))
        cur.execute("INSERT INTO files (scan_id, file_name, file_path) VALUES (?,?,?)", (2, 'fx', 'fx'))
        # contributors
        cur.execute("INSERT INTO contributors (name) VALUES (?)", ('Alice',))
        cur.execute("INSERT INTO contributors (name) VALUES (?)", ('Bob',))
        # file_contributors: Alice -> f1 and fx, Bob -> f2
        cur.execute("INSERT INTO file_contributors (file_id, contributor_id) VALUES (?,?)", (1, 1))
        cur.execute("INSERT INTO file_contributors (file_id, contributor_id) VALUES (?,?)", (3, 1))
        cur.execute("INSERT INTO file_contributors (file_id, contributor_id) VALUES (?,?)", (2, 2))
        self.conn.commit()

        with patch('rank_projects.get_connection', return_value=self.conn):
            res = rank_projects.rank_projects_by_contributor('Alice')

        # proj-b should rank higher (Alice did 1/1 files) than proj-a (1/2 -> 0.5)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]['project'], 'proj-b')
        self.assertAlmostEqual(res[0]['score'], 1.0)
        self.assertEqual(res[1]['project'], 'proj-a')
        self.assertAlmostEqual(res[1]['score'], 0.5)

    def test_contributor_with_no_files_returns_empty(self):
        cur = self.conn.cursor()
        # one project with files but no contributor links
        cur.execute("INSERT INTO scans (project) VALUES (?)", ('solo-project',))
        cur.execute("INSERT INTO files (scan_id, file_name, file_path) VALUES (?,?,?)", (1, 'a', 'a'))
        cur.execute("INSERT INTO contributors (name) VALUES (?)", ('Charlie',))
        self.conn.commit()

        with patch('rank_projects.get_connection', return_value=self.conn):
            res = rank_projects.rank_projects_by_contributor('Charlie')

        self.assertEqual(res, [])

    def test_tie_breaker_prefers_more_files_then_name(self):
        cur = self.conn.cursor()
        # proj1: 2 files, contrib X -> 1 file (score 0.5)
        # proj2: 4 files, contrib X -> 2 files (score 0.5) -> should come before proj1
        cur.execute("INSERT INTO scans (project) VALUES (?)", ('proj1',))
        cur.execute("INSERT INTO scans (project) VALUES (?)", ('proj2',))
        # files for proj1 (scan_id 1)
        cur.execute("INSERT INTO files (scan_id, file_name, file_path) VALUES (?,?,?)", (1, 'p1f1', 'p1f1'))
        cur.execute("INSERT INTO files (scan_id, file_name, file_path) VALUES (?,?,?)", (1, 'p1f2', 'p1f2'))
        # files for proj2 (scan_id 2)
        cur.execute("INSERT INTO files (scan_id, file_name, file_path) VALUES (?,?,?)", (2, 'p2f1', 'p2f1'))
        cur.execute("INSERT INTO files (scan_id, file_name, file_path) VALUES (?,?,?)", (2, 'p2f2', 'p2f2'))
        cur.execute("INSERT INTO files (scan_id, file_name, file_path) VALUES (?,?,?)", (2, 'p2f3', 'p2f3'))
        cur.execute("INSERT INTO files (scan_id, file_name, file_path) VALUES (?,?,?)", (2, 'p2f4', 'p2f4'))
        # contributor
        cur.execute("INSERT INTO contributors (name) VALUES (?)", ('Xavier',))
        # file_contributors: Xavier -> p1f1 (file_id 1) and p2f1,p2f2 (file_ids 3,4)
        cur.execute("INSERT INTO file_contributors (file_id, contributor_id) VALUES (?,?)", (1, 1))
        cur.execute("INSERT INTO file_contributors (file_id, contributor_id) VALUES (?,?)", (3, 1))
        cur.execute("INSERT INTO file_contributors (file_id, contributor_id) VALUES (?,?)", (4, 1))
        self.conn.commit()

        with patch('rank_projects.get_connection', return_value=self.conn):
            res = rank_projects.rank_projects_by_contributor('Xavier')

        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]['project'], 'proj2')
        self.assertEqual(res[1]['project'], 'proj1')

    def test_limit_parameter_honored(self):
        cur = self.conn.cursor()
        # create three projects and give contributor links to all
        for pname in ('a', 'b', 'c'):
            cur.execute("INSERT INTO scans (project) VALUES (?)", (pname,))
            cur.execute("INSERT INTO files (scan_id, file_name, file_path) VALUES (?,?,?)", (cur.lastrowid, 'f', 'f'))
        cur.execute("INSERT INTO contributors (name) VALUES (?)", ('LimitUser',))
        # Link LimitUser to one file in each project (file ids 1..3)
        cur.execute("INSERT INTO file_contributors (file_id, contributor_id) VALUES (?,?)", (1, 1))
        cur.execute("INSERT INTO file_contributors (file_id, contributor_id) VALUES (?,?)", (2, 1))
        cur.execute("INSERT INTO file_contributors (file_id, contributor_id) VALUES (?,?)", (3, 1))
        self.conn.commit()

        with patch('rank_projects.get_connection', return_value=self.conn):
            res = rank_projects.rank_projects_by_contributor('LimitUser', limit=1)

        self.assertEqual(len(res), 1)

    def test_exact_name_matching_is_case_sensitive(self):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO scans (project) VALUES (?)", ('pc',))
        cur.execute("INSERT INTO files (scan_id, file_name, file_path) VALUES (?,?,?)", (1, 'f', 'f'))
        cur.execute("INSERT INTO contributors (name) VALUES (?)", ('Alice',))
        cur.execute("INSERT INTO file_contributors (file_id, contributor_id) VALUES (?,?)", (1, 1))
        self.conn.commit()

        with patch('rank_projects.get_connection', return_value=self.conn):
            res_lower = rank_projects.rank_projects_by_contributor('alice')
            res_exact = rank_projects.rank_projects_by_contributor('Alice')

        # Contributor matching now uses canonical_username (case-insensitive normalization)
        self.assertEqual(len(res_lower), 1)
        self.assertEqual(len(res_exact), 1)


if __name__ == '__main__':
    unittest.main()
