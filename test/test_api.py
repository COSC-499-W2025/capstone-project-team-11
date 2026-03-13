import json
import importlib
import os
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import api as api_mod
from config import config_path
import db as db_mod


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "file_data.db")
        self.home_dir = os.path.join(self.tmpdir.name, "home")
        os.makedirs(self.home_dir, exist_ok=True)

        self._old_env = dict(os.environ)
        os.environ["FILE_DATA_DB_PATH"] = self.db_path
        os.environ["HOME"] = self.home_dir

        global db_mod, api_mod
        db_mod = importlib.reload(db_mod)
        db_mod.init_db()
        api_mod = importlib.reload(api_mod)
        self.client = TestClient(api_mod.app)

        self.output_root = os.path.join(self.tmpdir.name, "output")
        os.makedirs(self.output_root, exist_ok=True)
        self.resume_dir = os.path.join(self.tmpdir.name, "resumes")
        self.portfolio_dir = os.path.join(self.tmpdir.name, "portfolios")

    def tearDown(self):
        try:
            if getattr(self, "client", None) is not None:
                self.client.close()
        except Exception:
            pass
        os.environ.clear()
        os.environ.update(self._old_env)
        import gc
        gc.collect()
        self.tmpdir.cleanup()

    def _write_project_info(self, username="alice"):
        proj_dir = os.path.join(self.tmpdir.name, "demo_project")
        os.makedirs(proj_dir, exist_ok=True)
        git_metrics = {
            "project_start": "2025-01-01 00:00:00",
            "commits_per_author": {username: 2},
            "lines_added_per_author": {username: 10},
            "files_changed_per_author": {username: ["main.py"]},
            "total_commits": 2,
        }
        tech_summary = {
            "languages": ["Python"],
            "frameworks": ["FastAPI"],
            "high_confidence_languages": ["Python"],
            "medium_confidence_languages": [],
            "low_confidence_languages": [],
            "high_confidence_frameworks": ["FastAPI"],
            "medium_confidence_frameworks": [],
            "low_confidence_frameworks": [],
        }
        with db_mod.get_connection() as conn:
            conn.execute(
                "INSERT INTO projects (name, project_path, git_metrics_json, tech_json) VALUES (?, ?, ?, ?)",
                ("demo_project", proj_dir, json.dumps(git_metrics), json.dumps(tech_summary)),
            )
            conn.execute("INSERT OR IGNORE INTO skills (name) VALUES (?)", ("APIs",))
            skill_id = conn.execute(
                "SELECT id FROM skills WHERE name = ?",
                ("APIs",),
            ).fetchone()["id"]
            project_id = conn.execute(
                "SELECT id FROM projects WHERE name = ?",
                ("demo_project",),
            ).fetchone()["id"]
            conn.execute(
                "INSERT OR IGNORE INTO project_skills (project_id, skill_id) VALUES (?, ?)",
                (project_id, skill_id),
            )
            conn.commit()

    def _seed_web_portfolio_data(self, username="alice"):
        proj_dir = os.path.join(self.tmpdir.name, "demo_web_project")
        os.makedirs(proj_dir, exist_ok=True)
        portfolio_file = os.path.join(self.portfolio_dir, "portfolio_seed.md")
        os.makedirs(self.portfolio_dir, exist_ok=True)
        with open(portfolio_file, "w", encoding="utf-8") as fh:
            fh.write("# Seed Portfolio\n")

        with db_mod.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO projects (name, project_path, thumbnail_path, git_metrics_json, tech_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "demo_web_project",
                    proj_dir,
                    "/tmp/thumb.png",
                    json.dumps(
                        {
                            "project_start": "2025-01-01 00:00:00",
                            "commits_per_author": {"alice": 3, "bob": 1},
                            "files_changed_per_author": {"alice": ["main.py"], "bob": ["utils.py"]},
                        }
                    ),
                    json.dumps({"languages": ["Python"], "frameworks": ["FastAPI"]}),
                ),
            )
            project_id = conn.execute(
                "SELECT id FROM projects WHERE name = ?",
                ("demo_web_project",),
            ).fetchone()["id"]

            conn.execute("INSERT OR IGNORE INTO skills (name) VALUES (?)", ("APIs",))
            conn.execute("INSERT OR IGNORE INTO skills (name) VALUES (?)", ("Testing",))
            skill_rows = conn.execute(
                "SELECT id FROM skills WHERE name IN (?, ?)",
                ("APIs", "Testing"),
            ).fetchall()
            for row in skill_rows:
                conn.execute(
                    "INSERT OR IGNORE INTO project_skills (project_id, skill_id) VALUES (?, ?)",
                    (project_id, row["id"]),
                )

            conn.execute(
                "INSERT INTO scans (project, scanned_at, notes) VALUES (?, ?, ?)",
                ("demo_web_project", "2025-01-10 10:00:00", "init"),
            )
            conn.execute(
                "INSERT INTO scans (project, scanned_at, notes) VALUES (?, ?, ?)",
                ("demo_web_project", "2025-02-14 12:00:00", "improved"),
            )
            scan_rows = conn.execute(
                "SELECT id FROM scans WHERE project = ? ORDER BY scanned_at ASC",
                ("demo_web_project",),
            ).fetchall()

            conn.execute("INSERT OR IGNORE INTO contributors (name) VALUES (?)", ("alice",))
            conn.execute("INSERT OR IGNORE INTO contributors (name) VALUES (?)", ("bob",))
            alice_id = conn.execute(
                "SELECT id FROM contributors WHERE name = ?",
                ("alice",),
            ).fetchone()["id"]
            bob_id = conn.execute(
                "SELECT id FROM contributors WHERE name = ?",
                ("bob",),
            ).fetchone()["id"]

            for idx, scan in enumerate(scan_rows):
                conn.execute(
                    """
                    INSERT INTO files
                    (scan_id, file_name, file_path, file_extension, file_size, created_at, modified_at, owner, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        scan["id"],
                        f"file_{idx}.py",
                        f"/tmp/file_{idx}.py",
                        ".py",
                        120 + idx,
                        None,
                        None,
                        "alice",
                        "{}",
                    ),
                )
                file_id = conn.execute(
                    "SELECT id FROM files WHERE scan_id = ? ORDER BY id DESC LIMIT 1",
                    (scan["id"],),
                ).fetchone()["id"]
                conn.execute(
                    "INSERT OR IGNORE INTO file_contributors (file_id, contributor_id) VALUES (?, ?)",
                    (file_id, alice_id),
                )
                if idx == 0:
                    conn.execute(
                        "INSERT OR IGNORE INTO file_contributors (file_id, contributor_id) VALUES (?, ?)",
                        (file_id, bob_id),
                    )

            conn.execute(
                """
                INSERT INTO project_evidence (project_id, type, description, value, source, url)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (project_id, "impact", "Shipped API dashboard", "v1", "internal", None),
            )
            conn.commit()

        portfolio_id = db_mod.save_portfolio(username=username, portfolio_path=portfolio_file, metadata={}, generated_at="2025-02-14 12:00:00Z")
        return portfolio_id, project_id

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

    def test_scan_plan_reports_projects_and_existing_contributors(self):
        self.client.post("/privacy-consent", json={"data_consent": True})

        root_dir = os.path.join(self.tmpdir.name, "workspace")
        git_project = os.path.join(root_dir, "git_project")
        nongit_project = os.path.join(root_dir, "nongit_project")
        os.makedirs(os.path.join(git_project, ".git"), exist_ok=True)
        os.makedirs(nongit_project, exist_ok=True)

        with open(os.path.join(git_project, "main.py"), "w", encoding="utf-8") as fh:
            fh.write("print('git')\n")
        with open(os.path.join(nongit_project, "app.js"), "w", encoding="utf-8") as fh:
            fh.write("console.log('nongit');\n")

        with db_mod.get_connection() as conn:
            conn.execute("INSERT INTO contributors (name) VALUES (?)", ("alice",))
            conn.commit()

        resp = self.client.post("/projects/scan-plan", json={"project_path": root_dir})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["total_projects"], 2)
        self.assertIn("alice", body["existing_contributors"])
        projects = {item["project_name"]: item for item in body["projects"]}
        self.assertTrue(projects["git_project"]["is_git"])
        self.assertFalse(projects["git_project"]["requires_contributor_assignment"])
        self.assertFalse(projects["nongit_project"]["is_git"])
        self.assertTrue(projects["nongit_project"]["requires_contributor_assignment"])

    def test_scan_plan_for_zip_detects_inner_projects_not_zip_file(self):
        self.client.post("/privacy-consent", json={"data_consent": True})

        source_dir = os.path.join(self.tmpdir.name, "zip_workspace")
        git_project = os.path.join(source_dir, "git_project")
        other_project = os.path.join(source_dir, "other_project")
        os.makedirs(os.path.join(git_project, ".git"), exist_ok=True)
        os.makedirs(other_project, exist_ok=True)

        with open(os.path.join(git_project, "main.py"), "w", encoding="utf-8") as fh:
            fh.write("print('git')\n")
        with open(os.path.join(other_project, "app.js"), "w", encoding="utf-8") as fh:
            fh.write("console.log('other');\n")

        zip_path = os.path.join(self.tmpdir.name, "projects.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            for root, _, files in os.walk(source_dir):
                for file_name in files:
                    full_path = os.path.join(root, file_name)
                    rel_path = os.path.relpath(full_path, source_dir)
                    zf.write(full_path, arcname=rel_path)

        resp = self.client.post("/projects/scan-plan", json={"project_path": zip_path})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["total_projects"], 2)
        project_names = sorted(item["project_name"] for item in body["projects"])
        self.assertEqual(project_names, ["git_project", "other_project"])
        self.assertTrue(all(not item["project_name"].endswith(".zip") for item in body["projects"]))

    def test_scan_stream_includes_structured_multi_project_results(self):
        self.client.post("/privacy-consent", json={"data_consent": True})

        root_dir = os.path.join(self.tmpdir.name, "stream_project")
        os.makedirs(root_dir, exist_ok=True)

        fake_result = {
            "success": True,
            "partial_success": True,
            "project_name": "workspace",
            "project_names": ["proj_a"],
            "project_results": [
                {"project_name": "proj_a", "project_path": "/tmp/proj_a", "success": True},
                {"project_name": "proj_b", "project_path": "/tmp/proj_b", "success": False, "error": "boom"},
            ],
            "failed_projects": [
                {"project_name": "proj_b", "project_path": "/tmp/proj_b", "error": "boom"},
            ],
            "output_dir": None,
            "error": None,
        }

        with patch.object(api_mod, "scan_with_clean_output", return_value=fake_result), \
             patch.object(api_mod, "_load_latest_project_summary", return_value={"project_name": "proj_a"}), \
             patch.object(api_mod, "_load_llm_summary", return_value=None):
            with self.client.stream(
                "POST",
                "/projects/scan-stream",
                json={
                    "project_path": root_dir,
                    "manual_contributors_by_path": {"/tmp/proj_b": ["alice"]},
                },
            ) as resp:
                self.assertEqual(resp.status_code, 200)
                body = "".join(resp.iter_text())

        self.assertIn("SCAN_DONE::", body)
        payload = json.loads(body.split("SCAN_DONE::", 1)[1].strip())
        self.assertTrue(payload["success"])
        self.assertTrue(payload["partial_success"])
        self.assertEqual(len(payload["failed_projects"]), 1)
        self.assertEqual(payload["failed_projects"][0]["project_name"], "proj_b")

    def test_project_detail_and_skills(self):
        with db_mod.get_connection() as conn:
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

    def test_web_portfolio_endpoints(self):
        portfolio_id, project_id = self._seed_web_portfolio_data()

        timeline_resp = self.client.get(f"/web/portfolio/{portfolio_id}/timeline")
        self.assertEqual(timeline_resp.status_code, 200)
        timeline_body = timeline_resp.json()
        self.assertIn("timeline", timeline_body)
        self.assertTrue(isinstance(timeline_body["timeline"], list))

        heatmap_resp = self.client.get(f"/web/portfolio/{portfolio_id}/heatmap?granularity=month&metric=files")
        self.assertEqual(heatmap_resp.status_code, 200)
        heatmap_body = heatmap_resp.json()
        self.assertIn("cells", heatmap_body)
        self.assertTrue(heatmap_body["max_value"] >= 0)

        showcase_resp = self.client.get(f"/web/portfolio/{portfolio_id}/showcase")
        self.assertEqual(showcase_resp.status_code, 200)
        showcase_body = showcase_resp.json()
        self.assertIn("projects", showcase_body)
        self.assertLessEqual(len(showcase_body["projects"]), 3)

        customize_resp = self.client.patch(
            f"/web/portfolio/{portfolio_id}/customize",
            json={
                "is_public": False,
                "selected_project_ids": [project_id],
                "showcase_project_ids": [project_id],
                "hidden_skills": ["Testing"],
            },
        )
        self.assertEqual(customize_resp.status_code, 200)
        self.assertFalse(customize_resp.json()["web_config"]["is_public"])

        public_blocked_resp = self.client.get(f"/web/portfolio/{portfolio_id}/timeline?mode=public")
        self.assertEqual(public_blocked_resp.status_code, 403)

        private_ok_resp = self.client.get(f"/web/portfolio/{portfolio_id}/timeline?mode=private")
        self.assertEqual(private_ok_resp.status_code, 200)


    def test_delete_project_endpoint(self):
        with api_mod.get_connection() as conn:
            conn.execute(
                "INSERT INTO projects (name, repo_url) VALUES (?, ?)",
                ("Delete Me", None),
            )
            project_id = conn.execute(
                "SELECT id FROM projects WHERE name = ?",
                ("Delete Me",),
            ).fetchone()["id"]
            conn.commit()

        resp = self.client.delete(f"/projects/{project_id}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["message"], "Project deleted successfully")

        with api_mod.get_connection() as conn:
            row = conn.execute(
                "SELECT id FROM projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            self.assertIsNone(row)

    def test_project_details_includes_llm_summary(self):
        with api_mod.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO projects
                (name, repo_url, summary_text, summary_model, summary_updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "LLM Project",
                    None,
                    "This is an LLM-generated summary.",
                    "llama3",
                    "2026-03-11T12:00:00",
                ),
            )
            project_id = conn.execute(
                "SELECT id FROM projects WHERE name = ?",
                ("LLM Project",),
            ).fetchone()["id"]
            conn.commit()

        resp = self.client.get(f"/projects/{project_id}")
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIn("llm_summary", data)
        self.assertIsNotNone(data["llm_summary"])
        self.assertEqual(data["llm_summary"]["text"], "This is an LLM-generated summary.")
        self.assertEqual(data["llm_summary"]["model"], "llama3")
        self.assertEqual(data["llm_summary"]["updated_at"], "2026-03-11T12:00:00")

        def test_delete_project_endpoint(self):
         with api_mod.get_connection() as conn:
            conn.execute(
                "INSERT INTO projects (name, repo_url) VALUES (?, ?)",
                ("Delete Me", None),
            )
            project_id = conn.execute(
                "SELECT id FROM projects WHERE name = ?",
                ("Delete Me",),
            ).fetchone()["id"]
            conn.commit()

        resp = self.client.delete(f"/projects/{project_id}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["message"], "Project deleted successfully")

        with api_mod.get_connection() as conn:
            row = conn.execute(
                "SELECT id FROM projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            self.assertIsNone(row)

    def test_project_details_includes_llm_summary(self):
        with api_mod.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO projects
                (name, repo_url, summary_text, summary_model, summary_updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "LLM Project",
                    None,
                    "This is an LLM-generated summary.",
                    "llama3",
                    "2026-03-11T12:00:00",
                ),
            )
            project_id = conn.execute(
                "SELECT id FROM projects WHERE name = ?",
                ("LLM Project",),
            ).fetchone()["id"]
            conn.commit()

        resp = self.client.get(f"/projects/{project_id}")
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIn("llm_summary", data)
        self.assertIsNotNone(data["llm_summary"])
        self.assertEqual(data["llm_summary"]["text"], "This is an LLM-generated summary.")
        self.assertEqual(data["llm_summary"]["model"], "llama3")
        self.assertEqual(data["llm_summary"]["updated_at"], "2026-03-11T12:00:00")

    def test_update_project_endpoint(self):
        with api_mod.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO projects (name, custom_name, repo_url, thumbnail_path)
                VALUES (?, ?, ?, ?)
                """,
                ("demo_project", None, "https://old-url.com", "/old/thumb.png"),
            )
            project_id = conn.execute(
                "SELECT id FROM projects WHERE name = ?",
                ("demo_project",),
            ).fetchone()["id"]
            conn.commit()

        resp = self.client.patch(
            f"/projects/{project_id}",
            json={
                "custom_name": "Updated Display Name",
                "repo_url": "https://new-url.com",
                "thumbnail_path": "/new/thumb.png",
            },
        )

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("project", body)
        self.assertEqual(body["project"]["custom_name"], "Updated Display Name")
        self.assertEqual(body["project"]["repo_url"], "https://new-url.com")
        self.assertEqual(body["project"]["thumbnail_path"], "/new/thumb.png")

        with api_mod.get_connection() as conn:
            row = conn.execute(
                """
                SELECT custom_name, repo_url, thumbnail_path
                FROM projects
                WHERE id = ?
                """,
                (project_id,),
            ).fetchone()

        self.assertEqual(row["custom_name"], "Updated Display Name")
        self.assertEqual(row["repo_url"], "https://new-url.com")
        self.assertEqual(row["thumbnail_path"], "/new/thumb.png")

    def test_delete_project_endpoint_removes_orphaned_contributors_and_languages(self):
        with api_mod.get_connection() as conn:
            conn.execute(
                "INSERT INTO projects (name, repo_url) VALUES (?, ?)",
                ("Delete Me", None),
            )
            project_id = conn.execute(
                "SELECT id FROM projects WHERE name = ?",
                ("Delete Me",),
            ).fetchone()["id"]

            conn.execute(
                "INSERT INTO scans (project, notes) VALUES (?, ?)",
                ("Delete Me", "notes"),
            )
            scan_id = conn.execute(
                "SELECT id FROM scans WHERE project = ?",
                ("Delete Me",),
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
            file_id = conn.execute(
                "SELECT id FROM files WHERE scan_id = ?",
                (scan_id,),
            ).fetchone()["id"]

            conn.execute("INSERT INTO contributors (name) VALUES (?)", ("alice",))
            contributor_id = conn.execute(
                "SELECT id FROM contributors WHERE name = ?",
                ("alice",),
            ).fetchone()["id"]

            conn.execute("INSERT INTO languages (name) VALUES (?)", ("Python",))
            language_id = conn.execute(
                "SELECT id FROM languages WHERE name = ?",
                ("Python",),
            ).fetchone()["id"]

            conn.execute(
                "INSERT INTO file_contributors (file_id, contributor_id) VALUES (?, ?)",
                (file_id, contributor_id),
            )
            conn.execute(
                "INSERT INTO file_languages (file_id, language_id) VALUES (?, ?)",
                (file_id, language_id),
            )
            conn.commit()

        resp = self.client.delete(f"/projects/{project_id}")
        self.assertEqual(resp.status_code, 200)

        with api_mod.get_connection() as conn:
            contributor_row = conn.execute(
                "SELECT id FROM contributors WHERE name = ?",
                ("alice",),
            ).fetchone()
            language_row = conn.execute(
                "SELECT id FROM languages WHERE name = ?",
                ("Python",),
            ).fetchone()

        self.assertIsNone(contributor_row)
        self.assertIsNone(language_row)   


if __name__ == "__main__":
    unittest.main()


    
