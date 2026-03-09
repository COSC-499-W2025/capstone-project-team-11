# test_inspect_db_json.py
import sqlite3
import tempfile
import os
from inspect_db import inspect_database_json

def create_test_db_file():
    # In-memory DB
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Tables
    cur.executescript("""
        CREATE TABLE scans(id INTEGER PRIMARY KEY, scanned_at TEXT, project TEXT, notes TEXT);
        CREATE TABLE projects(id INTEGER PRIMARY KEY, name TEXT, repo_url TEXT, created_at TEXT, summary_text TEXT, thumbnail_path TEXT);
        CREATE TABLE files(id INTEGER PRIMARY KEY, file_name TEXT, file_path TEXT, file_extension TEXT, file_size INTEGER, modified_at TEXT, scan_id INTEGER);
        CREATE TABLE skills(id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE project_skills(project_id INTEGER, skill_id INTEGER);
        CREATE TABLE languages(id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE file_languages(file_id INTEGER, language_id INTEGER);
        CREATE TABLE contributors(id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE file_contributors(file_id INTEGER, contributor_id INTEGER);
    """)

    # Sample data
    cur.execute("INSERT INTO scans(id, scanned_at, project, notes) VALUES (1, '2026-03-08 12:00:00', 'ProjA', 'first scan')")
    cur.execute("INSERT INTO projects(id, name, repo_url, created_at, summary_text, thumbnail_path) VALUES (1, 'ProjA', 'http://repo.url', '2026-03-01', 'A summary', NULL)")
    cur.execute("INSERT INTO files(id, file_name, file_path, file_extension, file_size, modified_at, scan_id) VALUES (1, 'file1.py', '/tmp/file1.py', '.py', 123, '2026-03-08 12:00:00', 1)")
    cur.execute("INSERT INTO skills(id, name) VALUES (1, 'Python')")
    cur.execute("INSERT INTO project_skills(project_id, skill_id) VALUES (1, 1)")
    cur.execute("INSERT INTO languages(id, name) VALUES (1, 'Python')")
    cur.execute("INSERT INTO file_languages(file_id, language_id) VALUES (1, 1)")
    cur.execute("INSERT INTO contributors(id, name) VALUES (1, 'Alice')")
    cur.execute("INSERT INTO file_contributors(file_id, contributor_id) VALUES (1, 1)")

    conn.commit()

    # Save to a temporary file safely on Windows
    fd, temp_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)  # Close immediately so sqlite3 can access it
    disk_conn = sqlite3.connect(temp_path)
    conn.backup(disk_conn)
    disk_conn.close()
    conn.close()

    return temp_path

def test_inspect_database_json_structure():
    db_path = create_test_db_file()
    result = inspect_database_json(db_path=db_path)

    expected_keys = [
        'recent_scans', 'files', 'projects', 'project_summaries',
        'contributors', 'languages', 'thumbnails', 'skills_exercised'
    ]
    for key in expected_keys:
        assert key in result, f"Missing key in JSON output: {key}"

    # Check sample data
    assert len(result['recent_scans']) == 1
    assert result['recent_scans'][0]['project'] == 'ProjA'
    assert result['projects'][0]['skills'] == ['Python']
    assert result['languages'][0]['name'] == 'Python'
    assert result['contributors'][0]['name'] == 'Alice'
    assert result['thumbnails'][0]['project_name'] == 'ProjA'

    # Clean up temp file
    os.remove(db_path)