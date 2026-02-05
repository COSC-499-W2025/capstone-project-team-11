import builtins
import sys
from pathlib import Path

# Make repo root importable so "src" can be imported when running pytest directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.cli_username_selection import select_username_from_projects


def make_inputs(seq):
    it = iter(seq)

    def _fake_input(_prompt=""):
        # If inputs run out, return blank -> should cancel
        return next(it, "")

    return _fake_input


def test_valid_username_selection(monkeypatch):
    projects = {
        "ProjectA": {
            "contributions": {
                "alice": {"commits": 5},
                "bob": {"commits": 3},
            }
        }
    }

    monkeypatch.setattr(builtins, "input", make_inputs(["1"]))
    assert select_username_from_projects(projects) == "alice"


def test_invalid_input_then_cancel(monkeypatch):
    projects = {
        "ProjectA": {
            "contributions": {
                "alice": {"commits": 5},
            }
        }
    }

    monkeypatch.setattr(builtins, "input", make_inputs(["abc", ""]))
    assert select_username_from_projects(projects) is None


def test_blank_input_cancels(monkeypatch):
    projects = {
        "ProjectA": {
            "contributions": {
                "alice": {"commits": 5},
            }
        }
    }

    monkeypatch.setattr(builtins, "input", make_inputs([""]))
    assert select_username_from_projects(projects) is None


def test_nested_contributions_unwrapped(monkeypatch):
    projects = {
        "ProjectA": {
            "contributions": {
                "type": "root",
                "repo_root": "/tmp/repo",
                "contributions": {
                    "alice": {"commits": 5},
                    "bob": {"commits": 3},
                },
            }
        }
    }

    monkeypatch.setattr(builtins, "input", make_inputs(["2"]))
    assert select_username_from_projects(projects) == "bob"
