import importlib
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestContributorPrompt(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, 'test_file_data.db')
        os.environ['FILE_DATA_DB_PATH'] = self.db_path

        import db as db_module
        importlib.reload(db_module)
        self.db = db_module
        self.db.init_db()

        import scan as scan_module
        importlib.reload(scan_module)
        self.scan = scan_module

        with self.db.get_connection() as conn:
            conn.execute("INSERT OR IGNORE INTO contributors (name) VALUES (?)", ("alice",))
            conn.execute("INSERT OR IGNORE INTO contributors (name) VALUES (?)", ("bob",))
            conn.commit()

    def tearDown(self):
        try:
            del os.environ['FILE_DATA_DB_PATH']
        except KeyError:
            pass
        try:
            self.tmpdir.cleanup()
        except Exception:
            pass

    def test_prompt_selects_existing_and_new(self):
        with patch.object(self.scan, "ask_yes_no", return_value=True), \
             patch("sys.stdin.isatty", return_value=True), \
             patch("builtins.input", side_effect=["1,0,newuser", "Carol"]):
            result = self.scan._prompt_manual_contributors("demo")

        self.assertIn("alice", result)
        self.assertIn("newuser", result)
        self.assertIn("carol", result)
        self.assertEqual(len(set(result)), len(result))

    def test_prompt_skips_duplicates(self):
        with patch.object(self.scan, "ask_yes_no", return_value=True), \
             patch("sys.stdin.isatty", return_value=True), \
             patch("builtins.input", side_effect=["1,alice,0", "Alice"]):
            result = self.scan._prompt_manual_contributors("demo")

        self.assertEqual(result, ["alice"])


if __name__ == '__main__':
    unittest.main()
