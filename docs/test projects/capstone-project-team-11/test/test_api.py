import json
import os
import sys
import tempfile
import unittest

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from api import app
from config import config_path
from db import get_connection, init_db


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "file_data.db")
        self.home_dir = os.path.join(self.tmpdir.name, "home")
        os.makedirs(self.home_dir, exist_ok=True)

        self._old_env = dict(os.environ)
        os.environ["FILE_DATA_DB_PATH"] = self.db_path
        os.environ["HOME"] = self.home_dir

        init_db()
        self.client = TestClient(app)

        self.output_root = os.path.join(self.tmpdir.name, "output")
        os.makedirs(self.output_root, exist_ok=True)
        self.resume_dir = os.path.join(self.tmpdir.name, "resumes")
        self.portfolio_dir = os.path.join(self.tmpdir.name, "portfolios")

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._old_env)
        self.tmpdir.cleanup()

    def _write_project_info(self, username="alice"):
        proj_dir = os.path.join(self.output_root, "demo_project")
        os.makedirs(proj_dir, exist_ok=True)
        payload = {
            "project_name": "demo_project",
            "project_path": proj_dir,
            "detected_type": "coding_project",
            "languages": ["Python"],
            "frameworks": ["FastAPI"],
            "skills": ["APIs"],
            "high_confidence_languages": ["Python"],
            "medium_confidence_languages": [],
            "low_confidence_languages": [],
            "high_confidence_frameworks": ["FastAPI"],
            "medium_confidence_frameworks": [],
            "low_confidence_frameworks": [],
            "contributions": {
                username: {"commits": 2, "files": ["main.py"]},
            },
            "git_metrics": {"project_start": "2025-01-01 00:00:00"},
        }
        info_path = os.path.join(proj_dir, "demo_project_info_20250101.json")
        with open(info_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh)

    def test_privacy_consent(self):
        resp = self.client.post("/privacy-consent", json={"data_consent": True})
        self.assertEqual(resp.status_code, 200)
        cfg_path = config_path()
        self.assertTrue(os.path.isfile(cfg_path))
        with open(cfg_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        self.assertTrue(data.get("data_consent"))

    def test_projects_upload_and_list(self):
        self.client.post("/privacy-consent", json={"data_consent": True})
        project_dir = os.path.join(self.tmpdir.name, "project")
        os.makedirs(project_dir, exist_ok=True)
        with open(os.path.join(project_dir, "main.py"), "w", encoding="utf-8") as fh:
            fh.write("print('hello')\n")

        resp = self.client.post(
            "/projects/upload",
            json={
                "project_path": project_dir,
                "recursive_choice": False,
                "file_type": ".py",
                "save_to_db": True,
            },
        )
        self.assertEqual(resp.status_code, 201)
        body = resp.json()
        self.assertTrue(body.get("scan_id"))

        resp_list = self.client.get("/projects")
        self.assertEqual(resp_list.status_code, 200)
        self.assertTrue(isinstance(resp_list.json(), list))

    def test_project_detail_and_skills(self):
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO projects (name, repo_url, created_at, thumbnail_path) VALUES (?, ?, ?, ?)",
                ("demo_project", "https://example.com", "2025-01-01", None),
            )
            project_id = conn.execute(
                "SELECT id FROM projects WHERE name = ?", ("demo_project",)
            ).fetchone()["id"]
            conn.execute(
                "INSERT INTO scans (project, notes) VALUES (?, ?)",
                ("demo_project", "notes"),
            )
            scan_id = conn.execute(
                "SELECT id FROM scans WHERE project = ?", ("demo_project",)
            ).fetchone()["id"]
            conn.execute(
                """
                INSERT INTO files
                (scan_id, file_name, file_path, file_extension, file_size, created_at, modified_at, owner, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scan_id,
                    "main.py",
                    "/tmp/main.py",
                    ".py",
                    10,
                    None,
                    None,
                    "alice",
                    "{}",
                ),
            )
            conn.execute("INSERT INTO languages (name) VALUES (?)", ("Python",))
            lang_id = conn.execute(
                "SELECT id FROM languages WHERE name = ?", ("Python",)
            ).fetchone()["id"]
            file_id = conn.execute(
                "SELECT id FROM files WHERE scan_id = ?", (scan_id,)
            ).fetchone()["id"]
            conn.execute(
                "INSERT INTO file_languages (file_id, language_id) VALUES (?, ?)",
                (file_id, lang_id),
            )
            conn.execute("INSERT INTO contributors (name) VALUES (?)", ("alice",))
            contrib_id = conn.execute(
                "SELECT id FROM contributors WHERE name = ?", ("alice",)
            ).fetchone()["id"]
            conn.execute(
                "INSERT INTO file_contributors (file_id, contributor_id) VALUES (?, ?)",
                (file_id, contrib_id),
            )
            conn.execute("INSERT INTO skills (name) VALUES (?)", ("APIs",))
            skill_id = conn.execute(
                "SELECT id FROM skills WHERE name = ?", ("APIs",)
            ).fetchone()["id"]
            conn.execute(
                "INSERT INTO project_skills (project_id, skill_id) VALUES (?, ?)",
                (project_id, skill_id),
            )
            conn.execute(
                """
                INSERT INTO project_evidence (project_id, type, description, value, source, url)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (project_id, "award", "demo", "winner", "internal", None),
            )
            conn.commit()

        resp = self.client.get(f"/projects/{project_id}")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("project", data)
        self.assertIn("languages", data)
        self.assertIn("skills", data)
        self.assertIn("contributors", data)
        self.assertIn("files_summary", data)

        skills_resp = self.client.get("/skills")
        self.assertEqual(skills_resp.status_code, 200)
        self.assertIn("APIs", skills_resp.json())

    def test_resume_generate_get_edit(self):
        self._write_project_info()
        resp = self.client.post(
            "/resume/generate",
            json={
                "username": "alice",
                "output_root": self.output_root,
                "resume_dir": self.resume_dir,
                "save_to_db": True,
            },
        )
        self.assertEqual(resp.status_code, 201)
        resume_id = resp.json().get("resume_id")
        self.assertTrue(resume_id)

        resp_get = self.client.get(f"/resume/{resume_id}")
        self.assertEqual(resp_get.status_code, 200)
        self.assertIn("# Resume — alice", resp_get.json().get("content", ""))

        resp_edit = self.client.post(
            f"/resume/{resume_id}/edit",
            json={"content": "# Resume — alice\nUpdated\n", "metadata": {"edited": True}},
        )
        self.assertEqual(resp_edit.status_code, 200)
        self.assertTrue(resp_edit.json()["metadata"].get("edited"))

    def test_portfolio_generate_get_edit(self):
        self._write_project_info()
        resp = self.client.post(
            "/portfolio/generate",
            json={
                "username": "alice",
                "output_root": self.output_root,
                "portfolio_dir": self.portfolio_dir,
                "confidence_level": "high",
                "save_to_db": True,
            },
        )
        self.assertEqual(resp.status_code, 201)
        portfolio_id = resp.json().get("portfolio_id")
        self.assertTrue(portfolio_id)

        resp_get = self.client.get(f"/portfolio/{portfolio_id}")
        self.assertEqual(resp_get.status_code, 200)
        self.assertIn("# Portfolio — alice", resp_get.json().get("content", ""))

        resp_edit = self.client.post(
            f"/portfolio/{portfolio_id}/edit",
            json={"content": "# Portfolio — alice\nUpdated\n", "metadata": {"edited": True}},
        )
        self.assertEqual(resp_edit.status_code, 200)
        self.assertTrue(resp_edit.json()["metadata"].get("edited"))


if __name__ == "__main__":
    unittest.main()
