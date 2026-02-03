import os
import re
from typing import Optional

_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_.-]{3,32}$")


def normalize_path(raw: str) -> str:
    if raw is None:
        return ""
    s = raw.strip()

    # Strip surrounding quotes: "..." or '...'
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        s = s[1:-1].strip()

    s = os.path.expanduser(s)
    s = os.path.abspath(s)
    return s


def validate_project_path(raw: str, *, allow_zip: bool = True) -> str:
    """
    Returns normalized path if valid.
    Valid = existing directory OR existing .zip (if allow_zip).
    Raises ValueError with user-friendly message if invalid.
    """
    if raw is None or not raw.strip():
        raise ValueError("Please enter a directory path or a .zip file path.")

    # "Display" version for error messages (don't turn into absolute path)
    display = raw.strip()
    if len(display) >= 2 and display[0] == display[-1] and display[0] in ("'", '"'):
        display = display[1:-1].strip()
    display = os.path.expanduser(display)  # keep ~ friendly

    # Normalized version for actual checks + returns
    path = normalize_path(raw)

    if not os.path.exists(path):
        raise ValueError(f"Path does not exist: {display}")

    if allow_zip and os.path.isfile(path) and path.lower().endswith(".zip"):
        return path

    if os.path.isdir(path):
        return path

    if os.path.isfile(path):
        raise ValueError("That path points to a file (not a folder). Use a folder path or a .zip file.")

    raise ValueError("Invalid path. Use a folder path or a .zip file.")



def prompt_project_path(prompt: str, *, allow_zip: bool = True) -> Optional[str]:
    """
    Prompt until valid. Returns None if user presses Enter on empty input.
    """
    while True:
        raw = input(prompt).strip()
        if not raw:
            return None
        try:
            return validate_project_path(raw, allow_zip=allow_zip)
        except ValueError as e:
            print(f"{e}\n")


def validate_username(raw: str) -> str:
    u = (raw or "").strip()
    if not u:
        raise ValueError("Username cannot be empty.")
    if not _USERNAME_RE.match(u):
        raise ValueError("Username must be 3–32 chars and only use letters, numbers, _, -, or .")
    return u

