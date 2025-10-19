import os
import sys
import json
import tempfile
import unittest
from io import StringIO
from contextlib import redirect_stdout
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from config import load_config, save_config, merge_settings, DEFAULTS
from scan import run_with_saved_settings

class TestConfigSimple(unittest.TestCase):
    def test_load_missing_returns_defaults(self):
        with tempfile.TemporaryDirectory() as td:
            config_file = os.path.join(td, "nope.json")
            config = load_config(config_file)
            self.assertEqual(config["directory"], None)
            self.assertEqual(config["recursive_choice"], False)
            self.assertEqual(config["file_type"], None)

    def test_save_then_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            config_file = os.path.join(td, "config.json")
            data = {"directory": "/tmp/data", "recursive_choice": True, "file_type": ".TXT"}
            save_config(data, config_file)
            loaded = load_config(config_file)
            self.assertEqual(loaded["directory"], "/tmp/data")
            self.assertEqual(loaded["recursive_choice"], True)
            self.assertEqual(loaded["file_type"], ".txt")

    def test_bad_json_falls_back_to_defaults(self):
        with tempfile.TemporaryDirectory() as td:
            config_file = os.path.join(td, "bad.json")
            with open(config_file, "w", encoding="utf-8") as f:
                f.write("{not-json")
            config = load_config(config_file)
            self.assertEqual(config, DEFAULTS)

    def test_merge_settings_prefers_args_when_present(self):
        config = {"directory": "/from_config", "recursive_choice": False, "file_type": ".py"}
        args = {"directory": "/from_args", "recursive_choice": True, "file_type": None}
        merged = merge_settings(args, config)
        self.assertEqual(merged["directory"], "/from_args")
        self.assertEqual(merged["recursive_choice"], True)
        self.assertEqual(merged["file_type"], ".py")

class TestScanConfigIntegration(unittest.TestCase):
    def capture(self, fn, *args, **kwargs):
        buf = StringIO()
        with redirect_stdout(buf):
            fn(*args, **kwargs)
        return buf.getvalue()

    def test_uses_config_when_args_missing(self):
        with tempfile.TemporaryDirectory() as td:
            d = os.path.join(td, "data")
            os.makedirs(d, exist_ok=True)
            txt = os.path.join(d, "a.txt")
            with open(txt, "w") as f:
                f.write("x")
            config_file = os.path.join(td, "config.json")
            save_config({"directory": d, "recursive_choice": False, "file_type": ".txt"}, config_file)
            out = self.capture(run_with_saved_settings, config_path=config_file)
            self.assertIn("a.txt", out)

    def test_args_override_config(self):
        with tempfile.TemporaryDirectory() as td:
            d = os.path.join(td, "data")
            os.makedirs(d, exist_ok=True)
            py = os.path.join(d, "a.py")
            with open(py, "w") as f:
                f.write("print(1)")
            txt = os.path.join(d, "a.txt")
            with open(txt, "w") as f:
                f.write("x")

            config_file = os.path.join(td, "config.json")
            save_config({"directory": d, "recursive_choice": False, "file_type": ".txt"}, config_file)
            out = self.capture(run_with_saved_settings, directory=d, file_type=".py", recursive_choice=False, config_path=config_file)

            self.assertIn("a.py", out)
            self.assertNotIn("a.txt", out)

if __name__ == "__main__":
    unittest.main()
