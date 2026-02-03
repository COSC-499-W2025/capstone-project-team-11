import os
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import summarize_projects


def _setup_in_memory_db():
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            git_metrics_json TEXT,
            tech_json TEXT
        );
        CREATE TABLE scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scanned_at TEXT DEFAULT CURRENT_TIMESTAMP,
            project TEXT,
            notes TEXT
        );
        CREATE TABLE files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL
        );
        CREATE TABLE contributors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        );
        CREATE TABLE file_contributors (
            file_id INTEGER NOT NULL,
            contributor_id INTEGER NOT NULL,
            PRIMARY KEY (file_id, contributor_id)
        );
        CREATE TABLE languages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        );
        CREATE TABLE file_languages (
            file_id INTEGER NOT NULL,
            language_id INTEGER NOT NULL,
            PRIMARY KEY (file_id, language_id)
        );
        CREATE TABLE skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        );
        CREATE TABLE project_skills (
            project_id INTEGER NOT NULL,
            skill_id INTEGER NOT NULL,
            PRIMARY KEY (project_id, skill_id)
        );
        """
    )
    conn.commit()
    return conn


class TestGatherProjectInfoFromDB(unittest.TestCase):
    def setUp(self):
        self.conn = _setup_in_memory_db()

    def tearDown(self):
        try:
            self.conn.close()
        except Exception:
            pass

    def test_returns_languages_frameworks_skills_and_metrics(self):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO projects (name, git_metrics_json, tech_json) VALUES (?, ?, ?)",
            (
                'proj1',
                '{"commits_per_author": {"UserA": 3}, "files_changed_per_author": {"UserA": ["a.py"]}}',
                '{"frameworks": ["Django"]}',
            ),
        )
        project_id = cur.lastrowid
        cur.execute("INSERT INTO scans (project) VALUES ('proj1')")
        scan_id = cur.lastrowid
        cur.execute("INSERT INTO files (scan_id, file_name, file_path) VALUES (?, ?, ?)", (scan_id, 'a.py', '/tmp/a.py'))
        file_id = cur.lastrowid
        cur.execute("INSERT OR IGNORE INTO languages (name) VALUES ('Python')")
        cur.execute("SELECT id FROM languages WHERE name='Python'")
        lang_id = cur.fetchone()['id']
        cur.execute("INSERT INTO file_languages (file_id, language_id) VALUES (?, ?)", (file_id, lang_id))

        cur.execute("INSERT OR IGNORE INTO skills (name) VALUES ('Data Analysis')")
        cur.execute("SELECT id FROM skills WHERE name='Data Analysis'")
        skill_id = cur.fetchone()['id']
        cur.execute("INSERT INTO project_skills (project_id, skill_id) VALUES (?, ?)", (project_id, skill_id))
        self.conn.commit()

        with patch('summarize_projects.get_connection', return_value=self.conn):
            info = summarize_projects.gather_project_info_from_db('proj1')

        self.assertIn('Python', info['languages'])
        self.assertIn('Django', info['frameworks'])
        self.assertIn('Data Analysis', info['skills'])
        self.assertEqual(info['git_metrics']['commits_per_author']['UserA'], 3)
        self.assertEqual(info['projects_detected'], 1)

    def test_contributions_merge_commits_and_file_counts(self):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO projects (name, git_metrics_json, tech_json) VALUES (?, ?, ?)",
            (
                'proj2',
                '{"commits_per_author": {"UserB": 5}}',
                '{}',
            ),
        )
        project_id = cur.lastrowid
        cur.execute("INSERT INTO scans (project) VALUES ('proj2')")
        scan_id = cur.lastrowid
        cur.execute("INSERT INTO files (scan_id, file_name, file_path) VALUES (?, ?, ?)", (scan_id, 'b.py', '/tmp/b.py'))
        file_id = cur.lastrowid
        cur.execute("INSERT OR IGNORE INTO contributors (name) VALUES ('UserB')")
        cur.execute("SELECT id FROM contributors WHERE name='UserB'")
        contrib_id = cur.fetchone()['id']
        cur.execute("INSERT INTO file_contributors (file_id, contributor_id) VALUES (?, ?)", (file_id, contrib_id))
        self.conn.commit()

        with patch('summarize_projects.get_connection', return_value=self.conn):
            info = summarize_projects.gather_project_info_from_db('proj2')

        contrib = info['contributions']['userb']  # canonicalized
        self.assertEqual(contrib['file_count'], 1)
        self.assertEqual(contrib['commits'], 5)


class TestSummarizeTopRankedProjects(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        try:
            os.rmdir(self.temp_dir)
        except Exception:
            pass

    def test_returns_empty_list_for_unknown_contributor(self):
        with patch('summarize_projects.db_is_initialized', return_value=True):
            with patch('summarize_projects.rank_projects_by_contributor', return_value=[]):
                result = summarize_projects.summarize_top_ranked_projects('UnknownUser')
                self.assertEqual(result, [])

    def test_handles_gather_errors(self):
        mock_projects = [{'project': 'p1', 'contrib_files': 1, 'total_files': 1, 'score': 0.5}]
        with patch('summarize_projects.db_is_initialized', return_value=True):
            with patch('summarize_projects.rank_projects_by_contributor', return_value=mock_projects):
                with patch('summarize_projects.gather_project_info_from_db', side_effect=Exception('boom')):
                    result = summarize_projects.summarize_top_ranked_projects('UserX')
                    self.assertEqual(len(result), 1)
                    self.assertEqual(result[0]['project'], 'p1')
                    self.assertIsNone(result[0]['project_info'])
                    self.assertIn('boom', result[0]['error'])

    def test_successful_summary_path_flow(self):
        mock_projects = [{'project': 'p2', 'contrib_files': 2, 'total_files': 4, 'score': 0.5}]
        mock_info = {
            'languages': ['Python'],
            'frameworks': [],
            'skills': [],
            'contributions': {},
            'git_metrics': {'commits_per_author': {'userx': 3}},
            'projects_detected': 1,
        }
        with patch('summarize_projects.db_is_initialized', return_value=True):
            with patch('summarize_projects.rank_projects_by_contributor', return_value=mock_projects):
                with patch('summarize_projects.gather_project_info_from_db', return_value=mock_info):
                    with patch('summarize_projects.generate_combined_summary', return_value=os.path.join(self.temp_dir, 'out.txt')) as mock_gen:
                        result = summarize_projects.summarize_top_ranked_projects('UserX')
                        self.assertEqual(len(result), 1)
                        self.assertIsNone(result[0]['error'])
                        self.assertTrue(mock_gen.called)

    def test_limit_is_respected(self):
        mock_projects = [
            {'project': 'p1', 'contrib_files': 1, 'total_files': 2, 'score': 0.4},
            {'project': 'p2', 'contrib_files': 2, 'total_files': 3, 'score': 0.5},
        ]
        with patch('summarize_projects.db_is_initialized', return_value=True):
            with patch('summarize_projects.rank_projects_by_contributor', return_value=mock_projects[:1]):
                with patch('summarize_projects.gather_project_info_from_db', return_value={'projects_detected': 1}):
                    with patch('summarize_projects.generate_combined_summary', return_value=os.path.join(self.temp_dir, 'out.txt')):
                        result = summarize_projects.summarize_top_ranked_projects('UserY', limit=1)
                        self.assertEqual(len(result), 1)

    def test_commit_count_falls_back_to_contributions(self):
        mock_projects = [{'project': 'p3', 'contrib_files': 2, 'total_files': 5, 'score': 0.3}]
        mock_info = {
            'languages': [],
            'frameworks': [],
            'skills': [],
            'contributions': {'userz': {'commits': 6, 'files': [], 'file_count': 0}},
            'git_metrics': {'total_commits': 10},
            'projects_detected': 1,
        }
        with patch('summarize_projects.db_is_initialized', return_value=True):
            with patch('summarize_projects.rank_projects_by_contributor', return_value=mock_projects):
                with patch('summarize_projects.gather_project_info_from_db', return_value=mock_info):
                    with patch('summarize_projects.generate_combined_summary') as mock_gen:
                        summarize_projects.summarize_top_ranked_projects('UserZ')
                        args, kwargs = mock_gen.call_args
                        proj_info = kwargs['project_data_list'][0]['project_info']
                        self.assertEqual(proj_info['contributions']['userz']['commits'], 6)


if __name__ == '__main__':
    unittest.main()
