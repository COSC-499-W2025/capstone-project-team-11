import os
import sys
import tempfile
import unittest
import shutil

# Add src to path
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
)

from db import init_db, clear_database


class TestClearDatabaseOutputDirectory(unittest.TestCase):

    def setUp(self):
        # --- Temporary database ---
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.environ["FILE_DATA_DB_PATH"] = self.db_path
        init_db()

        # --- Create fake src/output structure ---
        self.src_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'src')
        )
        self.output_dir = os.path.join(self.src_dir, "output")

        os.makedirs(self.output_dir, exist_ok=True)

        # Create fake project output folders
        self.project_dirs = [
            os.path.join(self.output_dir, "project-one"),
            os.path.join(self.output_dir, "project-two"),
        ]

        for d in self.project_dirs:
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "dummy.txt"), "w", encoding="utf-8") as f:
                f.write("test data")

        # Sanity check
        for d in self.project_dirs:
            self.assertTrue(os.path.isdir(d))

    def tearDown(self):
        # Clean up temp DB
        os.close(self.db_fd)
        os.unlink(self.db_path)
        os.environ.pop("FILE_DATA_DB_PATH", None)

        # Clean up output directory if it still exists
        if os.path.isdir(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_clear_database_removes_output_subfolders(self):
        # Act
        clear_database()

        # Assert: output directory still exists
        self.assertTrue(
            os.path.isdir(self.output_dir),
            "src/output directory should not be deleted"
        )

        # Assert: output directory is empty
        remaining = os.listdir(self.output_dir)
        self.assertEqual(
            remaining,
            [],
            f"Expected src/output to be empty, found: {remaining}"
        )


if __name__ == "__main__":
    unittest.main()
