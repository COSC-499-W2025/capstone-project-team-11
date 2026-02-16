import os
import sys
import tempfile
import shutil
import unittest
from io import StringIO
from contextlib import redirect_stdout

# Make sure src is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from scan import list_files_in_directory

class TestRelativePaths(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory structure
        self.test_dir = tempfile.mkdtemp()
        self.sub_dir = os.path.join(self.test_dir, "subfolder")
        os.makedirs(self.sub_dir)

        # Create test files
        self.files = [
            os.path.join(self.test_dir, "file_root.txt"),
            os.path.join(self.sub_dir, "file_nested.txt")
        ]
        for f in self.files:
            with open(f, "w") as fp:
                fp.write("test content")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_relative_vs_absolute_paths(self):
        # Change current working directory to parent of temp dir
        original_cwd = os.getcwd()
        os.chdir(os.path.dirname(self.test_dir))
        try:
            relative_path = os.path.relpath(self.test_dir)
            # Capture stdout if your function prints
            buf = StringIO()
            with redirect_stdout(buf):
                result = list_files_in_directory(relative_path, recursive=True)
            # All files should be found
            found_files = [os.path.basename(f[0]) for f in result]
            self.assertIn("file_root.txt", found_files)
            self.assertIn("file_nested.txt", found_files)
        finally:
            os.chdir(original_cwd)

    def test_absolute_path_works_same_as_relative(self):
        # Using absolute path
        abs_path = os.path.abspath(self.test_dir)
        buf = StringIO()
        with redirect_stdout(buf):
            result_abs = list_files_in_directory(abs_path, recursive=True)
        found_abs = [os.path.basename(f[0]) for f in result_abs]

        # Using relative path
        rel_path = os.path.relpath(self.test_dir)
        buf = StringIO()
        with redirect_stdout(buf):
            result_rel = list_files_in_directory(rel_path, recursive=True)
        found_rel = [os.path.basename(f[0]) for f in result_rel]

        # Both lists should be identical
        self.assertEqual(sorted(found_abs), sorted(found_rel))


if __name__ == "__main__":
    unittest.main()
