import os
import re
import json
from datetime import datetime
from pathlib import Path
import sys
from typing import Dict, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from contrib_metrics import analyze_repo

def is_git_repo(path: str, strict: bool = False) -> bool:
    """
    Return True if the given path is inside a Git repository.
    If strict=True, only returns True if .git exists directly in the path.
    """
    p = os.path.abspath(path)
    if os.path.isfile(p):
        p = os.path.dirname(p)
    if strict:
        return os.path.isdir(os.path.join(p, ".git"))
    while True:
        if os.path.isdir(os.path.join(p, ".git")):
            return True
        parent = os.path.dirname(p)
        if parent == p:
            break
        p = parent
    return False


def _should_skip_file(path: Path) -> bool:
    """Return True for macOS artifacts or container archives we want to ignore."""
    name = path.name
    if name == '.DS_Store' or name.startswith('._'):
        return True
    if name.lower().endswith('.zip'):
        return True
    if any(part == '__MACOSX' for part in path.parts):
        return True
    return False


def _find_all_git_roots(base_path: str) -> List[str]:
    """Return all git repository roots under base_path."""
    roots = []
    base_abs = os.path.abspath(base_path)
    if not os.path.exists(base_abs):
        return roots

    for root, dirs, _ in os.walk(base_abs):
        if '.git' in dirs:
            roots.append(os.path.abspath(root))
            dirs[:] = []  # do not descend further inside a git repo
            continue
        dirs[:] = [d for d in dirs if d not in {'__MACOSX'}]
    return roots


def summarize_contributions_non_git(path: str) -> dict:
    """
    Fallback for non-Git projects.
    Detects authors from inline 'Author:' comments or defaults to Unknown.
    """
    path = Path(path).resolve()
    files = [f for f in Path(path).glob("**/*") if f.is_file() and not _should_skip_file(f)]
    if not files:
        return {}

    contributions = {}

    for file in files:
        try:
            with open(file, "r", errors="ignore") as f:
                content = f.read()
                matches = re.findall(r"(?:#|//|/\*|\*)\s*Author\s*:\s*([A-Za-z]+)", content, re.IGNORECASE)
                if matches:
                    for author in matches:
                        author = author.strip()
                        if author not in contributions:
                            contributions[author] = {"commits": 0, "files": []}
                        contributions[author]["files"].append(str(file))
                else:
                    if "Unknown" not in contributions:
                        contributions["Unknown"] = {"commits": 0, "files": []}
                    contributions["Unknown"]["files"].append(str(file))
        except Exception:
            pass

    return contributions


def identify_contributions(project_path: str, output_dir: str = "output", strict_git: bool = False, write_output: bool = True) -> dict:
    """
    Identify and summarize individual contributions for a project.
    Works for both Git and non-Git folders.

    When write_output is True, export a JSON summary to output_dir.
    """
    if not os.path.exists(project_path):
        raise FileNotFoundError(f"{project_path} not found")

    def _clean_contribs(contribs: Dict[str, Dict]) -> Dict[str, Dict]:
        cleaned = {}
        for author, data in contribs.items():
            commits = data.get("commits", 0) or 0
            files = data.get("files", []) or []
            file_count = data.get("file_count", len(files))
            if commits <= 0 and file_count == 0:
                continue
            cleaned[author] = {
                "commits": commits,
                "files": files,
                "file_count": file_count,
            }
        return cleaned

    git_roots = _find_all_git_roots(project_path)
    if strict_git and not os.path.isdir(os.path.join(os.path.abspath(project_path), '.git')):
        git_roots = []

    if git_roots:
        repos = []
        for root in git_roots:
            try:
                metrics = analyze_repo(root)
            except Exception:
                continue
            commits_per_author = metrics.get("commits_per_author", {})
            files_per_author = metrics.get("files_changed_per_author", {})
            contribs = {}
            for author, commits in commits_per_author.items():
                modified_files = files_per_author.get(author, [])
                contribs[author] = {
                    "commits": commits,
                    "files": modified_files,
                    "file_count": len(modified_files),
                }
            contribs = _clean_contribs(contribs)
            repos.append({"repo_root": root, "contributions": contribs})

        # If only one repo, simplify structure
        repos = [r for r in repos if r.get("contributions")]
        if not repos:
            return {}
        if len(repos) == 1:
            r = repos[0]
            return {
                "type": "git",
                "repo_root": r.get("repo_root"),
                "contributions": r.get("contributions", {}),
            }
        return {"type": "multi_git", "repos": repos}

    # Non-git fallback
    contributions = summarize_contributions_non_git(project_path)
    for author in list(contributions.keys()):
        files = contributions[author].get("files", [])
        contributions[author]["file_count"] = len(files)
        if contributions[author].get("commits", 0) <= 0 and len(files) == 0:
            contributions.pop(author, None)
    return {"type": "non_git", "contributions": contributions}


def summarize_project_contributions(directory: str, output_dir: str = "output"):
    """Summarize and print contribution details for a project directory."""
    try:
        print("\n=== Contribution Summary ===")
        contributions = identify_contributions(directory, output_dir=output_dir, write_output=False)
        if not contributions:
            print("No contributions detected.")
            return

        def _print_block(label: str, contribs: Dict[str, Dict]):
            if not contribs:
                print(f"{label}: No contributions detected.")
                return
            ordered = sorted(contribs.items(), key=lambda kv: (-kv[1].get("commits", 0), kv[0]))
            print(label)
            for author, stats in ordered:
                print(f"  {author}: {stats.get('commits', 0)} commits, {stats.get('file_count', len(stats.get('files', [])))} files")
                files = stats.get("files", []) or []
                if files:
                    for f in files:
                        print(f"    - {f}")

        ctype = contributions.get("type") if isinstance(contributions, dict) else None
        if ctype == "multi_git":
            repos = contributions.get("repos", [])
            if not repos:
                print("No contributions detected.")
                return
            printed = set()
            for repo in repos:
                root = repo.get("repo_root", "(repo)")
                if root in printed:
                    continue
                printed.add(root)
                _print_block(f"Repo: {root}", repo.get("contributions", {}))
        elif ctype == "git":
            root = contributions.get("repo_root", "(repo)")
            _print_block(f"Repo: {root}", contributions.get("contributions", {}))
        elif ctype == "non_git":
            _print_block("Files", contributions.get("contributions", {}))
        else:
            _print_block("Contributions", contributions)
    except FileNotFoundError:
        print(f"[Error] The directory '{directory}' does not exist.")
    except Exception as e:
        print(f"[Warning] Could not summarize contributions: {e}")
