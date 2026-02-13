"""
Clean, **no-loop**, non-mocking test suite for main_menu.py.

This test file NEVER calls main(), because main() contains an infinite
menu loop that cannot be unit tested without extensive mocking.

This suite instead tests:
- print_main_menu()
- safe_query()
- human_ts()
- handle_inspect_database() using an in-memory DB
"""

import sqlite3
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from main_menu import (
    print_main_menu,
    safe_query,
    human_ts,
    handle_inspect_database,
    handle_analyze_roles,
    _preview_resume,
    _markdown_to_plain,
    _delete_resume,
)


# Utility: create an in-memory temporary database

def create_temp_db():
    """Create minimal schema required for handle_inspect_database()."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE scans(
            id INTEGER PRIMARY KEY,
            scanned_at TEXT,
            project TEXT,
            notes TEXT
        );

        CREATE TABLE projects(
            id INTEGER PRIMARY KEY,
            name TEXT,
            repo_url TEXT,
            created_at TEXT,
            thumbnail_path TEXT
        );

        CREATE TABLE files(
            id INTEGER PRIMARY KEY,
            file_name TEXT,
            file_path TEXT,
            file_extension TEXT,
            file_size INTEGER,
            modified_at TEXT,
            scan_id INTEGER
        );

        CREATE TABLE skills(id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE project_skills(project_id INTEGER, skill_id INTEGER);
        CREATE TABLE languages(id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE file_languages(file_id INTEGER, language_id INTEGER);
        CREATE TABLE contributors(id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE file_contributors(file_id INTEGER, contributor_id INTEGER);
        CREATE TABLE resumes(id INTEGER PRIMARY KEY, contributor_id INTEGER, username TEXT, resume_path TEXT, metadata_json TEXT, generated_at TEXT);
    """)

    conn.commit()
    return conn


# Test print_main_menu()

def test_print_main_menu_outputs_correct_text(capsys):
    print_main_menu()
    output = capsys.readouterr().out

    assert "=== MDA OPERATIONS MENU ===" in output
    assert "1. Scan Project" in output
    assert "2. View/Manage Scanned Projects" in output
    assert "3. Generate Resume" in output
    assert "4. Generate Portfolio" in output
    assert "5. View/Manage Resumes" in output
    assert "6. View/Manage Portfolios" in output
    assert "7. Rank Projects" in output
    assert "8. Summarize Contributor Projects" in output
    assert "9. Manage Evidence of Success" in output
    assert "10. Analyze Contributor Roles" in output
    assert "11. Edit Thumbnail for a Project" in output
    assert "12. Manage Database" in output
    assert "0. Exit" in output



# Test safe_query()

def test_safe_query_valid():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("CREATE TABLE t (id INTEGER)")
    cur.execute("INSERT INTO t VALUES (1)")

    rows = safe_query(cur, "SELECT * FROM t")
    assert len(rows) == 1
    assert rows[0]["id"] == 1


def test_safe_query_missing_table():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    rows = safe_query(cur, "SELECT * FROM nope")
    assert rows == []


# =============================================================================
# Test human_ts()
# =============================================================================

def test_human_ts_standard():
    assert human_ts("2024-01-01 12:00:00") == "2024-01-01 12:00:00"


def test_human_ts_iso():
    assert human_ts("2024-01-01T12:00:00") == "2024-01-01 12:00:00"


def test_human_ts_invalid():
    assert human_ts("x123") == "x123"


def test_human_ts_none():
    assert human_ts(None) == "N/A"


# Test handle_inspect_database()

def test_handle_inspect_database_works(monkeypatch, capsys):
    temp_conn = create_temp_db()

    # Make main_menu use the in-memory DB instead of the real DB_PATH
    monkeypatch.setattr("main_menu.get_connection", lambda: temp_conn)
    monkeypatch.setattr("main_menu.DB_PATH", ":memory:")

    handle_inspect_database()

    out = capsys.readouterr().out

    assert "Inspecting DB" in out
    assert "Tables in database" in out
    assert "Recent scans" in out
    assert "Projects and skills" in out
    assert "Project thumbnails" in out
    assert "Top languages" in out
    assert "Contributors" in out


def test_preview_resume_reads_file(tmp_path):
    p = tmp_path / "resume.md"
    p.write_text("line1\nline2\nline3\n", encoding="utf-8")
    preview, truncated = _preview_resume(str(p))
    assert "line1" in preview and "line2" in preview and "line3" in preview
    assert truncated is False


