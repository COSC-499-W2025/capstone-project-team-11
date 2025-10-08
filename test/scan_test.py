import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import tempfile
import shutil
from io import StringIO
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


if __name__ == "__main__":
    unittest.main()
