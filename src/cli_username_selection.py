"""
Shared helper for safely selecting a username from scanned project data.

Used by:
- generate_resume.py
- generate_portfolio.py
"""

from __future__ import annotations



def get_candidate_usernames(projects: dict, root_repo_jsons: dict | None = None, blacklist=None):
    blacklist = set(blacklist or [])
    candidates = set()

    for info in (projects or {}).values():
        if not isinstance(info, dict):
            continue

        contribs = info.get("contributions") or {}
        if isinstance(contribs, dict) and isinstance(contribs.get("contributions"), dict):
            contribs = contribs["contributions"]

        if isinstance(contribs, dict):
            for uname, entry in contribs.items():
                if isinstance(entry, dict):
                    candidates.add(uname)

    if root_repo_jsons:
        for data in root_repo_jsons.values():
            if not isinstance(data, dict):
                continue
            for key in (
                "commits_per_author",
                "lines_added_per_author",
                "lines_removed_per_author",
                "files_changed_per_author",
            ):
                per_author = data.get(key)
                if isinstance(per_author, dict):
                    candidates.update(per_author.keys())

    return sorted(
        c for c in candidates
        if c and c not in blacklist and c.lower() not in {"unknown", "n/a", "none"}
    )


def select_username_from_projects(projects: dict, root_repo_jsons: dict | None = None, blacklist=None):
    blacklist = set(blacklist or [])

    candidates = set()

    # 1) Project-level contributions
    for info in (projects or {}).values():
        if not isinstance(info, dict):
            continue

        contribs = info.get("contributions") or {}

        # Handle nested structure like:
        # {"type": "...", "repo_root": "...", "contributions": {...real users...}}
        if isinstance(contribs, dict) and isinstance(contribs.get("contributions"), dict):
            contribs = contribs["contributions"]

        # Only keep keys where the value is a dict (real user objects)
        if isinstance(contribs, dict):
            for uname, entry in contribs.items():
                if isinstance(entry, dict):
                    candidates.add(uname)

    # 2) Optional repo-level contributor maps (only from known per-author maps)
    if root_repo_jsons:
        for data in root_repo_jsons.values():
            if not isinstance(data, dict):
                continue

            for key in (
                "commits_per_author",
                "lines_added_per_author",
                "lines_removed_per_author",
                "files_changed_per_author",
            ):
                per_author = data.get(key)
                if isinstance(per_author, dict):
                    candidates.update(per_author.keys())

    # 3) Clean + sort
    candidates = sorted(
        c for c in candidates
        if c
        and c not in blacklist
        and c.lower() not in {"unknown", "n/a", "none"}
    )

    if not candidates:
        print("No contributor usernames found.")
        print("Please run a scan first to populate contributor data.")
        return None

    print("\nDetected contributor usernames:")
    for i, name in enumerate(candidates, start=1):
        print(f"  {i}. {name}")

    while True:
        choice = input("\nSelect a user by number (blank to cancel): ").strip()

        if choice == "":
            print("No selection made. Aborting.")
            return None

        if not choice.isdigit():
            print("Invalid input. Please enter a number.")
            continue

        idx = int(choice)
        if 1 <= idx <= len(candidates):
            return candidates[idx - 1]

        print(f"Invalid choice. Enter a number 1-{len(candidates)}.")
