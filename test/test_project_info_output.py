import unittest
import os
import sys
import tempfile
import shutil
import json

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

try:
    from project_info_output import gather_project_info, output_project_info
except Exception:
    from project_info_output import gather_project_info, output_project_info

def _git_available():
    return shutil.which('git') is not None

def _robust_rmtree(path: str) -> None:
    """Remove directory tree robustly on Windows."""
    def onerror(func, p, excinfo):
        try:
            os.chmod(p, 0o700)
        except Exception:
            pass
        try:
            func(p)
        except Exception:
            pass
    shutil.rmtree(path, onerror=onerror)

class TestProjectInfoOutput(unittest.TestCase):

    def test_non_git_project_outputs_json_and_txt(self):
        td = tempfile.mkdtemp()
        out_dir = os.path.join(td, "output")
        os.makedirs(out_dir, exist_ok=True)
        try:
            # Create dummy files
            py_file = os.path.join(td, "app.py")
            md_file = os.path.join(td, "README.md")
            with open(py_file, "w", encoding="utf-8") as f:
                f.write("class Foo:\n    def bar(self):\n        return None\n")
            with open(md_file, "w", encoding="utf-8") as f:
                f.write("This is a README file used for testing.\n")

            info = gather_project_info(td)
            self.assertIn("project_name", info)
            self.assertIn("languages", info)
            self.assertIn("skills", info)
            self.assertIn("contributions", info)

            json_path, txt_path = output_project_info(info, output_dir=out_dir)
            self.assertTrue(os.path.exists(json_path))
            self.assertTrue(os.path.exists(txt_path))

            with open(json_path, "r", encoding="utf-8") as jf:
                loaded = json.load(jf)
            self.assertEqual(loaded.get("project_path"), info.get("project_path"))
        finally:
            _robust_rmtree(td)

    @unittest.skipUnless(_git_available(), "git is required for this test")
    def test_real_git_project_metrics(self):
        # Update this path to your local clone of the repo
        # Resolve the path relative to this test file to avoid calling os.getcwd()
        project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'capstone-project-team-11'))
        if not os.path.exists(project_path):
            self.skipTest(f"Expected local repo not found at {project_path}")
        out_dir = tempfile.mkdtemp()
        try:
            info = gather_project_info(project_path)
            self.assertIn("git_metrics", info)
            gm = info["git_metrics"]
            self.assertIsNotNone(gm)
            self.assertIn("total_commits", gm)
            self.assertGreaterEqual(gm["total_commits"], 1)  # at least 1 commit

            contributions = info["contributions"]
            self.assertIsInstance(contributions, dict)
            self.assertTrue(len(contributions) >= 1)

            json_path, txt_path = output_project_info(info, output_dir=out_dir)
            self.assertTrue(os.path.exists(json_path))
            self.assertTrue(os.path.exists(txt_path))
            with open(json_path, "r", encoding="utf-8") as jf:
                loaded = json.load(jf)
            self.assertIn("git_metrics", loaded)
            self.assertIn("total_commits", loaded["git_metrics"])
        finally:
            _robust_rmtree(out_dir)

if __name__ == '__main__':
    unittest.main()
