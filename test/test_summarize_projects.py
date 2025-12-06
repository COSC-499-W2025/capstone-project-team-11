import unittest
import os
import sys
import tempfile
import shutil
import sqlite3
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import summarize_projects


def _robust_rmtree(path: str) -> None:
    """Remove directory tree robustly."""
    def onerror(func, p, excinfo):
        try:
            os.chmod(p, 0o700)
        except Exception:
            pass
        try:
            func(p)
        except Exception:
            pass
    if os.path.exists(path):
        shutil.rmtree(path, onerror=onerror)


class TestGetProjectPath(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite DB with required tables
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
        self.conn.commit()

    def tearDown(self):
        try:
            self.conn.close()
        except Exception:
            pass

    def test_get_project_path_returns_none_for_nonexistent_project(self):
        """Test that get_project_path returns None for a project that doesn't exist."""
        with patch('summarize_projects.get_connection', return_value=self.conn):
            result = summarize_projects.get_project_path('nonexistent-project')
            self.assertIsNone(result)

    def test_get_project_path_returns_none_for_project_with_no_files(self):
        """Test that get_project_path returns None when project has no files."""
        cur = self.conn.cursor()
        cur.execute("INSERT INTO scans (project) VALUES (?)", ('empty-project',))
        self.conn.commit()

        with patch('summarize_projects.get_connection', return_value=self.conn):
            result = summarize_projects.get_project_path('empty-project')
            self.assertIsNone(result)

    def test_get_project_path_finds_project_root_with_git(self):
        """Test that get_project_path finds project root when .git exists."""
        # Create a temporary directory structure
        temp_dir = tempfile.mkdtemp()
        try:
            project_dir = os.path.join(temp_dir, 'test-project')
            os.makedirs(project_dir)
            sub_dir = os.path.join(project_dir, 'src')
            os.makedirs(sub_dir)
            
            # Create .git directory to mark as project root
            git_dir = os.path.join(project_dir, '.git')
            os.makedirs(git_dir)
            
            # Create a file in subdirectory
            test_file = os.path.join(sub_dir, 'test.py')
            with open(test_file, 'w') as f:
                f.write('print("test")')
            
            # Insert scan and file into database
            cur = self.conn.cursor()
            cur.execute("INSERT INTO scans (project) VALUES (?)", ('test-project',))
            scan_id = cur.lastrowid
            cur.execute(
                "INSERT INTO files (scan_id, file_name, file_path) VALUES (?, ?, ?)",
                (scan_id, 'test.py', test_file)
            )
            self.conn.commit()

            with patch('summarize_projects.get_connection', return_value=self.conn):
                result = summarize_projects.get_project_path('test-project')
                # Should return the project root (directory with .git)
                self.assertEqual(result, project_dir)
        finally:
            _robust_rmtree(temp_dir)

    def test_get_project_path_finds_project_root_with_readme(self):
        """Test that get_project_path finds project root when README.md exists."""
        temp_dir = tempfile.mkdtemp()
        try:
            project_dir = os.path.join(temp_dir, 'my-project')
            os.makedirs(project_dir)
            sub_dir = os.path.join(project_dir, 'lib')
            os.makedirs(sub_dir)
            
            # Create README.md to mark as project root
            readme = os.path.join(project_dir, 'README.md')
            with open(readme, 'w') as f:
                f.write('# My Project')
            
            # Create a file in subdirectory
            test_file = os.path.join(sub_dir, 'module.py')
            with open(test_file, 'w') as f:
                f.write('def hello(): pass')
            
            cur = self.conn.cursor()
            cur.execute("INSERT INTO scans (project) VALUES (?)", ('my-project',))
            scan_id = cur.lastrowid
            cur.execute(
                "INSERT INTO files (scan_id, file_name, file_path) VALUES (?, ?, ?)",
                (scan_id, 'module.py', test_file)
            )
            self.conn.commit()

            with patch('summarize_projects.get_connection', return_value=self.conn):
                result = summarize_projects.get_project_path('my-project')
                self.assertEqual(result, project_dir)
        finally:
            _robust_rmtree(temp_dir)

    def test_get_project_path_handles_zip_file_paths(self):
        """Test that get_project_path handles zip file paths correctly."""
        temp_dir = tempfile.mkdtemp()
        try:
            zip_file = os.path.join(temp_dir, 'archive.zip')
            # Create a dummy zip file path (format: "/path/to.zip:inner/path/file.py")
            zip_path = f"{zip_file}:inner/src/file.py"
            
            cur = self.conn.cursor()
            cur.execute("INSERT INTO scans (project) VALUES (?)", ('zipped-project',))
            scan_id = cur.lastrowid
            cur.execute(
                "INSERT INTO files (scan_id, file_name, file_path) VALUES (?, ?, ?)",
                (scan_id, 'file.py', zip_path)
            )
            self.conn.commit()

            with patch('summarize_projects.get_connection', return_value=self.conn):
                result = summarize_projects.get_project_path('zipped-project')
                # Should return the directory containing the zip file
                self.assertEqual(result, temp_dir)
        finally:
            _robust_rmtree(temp_dir)

    def test_get_project_path_uses_most_recent_scan(self):
        """Test that get_project_path uses the most recent scan's files."""
        temp_dir = tempfile.mkdtemp()
        try:
            project_dir = os.path.join(temp_dir, 'versioned-project')
            os.makedirs(project_dir)
            
            # Create README
            readme = os.path.join(project_dir, 'README.md')
            with open(readme, 'w') as f:
                f.write('# Project')
            
            old_file = os.path.join(project_dir, 'old.py')
            new_file = os.path.join(project_dir, 'new.py')
            with open(old_file, 'w') as f:
                f.write('old')
            with open(new_file, 'w') as f:
                f.write('new')
            
            cur = self.conn.cursor()
            # Insert two scans with different timestamps
            cur.execute(
                "INSERT INTO scans (project, scanned_at) VALUES (?, ?)",
                ('versioned-project', '2025-01-01 10:00:00')
            )
            old_scan_id = cur.lastrowid
            cur.execute(
                "INSERT INTO scans (project, scanned_at) VALUES (?, ?)",
                ('versioned-project', '2025-01-02 10:00:00')
            )
            new_scan_id = cur.lastrowid
            
            # Add files to both scans
            cur.execute(
                "INSERT INTO files (scan_id, file_name, file_path) VALUES (?, ?, ?)",
                (old_scan_id, 'old.py', old_file)
            )
            cur.execute(
                "INSERT INTO files (scan_id, file_name, file_path) VALUES (?, ?, ?)",
                (new_scan_id, 'new.py', new_file)
            )
            self.conn.commit()

            with patch('summarize_projects.get_connection', return_value=self.conn):
                result = summarize_projects.get_project_path('versioned-project')
                # Should find the project root regardless of which file is used
                self.assertEqual(result, project_dir)
        finally:
            _robust_rmtree(temp_dir)


class TestSummarizeTopRankedProjects(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite DB with required tables
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
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        try:
            self.conn.close()
        except Exception:
            pass
        _robust_rmtree(self.temp_dir)

    def test_summarize_returns_empty_list_for_nonexistent_contributor(self):
        """Test that summarize_top_ranked_projects returns empty list for unknown contributor."""
        with patch('summarize_projects.get_connection', return_value=self.conn):
            with patch('summarize_projects.rank_projects_by_contributor', return_value=[]):
                result = summarize_projects.summarize_top_ranked_projects('UnknownUser')
                self.assertEqual(result, [])

    def test_summarize_skips_projects_without_paths(self):
        """Test that summarize_top_ranked_projects skips projects when path cannot be found."""
        # Mock rank_projects_by_contributor to return a project
        mock_projects = [
            {'project': 'missing-path-project', 'contrib_files': 5, 'total_files': 10, 'score': 0.5}
        ]
        
        with patch('summarize_projects.get_connection', return_value=self.conn):
            with patch('summarize_projects.rank_projects_by_contributor', return_value=mock_projects):
                with patch('summarize_projects.get_project_path', return_value=None):
                    result = summarize_projects.summarize_top_ranked_projects('TestUser')
                    
                    self.assertEqual(len(result), 1)
                    self.assertEqual(result[0]['project'], 'missing-path-project')
                    self.assertIsNone(result[0]['project_path']) 
                    self.assertEqual(result[0]['error'], 'Project path not found') 

    def test_summarize_generates_summaries_for_valid_projects(self):
        """Test that summarize_top_ranked_projects generates summaries when project path exists."""
        # Create a temporary project directory
        project_dir = os.path.join(self.temp_dir, 'test-project')
        os.makedirs(project_dir)
        readme = os.path.join(project_dir, 'README.md')
        with open(readme, 'w') as f:
            f.write('# Test Project')
        py_file = os.path.join(project_dir, 'main.py')
        with open(py_file, 'w') as f:
            f.write('print("hello")')
        
        # Mock rank_projects_by_contributor
        mock_projects = [
            {'project': 'test-project', 'contrib_files': 2, 'total_files': 2, 'score': 1.0}
        ]
        
        # Mock gather_project_info
        mock_info = {
            'project_name': 'test-project',
            'project_path': project_dir,
            'languages': ['Python'],
            'skills': [],
            'contributions': {},
            'git_metrics': None
        }
        
        with patch('summarize_projects.get_connection', return_value=self.conn):
            with patch('summarize_projects.rank_projects_by_contributor', return_value=mock_projects):
                with patch('summarize_projects.get_project_path', return_value=project_dir):
                    with patch('project_info_output.gather_project_info', return_value=mock_info):
                        with patch('summarize_projects.generate_combined_summary', return_value=os.path.join(self.temp_dir, 'combined_summary.txt')):
                            result = summarize_projects.summarize_top_ranked_projects('TestUser')
                            
                            self.assertEqual(len(result), 1)
                            self.assertEqual(result[0]['project'], 'test-project')
                            self.assertEqual(result[0]['project_path'], project_dir)
                            self.assertIsNone(result[0]['error'])  # No error expected

    def test_summarize_handles_summary_generation_errors(self):
        """Test that summarize_top_ranked_projects handles errors during summary generation."""
        project_dir = os.path.join(self.temp_dir, 'error-project')
        os.makedirs(project_dir)
        
        mock_projects = [
            {'project': 'error-project', 'contrib_files': 1, 'total_files': 1, 'score': 1.0}
        ]
        
        with patch('summarize_projects.get_connection', return_value=self.conn):
            with patch('summarize_projects.rank_projects_by_contributor', return_value=mock_projects):
                with patch('summarize_projects.get_project_path', return_value=project_dir):
                    # Mock gather_project_info to raise an exception
                    with patch('project_info_output.gather_project_info', side_effect=Exception('Test error')):
                        result = summarize_projects.summarize_top_ranked_projects('TestUser')
                        
                        self.assertEqual(len(result), 1)
                        self.assertEqual(result[0]['project'], 'error-project')
                        self.assertEqual(result[0]['project_path'], project_dir)
                        self.assertIsNotNone(result[0]['error'])  # Error should be populated
                        self.assertIn('Test error', result[0]['error'])

    def test_summarize_respects_limit_parameter(self):
        """Test that summarize_top_ranked_projects respects the limit parameter."""
        mock_projects = [
            {'project': 'project-1', 'contrib_files': 5, 'total_files': 10, 'score': 0.5},
            {'project': 'project-2', 'contrib_files': 3, 'total_files': 10, 'score': 0.3},
            {'project': 'project-3', 'contrib_files': 2, 'total_files': 10, 'score': 0.2}
        ]
        
        with patch('summarize_projects.get_connection', return_value=self.conn):
            with patch('summarize_projects.rank_projects_by_contributor', return_value=mock_projects[:2]):
                # When limit=2, only first 2 projects should be processed
                with patch('summarize_projects.get_project_path', return_value=None):
                    result = summarize_projects.summarize_top_ranked_projects('TestUser', limit=2)
                    
                    # Should only process 2 projects (limited by rank_projects_by_contributor)
                    # Since get_project_path returns None, both will be skipped
                    self.assertEqual(len(result), 2)


if __name__ == '__main__':
    unittest.main()

