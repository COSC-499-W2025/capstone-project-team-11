import os
import unittest
import sys
import glob
import tempfile
import shutil
import subprocess
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from collab_summary import identify_contributions


class TestCollaborationSummary(unittest.TestCase):
    """Tests for identifying and summarizing contributions in both Git and non-Git projects."""

    def setUp(self):
        """Create a temporary test project directory."""
        self.test_dir = os.path.join(os.getcwd(), "temp_project")
        os.makedirs(self.test_dir, exist_ok=True)
        with open(os.path.join(self.test_dir, "example.txt"), "w") as f:
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
                result = identify_contributions(self.test_dir)
                self.assertIn(expected_author, result)

    def test_empty_folder_returns_empty_dict(self):
        """Empty folder returns {}."""
        empty_dir = tempfile.mkdtemp()
        result = identify_contributions(empty_dir)
        self.assertEqual(result, {})

    def test_git_repo_detects_commits(self):
        """Git repo should detect commit authors."""
        subprocess.run(["git", "init"], cwd=self.test_dir, check=True)
        subprocess.run(["git", "config", "user.name", "John Doe"], cwd=self.test_dir, check=True)
        subprocess.run(["git", "config", "user.email", "john@example.com"], cwd=self.test_dir, check=True)
        subprocess.run(["git", "add", "."], cwd=self.test_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=self.test_dir, check=True)

        result = identify_contributions(self.test_dir)
        self.assertIn("John Doe", result)
        self.assertGreaterEqual(result["John Doe"]["commits"], 1)

    def test_invalid_path_raises_error(self):
        """Invalid path raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            identify_contributions("fake_path_123")

    def test_json_output_file_created(self):
        """Should export a JSON summary file."""
        with tempfile.TemporaryDirectory() as output_dir:
            identify_contributions(self.test_dir, output_dir=output_dir)
            files = glob.glob(os.path.join(output_dir, "contributions_*.json"))
            self.assertTrue(len(files) > 0, "Expected at least one JSON file output")

    def test_json_output_file_content(self):
        """Should verify the content of the JSON summary file."""
        with tempfile.TemporaryDirectory() as output_dir:
            identify_contributions(self.test_dir, output_dir=output_dir)
            files = glob.glob(os.path.join(output_dir, "contributions_*.json"))
            self.assertTrue(len(files) > 0, "Expected at least one JSON file output")
            with open(files[0], "r") as f:
                data = json.load(f)
                self.assertIn("John", data)


if __name__ == "__main__":
    unittest.main()
