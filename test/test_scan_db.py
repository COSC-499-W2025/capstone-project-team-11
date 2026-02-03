import io
import json
import os
import shutil
import sys
import tempfile
import unittest
import zipfile

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import db as dbmod
from db import get_connection, init_db
from scan import list_files_in_directory


class TestScanDbPersistence(unittest.TestCase):
    def setUp(self):
        # create temporary DB file and initialize schema
        self.tmp_db = tempfile.NamedTemporaryFile(delete=False)
        self.tmp_db.close()
        dbmod.DB_PATH = self.tmp_db.name
        init_db()

        # create a temporary directory to scan
        self.tmp_dir = tempfile.mkdtemp()
        # create a couple of files
        self.file_paths = []
        for name in ('one.txt', 'two.py'):
            p = os.path.join(self.tmp_dir, name)
            with open(p, 'w', encoding='utf-8') as f:
                f.write('hello')
            self.file_paths.append(p)

    def tearDown(self):
        try:
            os.unlink(self.tmp_db.name)
        except Exception:
            pass
        shutil.rmtree(self.tmp_dir)

    def test_directory_scan_persists_to_db(self):
        # Run a directory scan and persist results
        list_files_in_directory(self.tmp_dir, recursive=False, file_type=None, save_to_db=True)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM scans')
        scans_count = cur.fetchone()[0]
        cur.execute('SELECT COUNT(*) FROM files')
        files_count = cur.fetchone()[0]
        conn.close()

        self.assertGreaterEqual(scans_count, 1)
        self.assertGreaterEqual(files_count, len(self.file_paths))


class TestZipScanDbPersistence(unittest.TestCase):
    def setUp(self):
        # DB
        self.tmp_db = tempfile.NamedTemporaryFile(delete=False)
        self.tmp_db.close()
        dbmod.DB_PATH = self.tmp_db.name
        init_db()

        # Build nested zip: inner.zip contains inner.txt, outer.zip contains inner.zip and root.txt
        self.tmp_dir = tempfile.mkdtemp()
        inner_bytes = io.BytesIO()
        with zipfile.ZipFile(inner_bytes, 'w') as inner:
            inner.writestr('inner.txt', 'inner content')
        inner_data = inner_bytes.getvalue()

        outer_path = os.path.join(self.tmp_dir, 'outer.zip')
        with zipfile.ZipFile(outer_path, 'w') as outer:
            outer.writestr('root.txt', 'root')
            outer.writestr('inner.zip', inner_data)

        self.outer_zip = outer_path

    def tearDown(self):
        try:
            os.unlink(self.tmp_db.name)
        except Exception:
            pass
        shutil.rmtree(self.tmp_dir)

    def test_zip_scan_persists_nested_files(self):
        # recursive True to descend into nested zips
        list_files_in_directory(self.outer_zip, recursive=True, file_type=None, save_to_db=True)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM scans')
        scans_count = cur.fetchone()[0]
        cur.execute('SELECT COUNT(*) FROM files')
        files_count = cur.fetchone()[0]
        conn.close()

        self.assertGreaterEqual(scans_count, 1)
        # expect at least root.txt and inner.txt to be recorded
        self.assertGreaterEqual(files_count, 2)


class TestSaveToDbFalse(unittest.TestCase):
    def setUp(self):
        self.tmp_db = tempfile.NamedTemporaryFile(delete=False)
        self.tmp_db.close()
        dbmod.DB_PATH = self.tmp_db.name
        init_db()

        self.tmp_dir = tempfile.mkdtemp()
        p = os.path.join(self.tmp_dir, 'a.txt')
        with open(p, 'w', encoding='utf-8') as f:
            f.write('data')
        self.file_path = p

    def tearDown(self):
        try:
            os.unlink(self.tmp_db.name)
        except Exception:
            pass
        shutil.rmtree(self.tmp_dir)

    def test_save_to_db_false_does_not_create_rows(self):
        list_files_in_directory(self.tmp_dir, recursive=False, file_type=None, save_to_db=False)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM scans')
        scans_count = cur.fetchone()[0]
        cur.execute('SELECT COUNT(*) FROM files')
        files_count = cur.fetchone()[0]
        conn.close()

        self.assertEqual(scans_count, 0)
        self.assertEqual(files_count, 0)


