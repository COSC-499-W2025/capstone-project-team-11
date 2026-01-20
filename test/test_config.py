import os
import sys
import tempfile
import unittest
from io import StringIO
from contextlib import redirect_stdout

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from config import load_config, save_config, merge_settings, DEFAULTS
from scan import run_with_saved_settings

# Unit tests for config load/save/merge behavior
class TestConfigSimple(unittest.TestCase):
    # Tests that loading a non-existent config file returns the default scan settings
    def test_load_missing_returns_defaults(self):
        with tempfile.TemporaryDirectory() as td:
            config_file = os.path.join(td, "nope.json")
            config = load_config(config_file)
            self.assertEqual(config, DEFAULTS)

    # Tests that saving a config and then loading it is functional (also verify formatting of file_type) 
    def test_save_then_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            config_file = os.path.join(td, "config.json")
            data = {
                "directory": "/tmp/data",
                "recursive_choice": True,
                "file_type": ".TXT",
                "data_consent": True,
                "show_collaboration": False,
                "show_contribution_metrics": True,
                "show_contribution_summary": False
            }
            save_config(data, config_file)
            loaded = load_config(config_file)
            self.assertEqual(loaded["directory"], "/tmp/data")
            self.assertEqual(loaded["recursive_choice"], True)
            self.assertEqual(loaded["file_type"], ".txt")
            self.assertEqual(loaded["data_consent"], True)
            self.assertEqual(loaded["show_collaboration"], False)
            self.assertEqual(loaded["show_contribution_metrics"], True)
            self.assertEqual(loaded["show_contribution_summary"], False)

    # Tests that if the config file contains invalid JSON, load_config should fall back to the default scan settings
    def test_bad_json_falls_back_to_defaults(self):
        with tempfile.TemporaryDirectory() as td:
            config_file = os.path.join(td, "bad.json")
            with open(config_file, "w", encoding="utf-8") as f:
                f.write("{not-json")
            config = load_config(config_file)
            self.assertEqual(config, DEFAULTS)

    # Tests that merge_settings should let explicit arguments override values from the saved config
    def test_merge_settings_prefers_args_when_present(self):
        config = {
            "directory": "/from_config",
            "recursive_choice": False,
            "file_type": ".py",
            "data_consent": False,
            "show_collaboration": False,
            "show_contribution_metrics": False,
            "show_contribution_summary": False
        }
        args = {
            "directory": "/from_args",
            "recursive_choice": True,
            "file_type": None,
            "data_consent": True,
            "show_collaboration": True,
            "show_contribution_metrics": True,
            "show_contribution_summary": True
        }
        merged = merge_settings(args, config)
        self.assertEqual(merged["directory"], "/from_args")
        self.assertEqual(merged["recursive_choice"], True)
        self.assertEqual(merged["file_type"], None)
        self.assertEqual(merged["data_consent"], True)
        self.assertEqual(merged["show_collaboration"], True)
        self.assertEqual(merged["show_contribution_metrics"], True)
        self.assertEqual(merged["show_contribution_summary"], True)

    # Test for handling default values
    def test_partial_config_uses_defaults(self):
        config = {"directory": "/some/path"}
        args = {}
        merged = merge_settings(args, config)
        self.assertEqual(merged["directory"], "/some/path")
        self.assertEqual(merged["recursive_choice"], DEFAULTS["recursive_choice"])
        self.assertEqual(merged["file_type"], DEFAULTS["file_type"])
        self.assertEqual(merged["data_consent"], DEFAULTS["data_consent"])
        self.assertEqual(merged["show_collaboration"], DEFAULTS["show_collaboration"])
        self.assertEqual(merged["show_contribution_metrics"], DEFAULTS["show_contribution_metrics"])
        self.assertEqual(merged["show_contribution_summary"], DEFAULTS["show_contribution_summary"])

# Unit tests for config.py's integration with scan.py
class TestScanConfigIntegration(unittest.TestCase):
    def capture(self, fn, *args, **kwargs):
        buf = StringIO()
        with redirect_stdout(buf):
            fn(*args, **kwargs)
        return buf.getvalue()

    # Tests that when arguments are not provided, run_with_saved_settings should use the saved config values
    def test_uses_config_when_args_missing(self):
        with tempfile.TemporaryDirectory() as td:
            # Create a simple directory with a single .txt file
            d = os.path.join(td, "data")
            os.makedirs(d, exist_ok=True)
            txt = os.path.join(d, "a.txt")
            with open(txt, "w") as f:
                f.write("x")

            # Persist a config that points at the directory and filters to .txt files
            config_file = os.path.join(td, "config.json")
            save_config({
                "directory": d,
                "recursive_choice": False,
                "file_type": ".txt",
                "show_collaboration": False,
                "show_contribution_metrics": False,
                "show_contribution_summary": False,
                "data_consent": True
            }, config_file)

            # Pass directory explicitly since skills detection requires it
            out = self.capture(
                run_with_saved_settings, 
                directory=d,  # Add this line
                config_path=config_file
            )
            self.assertIn("a.txt", out)

    # Tests that explicit arguments passed to run_with_saved_settings should override the saved config values
    def test_args_override_config(self):
        with tempfile.TemporaryDirectory() as td:
            # Prepare one .py and one .txt file in the same directory
            d = os.path.join(td, "data")
            os.makedirs(d, exist_ok=True)
            py = os.path.join(d, "a.py")
            with open(py, "w") as f:
                f.write("print(1)")
            txt = os.path.join(d, "a.txt")
            with open(txt, "w") as f:
                f.write("x")

            # Save a config that would normally filter to .txt
            config_file = os.path.join(td, "config.json")
            save_config({
                "directory": d,
                "recursive_choice": False,
                "file_type": ".txt",
                "show_collaboration": False,
                "show_contribution_metrics": False,
                "show_contribution_summary": False,
                "data_consent": True
            }, config_file)

            # Call run_with_saved_settings with explicit arguments (file_type=".py") to override the saved .txt filter
            out = self.capture(run_with_saved_settings, directory=d, file_type=".py", recursive_choice=False, config_path=config_file)
            # Verify that .py file is shown and .txt is not
            self.assertIn("a.py", out)
            self.assertNotIn("a.txt", out)

# Run all unit tests for config.py, and its integration with scan.py 
if __name__ == "__main__":
    unittest.main()
