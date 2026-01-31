# test/test_cli_validators.py
import os
import sys
import pytest

# Add repo/src to sys.path so imports work in pytest
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(REPO_ROOT, "src")
sys.path.insert(0, SRC_DIR)

from cli_validators import (
    normalize_path,
    validate_project_path,
    validate_username,
)


def test_normalize_path_strips_whitespace_and_makes_absolute(tmp_path):
    p = tmp_path / "proj"
    p.mkdir()

    raw = f"   {p}   "
    out = normalize_path(raw)

    assert os.path.isabs(out)
    assert out == os.path.abspath(str(p))


def test_normalize_path_strips_surrounding_quotes(tmp_path):
    p = tmp_path / "proj"
    p.mkdir()

    raw = f'"{p}"'
    out = normalize_path(raw)

    assert out == os.path.abspath(str(p))


def test_validate_project_path_accepts_directory(tmp_path):
    p = tmp_path / "proj"
    p.mkdir()

    out = validate_project_path(str(p))
    assert out == os.path.abspath(str(p))


def test_validate_project_path_accepts_zip_when_allowed(tmp_path):
    z = tmp_path / "proj.zip"
    z.write_text("fake zip content")

    out = validate_project_path(str(z), allow_zip=True)
    assert out == os.path.abspath(str(z))


def test_validate_project_path_rejects_zip_when_not_allowed(tmp_path):
    z = tmp_path / "proj.zip"
    z.write_text("fake zip content")

    with pytest.raises(ValueError) as e:
        validate_project_path(str(z), allow_zip=False)

    assert "zip" in str(e.value).lower() or "folder" in str(e.value).lower()


def test_validate_project_path_rejects_nonexistent_path(tmp_path):
    missing = tmp_path / "does_not_exist"

    with pytest.raises(ValueError) as e:
        validate_project_path(str(missing))

    assert "does not exist" in str(e.value).lower()


def test_validate_project_path_rejects_regular_file(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("hello")

    with pytest.raises(ValueError) as e:
        validate_project_path(str(f), allow_zip=True)

    assert "file" in str(e.value).lower()


def test_validate_username_accepts_valid_usernames():
    assert validate_username("priyanshu") == "priyanshu"
    assert validate_username("user.name") == "user.name"
    assert validate_username("user_name") == "user_name"
    assert validate_username("user-name") == "user-name"


def test_validate_username_rejects_empty():
    with pytest.raises(ValueError):
        validate_username("")


def test_validate_username_rejects_bad_chars():
    with pytest.raises(ValueError):
        validate_username("bad username!")
