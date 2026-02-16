"""
Shared helper for safely selecting a username from scanned project data.

Used by:
- generate_resume.py
- generate_portfolio.py
"""

from __future__ import annotations

from cli_output import print_error

def get_non_git_projects(projects: dict) -> list[str]:
    """
    Non-git projects = projects with no usable contribution map.
    We'll treat contributions == {} / None / missing as non-git.
    """
    non_git = []

    for name, info in (projects or {}).items():
        if not isinstance(info, dict):
            continue

        contribs = info.get("contributions")

        # unwrap nested shape if present
        if isinstance(contribs, dict) and isinstance(contribs.get("contributions"), dict):
            contribs = contribs["contributions"]

        has_contribs = isinstance(contribs, dict) and any(isinstance(v, dict) for v in contribs.values())

        if not has_contribs:
            # only include if it has some metadata (otherwise it's probably junk)
            has_metadata = bool(info.get("languages") or info.get("frameworks") or info.get("skills"))
            if has_metadata:
                non_git.append(name)

    return sorted(non_git)


def prompt_select_non_git_projects(non_git_projects: list[str]) -> list[str] | None:
    """
    Returns a list of selected project names.
    Blank input cancels -> None
    """
    if not non_git_projects:
        print_error("No non-git projects found in the database.")
        return []

    print("\nNon-git projects found:")
    for i, name in enumerate(non_git_projects, start=1):
        print(f"  {i}. {name}")

    print("Select projects by number (comma-separated). Example: 1,3,4")
    choice = input("Enter selection (blank to cancel): ").strip()

    if choice == "":
        return None

    parts = [p.strip() for p in choice.split(",") if p.strip()]
    if not parts:
        print_error("Invalid selection.", "Enter project numbers like 1,3,4 or press Enter to cancel.")
        return None

    nums = []
    for p in parts:
        if not p.isdigit():
            print_error("Invalid selection.", "Use numbers only (example: 1,3,4).")
            return None
        nums.append(int(p))

    selected = []
    for n in nums:
        if n < 1 or n > len(non_git_projects):
            print_error("Selection out of range.", f"Enter numbers between 1 and {len(non_git_projects)}.")
            return None
        selected.append(non_git_projects[n - 1])

    # de-dup, keep order
    seen = set()
    out = []
    for x in selected:
        if x not in seen:
            seen.add(x)
            out.append(x)

    return out



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
        print_error("No contributor usernames found.", "Run a scan first to populate contributor data.")
        return None

    print("\nDetected contributor usernames:")
    for i, name in enumerate(candidates, start=1):
        print(f"  {i}. {name}")

    while True:
        choice = input("\nSelect a user by number (blank to cancel): ").strip()

        if choice == "":
            return None

        if not choice.isdigit():
            print_error("Invalid selection.", "Enter a number or press Enter to cancel.")
            continue

        idx = int(choice)
        if 1 <= idx <= len(candidates):
            return candidates[idx - 1]

    return candidates[idx]

def get_candidate_usernames(projects: dict, root_repo_jsons: dict | None = None, blacklist=None):
    blacklist = set(blacklist or [])
    candidates = set()

    # project-level contributors
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

    # repo-level contributor maps
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


def select_identity_from_projects(
    projects: dict,
    root_repo_jsons: dict | None = None,
    blacklist=None
) -> tuple[str | None, list[str]]:
    """
    Returns (username, selected_non_git_projects)

    username:
      - string = selected git username
      - None   = "local/guest" mode (no git username)

    selected_non_git_projects:
      - list of project names the user picked
    """
    blacklist = set(blacklist or [])

    usernames = get_candidate_usernames(projects, root_repo_jsons, blacklist)
    non_git_projects = get_non_git_projects(projects)

    if not usernames and not non_git_projects:
        print_error("No usernames or non-git projects found.", "Run a scan first to populate data.")
        return (None, [])

    print("\nChoose a GitHub username from the list below:")
    print("  0. Generate using NO git username (local/guest)")

    for i, name in enumerate(usernames, start=1):
        print(f"  {i}. {name}")

    while True:
        choice = input("\nSelect by number (blank to cancel): ").strip()

        if choice == "":
            return (None, [])

        if not choice.isdigit():
            print_error("Invalid selection.", "Enter a number or press Enter to cancel.")
            continue

        idx = int(choice)

        # local/guest mode
        if idx == 0:
            selected = prompt_select_non_git_projects(non_git_projects)
            if selected is None:
                return (None, [])
            return (None, selected)

        if 1 <= idx <= len(usernames):
            username = usernames[idx - 1]

            include = input("Include non-git projects too? (y/n): ").strip().lower()
            if include == "y":
                selected = prompt_select_non_git_projects(non_git_projects)
                if selected is None:
                    return (None, [])
                return (username, selected)

            return (username, [])

        print_error("Selection out of range.", f"Enter a number between 0 and {len(usernames)}, or press Enter to cancel.")

