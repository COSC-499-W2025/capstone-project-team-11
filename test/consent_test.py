import os
import sys
import tempfile
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from consent import describe_data_access, ask_yes_no, ask_for_data_consent
from config import load_config, save_config, DEFAULTS
from io import StringIO
from contextlib import redirect_stdout
from unittest.mock import patch

class TestConsentHelpers(unittest.TestCase):
    # Helper function to call functions with parameters and store their printed output
    def capture(self, fn, *args, **kwargs):
        buf = StringIO()
        with redirect_stdout(buf):
            fn(*args, **kwargs)
        return buf.getvalue()

    # Tests that describe_data_access() functions correctly
    def test_describe_data_access_prints_items(self):
        # Provide explicit items and ensure that they appear in output
        out1 = self.capture(describe_data_access, ["item1", "item2"])
        self.assertIn("item1", out1)
        self.assertIn("item2", out1)

        # Call with no items to get default list
        out2 = self.capture(describe_data_access)
        self.assertIn("file names and directory structure", out2)
        self.assertIn("file metadata (size, modification time)", out2)
        self.assertIn("file contents when opened for scanning/parsing", out2)

    # Tests that ask_yes_no() returns correct boolean for accepted inputs, and reprompts until a valid input is given
    def test_ask_yes_no_accepts_valid_and_reprompts(self):
        # Pass in an invalid input first, then a valid one (y).
        with patch('builtins.input', side_effect=['', 'maybe', 'honey', 'buyant', 'y']):
            self.assertTrue(ask_yes_no("Prompt: "))
        # Pass in a direct no
        with patch('builtins.input', return_value='n'):
            self.assertFalse(ask_yes_no("Prompt: "))

    # Tests that ask_for_data_consent() correctly saves user preference when requested
    def test_ask_for_data_consent_saves_preference(self):
        with tempfile.TemporaryDirectory() as td:
            config = os.path.join(td, "config.json")
            # Simulates granting consent and choosing to save preference.
            with patch('builtins.input', return_value='y'):
                out = self.capture(ask_for_data_consent, config_path=config)
            # Verify config file was written and contains data_consent=true
            loaded = load_config(config)
            self.assertTrue(loaded.get("data_consent"))

    # Tests that ask_for_data_consent() does not save preference when user opts out
    def test_ask_for_data_consent_no_save_leaves_config_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            config = os.path.join(td, "config.json")
            # Simulates not granting consent and not saving
            with patch('builtins.input', side_effect=['n', 'n']):
                out = self.capture(ask_for_data_consent, config_path=config)
            # Since we didn't save, config file shouldn't exist, so load_config() returns default values
            loaded = load_config(config)
            self.assertEqual(loaded, DEFAULTS)

if __name__ == "__main__":
    unittest.main()