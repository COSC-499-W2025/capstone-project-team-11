import os
import sqlite3
import sys
import unittest

# Allow importing from src/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from db import _ensure_schema


class TestDbSchemaInit(unittest.TestCase):
    def setUp(self):
        # In-memory database for testing
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row

    def tearDown(self):
        self.conn.close()

    def test_schema_creation(self):
        """Ensure all tables and indexes are created."""
        _ensure_schema(self.conn)
        cur = self.conn.cursor()

        # Tables should exist
        tables = [row["name"] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        expected_tables = [
            "scans", "projects", "files", "contributors", "languages", "skills",
            "file_contributors", "file_languages", "project_skills", "project_evidence",
            "resumes", "portfolios"
        ]
        for table in expected_tables:
            self.assertIn(table, tables)

        # Indexes should exist
        indexes = [row["name"] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='index'")]
        expected_indexes = [
            "idx_file_path", "idx_file_name", "idx_files_scan_id", "idx_projects_name",
            "idx_contributors_name", "idx_languages_name", "idx_skills_name",
            "idx_resumes_username", "idx_resumes_generated_at",
            "idx_portfolios_username", "idx_portfolios_generated_at",
            "idx_project_evidence_project_id"
        ]
        for idx in expected_indexes:
            self.assertIn(idx, indexes)

    def test_foreign_keys_and_cascade(self):
        """Check that ON DELETE CASCADE works for project_evidence."""
        _ensure_schema(self.conn)
        cur = self.conn.cursor()

        # Insert a project
        cur.execute("INSERT INTO projects (name) VALUES (?)", ("proj1",))
        project_id = cur.lastrowid

        # Insert evidence linked to project
        cur.execute(
            "INSERT INTO project_evidence (project_id, type) VALUES (?, ?)",
            (project_id, "test_type")
        )
        evidence_id = cur.lastrowid

        self.conn.commit()

        # Delete project
        cur.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        self.conn.commit()

        cur.execute("SELECT COUNT(*) AS c FROM project_evidence WHERE id = ?", (evidence_id,))
        self.assertEqual(cur.fetchone()["c"], 0)

    def test_default_values(self):
        """Test that default values (e.g., scanned_at) are set."""
        _ensure_schema(self.conn)
        cur = self.conn.cursor()

        # Insert a scan without specifying scanned_at
        cur.execute("INSERT INTO scans (project) VALUES (?)", ("proj_default",))
        self.conn.commit()

        cur.execute("SELECT scanned_at FROM scans WHERE project = ?", ("proj_default",))
        scanned_at = cur.fetchone()["scanned_at"]

        self.assertIsNotNone(scanned_at)
        self.assertTrue(len(scanned_at) > 0)

    # --- Extended tests for foreign keys and join tables ---
    def test_join_table_foreign_keys(self):
        """Ensure join tables enforce foreign keys correctly."""
        _ensure_schema(self.conn)
        cur = self.conn.cursor()

        # Create parent rows first
        cur.execute("INSERT INTO scans (project, notes) VALUES (?, ?)", ("ProjX", "note"))
        scan_id = cur.lastrowid
        cur.execute("INSERT INTO contributors (name) VALUES (?)", ("Alice",))
        contributor_id = cur.lastrowid
        cur.execute("INSERT INTO languages (name) VALUES (?)", ("Python",))
        language_id = cur.lastrowid
        cur.execute("INSERT INTO skills (name) VALUES (?)", ("Testing",))
        skill_id = cur.lastrowid
        cur.execute("INSERT INTO projects (name) VALUES (?)", ("ProjY",))
        project_id = cur.lastrowid

        # Insert file referencing scan
        cur.execute(
            "INSERT INTO files (scan_id, file_name, file_path) VALUES (?, ?, ?)",
            (scan_id, "a.py", "/a.py")
        )
        file_id = cur.lastrowid

        # Insert join rows
        cur.execute("INSERT INTO file_contributors (file_id, contributor_id) VALUES (?, ?)", (file_id, contributor_id))
        cur.execute("INSERT INTO file_languages (file_id, language_id) VALUES (?, ?)", (file_id, language_id))
        cur.execute("INSERT INTO project_skills (project_id, skill_id) VALUES (?, ?)", (project_id, skill_id))
        self.conn.commit()

        # Basic check
        cur.execute("SELECT COUNT(*) AS c FROM file_contributors WHERE file_id = ?", (file_id,))
        self.assertEqual(cur.fetchone()["c"], 1)
        cur.execute("SELECT COUNT(*) AS c FROM file_languages WHERE file_id = ?", (file_id,))
        self.assertEqual(cur.fetchone()["c"], 1)
        cur.execute("SELECT COUNT(*) AS c FROM project_skills WHERE project_id = ?", (project_id,))
        self.assertEqual(cur.fetchone()["c"], 1)

    def test_scan_file_fk_cascade_safe(self):
        """Ensure files reference scans, and deletion is safe if cascade is handled manually."""
        _ensure_schema(self.conn)
        cur = self.conn.cursor()

        # Insert scan and file
        cur.execute("INSERT INTO scans (project, notes) VALUES (?, ?)", ("ProjScan", "note"))
        scan_id = cur.lastrowid
        cur.execute("INSERT INTO files (scan_id, file_name, file_path) VALUES (?, ?, ?)",
                    (scan_id, "f.py", "/f.py"))
        self.conn.commit()

        # Delete file first, then scan (avoids IntegrityError)
        cur.execute("DELETE FROM files WHERE scan_id = ?", (scan_id,))
        cur.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
        self.conn.commit()

        cur.execute("SELECT COUNT(*) AS c FROM scans WHERE id = ?", (scan_id,))
        self.assertEqual(cur.fetchone()["c"], 0)

    def test_project_evidence_cascade(self):
        """Extra test to explicitly confirm cascade on project_evidence.project_id"""
        _ensure_schema(self.conn)
        cur = self.conn.cursor()

        # Insert project
        cur.execute("INSERT INTO projects (name) VALUES (?)", ("CascadeProj",))
        project_id = cur.lastrowid
        cur.execute("INSERT INTO project_evidence (project_id, type) VALUES (?, ?)", (project_id, "TypeA"))
        evidence_id = cur.lastrowid
        self.conn.commit()

        # Delete project
        cur.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        self.conn.commit()

        cur.execute("SELECT COUNT(*) AS c FROM project_evidence WHERE id = ?", (evidence_id,))
        self.assertEqual(cur.fetchone()["c"], 0)


if __name__ == "__main__":
    unittest.main()
