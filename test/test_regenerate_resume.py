import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import pytest

import regenerate_resume
import regenerate_resume_scan


class TestRegenerateResume(unittest.TestCase):
    def setUp(self):
        # Temporary directory for output and resume
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_root = os.path.join(self.temp_dir.name, "output")
        os.makedirs(self.output_root, exist_ok=True)
        self.resume_path = os.path.join(self.temp_dir.name, "resume.md")
        self.username = "testuser"

        # Create fake project JSON
        self.project_json_path = os.path.join(self.output_root, "proj1_info.json")
        with open(self.project_json_path, "w", encoding="utf-8") as f:
            f.write("""{
                "project_name": "proj1",
                "project_path": "/fake/path/proj1",
                "languages": ["Python"],
                "frameworks": ["Django"],
                "skills": ["Testing"],
                "contributions": {
                    "testuser": {
                        "commits": 5,
                        "files": ["a.py", "b.py"]
                    }
                },
                "git_metrics": {
                    "lines_added_per_author": {"testuser": 42},
                    "project_start": "2026-01-01"
                }
            }""")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_normalize_project_name_preserves_acronyms(self):
        result = regenerate_resume.normalize_project_name("api_service-python")
        self.assertIn("API", result)
        self.assertIn("Python", result)

    def test_aggregate_for_user_collects_projects_and_metrics(self):
        projects = regenerate_resume.collect_projects(self.output_root)
        agg = regenerate_resume.aggregate_for_user(self.username, projects)
        self.assertEqual(agg["username"], self.username)
        self.assertEqual(len(agg["projects"]), 1)
        self.assertIn("Python", agg["technologies"])
        self.assertIn("Django", agg["technologies"])
        self.assertIn("Testing", agg["skills"])
        self.assertEqual(agg["total_commits"], 5)
        self.assertEqual(agg["total_lines_added"], 42)

    def test_render_markdown_includes_key_sections(self):
        projects = regenerate_resume.collect_projects(self.output_root)
        agg = regenerate_resume.aggregate_for_user(self.username, projects)
        md = regenerate_resume.render_markdown(agg)
        self.assertIn("# Resume — testuser", md)
        self.assertIn("## Summary", md)
        self.assertIn("## Technical Skills", md)
        self.assertIn("## Projects", md)
        self.assertIn("## Evidence & Metrics", md)
        self.assertIn("Total commits (detected): 5", md)

    @patch("regenerate_resume.save_resume")
    def test_regenerate_resume_writes_file_and_saves_metadata(self, mock_save):
        regenerate_resume.regenerate_resume(self.username, self.resume_path, output_root=self.output_root)
        self.assertTrue(os.path.exists(self.resume_path))
        mock_save.assert_called_once()  # Ensures save_resume was called

    def test_regenerate_resume_missing_username_raises(self):
        with self.assertRaises(ValueError):
            regenerate_resume.regenerate_resume("", self.resume_path, output_root=self.output_root)

    def test_regenerate_resume_missing_path_raises(self):
        with self.assertRaises(ValueError):
            regenerate_resume.regenerate_resume(self.username, "", output_root=self.output_root)

    def test_regenerate_resume_missing_output_root_raises(self):
        with self.assertRaises(ValueError):
            regenerate_resume.regenerate_resume(self.username, self.resume_path, output_root="/nonexistent/path")


class TestRegenerateResumeScan(unittest.TestCase):
    @patch("regenerate_resume_scan.run_headless_scan")
    def test_resume_scan_calls_headless_scan(self, mock_scan):
        # create a fake directory
        with tempfile.TemporaryDirectory() as tmp:
            path = tmp
            regenerate_resume_scan.resume_scan(path)
            mock_scan.assert_called_once()
            args, kwargs = mock_scan.call_args
            self.assertEqual(kwargs["path"], path)
            self.assertTrue(kwargs["recursive"])
            self.assertTrue(kwargs["save_to_db"])

    def test_resume_scan_nonexistent_path_raises(self):
        with self.assertRaises(ValueError):
            regenerate_resume_scan.resume_scan("/nonexistent/path")

    @patch("regenerate_resume_scan.run_headless_scan")
    def test_resume_scan_with_zip_file_creates_temp_dir(self, mock_scan):
        with tempfile.TemporaryDirectory() as tmp:
            zip_path = os.path.join(tmp, "archive.zip")
            with open(zip_path, "w") as f:
                f.write("fake zip content")
            regenerate_resume_scan.resume_scan(zip_path)
            mock_scan.assert_called_once()
            args, kwargs = mock_scan.call_args
            self.assertEqual(kwargs["path"], zip_path)
            self.assertIsNotNone(kwargs["zip_extract_dir"])


if __name__ == "__main__":
    unittest.main()
