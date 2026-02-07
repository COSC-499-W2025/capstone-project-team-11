import builtins
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.cli_username_selection import select_username_from_projects, select_identity_from_projects


def test_select_identity_git_username_no_non_git(monkeypatch):
    projects = {
        "Proj": {"contributions": {"alice": {"commits": 1}}, "languages": ["Python"]}
    }
    monkeypatch.setattr(builtins, "input", lambda _: "1")  
    username, selected = select_identity_from_projects(projects, root_repo_jsons={}, blacklist=set())
    assert username == "alice"
    assert selected == []

def test_select_identity_git_username_with_non_git(monkeypatch):
    projects = {
        "GitProj": {"contributions": {"alice": {"commits": 1}}, "languages": ["Python"]},
        "NonGit": {"contributions": {}, "languages": ["Java"]},
    }

    inputs = iter(["1", "y", "1"])  
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    username, selected = select_identity_from_projects(projects, root_repo_jsons={}, blacklist=set())
    assert username == "alice"
    assert selected == ["NonGit"]

def test_select_identity_local_guest_requires_selection(monkeypatch):
    projects = {
        "NonGit": {"contributions": {}, "languages": ["Java"]},
    }
    inputs = iter(["0", "1"])  
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    username, selected = select_identity_from_projects(projects, root_repo_jsons={}, blacklist=set())
    assert username is None
    assert selected == ["NonGit"]

def test_select_identity_blank_cancels(monkeypatch):
    projects = {"Proj": {"contributions": {"alice": {"commits": 1}}, "languages": ["Python"]}}
    monkeypatch.setattr(builtins, "input", lambda _: "")  
    username, selected = select_identity_from_projects(projects, root_repo_jsons={}, blacklist=set())
    assert username is None
    assert selected == []
