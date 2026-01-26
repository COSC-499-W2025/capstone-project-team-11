import os
import importlib
import sqlite3

def _load_db_with_temp_path(monkeypatch, tmp_path):
    """
    Ensures db.DB_PATH points to a temp db file by setting env var BEFORE importing db.
    Returns imported db module.
    """
    temp_db = tmp_path / "test_file_data.db"
    monkeypatch.setenv("FILE_DATA_DB_PATH", str(temp_db))

    # Import (or reload) db after env var is set so DB_PATH uses the temp path
    import db
    importlib.reload(db)

    # Initialize schema
    db.init_db()
    return db


def test_set_and_get_project_display_name(monkeypatch, tmp_path):
    db = _load_db_with_temp_path(monkeypatch, tmp_path)

    # Insert a project row (custom_name may default to NULL)
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO projects (name) VALUES (?)", ("capstone-project-team-11",))
    conn.commit()
    conn.close()

    # Set custom name
    rows_updated = db.set_project_display_name("capstone-project-team-11", "ZZZ TEST NAME")
    assert rows_updated == 1

    # Get custom name
    custom = db.get_project_display_name("capstone-project-team-11")
    assert custom == "ZZZ TEST NAME"

    # Clear custom name
    rows_updated = db.set_project_display_name("capstone-project-team-11", "")
    assert rows_updated == 1

    custom = db.get_project_display_name("capstone-project-team-11")
    assert custom is None


def test_list_projects_for_display_includes_custom_name(monkeypatch, tmp_path):
    db = _load_db_with_temp_path(monkeypatch, tmp_path)

    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO projects (name, custom_name) VALUES (?, ?)", ("p1", "Pretty Name"))
    cur.execute("INSERT INTO projects (name, custom_name) VALUES (?, ?)", ("p2", None))
    conn.commit()
    conn.close()

    rows = db.list_projects_for_display()
    by_name = {r["name"]: r for r in rows}

    assert by_name["p1"]["custom_name"] == "Pretty Name"
    assert by_name["p2"]["custom_name"] is None
