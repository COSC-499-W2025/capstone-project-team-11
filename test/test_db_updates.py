import os
import sys
import tempfile
import time
import unittest
import importlib

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestDatabaseModule(unittest.TestCase):
    def setUp(self):
        # Create a temporary file to act as our SQLite DB and force the db module to use it
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, 'test_file_data.db')
        os.environ['FILE_DATA_DB_PATH'] = self.db_path

        # (re)import the db module so it picks up the env var at import-time
        import db as db_module
        importlib.reload(db_module)
        self.db = db_module

        # Initialize schema
        self.db.init_db()

    def tearDown(self):
        try:
            del os.environ['FILE_DATA_DB_PATH']
        except KeyError:
            pass
        try:
            self.tmpdir.cleanup()
        except Exception:
            pass

    def _fetchall(self, query, params=()):
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.fetchall()

    def test_tables_created(self):
        rows = self._fetchall("SELECT name FROM sqlite_master WHERE type='table'")
        names = {r[0] for r in rows}
        expected = {'scans', 'files', 'projects', 'contributors', 'languages', 'skills', 'file_contributors', 'file_languages', 'project_skills'}
        # All expected tables should be present (init_db.sql may create others as well)
        self.assertTrue(expected.issubset(names))
        cols = {r[1] for r in self._fetchall("PRAGMA table_info(projects)")}
        self.assertIn('thumbnail_path', cols)

    def test_save_scan_with_file_metadata_and_links(self):
        # Prepare two file tuples
        now = time.time()
        files_found = [
            ("a.py", 10, now),
            ("config.json:inner", 20, now)
        ]

        file_metadata = {
            "a.py": {"owner": "individual (Alice)", "language": "Python"},
            "config.json:inner": {"owner": "collaborative (Bob, Carol)", "language": "JSON (Web Config)"}
        }

        scan_id = self.db.save_scan(
            scan_source=self.tmpdir.name,
            files_found=files_found,
            project="proj1",
            notes="unit test",
            detected_languages=['Python', 'JSON (Web Config)'],
            detected_skills=['testing'],
            contributors=['Alice', 'Bob'],
            file_metadata=file_metadata,
            project_thumbnail_path="output/proj1/thumb.png",
        )

        # One scan inserted
        scans = self._fetchall("SELECT id, project, notes FROM scans WHERE id = ?", (scan_id,))
        self.assertEqual(len(scans), 1)
        self.assertEqual(scans[0][1], 'proj1')

        # Two files inserted
        files = self._fetchall("SELECT file_name, file_path, owner FROM files WHERE scan_id = ?", (scan_id,))
        self.assertEqual(len(files), 2)
        names = {f[0] for f in files}
        self.assertIn('a.py', names)
        # When a display path contains a colon, the implementation extracts the part after the last ':'
        # so the second file is expected to appear as 'inner' (display.split(':')[-1])
        self.assertIn('inner', names)

        # Languages exist and are linked per-file according to metadata
        langs = self._fetchall("SELECT name FROM languages")
        lang_names = {l[0] for l in langs}
        self.assertTrue({'Python', 'JSON (Web Config)'} <= lang_names)

        # Check file -> language link
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT f.file_name, l.name FROM files f JOIN file_languages fl ON f.id = fl.file_id JOIN languages l ON fl.language_id = l.id WHERE f.scan_id = ?", (scan_id,))
            pairs = cur.fetchall()
            mapping = {p[0]: p[1] for p in pairs}
            self.assertEqual(mapping.get('a.py'), 'Python')
            self.assertEqual(mapping.get('inner'), 'JSON (Web Config)')

        # Contributors created and linked per-file
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM contributors")
            contribs = {r[0] for r in cur.fetchall()}
            self.assertTrue({'Alice', 'Bob', 'Carol'} <= contribs)

            # file contributors
            cur.execute("SELECT f.file_name, c.name FROM files f JOIN file_contributors fc ON f.id = fc.file_id JOIN contributors c ON fc.contributor_id = c.id WHERE f.scan_id = ?", (scan_id,))
            file_contribs = cur.fetchall()
            fc_map = {}
            for fn, name in file_contribs:
                fc_map.setdefault(fn, set()).add(name)

            self.assertEqual(fc_map.get('a.py'), {'Alice'})
            self.assertEqual(fc_map.get('inner'), {'Bob', 'Carol'})

        # Project and project_skills
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM projects WHERE name = ?", ('proj1',))
            self.assertIsNotNone(cur.fetchone())
            cur.execute("SELECT thumbnail_path FROM projects WHERE name = ?", ('proj1',))
            thumb = cur.fetchone()[0]
            self.assertEqual(thumb, "output/proj1/thumb.png")
            cur.execute("SELECT s.name FROM skills s JOIN project_skills ps ON s.id = ps.skill_id JOIN projects p ON ps.project_id = p.id WHERE p.name = ?", ('proj1',))
            skills = {r[0] for r in cur.fetchall()}
            self.assertIn('testing', skills)

    def test_project_level_language_and_contributor_fallback_and_idempotency(self):
        # No file metadata: languages and contributors should be applied to all files
        now = time.time()
        files_found = [("one.txt", 5, now), ("two.txt", 6, now)]

        scan1 = self.db.save_scan(scan_source=self.tmpdir.name, files_found=files_found, project=None,
                                 detected_languages=['YAML'], detected_skills=None, contributors=['X'])

        # Two files inserted for scan1
        files = self._fetchall("SELECT id FROM files WHERE scan_id = ?", (scan1,))
        self.assertEqual(len(files), 2)

        # file_languages should have links for both files to YAML
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM languages WHERE name = ?", ('YAML',))
            self.assertEqual(cur.fetchone()[0], 1)

            cur.execute("SELECT COUNT(*) FROM file_languages fl JOIN languages l ON fl.language_id = l.id WHERE l.name = ? AND fl.file_id IN (SELECT id FROM files WHERE scan_id = ?)", ('YAML', scan1))
            cnt = cur.fetchone()[0]
            self.assertEqual(cnt, 2)

        # Call save_scan again with the same contributor/language names - contributors/languages should not duplicate
        scan2 = self.db.save_scan(scan_source=self.tmpdir.name, files_found=files_found, project=None,
                                 detected_languages=['YAML'], detected_skills=None, contributors=['X'])

        # contributors table should only have a single 'X'
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM contributors WHERE name = ?", ('X',))
            self.assertEqual(cur.fetchone()[0], 1)


if __name__ == '__main__':
    unittest.main()
