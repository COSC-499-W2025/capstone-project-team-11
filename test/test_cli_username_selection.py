import builtins
import sys
from pathlib import Path

# Make repo root importable so "src" can be imported when running pytest directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.cli_username_selection import select_username_from_projects


def test_valid_username_selection(monkeypatch):
    projects = {
        "ProjectA": {
            "contributions": {
                "alice": {"commits": 5},
                "bob": {"commits": 3},
            }
        }
    }

    monkeypatch.setattr(builtins, "input", lambda _: "1")
    username = select_username_from_projects(projects)
    assert username == "alice"


def test_invalid_input_rejected(monkeypatch):
    projects = {
        "ProjectA": {
            "contributions": {
                "alice": {"commits": 5},
            }
        }
    }

    monkeypatch.setattr(builtins, "input", lambda _: "abc")
    username = select_username_from_projects(projects)
    assert username is None


def test_blank_input_cancels(monkeypatch):
    projects = {
        "ProjectA": {
            "contributions": {
                "alice": {"commits": 5},
            }
        }
    }

    monkeypatch.setattr(builtins, "input", lambda _: "")
    username = select_username_from_projects(projects)
    assert username is None


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

    monkeypatch.setattr(builtins, "input", lambda _: "2")
    username = select_username_from_projects(projects)
    assert username == "bob"