def test_markdown_to_plain_simple():
    md = "# Title\n- bullet\n**bold** and `code`\n[link](http://x.com)"
    out = _markdown_to_plain(md)
    assert "TITLE" in out
    assert "- bullet" in out
    assert "bold" in out and "code" in out
    assert "link (http://x.com)" in out


def test_delete_resume_removes_db_row_and_file(tmp_path):
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    cur.executescript("""
        CREATE TABLE contributors(id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE resumes(id INTEGER PRIMARY KEY, contributor_id INTEGER, username TEXT, resume_path TEXT, metadata_json TEXT, generated_at TEXT);
    """)
    db.commit()

    # create file
    resume_file = tmp_path / "resume.md"
    resume_file.write_text("hello", encoding="utf-8")

    cur.execute("INSERT INTO contributors(name) VALUES ('alice')")
    cur.execute(
        "INSERT INTO resumes(contributor_id, username, resume_path, metadata_json, generated_at) VALUES (1, 'alice', ?, '{}', '2025-01-01')",
        (str(resume_file),)
    )
    db.commit()

    row = db.execute("SELECT * FROM resumes WHERE id = 1").fetchone()
    ok, msg = _delete_resume(db, row)
    assert ok is True
    assert not os.path.exists(resume_file)
    rows = db.execute("SELECT COUNT(*) AS c FROM resumes").fetchone()
    assert rows["c"] == 0


def test_delete_resume_handles_missing_file(tmp_path):
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    cur.executescript("""
        CREATE TABLE contributors(id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE resumes(id INTEGER PRIMARY KEY, contributor_id INTEGER, username TEXT, resume_path TEXT, metadata_json TEXT, generated_at TEXT);
    """)
    db.commit()

    missing_path = tmp_path / "missing.md"
    cur.execute("INSERT INTO contributors(name) VALUES ('bob')")
    cur.execute(
        "INSERT INTO resumes(contributor_id, username, resume_path, metadata_json, generated_at) VALUES (1, 'bob', ?, '{}', '2025-01-02')",
        (str(missing_path),)
    )
    db.commit()

    row = db.execute("SELECT * FROM resumes WHERE id = 1").fetchone()
    ok, msg = _delete_resume(db, row)
    assert ok is True
    assert "file not found" in msg.lower() or "already removed" in msg.lower()
    rows = db.execute("SELECT COUNT(*) AS c FROM resumes").fetchone()
    assert rows["c"] == 0


# =============================================================================
# Test handle_analyze_roles()
# =============================================================================

def test_handle_analyze_roles_with_no_data(monkeypatch, capsys):
    """Test that handle_analyze_roles handles empty database gracefully."""
    # Mock load_contributors_from_db to return empty dict
    monkeypatch.setattr("main_menu.load_contributors_from_db", lambda: {})
    monkeypatch.setattr("main_menu.ask_yes_no", lambda prompt: False)  # Mock input

    handle_analyze_roles()

    out = capsys.readouterr().out
    assert "Error: No contributor data found in the database" in out
    assert "Run a directory scan first" in out


def test_handle_analyze_roles_with_data_no_per_project(monkeypatch, capsys):
    """Test handle_analyze_roles displays overall analysis without per-project breakdown."""
    # Mock data
    mock_contributors = {
        "alice": {
            "files_changed": ["main.py", "utils.py", "config.py"],
            "commits": 10,
            "lines_added": 500,
            "lines_removed": 50,
            "activity_by_category": {"code": 3, "test": 0, "docs": 0, "design": 0, "other": 0}
        }
    }
    
    # Mock functions
    monkeypatch.setattr("main_menu.load_contributors_from_db", lambda: mock_contributors)
    monkeypatch.setattr("main_menu.ask_yes_no", lambda prompt: False)  # No per-project

    handle_analyze_roles()

    out = capsys.readouterr().out
    assert "Analyze Contributor Roles" in out
    assert "Found 1 contributors" in out
    assert "PROJECT ROLE ANALYSIS REPORT" in out
    assert "ALICE" in out
    # Should NOT have per-project section
    assert "PER-PROJECT CONTRIBUTIONS" not in out


