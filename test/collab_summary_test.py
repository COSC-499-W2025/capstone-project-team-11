import os
import unittest
import sys
import glob
import tempfile
import shutil
import subprocess
import json
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from collab_summary import identify_contributions, summarize_contributions_non_git, is_git_repo


class TestCollaborationSummary(unittest.TestCase):
    """Tests for identifying and summarizing contributions in both Git and non-Git projects."""

    def setUp(self):
        """Create a temporary test project directory."""
        self.test_dir = tempfile.mkdtemp()
        with open(os.path.join(self.test_dir, "example.txt"), "w", encoding="utf-8") as f:
            f.write("# Author: John\nprint('test')")

    def tearDown(self):
        """Clean up any created test files or directories."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_non_git_detects_author(self):
        """Detects author from inline comment in non-Git project."""
        test_cases = [
            ("# Author: John\nprint('test')", "John"),
            ("// Author: Alice\nconsole.log('x')", "Alice"),
            ("/* Author: Bob */\nint main() {}", "Bob"),
            ("print('no author here')", "Unknown"),
        ]
        for content, expected_author in test_cases:
            with self.subTest(content=content):
                with open(os.path.join(self.test_dir, "example.txt"), "w") as f:
                    f.write(content)
                result = summarize_contributions_non_git(self.test_dir)
                self.assertIn(expected_author, result)

    def test_non_git_multiple_authors(self):
        """Detects multiple authors in a single file."""
        content = "# Author: Alice\n# Author: Bob\nprint('test')"
        with open(os.path.join(self.test_dir, "example.txt"), "w") as f:
            f.write(content)
        result = summarize_contributions_non_git(self.test_dir)
        self.assertIn("Alice", result)
        self.assertIn("Bob", result)

    def test_empty_folder_returns_empty_dict(self):
        """Empty folder returns {}."""
        empty_dir = tempfile.mkdtemp()
        result = summarize_contributions_non_git(empty_dir)
        self.assertEqual(result, {})

    def test_git_repo_detects_commits(self):
        """Git repo should detect commit authors."""
        subprocess.run(["git", "init"], cwd=self.test_dir, check=True)
        subprocess.run(["git", "config", "user.name", "John Doe"], cwd=self.test_dir, check=True)
        subprocess.run(["git", "config", "user.email", "john@example.com"], cwd=self.test_dir, check=True)
        subprocess.run(["git", "add", "."], cwd=self.test_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=self.test_dir, check=True)

        # Use strict_git=True so we don't walk up into the real repo
        result = identify_contributions(self.test_dir, strict_git=True)

        keys = list(result.keys())
        # identify_contributions uses canonicalized author keys (e.g. 'johndoe')
        self.assertTrue(any('john' in k.lower() for k in keys), msg=f"Expected an author containing 'john' in {keys}")
        self.assertTrue(any(v.get('commits', 0) >= 1 for v in result.values()))

    def test_invalid_path_raises_error(self):
        """Invalid path raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            identify_contributions("fake_path_123")

                
    def test_git_repo_tracks_changed_files(self):
        """Git repo should include per-author changed files in contribution summary."""
        subprocess.run(["git", "init"], cwd=self.test_dir, check=True)
        subprocess.run(["git", "config", "user.name", "John Doe"], cwd=self.test_dir, check=True)
        subprocess.run(["git", "config", "user.email", "john@example.com"], cwd=self.test_dir, check=True)

        # Create and commit a file
        file_path = os.path.join(self.test_dir, "scan.py")
        with open(file_path, "w") as f:
            f.write("print('hello')")
        subprocess.run(["git", "add", "scan.py"], cwd=self.test_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Add scan.py"], cwd=self.test_dir, check=True)

        result = identify_contributions(self.test_dir, strict_git=True)

        # Ensure some author was detected and that at least one author's file list contains scan.py
        keys = list(result.keys())
        self.assertTrue(any('john' in k.lower() for k in keys), msg=f"Expected an author containing 'john' in {keys}")
        self.assertTrue(any('scan.py' in f for v in result.values() for f in v.get('files', [])), msg="Changed file scan.py should appear in some author's file list")



if __name__ == "__main__":
    unittest.main()
