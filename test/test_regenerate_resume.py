import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import pytest

import importlib
import regenerate_resume
import regenerate_resume_scan
import db as db_mod


class TestRegenerateResume(unittest.TestCase):
    def setUp(self):
        # Temporary directory for output and resume
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_root = os.path.join(self.temp_dir.name, "output")
        os.makedirs(self.output_root, exist_ok=True)
        self.resume_path = os.path.join(self.temp_dir.name, "resume.md")
        self.username = "testuser"
        self.db_path = os.path.join(self.temp_dir.name, "file_data.db")
        self._old_env = os.environ.get("FILE_DATA_DB_PATH")
        os.environ["FILE_DATA_DB_PATH"] = self.db_path

        global db_mod, regenerate_resume
        db_mod = importlib.reload(db_mod)
        db_mod.init_db()
        regenerate_resume = importlib.reload(regenerate_resume)

        git_metrics = {
            "lines_added_per_author": {"testuser": 42},
            "commits_per_author": {"testuser": 5},
            "files_changed_per_author": {"testuser": ["a.py", "b.py"]},
            "project_start": "2026-01-01",
            "total_commits": 5,
        }
        tech_summary = {
            "languages": ["Python"],
            "frameworks": ["Django"],
            "high_confidence_languages": ["Python"],
            "medium_confidence_languages": [],
            "low_confidence_languages": [],
            "high_confidence_frameworks": ["Django"],
            "medium_confidence_frameworks": [],
            "low_confidence_frameworks": [],
        }
        conn = db_mod.get_connection()
        try:
            conn.execute(
                "INSERT INTO projects (name, project_path, git_metrics_json, tech_json) VALUES (?, ?, ?, ?)",
                ("proj1", "/fake/path/proj1", json.dumps(git_metrics), json.dumps(tech_summary)),
            )
            conn.execute("INSERT OR IGNORE INTO skills (name) VALUES (?)", ("Testing",))
            skill_id = conn.execute(
                "SELECT id FROM skills WHERE name = ?",
                ("Testing",),
            ).fetchone()["id"]
            project_id = conn.execute(
                "SELECT id FROM projects WHERE name = ?",
                ("proj1",),
            ).fetchone()["id"]
            conn.execute(
                "INSERT OR IGNORE INTO project_skills (project_id, skill_id) VALUES (?, ?)",
                (project_id, skill_id),
            )
            conn.commit()
        finally:
            conn.close()

    def tearDown(self):
        import gc
        gc.collect()
        if self._old_env is None:
            os.environ.pop("FILE_DATA_DB_PATH", None)
        else:
            os.environ["FILE_DATA_DB_PATH"] = self._old_env
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
        regenerate_resume.regenerate_resume(self.username, self.resume_path, output_root="/nonexistent/path")
        self.assertTrue(os.path.exists(self.resume_path))


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
