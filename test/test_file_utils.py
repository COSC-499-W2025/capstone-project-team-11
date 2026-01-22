import os
import sys
import unittest

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from file_utils import is_valid_format


class TestFileUtils(unittest.TestCase):

    def test_valid_formats(self):
        """Test that valid file formats are accepted."""
        self.assertTrue(is_valid_format("example.txt"))
        self.assertTrue(is_valid_format("data.csv"))
        self.assertTrue(is_valid_format("image.jpg"))
        self.assertTrue(is_valid_format("archive.zip"))

    def test_invalid_formats(self):
        """Test that invalid file formats are rejected."""
        self.assertFalse(is_valid_format("malware.exe"))
        self.assertFalse(is_valid_format("script.bat"))
        self.assertFalse(is_valid_format("unknown.xyz"))

    def test_case_insensitivity(self):
        """Test that file format validation is case-insensitive."""
        self.assertTrue(is_valid_format("example.TXT"))
        self.assertTrue(is_valid_format("data.CSV"))
        self.assertTrue(is_valid_format("image.JPG"))
        self.assertTrue(is_valid_format("archive.ZIP"))

    def test_no_extension(self):
        """Test that files with no extension are rejected."""
        self.assertFalse(is_valid_format("no_extension"))

    def test_hidden_files(self):
        """Test that hidden files with valid extensions are accepted."""
        self.assertTrue(is_valid_format(".hidden.txt"))
        self.assertFalse(is_valid_format(".hiddenfile"))

    def test_empty_filename(self):
        """Test that empty filenames are rejected."""
        self.assertFalse(is_valid_format(""))

    def test_whitespace_in_filename(self):
        """Test that filenames with leading/trailing whitespace are handled correctly."""
        self.assertTrue(is_valid_format(" example.txt "))
        self.assertFalse(is_valid_format(" unknown.xyz "))

    def test_special_characters_in_filename(self):
        """Test that filenames with special characters are handled correctly."""
        self.assertTrue(is_valid_format("file-name.txt"))
        self.assertTrue(is_valid_format("file_name.csv"))
        self.assertFalse(is_valid_format("file@name.exe"))


if __name__ == "__main__":
    unittest.main()
