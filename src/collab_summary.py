import os
import re
import json
from datetime import datetime
from pathlib import Path
import sys

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


def summarize_contributions_non_git(path: str) -> dict:
    """
    Fallback for non-Git projects.
    Detects authors from inline 'Author:' comments or defaults to Unknown.
    """
    path = Path(path).resolve()
    files = [f for f in Path(path).glob("**/*") if f.is_file()]
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

    if is_git_repo(project_path, strict=strict_git):
        detailed_metrics = analyze_repo(project_path)
        contributions = {}
        commits_per_author = detailed_metrics.get("commits_per_author", {})
        files_per_author = detailed_metrics.get("files_changed_per_author", {})

        for author, commits in commits_per_author.items():
            modified_files = files_per_author.get(author, [])
            contributions[author] = {
                "commits": commits,
                "files": modified_files,
                "file_count": len(modified_files),
            }
        project_type = "git"
    else:
        contributions = summarize_contributions_non_git(project_path)
        for author in contributions:
            contributions[author]["file_count"] = len(contributions[author]["files"])
        project_type = "non_git"

    return contributions


def summarize_project_contributions(directory: str, output_dir: str = "output"):
    """Summarize and print contribution details for a project directory."""
    try:
        print("\n=== Contribution Summary ===")
        contributions = identify_contributions(directory, output_dir=output_dir, write_output=False)
        if not contributions:
            print("No contributions detected.")
            return

        for author, stats in contributions.items():
            print(f"{author}: {stats.get('commits', 0)} commits, {stats.get('file_count', len(stats.get('files', [])))} files")
            if stats.get("files"):
                print("  Changed files:")
                for f in stats["files"]:
                    print(f"    - {f}")
    except FileNotFoundError:
        print(f"[Error] The directory '{directory}' does not exist.")
    except Exception as e:
        print(f"[Warning] Could not summarize contributions: {e}")
