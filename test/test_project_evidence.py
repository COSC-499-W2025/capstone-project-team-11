import os
import sys
import tempfile
import unittest
import importlib

# Make src importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import db as db_module  # will be reloaded after setting env
import project_evidence as pe_module  # will be reloaded after setting env


class TestProjectEvidence(unittest.TestCase):
    def setUp(self):
        # Isolate each test with its own temporary database
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "file_data.db")
        os.environ["FILE_DATA_DB_PATH"] = self.db_path

        self.db = importlib.reload(db_module)
        self.db.init_db()
        self.pe = importlib.reload(pe_module)

        # Seed a project to satisfy the FK constraint
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO projects (name, repo_url) VALUES (?, ?)",
                ("demo-project", "https://example.com/demo"),
            )
            self.project_id = cur.lastrowid
            conn.commit()

    def tearDown(self):
        # Close all database connections before cleanup
        if hasattr(self, 'db'):
            # Close any open connections
            try:
                conn = self.db.get_connection()
                conn.close()
            except Exception:
                pass

        # Force garbage collection (gc) to close any remaining connections
        import gc
        gc.collect()

        try:
            del os.environ["FILE_DATA_DB_PATH"]
        except KeyError:
            pass

        # Small delay to let connections close properly
        import time
        time.sleep(0.1)

        self.tmpdir.cleanup()

    def test_add_and_fetch_evidence_orders_by_created_at(self):
        ev1_id = self.pe.add_evidence(
            self.project_id,
            {
                "type": "metric",
                "value": "500 users",
                "source": "Analytics",
                "url": "https://example.com/report1",
            },
        )
        ev2_id = self.pe.add_evidence(
            self.project_id,
            {
                "type": "feedback",
                "value": "Great polish",
                "source": "Email",
                "url": "https://example.com/review",
            },
        )

        # Force deterministic ordering by created_at (DESC)
        with self.db.get_connection() as conn:
            conn.execute(
                "UPDATE project_evidence SET created_at = ? WHERE id = ?",
                ("2025-01-01 10:00:00", ev1_id),
            )
            conn.execute(
                "UPDATE project_evidence SET created_at = ? WHERE id = ?",
                ("2025-02-01 09:00:00", ev2_id),
            )
            conn.commit()

        evidence = self.pe.get_evidence_for_project(self.project_id)
        self.assertEqual([ev["id"] for ev in evidence], [ev2_id, ev1_id])
        self.assertEqual(evidence[0]["type"], "feedback")
        self.assertEqual(evidence[0]["added_by_user"], 1)

    def test_update_evidence_changes_only_requested_fields(self):
        ev_id = self.pe.add_evidence(
            self.project_id,
            {
                "type": "metric",
                "value": "100 downloads",
                "source": "Store",
                "url": None,
            },
        )

        updated = self.pe.update_evidence(
            ev_id,
            {
                "value": "1,000 downloads",
            },
        )
        self.assertTrue(updated)

        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT value, description, source FROM project_evidence WHERE id = ?",
                (ev_id,),
            ).fetchone()
        self.assertEqual(row["value"], "1,000 downloads")
        self.assertEqual(row["description"], "")
        self.assertEqual(row["source"], "Store")

        # Empty updates should return False and not alter the row
        no_change = self.pe.update_evidence(ev_id, {})
        self.assertFalse(no_change)
        with self.db.get_connection() as conn:
            row_after = conn.execute(
                "SELECT value FROM project_evidence WHERE id = ?",
                (ev_id,),
            ).fetchone()
        self.assertEqual(row_after["value"], "1,000 downloads")

    def test_delete_evidence_removes_row(self):
        ev_id = self.pe.add_evidence(
            self.project_id,
            {
                "type": "award",
                "value": "1st place",
                "source": "City Hackathon",
                "url": "",
            },
        )

        deleted = self.pe.delete_evidence(ev_id)
        self.assertTrue(deleted)

        with self.db.get_connection() as conn:
            remaining = conn.execute(
                "SELECT COUNT(*) FROM project_evidence WHERE project_id = ?",
                (self.project_id,),
            ).fetchone()[0]
        self.assertEqual(remaining, 0)

        # Non-existent id returns False
        self.assertFalse(self.pe.delete_evidence(9999))

    def test_format_evidence_list_includes_source_and_timestamp(self):
        evidence_list = [
            {
                "id": 1,
                "project_id": self.project_id,
                "type": "metric",
                "value": "10,000 MAU",
                "source": "Analytics",
                "url": "https://example.com/metrics",
                "added_by_user": True,
                "created_at": "2025-01-01 12:30:45.123456",
            },
            {
                "id": 2,
                "project_id": self.project_id,
                "type": "link",
                "value": "",
                "source": "",
                "url": "",
                "added_by_user": True,
                "created_at": None,
            },
        ]

        formatted = self.pe.format_evidence_list(evidence_list)
        self.assertIn("- **Metric** (Analytics): 10,000 MAU", formatted)
        self.assertIn("[View →](https://example.com/metrics)", formatted)
        self.assertIn("Added: 2025-01-01 12:30:45", formatted)  # microseconds trimmed
        self.assertIn("- **Link** : (no statement)", formatted)

        self.assertEqual(
            self.pe.format_evidence_list([]),
            "No evidence of success added yet.",
        )

    def test_validate_evidence_type(self):
        self.assertEqual(self.pe.validate_evidence_type("metric"), "metric")
        self.assertEqual(self.pe.validate_evidence_type("FEEDBACK"), "feedback")
        with self.assertRaises(ValueError):
            self.pe.validate_evidence_type("invalid")

    def test_add_evidence_requires_valid_type_and_statement(self):
        with self.assertRaises(ValueError):
            self.pe.add_evidence(self.project_id, {"value": "Missing type"})
        with self.assertRaises(ValueError):
            self.pe.add_evidence(self.project_id, {"type": "invalid", "value": "Bad type"})
        with self.assertRaises(ValueError):
            self.pe.add_evidence(self.project_id, {"type": "metric"})

    def test_get_project_id_by_name(self):
        self.assertEqual(self.pe.get_project_id_by_name("demo-project"), self.project_id)
        self.assertIsNone(self.pe.get_project_id_by_name("missing-project"))
        self.assertIsNone(self.pe.get_project_id_by_name(""))

    def test_format_evidence_for_resume_limits_items_and_uses_source(self):
        ev_list = [
            {"value": "A", "source": "Email"},
            {"value": "B", "source": ""},
            {"value": "C", "source": "Slack"},
        ]
        formatted = self.pe.format_evidence_for_resume(ev_list, max_items=2)
        self.assertIn("Impact:", formatted)
        self.assertIn("A (Email)", formatted)
        self.assertIn("B", formatted)
        self.assertNotIn("C", formatted)

    def test_format_evidence_for_resume_uses_legacy_description(self):
        ev_list = [
            {"value": "", "description": "Legacy statement", "source": "Email"},
        ]
        formatted = self.pe.format_evidence_for_resume(ev_list, max_items=2)
        self.assertIn("Legacy statement (Email)", formatted)

    def test_format_evidence_for_portfolio_basic(self):
        ev_list = [
            {"type": "metric", "value": "500 users", "source": "Analytics"},
            {"type": "feedback", "value": "Great polish", "source": ""},
        ]
        formatted = self.pe.format_evidence_for_portfolio(ev_list)
        self.assertIn("- **Metric** (Analytics): 500 users", formatted)
        self.assertIn("- **Feedback**: Great polish", formatted)

    def test_format_evidence_for_portfolio_uses_legacy_description(self):
        ev_list = [
            {"type": "feedback", "value": "", "description": "Legacy note", "source": "Email"},
        ]
        formatted = self.pe.format_evidence_for_portfolio(ev_list)
        self.assertIn("- **Feedback** (Email): Legacy note", formatted)

    def test_format_evidence_for_portfolio_empty_returns_none(self):
        self.assertIsNone(self.pe.format_evidence_for_portfolio([]))


if __name__ == "__main__":
    unittest.main()