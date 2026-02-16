import os
import sys
import tempfile
import shutil
import time
import unittest
import zipfile
from io import StringIO
from contextlib import redirect_stdout
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from scan import (
    list_files_in_directory,
    get_collaboration_info,
    scan_with_clean_output,
    ScanProgress,
    get_scan_progress,
    _find_all_project_roots,
    _find_candidate_project_roots,
    _map_files_to_repos,
)


class TestListFilesInDirectory(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory structure for testing
        self.test_dir = tempfile.mkdtemp()

        self.file_txt = os.path.join(self.test_dir, "file1.txt")
        self.file_py = os.path.join(self.test_dir, "script.py")
        self.file_jpg = os.path.join(self.test_dir, "image.jpg")

        for file in [self.file_txt, self.file_py, self.file_jpg]:
            with open(file, "w") as f:
                f.write("test")

        self.sub_dir = os.path.join(self.test_dir, "subdir")
        os.makedirs(self.sub_dir)
        self.sub_file_txt = os.path.join(self.sub_dir, "nested.txt")
        with open(self.sub_file_txt, "w") as f:
            f.write("nested test")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def capture_output(self, *args, **kwargs):
        # Helper to capture stdout from list_files_in_directory
        buffer = StringIO()
        with redirect_stdout(buffer):
            rv = list_files_in_directory(*args, **kwargs)
        return buffer.getvalue(), rv

    # Non-recursive should list only root-level files
    def test_non_recursive_all_files(self):
        output, rv = self.capture_output(self.test_dir, recursive=False)
        basenames = {os.path.basename(t[0]) for t in rv}
        self.assertIn("file1.txt", basenames)
        self.assertIn("script.py", basenames)
        self.assertIn("image.jpg", basenames)
        self.assertNotIn("nested.txt", basenames)

    # Recursive should include files in subdirectories
    def test_recursive_all_files(self):
        output, rv = self.capture_output(self.test_dir, recursive=True)
        basenames = {os.path.basename(t[0]) for t in rv}
        self.assertIn("nested.txt", basenames)

    # File type filter should restrict results to matching extensions
    def test_file_type_filter_txt(self):
        output, rv = self.capture_output(self.test_dir, recursive=True, file_type=".txt")
        basenames = {os.path.basename(t[0]) for t in rv}
        self.assertIn("file1.txt", basenames)
        self.assertIn("nested.txt", basenames)
        self.assertNotIn("script.py", basenames)
        self.assertNotIn("image.jpg", basenames)

    # Invalid directory path should print error and return None
    def test_invalid_directory(self):
        output, rv = self.capture_output("invalid/path", recursive=False)
        self.assertIn("Directory does not exist", output)
        self.assertIsNone(rv)

    # Non-recursive zip should list only top-level entries
    def test_zip_non_recursive_lists_only_root_files(self):
        zip_path = os.path.join(self.test_dir, "archive.zip")
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr('root.txt', 'root')
            zf.writestr('subdir/nested.txt', 'nested')

        output, rv = self.capture_output(zip_path, recursive=False)
        basenames = {os.path.basename(t[0].split(':')[-1]) for t in rv}
        self.assertIn('root.txt', basenames)
        self.assertNotIn('nested.txt', basenames)

    # Zip scanning should honor the file_type filter
    def test_zip_respects_file_type_filter(self):
        zip_path = os.path.join(self.test_dir, "code.zip")
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr('a.py', 'print(1)')
            zf.writestr('a.txt', 'x')

        output, rv = self.capture_output(zip_path, recursive=True, file_type='.py')
        basenames = {os.path.basename(t[0].split(':')[-1]) for t in rv}
        self.assertIn('a.py', basenames)
        self.assertNotIn('a.txt', basenames)

    # Recursive zip scan should descend into nested zip entries
    def test_nested_zip_recursive_lists_inner_files(self):
        outer_zip = os.path.join(self.test_dir, 'outer.zip')
        import io as _io
        inner_bytes = _io.BytesIO()
        with zipfile.ZipFile(inner_bytes, 'w') as inner:
            inner.writestr('inner.txt', 'hi')
        inner_data = inner_bytes.getvalue()

        with zipfile.ZipFile(outer_zip, 'w') as outer:
            outer.writestr('level1/readme.md', 'readme')
            outer.writestr('inner.zip', inner_data)

        out, rv = self.capture_output(outer_zip, recursive=True)
        entries = {t[0] for t in rv}
        self.assertTrue(any('inner.txt' in e for e in entries))
        self.assertTrue(any('outer.zip:inner.zip:inner.txt' in e for e in entries))

    # Non-recursive zip scan should not descend into nested zips
    def test_nested_zip_non_recursive_does_not_list_inner_files(self):
        outer_zip = os.path.join(self.test_dir, 'outer_nr.zip')
        import io as _io
        inner_bytes = _io.BytesIO()
        with zipfile.ZipFile(inner_bytes, 'w') as inner:
            inner.writestr('inner.txt', 'hi')
        inner_data = inner_bytes.getvalue()

        with zipfile.ZipFile(outer_zip, 'w') as outer:
            outer.writestr('inner.zip', inner_data)

        out, rv = self.capture_output(outer_zip, recursive=False)
        entries = {t[0] for t in rv}
        self.assertFalse(any('inner.txt' in e for e in entries))

    # Recursive should find files at every nesting level
    def test_deeply_nested_folders_recursive(self):
        deep_path = self.test_dir
        for i in range(1, 5):
            deep_path = os.path.join(deep_path, f"level{i}")
            os.makedirs(deep_path)
            test_file = os.path.join(deep_path, f"file_at_level{i}.txt")
            with open(test_file, "w") as f:
                f.write(f"content at level {i}")

        output, rv = self.capture_output(self.test_dir, recursive=True)
        basenames = {os.path.basename(t[0]) for t in rv}
        for i in range(1, 5):
            self.assertIn(f"file_at_level{i}.txt", basenames)

    # Non-recursive should only return root-level files
    def test_deeply_nested_folders_non_recursive(self):
        level1 = os.path.join(self.test_dir, "level1")
        level2 = os.path.join(level1, "level2")
        os.makedirs(level2)

        root_file = os.path.join(self.test_dir, "root.txt")
        level1_file = os.path.join(level1, "level1.txt")
        level2_file = os.path.join(level2, "level2.txt")

        for f in [root_file, level1_file, level2_file]:
            with open(f, "w") as fp:
                fp.write("test")

        output, rv = self.capture_output(self.test_dir, recursive=False)
        basenames = {os.path.basename(t[0]) for t in rv}
        self.assertIn("root.txt", basenames)
        self.assertNotIn("level1.txt", basenames)
        self.assertNotIn("level2.txt", basenames)

    # File type filter should work across nested directory structures
    def test_nested_folders_with_various_file_types(self):
        folder1 = os.path.join(self.test_dir, "docs")
        folder2 = os.path.join(self.test_dir, "src")
        folder3 = os.path.join(folder2, "utils")
        os.makedirs(folder1)
        os.makedirs(folder3)

        files = {
            os.path.join(folder1, "readme.md"): "# README",
            os.path.join(folder1, "notes.txt"): "notes",
            os.path.join(folder2, "main.py"): "print('hello')",
            os.path.join(folder3, "helper.py"): "def help(): pass",
            os.path.join(folder3, "config.json"): "{}",
        }
        for path, content in files.items():
            with open(path, "w") as f:
                f.write(content)

        output, rv = self.capture_output(self.test_dir, recursive=True, file_type=".py")
        basenames = {os.path.basename(t[0]) for t in rv}
        self.assertIn("main.py", basenames)
        self.assertIn("helper.py", basenames)
        self.assertNotIn("readme.md", basenames)
        self.assertNotIn("notes.txt", basenames)
        self.assertNotIn("config.json", basenames)

    # Nested zip paths should use colon-separated display notation
    def test_nested_zip_preserves_path_structure(self):
        import io as _io
        inner_bytes = _io.BytesIO()
        with zipfile.ZipFile(inner_bytes, 'w') as inner:
            inner.writestr('folder/document.txt', 'content')

        outer_zip = os.path.join(self.test_dir, 'container.zip')
        with zipfile.ZipFile(outer_zip, 'w') as outer:
            outer.writestr('archives/inner.zip', inner_bytes.getvalue())

        output, rv = self.capture_output(outer_zip, recursive=True)
        entries = {t[0] for t in rv}
        self.assertTrue(any('container.zip:archives/inner.zip:folder/document.txt' in e
                           for e in entries))

    # Empty nested directories should not produce spurious results
    def test_empty_nested_folders(self):
        empty1 = os.path.join(self.test_dir, "empty1")
        empty2 = os.path.join(empty1, "empty2")
        os.makedirs(empty2)

        test_file = os.path.join(self.test_dir, "file.txt")
        with open(test_file, "w") as f:
            f.write("test")

        output, rv = self.capture_output(self.test_dir, recursive=True)
        basenames = {os.path.basename(t[0]) for t in rv}
        self.assertIn("file.txt", basenames)

    # Zip directory entries (trailing slash) should not appear as files
    def test_nested_zip_with_empty_folders(self):
        zip_path = os.path.join(self.test_dir, 'sparse.zip')
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr('empty_folder/', '')
            zf.writestr('folder/subfolder/', '')
            zf.writestr('folder/file.txt', 'content')

        output, rv = self.capture_output(zip_path, recursive=True)
        basenames = {os.path.basename(t[0].split(':')[-1]) for t in rv if t[0].split(':')[-1]}
        self.assertIn('file.txt', basenames)

    # Non-git files should return "unknown" for collaboration info
    def test_collaboration_info_unknown_when_no_git(self):
        some_file = os.path.join(self.test_dir, 'file1.txt')
        info = get_collaboration_info(some_file)
        self.assertEqual(info, 'unknown')


# =============================================================================
# NEW FUNCTIONALITY TESTS (scan progress, project detection, clean output)
# =============================================================================

# Scan progress tests
class TestScanProgressOutput(unittest.TestCase):

    # Ensures that instances of the ScanProgress class should store results and display them in the complete summary
    def test_store_and_complete_summary(self):
        # Create a ScanProgress instance and store various scan metrics
        sp = ScanProgress()
        sp.store('files_found', 10)
        sp.store('files_skipped', 2)
        sp.store('languages', ['Python', 'Java'])
        sp.store('skills', ['API Development'])
        sp.store('contributors', ['alice', 'bob'])
        sp.store('project_type', 'Collaborative')
        # Capture the output of the complete() method and verify it includes all stored information
        buf = StringIO()
        with redirect_stdout(buf):
            sp.complete("my-project", output_dir="/tmp/output")
        output = buf.getvalue()
        self.assertIn("Scan Complete", output)
        self.assertIn("my-project", output)
        self.assertIn("Python", output)
        self.assertIn("API Development", output)
        self.assertIn("Collaborative", output)

    # Ensures that `get_scan_progress()` should return the same instance unless reset=True is passed as an argument
    def test_get_scan_progress_singleton_and_reset(self):
        # WITHOUT reset, a should be the same instance as b
        a = get_scan_progress(reset=True)
        b = get_scan_progress()
        self.assertIs(a, b)
        # WITH reset, a should NOT be the same instance as c
        c = get_scan_progress(reset=True)
        self.assertIsNot(a, c)

# Project root detection tests
class TestProjectRootDetection(unittest.TestCase):

    # setUp() and tearDown() create a temporary directory for testing purposes, ensuring a clean environment for each test case.
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    # Ensures that _find_all_project_roots() should detect both git and non-git projects stored within a single directory
    def test_find_all_project_roots_merges_git_and_nongit(self):
        # Create two sibling directories, one with a .git folder and one without
        git_proj = os.path.join(self.test_dir, "git_project")
        nongit_proj = os.path.join(self.test_dir, "nongit_project")
        os.makedirs(os.path.join(git_proj, ".git"))
        os.makedirs(nongit_proj)
        with open(os.path.join(git_proj, "main.py"), "w") as f:
            f.write("pass")
        with open(os.path.join(nongit_proj, "app.js"), "w") as f:
            f.write("//")

        # _find_all_project_roots() should return both directories as project roots
        roots = _find_all_project_roots(self.test_dir)
        root_names = {os.path.basename(r) for r in roots}
        self.assertIn("git_project", root_names)
        self.assertIn("nongit_project", root_names)

    # Ensures that _find_candidate_project_roots() should ignore empty and "junk" directories
    def test_find_candidate_roots_skips_empty_and_macos_junk(self):
        # Create three sibling directories: a valid project, an empty directory, and a __MACOSX directory
        proj = os.path.join(self.test_dir, "real_project")
        empty = os.path.join(self.test_dir, "empty_dir")
        macos = os.path.join(self.test_dir, "__MACOSX")
        os.makedirs(proj)
        os.makedirs(empty)
        os.makedirs(macos)
        with open(os.path.join(proj, "a.py"), "w") as f:
            f.write("pass")
        with open(os.path.join(macos, "junk.txt"), "w") as f:
            f.write("junk")

        # Only the real project should contain files, while the empty and __MACOSX directories should be ignored
        roots = _find_candidate_project_roots(self.test_dir)
        root_names = {os.path.basename(r) for r in roots}
        self.assertIn("real_project", root_names)
        self.assertNotIn("empty_dir", root_names)
        self.assertNotIn("__MACOSX", root_names)

    # Ensures that Windows drive letter paths will not break when passed in during _map_files_to_repos() calls
    def test_map_files_to_repos_handles_drive_letter_paths(self):
        # Create a file with a Windows-style drive letter path
        repo_root = os.path.join(self.test_dir, "project")
        os.makedirs(repo_root)
        file_path = os.path.join(repo_root, "main.py")
        with open(file_path, "w") as f:
            f.write("pass")

        # _map_files_to_repos() should correctly map the file to the repo root without issues from the drive letter
        file_list = [(file_path, 100, time.time())]
        result = _map_files_to_repos(file_list, [repo_root])
        self.assertIn(repo_root, result)
        self.assertEqual(len(result[repo_root]), 1)

# Clean output tests
class TestScanWithCleanOutput(unittest.TestCase):

    # setUp() and tearDown() create a temporary directory for testing purposes, ensuring a clean environment for each test case.
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    # Ensures that empty directory arguments should return a failure result when passed to the new scan entry point: scan_with_clean_output()
    def test_empty_directory_returns_error(self):
        buf = StringIO()
        with redirect_stdout(buf):
            result = scan_with_clean_output("", save_to_db=False)
        self.assertFalse(result['success'])

    # Single-project scan should return success with all expected keys
    @patch('scan.identify_contributions', return_value=None)
    @patch('scan.analyze_repo_path', return_value=None)
    @patch('scan.detect_skills', return_value={'skills': ['Testing']})
    @patch('scan.detect_languages_and_frameworks', return_value={
        'languages': ['Python'], 'high_confidence': ['Python'],
        'frameworks': [], 'high_confidence_frameworks': [],
    })

    # Ensures that a simple single-project directory should produce a comprehensive, accurate, and successful scan result when passed to the new scan entry point
    def test_single_project_returns_success(self, mock_langs, mock_skills, mock_analyze, mock_contrib):
        # Create a simple project structure with one file to scan
        with open(os.path.join(self.test_dir, "app.py"), "w") as f:
            f.write("print('hello')")

        # Capture the output of scan_with_clean_output() and verify the result contains expected results and keys/metrics
        buf = StringIO()
        with redirect_stdout(buf):
            result = scan_with_clean_output(self.test_dir, save_to_db=False)
        self.assertTrue(result['success'])
        self.assertFalse(result['is_multi_project'])
        self.assertIn('project_name', result)
        self.assertIn('files_found', result)
        self.assertGreater(result['files_found'], 0)


if __name__ == "__main__":
    unittest.main()
