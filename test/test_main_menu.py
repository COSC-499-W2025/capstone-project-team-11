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
            created_at TEXT
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
    """)

    conn.commit()
    return conn


# Test print_main_menu()

def test_print_main_menu_outputs_correct_text(capsys):
    print_main_menu()
    output = capsys.readouterr().out

    assert "MDA OPERATIONS MENU" in output
    assert "1. Run directory scan" in output
    assert "2. Inspect database" in output
    assert "3. Rank projects" in output
    assert "4. Summarize contributor projects" in output
    assert "5. Generate Project Summary Report" in output
    assert "6. Generate Resume" in output
    assert "7. Exit" in output


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
    assert "Top languages" in out
    assert "Contributors" in out
