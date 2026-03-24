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

        portfolio_id = db_mod.save_portfolio(username=username, portfolio_name="Test Portfolio", included_project_ids=[project_id], created_at="2025-02-14 12:00:00Z")
        return portfolio_id, project_id

    def test_privacy_consent(self):
        resp = self.client.post("/privacy-consent", json={"data_consent": True})
        self.assertEqual(resp.status_code, 200)
        cfg_path = config_path()
        self.assertTrue(os.path.isfile(cfg_path))
        with open(cfg_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        self.assertTrue(data.get("data_consent"))

    def test_get_config_returns_consent_flags(self):
        # Write a known config state using the privacy-consent endpoint first
        self.client.post("/privacy-consent", json={
            "data_consent": True,
            "llm_summary_consent": False,
            "llm_resume_consent": True,
        })

        resp = self.client.get("/config")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("data_consent", body)
        self.assertIn("llm_summary_consent", body)
        self.assertIn("llm_resume_consent", body)
        self.assertIsInstance(body["data_consent"], bool)
        self.assertIsInstance(body["llm_summary_consent"], bool)
        self.assertIsInstance(body["llm_resume_consent"], bool)
        self.assertTrue(body["data_consent"])
        self.assertFalse(body["llm_summary_consent"])
        self.assertTrue(body["llm_resume_consent"])

    def test_list_resumes_empty(self):
        resp = self.client.get("/resumes")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), [])

    def test_list_resumes_filters_by_username(self):
        # Seed two resumes for different users directly into the DB
        resume_dir = os.path.join(self.tmpdir.name, "resumes")
        os.makedirs(resume_dir, exist_ok=True)

        alice_path = os.path.join(resume_dir, "resume_alice.md")
        bob_path = os.path.join(resume_dir, "resume_bob.md")
        with open(alice_path, "w") as f:
            f.write("# Resume — alice\n")
        with open(bob_path, "w") as f:
            f.write("# Resume — bob\n")

        with db_mod.get_connection() as conn:
            conn.execute(
                "INSERT INTO resumes (username, resume_path, metadata_json, generated_at) VALUES (?, ?, ?, ?)",
                ("alice", alice_path, "{}", "2026-01-01 10:00:00Z"),
            )
            conn.execute(
                "INSERT INTO resumes (username, resume_path, metadata_json, generated_at) VALUES (?, ?, ?, ?)",
                ("bob", bob_path, "{}", "2026-01-02 10:00:00Z"),
            )
            conn.commit()

        resp = self.client.get("/resumes?username=alice")
        self.assertEqual(resp.status_code, 200)
        results = resp.json()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["username"], "alice")

    def test_list_resumes_llm_used_flag(self):
        resume_dir = os.path.join(self.tmpdir.name, "resumes")
        os.makedirs(resume_dir, exist_ok=True)

        llm_path = os.path.join(resume_dir, "resume_llm.md")
        no_llm_path = os.path.join(resume_dir, "resume_no_llm.md")
        with open(llm_path, "w") as f:
            f.write("# Resume — alice\n")
        with open(no_llm_path, "w") as f:
            f.write("# Resume — alice\n")

        with db_mod.get_connection() as conn:
            conn.execute(
                "INSERT INTO resumes (username, resume_path, metadata_json, generated_at) VALUES (?, ?, ?, ?)",
                ("alice", llm_path, json.dumps({"llm_summary": "Some summary text"}), "2026-01-01 10:00:00Z"),
            )
            conn.execute(
                "INSERT INTO resumes (username, resume_path, metadata_json, generated_at) VALUES (?, ?, ?, ?)",
                ("alice", no_llm_path, json.dumps({}), "2026-01-02 10:00:00Z"),
            )
            conn.commit()

        resp = self.client.get("/resumes?username=alice")
        self.assertEqual(resp.status_code, 200)
        results = resp.json()
        # ordered by generated_at DESC so no_llm is first
        self.assertFalse(results[0]["llm_used"])
        self.assertTrue(results[1]["llm_used"])

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
        self.assertIn("contributor_roles", data)
        self.assertIn("files_summary", data)
        self.assertTrue(isinstance(data["contributor_roles"], dict))
        self.assertIn("contributors", data["contributor_roles"])
        self.assertTrue(len(data["contributor_roles"]["contributors"]) >= 1)
        self.assertEqual(data["contributor_roles"]["contributors"][0]["name"], "alice")

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

    def test_resume_pdf_download(self):
        resume_dir = os.path.join(self.tmpdir.name, "resumes")
        os.makedirs(resume_dir, exist_ok=True)
        resume_path = os.path.join(resume_dir, "resume_alice.md")
        with open(resume_path, "w", encoding="utf-8") as f:
            f.write("# Alice Example\n\n## Summary\nBuilt robust APIs.\n")

        with db_mod.get_connection() as conn:
            conn.execute(
                "INSERT INTO resumes (username, resume_path, metadata_json, generated_at) VALUES (?, ?, ?, ?)",
                ("alice", resume_path, "{}", "2026-01-01 10:00:00Z"),
            )
            resume_id = conn.execute(
                "SELECT id FROM resumes ORDER BY id DESC LIMIT 1"
            ).fetchone()["id"]
            conn.commit()

        with patch.object(api_mod, "HTML") as html_mock:
            html_mock.return_value.write_pdf.return_value = b"%PDF-1.4 test"
            resp = self.client.get(f"/resume/{resume_id}/pdf")

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("content-type"), "application/pdf")
        self.assertIn("attachment; filename=", resp.headers.get("content-disposition", ""))
        self.assertEqual(resp.content, b"%PDF-1.4 test")

    def test_resume_pdf_info_returns_page_count(self):
        resume_dir = os.path.join(self.tmpdir.name, "resumes")
        os.makedirs(resume_dir, exist_ok=True)
        resume_path = os.path.join(resume_dir, "resume_alice.md")
        with open(resume_path, "w", encoding="utf-8") as f:
            f.write("# Alice Example\n\n## Summary\nBuilt robust APIs.\n")

        with db_mod.get_connection() as conn:
            conn.execute(
                "INSERT INTO resumes (username, resume_path, metadata_json, generated_at) VALUES (?, ?, ?, ?)",
                ("alice", resume_path, "{}", "2026-01-01 10:00:00Z"),
            )
            resume_id = conn.execute(
                "SELECT id FROM resumes ORDER BY id DESC LIMIT 1"
            ).fetchone()["id"]
            conn.commit()

        with patch.object(api_mod, "_build_resume_pdf_payload", return_value={
            "filename": "resume_alice_1.pdf",
            "page_count": 2,
            "pdf_bytes": b"%PDF-1.4 test",
        }):
            resp = self.client.get(f"/resume/{resume_id}/pdf/info")

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {
            "filename": "resume_alice_1.pdf",
            "page_count": 2,
            "is_multi_page": True,
        })

    def test_count_pdf_pages_fallback_uses_pages_count_object(self):
        pdf_bytes = (
            b"%PDF-1.4\n"
            b"4 0 obj\n<< /Type /Page >>\nendobj\n"
            b"6 0 obj\n<< /Type /Page >>\nendobj\n"
            b"9 0 obj\n<< /Count 2 /Kids [ 4 0 R 6 0 R ] /Type /Pages >>\nendobj\n"
        )

        with patch.object(api_mod, "PdfReader", None):
            self.assertEqual(api_mod._count_pdf_pages(pdf_bytes), 2)

    def test_resume_pdf_missing_file_returns_404(self):
        missing_path = os.path.join(self.tmpdir.name, "resumes", "missing_resume.md")
        with db_mod.get_connection() as conn:
            conn.execute(
                "INSERT INTO resumes (username, resume_path, metadata_json, generated_at) VALUES (?, ?, ?, ?)",
                ("alice", missing_path, "{}", "2026-01-01 10:00:00Z"),
            )
            resume_id = conn.execute(
                "SELECT id FROM resumes ORDER BY id DESC LIMIT 1"
            ).fetchone()["id"]
            conn.commit()

        resp = self.client.get(f"/resume/{resume_id}/pdf")
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json().get("detail"), "Resume file not found")

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
    def test_portfolio_save_list_rename_get(self):
        portfolio_id, project_id = self._seed_web_portfolio_data()

        # GET by id
        resp_get = self.client.get(f"/portfolios/{portfolio_id}")
        self.assertEqual(resp_get.status_code, 200)
        body = resp_get.json()
        self.assertEqual(body["username"], "alice")
        self.assertEqual(body["portfolio_name"], "Test Portfolio")
        self.assertIn(project_id, body["included_project_ids"])

        # LIST by username
        resp_list = self.client.get("/portfolios", params={"username": "alice"})
        self.assertEqual(resp_list.status_code, 200)
        names = [p["portfolio_name"] for p in resp_list.json()]
        self.assertIn("Test Portfolio", names)

        # RENAME
        resp_rename = self.client.patch(
            f"/portfolios/{portfolio_id}/name",
            json={"portfolio_name": "Renamed Portfolio"},
        )
        self.assertEqual(resp_rename.status_code, 200)
        self.assertEqual(resp_rename.json()["portfolio_name"], "Renamed Portfolio")

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
                "selected_project_ids": [project_id],
                "featured_project_ids": [project_id],
            },
        )
        self.assertEqual(customize_resp.status_code, 200)
        self.assertIn(project_id, customize_resp.json()["featured_project_ids"])

        timeline_after_resp = self.client.get(f"/web/portfolio/{portfolio_id}/timeline")
        self.assertEqual(timeline_after_resp.status_code, 200)


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

    def test_update_project_endpoint_preserves_unspecified_fields(self):
        with api_mod.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO projects (name, custom_name, repo_url, thumbnail_path)
                VALUES (?, ?, ?, ?)
                """,
                ("demo_project", "Existing Name", "https://keep-url.com", "/keep/thumb.png"),
            )
            project_id = conn.execute(
                "SELECT id FROM projects WHERE name = ?",
                ("demo_project",),
            ).fetchone()["id"]
            conn.commit()

        resp = self.client.patch(
            f"/projects/{project_id}",
            json={"thumbnail_path": "/new/thumb.png"},
        )

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["project"]["custom_name"], "Existing Name")
        self.assertEqual(body["project"]["repo_url"], "https://keep-url.com")
        self.assertEqual(body["project"]["thumbnail_path"], "/new/thumb.png")

    def test_project_thumbnail_image_endpoint(self):
        thumbnail_path = os.path.join(self.tmpdir.name, "thumb.png")
        with open(thumbnail_path, "wb") as fh:
            fh.write(b"fake-png-data")

        with api_mod.get_connection() as conn:
            conn.execute(
                "INSERT INTO projects (name, thumbnail_path) VALUES (?, ?)",
                ("demo_project", thumbnail_path),
            )
            project_id = conn.execute(
                "SELECT id FROM projects WHERE name = ?",
                ("demo_project",),
            ).fetchone()["id"]
            conn.commit()

        resp = self.client.get(f"/projects/{project_id}/thumbnail/image")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b"fake-png-data")
        self.assertEqual(resp.headers["content-type"], "image/png")

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

    def test_delete_resume_endpoint(self):
        resume_dir = os.path.join(self.tmpdir.name, "resumes")
        os.makedirs(resume_dir, exist_ok=True)
        resume_path = os.path.join(resume_dir, "resume_alice.md")
        with open(resume_path, "w") as f:
            f.write("# Resume — alice\n")

        with db_mod.get_connection() as conn:
            conn.execute(
                "INSERT INTO resumes (username, resume_path, metadata_json, generated_at) VALUES (?, ?, ?, ?)",
                ("alice", resume_path, "{}", "2026-01-01 10:00:00Z"),
            )
            resume_id = conn.execute(
                "SELECT id FROM resumes ORDER BY id DESC LIMIT 1"
            ).fetchone()["id"]
            conn.commit()

        resp = self.client.delete(f"/resume/{resume_id}")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["deleted"])
        self.assertFalse(os.path.isfile(resume_path))

        resp_again = self.client.delete(f"/resume/{resume_id}")
        self.assertEqual(resp_again.status_code, 404)





    def test_create_project_evidence_endpoint(self):
        with api_mod.get_connection() as conn:
            conn.execute(
                "INSERT INTO projects (name, repo_url) VALUES (?, ?)",
                ("Evidence Project", None),
            )
            project_id = conn.execute(
                "SELECT id FROM projects WHERE name = ?",
                ("Evidence Project",),
            ).fetchone()["id"]
            conn.commit()

        resp = self.client.post(
            f"/projects/{project_id}/evidence",
            json={
                "type": "metric",
                "value": "10k+ downloads",
                "source": "GitHub",
                "url": "https://example.com/proof",
            },
        )

        self.assertEqual(resp.status_code, 201)
        body = resp.json()
        self.assertEqual(body["message"], "Evidence added successfully")
        self.assertIn("evidence_id", body)

        detail_resp = self.client.get(f"/projects/{project_id}")
        self.assertEqual(detail_resp.status_code, 200)
        evidence = detail_resp.json()["evidence"]
        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0]["type"], "metric")
        self.assertEqual(evidence[0]["value"], "10k+ downloads")
        self.assertEqual(evidence[0]["source"], "GitHub")

    def test_delete_project_evidence_endpoint(self):
        with api_mod.get_connection() as conn:
            conn.execute(
                "INSERT INTO projects (name, repo_url) VALUES (?, ?)",
                ("Evidence Project", None),
            )
            project_id = conn.execute(
                "SELECT id FROM projects WHERE name = ?",
                ("Evidence Project",),
            ).fetchone()["id"]

            conn.execute(
                """
                INSERT INTO project_evidence (project_id, type, description, value, source, url)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (project_id, "metric", "", "10k+ downloads", "GitHub", "https://example.com/proof"),
            )
            evidence_id = conn.execute(
                "SELECT id FROM project_evidence WHERE project_id = ?",
                (project_id,),
            ).fetchone()["id"]
            conn.commit()

        resp = self.client.delete(f"/projects/{project_id}/evidence/{evidence_id}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["message"], "Evidence deleted successfully")

        detail_resp = self.client.get(f"/projects/{project_id}")
        self.assertEqual(detail_resp.status_code, 200)
        self.assertEqual(detail_resp.json()["evidence"], [])


    def test_create_project_evidence_rejects_invalid_type(self):
        with api_mod.get_connection() as conn:
            conn.execute(
                "INSERT INTO projects (name, repo_url) VALUES (?, ?)",
                ("Evidence Project", None),
            )
            project_id = conn.execute(
                "SELECT id FROM projects WHERE name = ?",
                ("Evidence Project",),
            ).fetchone()["id"]
            conn.commit()

        resp = self.client.post(
            f"/projects/{project_id}/evidence",
            json={
                "type": "fake_type",
                "value": "Some impact",
                "source": "GitHub",
                "url": "",
            },
        )

        self.assertEqual(resp.status_code, 400)
        self.assertIn("Invalid type", resp.json()["detail"])
    
    def test_update_project_evidence(self):
        with api_mod.get_connection() as conn:
                conn.execute(
                    "INSERT INTO projects (name, repo_url) VALUES (?, ?)",
                    ("Test Project", None),
                )
                project_id = conn.execute(
                    "SELECT id FROM projects WHERE name = ?",
                    ("Test Project",),
                ).fetchone()["id"]

                conn.execute(
                    """
                    INSERT INTO project_evidence (project_id, type, description, value, source, url)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (project_id, "metric", "", "100 users", "GitHub", "https://example.com"),
                )

                evidence_id = conn.execute(
                    "SELECT id FROM project_evidence WHERE project_id = ?",
                    (project_id,),
                ).fetchone()["id"]

                conn.commit()

        resp = self.client.patch(
                f"/projects/{project_id}/evidence/{evidence_id}",
                json={
                    "value": "200 users",
                    "source": "Updated Source",
                },
            )

        self.assertEqual(resp.status_code, 200)
        
        detail_resp = self.client.get(f"/projects/{project_id}")
        updated = detail_resp.json()["evidence"][0]

        self.assertEqual(updated["value"], "200 users")
        self.assertEqual(updated["source"], "Updated Source")