def test_handle_analyze_roles_with_per_project_data(monkeypatch, capsys):
    """Test handle_analyze_roles displays per-project breakdown when requested."""
    # Mock overall data
    mock_contributors = {
        "alice": {
            "files_changed": ["main.py", "utils.py", "app.js"],
            "commits": 15,
            "lines_added": 750,
            "lines_removed": 75,
            "activity_by_category": {"code": 3, "test": 0, "docs": 0, "design": 0, "other": 0}
        }
    }
    
    # Mock per-project data
    mock_per_project = {
        "Project1": {
            "alice": {
                "files_changed": ["main.py", "utils.py"],
                "commits": 10,
                "lines_added": 500,
                "lines_removed": 50,
                "activity_by_category": {"code": 2, "test": 0, "docs": 0, "design": 0, "other": 0}
            }
        },
        "Project2": {
            "alice": {
                "files_changed": ["app.js"],
                "commits": 5,
                "lines_added": 250,
                "lines_removed": 25,
                "activity_by_category": {"code": 1, "test": 0, "docs": 0, "design": 0, "other": 0}
            }
        }
    }
    
    # Mock functions - return True for per-project question
    monkeypatch.setattr("main_menu.load_contributors_from_db", lambda: mock_contributors)
    monkeypatch.setattr("main_menu.load_contributors_per_project_from_db", lambda: mock_per_project)
    monkeypatch.setattr("main_menu.ask_yes_no", lambda prompt: True)

    handle_analyze_roles()

    out = capsys.readouterr().out
    assert "Analyze Contributor Roles" in out
    assert "Found 1 contributors" in out
    assert "Found 2 projects" in out
    assert "PROJECT ROLE ANALYSIS REPORT" in out
    assert "PER-PROJECT CONTRIBUTIONS" in out
    assert "Project1" in out
    assert "Project2" in out
    assert "alice" in out


def test_handle_analyze_roles_per_project_empty(monkeypatch, capsys):
    """Test handle_analyze_roles handles empty per-project data."""
    mock_contributors = {
        "bob": {
            "files_changed": ["test.py", "test2.py", "test3.py"],
            "commits": 8,
            "lines_added": 400,
            "lines_removed": 40,
            "activity_by_category": {"code": 0, "test": 3, "docs": 0, "design": 0, "other": 0}
        }
    }
    
    # Mock functions - return True for per-project but empty data
    monkeypatch.setattr("main_menu.load_contributors_from_db", lambda: mock_contributors)
    monkeypatch.setattr("main_menu.load_contributors_per_project_from_db", lambda: {})
    monkeypatch.setattr("main_menu.ask_yes_no", lambda prompt: True)

    handle_analyze_roles()

    out = capsys.readouterr().out
    assert "No per-project data found" in out
    assert "PROJECT ROLE ANALYSIS REPORT" in out
    # Should still show overall analysis
    assert "BOB" in out


def test_handle_analyze_roles_multiple_contributors(monkeypatch, capsys):
    """Test handle_analyze_roles with multiple contributors."""
    mock_contributors = {
        "alice": {
            "files_changed": ["main.py", "utils.py", "config.py"],
            "commits": 10,
            "lines_added": 500,
            "lines_removed": 50,
            "activity_by_category": {"code": 3, "test": 0, "docs": 0, "design": 0, "other": 0}
        },
        "bob": {
            "files_changed": ["test_main.py", "test_utils.py", "test_config.py"],
            "commits": 8,
            "lines_added": 400,
            "lines_removed": 40,
            "activity_by_category": {"code": 0, "test": 3, "docs": 0, "design": 0, "other": 0}
        },
        "charlie": {
            "files_changed": ["icon.svg", "logo.png"],
            "commits": 3,
            "lines_added": 0,
            "lines_removed": 0,
            "activity_by_category": {"code": 0, "test": 0, "docs": 0, "design": 2, "other": 0}
        }
    }
    
    monkeypatch.setattr("main_menu.load_contributors_from_db", lambda: mock_contributors)
    monkeypatch.setattr("main_menu.ask_yes_no", lambda prompt: False)

    handle_analyze_roles()

    out = capsys.readouterr().out
    assert "Found 3 contributors" in out
    assert "ALICE" in out
    assert "BOB" in out
    assert "CHARLIE" in out
    assert "Total Contributors: 3" in out


def test_handle_analyze_roles_displays_metrics(monkeypatch, capsys):
    """Test that handle_analyze_roles displays contribution metrics."""
    mock_contributors = {
        "developer": {
            "files_changed": ["app.py", "models.py", "views.py", "utils.py"],
            "commits": 20,
            "lines_added": 1000,
            "lines_removed": 100,
            "activity_by_category": {"code": 4, "test": 0, "docs": 0, "design": 0, "other": 0}
        }
    }
    
    monkeypatch.setattr("main_menu.load_contributors_from_db", lambda: mock_contributors)
    monkeypatch.setattr("main_menu.ask_yes_no", lambda prompt: False)

    handle_analyze_roles()

    out = capsys.readouterr().out
    assert "DEVELOPER" in out
    assert "Primary Role:" in out
    assert "Metrics:" in out or "Files:" in out
    assert "Contribution Breakdown:" in out or "Breakdown:" in out
