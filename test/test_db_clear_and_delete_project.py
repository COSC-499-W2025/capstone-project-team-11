import os
import sys
import tempfile
import unittest
import json

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from db import (
    get_connection,
    init_db,
    clear_database,
    delete_project_by_id
)

class TestDatabaseClearAndDeleteProject(unittest.TestCase):

    def setUp(self):
        # Create temp DB
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.environ["FILE_DATA_DB_PATH"] = self.db_path
        init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)
        os.environ.pop("FILE_DATA_DB_PATH", None)

    # -----------------------------
    # CLEAR DATABASE TESTS
    # -----------------------------

    def test_clear_database_removes_all_data(self):
        with get_connection() as conn:
            cur = conn.cursor()

            # Insert sample data into multiple tables
            cur.execute("INSERT INTO projects (name) VALUES ('TestProject')")
            cur.execute("INSERT INTO scans (project, notes) VALUES ('TestProject', 'note')")
            cur.execute("""
                INSERT INTO contributors (name) VALUES ('Alice')
            """)
            conn.commit()

            # Sanity check data exists
            cur.execute("SELECT COUNT(*) FROM projects")
            self.assertGreater(cur.fetchone()[0], 0)

        # Act
        clear_database()

        # Assert all tables are empty
        with get_connection() as conn:
            cur = conn.cursor()
            tables = cur.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%';
            """).fetchall()

            for (table,) in tables:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                self.assertEqual(
                    count, 0,
                    f"Table '{table}' was not cleared"
                )

    # -----------------------------
    # DELETE PROJECT TESTS
    # -----------------------------

    def test_delete_project_removes_related_data(self):
        with get_connection() as conn:
            cur = conn.cursor()

            # Create project
            cur.execute("""
                INSERT INTO projects (name, repo_url)
                VALUES ('DeleteMe', 'https://github.com/example/repo')
            """)
            project_id = cur.lastrowid

            # Add related evidence
            cur.execute("""
                INSERT INTO project_evidence (project_id, type, value)
                VALUES (?, 'metric', '100 stars')
            """, (project_id,))

            # Add project skill
            cur.execute("INSERT INTO skills (name) VALUES ('Python')")
            skill_id = cur.lastrowid

            cur.execute("""
                INSERT INTO project_skills (project_id, skill_id)
                VALUES (?, ?)
            """, (project_id, skill_id))

            conn.commit()

        # Act
        result = delete_project_by_id(project_id)
        self.assertTrue(result)

        # Assert project and related rows are gone
        with get_connection() as conn:
            cur = conn.cursor()

            cur.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            self.assertIsNone(cur.fetchone())

            cur.execute("SELECT * FROM project_evidence WHERE project_id = ?", (project_id,))
            self.assertIsNone(cur.fetchone())

            cur.execute("SELECT * FROM project_skills WHERE project_id = ?", (project_id,))
            self.assertIsNone(cur.fetchone())

    def test_delete_project_invalid_id(self):
        # Should fail gracefully
        self.assertFalse(delete_project_by_id(999999))

    def test_delete_project_none_id(self):
        with self.assertRaises(ValueError):
            delete_project_by_id(None)


if __name__ == "__main__":
    unittest.main()