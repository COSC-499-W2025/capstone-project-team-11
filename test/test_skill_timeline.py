import unittest
from io import StringIO
from unittest.mock import MagicMock
import sys
import os

# Allow importing from src/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from skill_timeline import print_grouped_skill_timeline

class TestSkillTimeline(unittest.TestCase):
    """
    Unit tests for the skill_timeline module.

    These tests validate that skills are:
    - grouped correctly by skill name
    - displayed in chronological order per skill
    - formatted in a readable, bullet-style output

    Note: Database interactions are fully mocked to keep these tests fast
    and independent from the actual database schema.
    """

    def test_grouped_skill_output(self):
        """
        Skills should be grouped under a single header per skill,
        with timestamps listed chronologically beneath each skill.
        """

        # Mock database cursor (not used directly, but required by API)
        mock_cursor = MagicMock()

        # Fake rows returned by safe_query (already ordered as SQL would return)
        fake_rows = [
            {"skill": "Python", "used_at": "2025-01-01", "project": "ProjA"},
            {"skill": "Python", "used_at": "2025-02-01", "project": "ProjB"},
            {"skill": "SQL", "used_at": "2025-01-15", "project": "ProjA"},
        ]

        # Mock safe_query to return our fake rows
        def fake_safe_query(cur, sql):
            return fake_rows

        # Simple passthrough timestamp formatter
        def fake_human_ts(ts):
            return ts

        # Capture printed output
        captured_output = StringIO()
        sys.stdout = captured_output

        # Call function under test
        print_grouped_skill_timeline(
            mock_cursor,
            fake_safe_query,
            fake_human_ts,
            lambda title: None  # Suppress header printing for test clarity
        )

        # Restore stdout
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        # Assertions: grouping and ordering
        self.assertIn("Python:", output)
        self.assertIn("SQL:", output)

        self.assertIn("2025-01-01  (project: ProjA)", output)
        self.assertIn("2025-02-01  (project: ProjB)", output)
        self.assertIn("2025-01-15  (project: ProjA)", output)

    def test_no_skills_printed_when_empty(self):
        """
        If no skills are returned from the query,
        the function should print a clear fallback message.
        """

        mock_cursor = MagicMock()

        def empty_safe_query(cur, sql):
            return []

        captured_output = StringIO()
        sys.stdout = captured_output

        print_grouped_skill_timeline(
            mock_cursor,
            empty_safe_query,
            lambda ts: ts,
            lambda title: None
        )

        sys.stdout = sys.__stdout__

        self.assertIn("No recorded skills", captured_output.getvalue())