class TestPersistedFilePathFormat(unittest.TestCase):
    def setUp(self):
        self.tmp_db = tempfile.NamedTemporaryFile(delete=False)
        self.tmp_db.close()
        dbmod.DB_PATH = self.tmp_db.name
        init_db()

        # Build nested zip: inner.zip contains inner.txt, outer.zip contains inner.zip and root.txt
        self.tmp_dir = tempfile.mkdtemp()
        inner_bytes = io.BytesIO()
        with zipfile.ZipFile(inner_bytes, 'w') as inner:
            inner.writestr('inner.txt', 'inner content')
        inner_data = inner_bytes.getvalue()

        outer_path = os.path.join(self.tmp_dir, 'outer.zip')
        with zipfile.ZipFile(outer_path, 'w') as outer:
            outer.writestr('root.txt', 'root')
            outer.writestr('inner.zip', inner_data)

        self.outer_zip = outer_path

    def tearDown(self):
        try:
            os.unlink(self.tmp_db.name)
        except Exception:
            pass
        shutil.rmtree(self.tmp_dir)

    def test_nested_zip_file_paths_are_recorded_with_zip_colon_format(self):
        list_files_in_directory(self.outer_zip, recursive=True, file_type=None, save_to_db=True)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT file_path FROM files')
        rows = [r[0] for r in cur.fetchall()]
        conn.close()

        expected_root = f"{self.outer_zip}:root.txt"
        expected_inner = f"{self.outer_zip}:inner.zip:inner.txt"

        self.assertIn(expected_root, rows)
        self.assertIn(expected_inner, rows)


class TestMetadataJsonValid(unittest.TestCase):
    def setUp(self):
        self.tmp_db = tempfile.NamedTemporaryFile(delete=False)
        self.tmp_db.close()
        dbmod.DB_PATH = self.tmp_db.name
        init_db()

        self.tmp_dir = tempfile.mkdtemp()
        p = os.path.join(self.tmp_dir, 'a.txt')
        with open(p, 'w', encoding='utf-8') as f:
            f.write('data')
        self.file_path = p

    def tearDown(self):
        try:
            os.unlink(self.tmp_db.name)
        except Exception:
            pass
        shutil.rmtree(self.tmp_dir)


class TestProjectThumbnailPersistence(unittest.TestCase):
    def setUp(self):
        self.tmp_db = tempfile.NamedTemporaryFile(delete=False)
        self.tmp_db.close()
        dbmod.DB_PATH = self.tmp_db.name
        init_db()

        self.tmp_dir = tempfile.mkdtemp()
        p = os.path.join(self.tmp_dir, 'a.txt')
        with open(p, 'w', encoding='utf-8') as f:
            f.write('data')
        self.file_path = p

        self.thumb_dir = tempfile.mkdtemp()
        self.thumb_path = os.path.join(self.thumb_dir, 'thumb.png')
        with open(self.thumb_path, 'wb') as f:
            f.write(b'\x89PNG\r\n\x1a\n')

    def tearDown(self):
        try:
            os.unlink(self.tmp_db.name)
        except Exception:
            pass
        shutil.rmtree(self.tmp_dir)
        shutil.rmtree(self.thumb_dir)

    def test_thumbnail_path_saved_on_project(self):
        project_name = os.path.basename(os.path.abspath(self.tmp_dir))
        expected_path = self.thumb_path
        list_files_in_directory(
            self.tmp_dir,
            recursive=False,
            file_type=None,
            save_to_db=True,
            project_thumbnail_path=expected_path,
        )

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT thumbnail_path FROM projects WHERE name = ?", (project_name,))
        row = cur.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row[0], expected_path)

    def test_metadata_json_is_valid_json_string(self):
        list_files_in_directory(self.tmp_dir, recursive=False, file_type=None, save_to_db=True)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT metadata_json FROM files LIMIT 1')
        row = cur.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        metadata = row[0]
        if metadata is None:
            metadata = '{}'
        parsed = json.loads(metadata)
        self.assertIsInstance(parsed, dict)


if __name__ == '__main__':
    unittest.main()
