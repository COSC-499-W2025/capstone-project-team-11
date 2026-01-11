import os
import sys
import sqlite3
import unittest

# Allow importing from src/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from db_maintenance import prune_old_project_scans


def _create_min_schema(conn: sqlite3.Connection) -> None:
    """
    Minimal schema needed to test prune_old_project_scans.
    Matches the tables that function touches.
    """
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scanned_at TEXT DEFAULT CURRENT_TIMESTAMP,
        project TEXT,
        notes TEXT
    );

    CREATE TABLE files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id INTEGER NOT NULL,
        file_name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_extension TEXT,
        file_size INTEGER,
        created_at TEXT,
        modified_at TEXT,
        owner TEXT,
        metadata_json TEXT,
        FOREIGN KEY (scan_id) REFERENCES scans(id)
    );

    CREATE TABLE file_contributors (
        file_id INTEGER NOT NULL,
        contributor_id INTEGER NOT NULL,
        PRIMARY KEY (file_id, contributor_id)
    );

    CREATE TABLE file_languages (
        file_id INTEGER NOT NULL,
        language_id INTEGER NOT NULL,
        PRIMARY KEY (file_id, language_id)
    );
    """)
    conn.commit()


class TestDbMaintenance(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        _create_min_schema(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_prune_deletes_old_scans_and_related_rows(self):
        cur = self.conn.cursor()
        project = "my_project"

        # Create OLD scan
        cur.execute("INSERT INTO scans (project, notes) VALUES (?, ?)", (project, "old"))
        old_scan_id = cur.lastrowid

        # Create NEW scan (keep this one)
        cur.execute("INSERT INTO scans (project, notes) VALUES (?, ?)", (project, "new"))
        keep_scan_id = cur.lastrowid

        # Old scan files
        cur.execute(
            "INSERT INTO files (scan_id, file_name, file_path) VALUES (?, ?, ?)",
            (old_scan_id, "old_a.py", "/tmp/old_a.py"),
        )
        old_file_1 = cur.lastrowid
        cur.execute(
            "INSERT INTO files (scan_id, file_name, file_path) VALUES (?, ?, ?)",
            (old_scan_id, "old_b.py", "/tmp/old_b.py"),
        )
        old_file_2 = cur.lastrowid

        # New scan file
        cur.execute(
            "INSERT INTO files (scan_id, file_name, file_path) VALUES (?, ?, ?)",
            (keep_scan_id, "new_a.py", "/tmp/new_a.py"),
        )
        new_file_1 = cur.lastrowid

        # Join rows for OLD files
        cur.execute("INSERT INTO file_contributors (file_id, contributor_id) VALUES (?, ?)", (old_file_1, 1))
        cur.execute("INSERT INTO file_contributors (file_id, contributor_id) VALUES (?, ?)", (old_file_2, 2))
        cur.execute("INSERT INTO file_languages (file_id, language_id) VALUES (?, ?)", (old_file_1, 10))
        cur.execute("INSERT INTO file_languages (file_id, language_id) VALUES (?, ?)", (old_file_2, 11))

        # Join rows for NEW file (should remain)
        cur.execute("INSERT INTO file_contributors (file_id, contributor_id) VALUES (?, ?)", (new_file_1, 3))
        cur.execute("INSERT INTO file_languages (file_id, language_id) VALUES (?, ?)", (new_file_1, 12))

        self.conn.commit()

        deleted = prune_old_project_scans(self.conn, project, keep_scan_id)
        self.assertEqual(deleted, 1)

        # Old scan should be gone
        cur.execute("SELECT COUNT(*) AS c FROM scans WHERE id = ?", (old_scan_id,))
        self.assertEqual(cur.fetchone()["c"], 0)

        # New scan should remain
        cur.execute("SELECT COUNT(*) AS c FROM scans WHERE id = ?", (keep_scan_id,))
        self.assertEqual(cur.fetchone()["c"], 1)

        # Old scan files should be gone
        cur.execute("SELECT COUNT(*) AS c FROM files WHERE scan_id = ?", (old_scan_id,))
        self.assertEqual(cur.fetchone()["c"], 0)

        # New scan files should remain
        cur.execute("SELECT COUNT(*) AS c FROM files WHERE scan_id = ?", (keep_scan_id,))
        self.assertEqual(cur.fetchone()["c"], 1)

        # Old join rows should be gone
        cur.execute("SELECT COUNT(*) AS c FROM file_contributors WHERE file_id IN (?, ?)", (old_file_1, old_file_2))
        self.assertEqual(cur.fetchone()["c"], 0)

        cur.execute("SELECT COUNT(*) AS c FROM file_languages WHERE file_id IN (?, ?)", (old_file_1, old_file_2))
        self.assertEqual(cur.fetchone()["c"], 0)

        # New join rows should remain
        cur.execute("SELECT COUNT(*) AS c FROM file_contributors WHERE file_id = ?", (new_file_1,))
        self.assertEqual(cur.fetchone()["c"], 1)

        cur.execute("SELECT COUNT(*) AS c FROM file_languages WHERE file_id = ?", (new_file_1,))
        self.assertEqual(cur.fetchone()["c"], 1)

    def test_prune_returns_zero_if_no_old_scans(self):
        cur = self.conn.cursor()
        project = "solo_project"

        cur.execute("INSERT INTO scans (project, notes) VALUES (?, ?)", (project, "only"))
        keep_scan_id = cur.lastrowid

        self.conn.commit()

        deleted = prune_old_project_scans(self.conn, project, keep_scan_id)
        self.assertEqual(deleted, 0)

        # Still has the scan
        cur.execute("SELECT COUNT(*) AS c FROM scans WHERE project = ?", (project,))
        self.assertEqual(cur.fetchone()["c"], 1)

    def test_prune_ignores_other_projects(self):
        cur = self.conn.cursor()

        # Project A old/new
        cur.execute("INSERT INTO scans (project, notes) VALUES (?, ?)", ("A", "old"))
        a_old = cur.lastrowid
        cur.execute("INSERT INTO scans (project, notes) VALUES (?, ?)", ("A", "new"))
        a_new = cur.lastrowid

        # Project B scan (should not be touched)
        cur.execute("INSERT INTO scans (project, notes) VALUES (?, ?)", ("B", "keep"))
        b_scan = cur.lastrowid

        # Add files for A old + B
        cur.execute("INSERT INTO files (scan_id, file_name, file_path) VALUES (?, ?, ?)", (a_old, "a_old.py", "/a_old.py"))
        cur.execute("INSERT INTO files (scan_id, file_name, file_path) VALUES (?, ?, ?)", (b_scan, "b.py", "/b.py"))
        self.conn.commit()

        deleted = prune_old_project_scans(self.conn, "A", a_new)
        self.assertEqual(deleted, 1)

        # B scan still exists
        cur.execute("SELECT COUNT(*) AS c FROM scans WHERE id = ?", (b_scan,))
        self.assertEqual(cur.fetchone()["c"], 1)

        # B file still exists
        cur.execute("SELECT COUNT(*) AS c FROM files WHERE scan_id = ?", (b_scan,))
        self.assertEqual(cur.fetchone()["c"], 1)


if __name__ == "__main__":
    unittest.main()
