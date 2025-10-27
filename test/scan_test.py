import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import tempfile
import shutil
import time
from io import StringIO
import zipfile
from contextlib import redirect_stdout

from scan import list_files_in_directory


class TestListFilesInDirectory(unittest.TestCase):
    def setUp(self):
        """Create a temporary directory structure for testing."""
        self.test_dir = tempfile.mkdtemp()

        # Create files in the root directory
        self.file_txt = os.path.join(self.test_dir, "file1.txt")
        self.file_py = os.path.join(self.test_dir, "script.py")
        self.file_jpg = os.path.join(self.test_dir, "image.jpg")

        for file in [self.file_txt, self.file_py, self.file_jpg]:
            with open(file, "w") as f:
                f.write("test")

        # Create a subdirectory with files
        self.sub_dir = os.path.join(self.test_dir, "subdir")
        os.makedirs(self.sub_dir)
        self.sub_file_txt = os.path.join(self.sub_dir, "nested.txt")
        with open(self.sub_file_txt, "w") as f:
            f.write("nested test")

    def tearDown(self):
        """Remove temporary directory after tests."""
        shutil.rmtree(self.test_dir)

    def capture_output(self, *args, **kwargs):
        """Helper to capture printed output from the function."""
        buffer = StringIO()
        with redirect_stdout(buffer):
            list_files_in_directory(*args, **kwargs)
        return buffer.getvalue()

    def test_non_recursive_all_files(self):
        """Should list only files in the root directory."""
        output = self.capture_output(self.test_dir, recursive=False)
        self.assertIn("file1.txt", output)
        self.assertIn("script.py", output)
        self.assertIn("image.jpg", output)
        self.assertNotIn("nested.txt", output)

    def test_recursive_all_files(self):
        """Should include files in subdirectories."""
        output = self.capture_output(self.test_dir, recursive=True)
        self.assertIn("nested.txt", output)

    def test_file_type_filter_txt(self):
        """Should only show .txt files."""
        output = self.capture_output(self.test_dir, recursive=True, file_type=".txt")
        self.assertIn("file1.txt", output)
        self.assertIn("nested.txt", output)
        self.assertNotIn("script.py", output)
        self.assertNotIn("image.jpg", output)

    def test_invalid_directory(self):
        """Should print an error message for non-existent directories."""
        output = self.capture_output("invalid/path", recursive=False)
        self.assertIn("Directory does not exist", output)

    def test_file_statistics(self):
        """Should print largest, smallest, newest, and oldest files."""
        # Create files with controlled sizes
        small = os.path.join(self.test_dir, "small.txt")
        medium = os.path.join(self.test_dir, "medium.txt")
        large = os.path.join(self.test_dir, "large.txt")

        with open(small, "w") as f:
            f.write("a")  # 1 byte
        with open(medium, "w") as f:
            f.write("b" * 10)  # 10 bytes
        with open(large, "w") as f:
            f.write("c" * 100)  # 100 bytes

        # Set mtimes so we can predict newest/oldest
        now = time.time()
        os.utime(small, (now - 300, now - 300))   # oldest
        os.utime(medium, (now - 150, now - 150))  # middle
        os.utime(large, (now, now))               # newest

        output = self.capture_output(self.test_dir, recursive=True)

        # Check size-based stats mentioned
        self.assertIn("Largest file", output)
        self.assertIn(os.path.basename(large), output)
        self.assertIn(f"({os.path.getsize(large)} bytes)", output)

        self.assertIn("Smallest file", output)
        self.assertIn(os.path.basename(small), output)
        self.assertIn(f"({os.path.getsize(small)} bytes)", output)

        # Check time-based stats mentioned
        self.assertIn("Most recently modified", output)
        self.assertIn(os.path.basename(large), output)

        self.assertIn("Least recently modified", output)
        self.assertIn(os.path.basename(small), output)

    def test_zip_non_recursive_lists_only_root_files(self):
        """When given a zip file, non-recursive should list only top-level files."""
        zip_path = os.path.join(self.test_dir, "archive.zip")
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr('root.txt', 'root')
            zf.writestr('subdir/nested.txt', 'nested')

        output = self.capture_output(zip_path, recursive=False)
        self.assertIn('root.txt', output)
        self.assertNotIn('nested.txt', output)

    def test_zip_respects_file_type_filter(self):
        """Zip scanning should honor the file_type filter."""
        zip_path = os.path.join(self.test_dir, "code.zip")
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr('a.py', 'print(1)')
            zf.writestr('a.txt', 'x')

        output = self.capture_output(zip_path, recursive=True, file_type='.py')
        self.assertIn('a.py', output)
        self.assertNotIn('a.txt', output)

    def test_nested_zip_recursive_lists_inner_files(self):
        """Recursive zip scan should show files inside nested zip entries."""
        outer_zip = os.path.join(self.test_dir, 'outer.zip')
        # Build a nested zip in-memory first
        import io as _io
        inner_bytes = _io.BytesIO()
        with zipfile.ZipFile(inner_bytes, 'w') as inner:
            inner.writestr('inner.txt', 'hi')
        inner_data = inner_bytes.getvalue()

        with zipfile.ZipFile(outer_zip, 'w') as outer:
            outer.writestr('level1/readme.md', 'readme')
            outer.writestr('inner.zip', inner_data)

        out = self.capture_output(outer_zip, recursive=True)
        self.assertIn('inner.txt', out)
        # Expect the displayed path to include both outer and inner zip
        self.assertIn('outer.zip:inner.zip:inner.txt', out)

    def test_nested_zip_non_recursive_does_not_list_inner_files(self):
        """Non-recursive zip scan should not descend into nested zips."""
        outer_zip = os.path.join(self.test_dir, 'outer_nr.zip')
        import io as _io
        inner_bytes = _io.BytesIO()
        with zipfile.ZipFile(inner_bytes, 'w') as inner:
            inner.writestr('inner.txt', 'hi')
        inner_data = inner_bytes.getvalue()

        with zipfile.ZipFile(outer_zip, 'w') as outer:
            outer.writestr('inner.zip', inner_data)

        out = self.capture_output(outer_zip, recursive=False)
        self.assertNotIn('inner.txt', out)

    def test_collaboration_info_unknown_when_no_git(self):
        """When run in a non-git temp directory, collaboration info should be unknown."""
        output = self.capture_output(self.test_dir, recursive=True, show_collaboration=True)
        # Our implementation returns 'unknown' when git isn't available or file isn't tracked
        self.assertIn('Collaboration: unknown', output)


if __name__ == "__main__":
    unittest.main()
