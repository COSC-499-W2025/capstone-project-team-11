import sqlite3
import os
import time
import json
from db_maintenance import prune_old_project_scans
from datetime import datetime

# Allow overriding database path via environment for tests or custom locations
DB_PATH = os.environ.get('FILE_DATA_DB_PATH') or os.path.join(os.path.dirname(__file__), '..', 'file_data.db')

def get_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database using init_db.sql."""
    sql_path = os.path.join(os.path.dirname(__file__), '..', 'init_db.sql')
    with get_connection() as conn:
        with open(sql_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
    print("Database initialized successfully at", DB_PATH)

if __name__ == "__main__":
    init_db()


def _get_or_create(conn, table: str, name: str):
    """Return id for name in table (creates row if missing)."""
    cur = conn.cursor()
    cur.execute(f"INSERT OR IGNORE INTO {table} (name) VALUES (?)", (name,))
    conn.commit()
    cur.execute(f"SELECT id FROM {table} WHERE name = ?", (name,))
    row = cur.fetchone()
    return row['id'] if row else None

def _ensure_projects_thumbnail_column(conn):
    """Ensure the projects table has a thumbnail_path column."""
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(projects)")
    cols = {row['name'] for row in cur.fetchall()}
    if 'thumbnail_path' not in cols:
        cur.execute("ALTER TABLE projects ADD COLUMN thumbnail_path TEXT")
        conn.commit()


def save_scan(scan_source: str, files_found: list, project: str = None, notes: str = None,
              detected_languages: list = None, detected_skills: list = None, contributors: list = None,
              file_metadata: dict = None, project_created_at: str = None, project_repo_url: str = None,
              project_thumbnail_path: str = None):
    """Persist a scan and related metadata into the DB in a single transaction.

    - files_found: list of filesystem paths OR list of tuples (display_path, size, mtime)
    - detected_languages: list of language strings
    - detected_skills: list of skill strings
    - contributors: list of contributor names (strings)
    Returns scan_id
    """
    conn = get_connection()
    conn.execute('PRAGMA foreign_keys = ON')
    cur = conn.cursor()

    try:
        if project_thumbnail_path is not None:
            _ensure_projects_thumbnail_column(conn)

        cur.execute('BEGIN')

        project_name = project or os.path.basename(scan_source)

        # create scan
        cur.execute(
            "INSERT INTO scans (project, notes) VALUES (?, ?)",
            (project_name, notes)
        )
        scan_id = cur.lastrowid

        #  keep ONLY the newest scan's data for this project
        prune_old_project_scans(conn, project_name, keep_scan_id=scan_id)


        # link or create project row if provided, and persist project-level metadata
        project_id = None
        if project:
            # create row if missing; include repo_url/created_at when present
            if project_repo_url is not None or project_created_at is not None or project_thumbnail_path is not None:
                # Try to insert with provided metadata; INSERT OR IGNORE will skip if exists
                cur.execute(
                    "INSERT OR IGNORE INTO projects (name, repo_url, created_at, thumbnail_path) VALUES (?, ?, ?, ?)",
                    (project, project_repo_url, project_created_at, project_thumbnail_path),
                )
            else:
                cur.execute("INSERT OR IGNORE INTO projects (name) VALUES (?)", (project,))

            # If the row existed but metadata fields are empty, update them non-destructively
            if project_repo_url is not None or project_created_at is not None:
                cur.execute(
                    "UPDATE projects SET repo_url = COALESCE(repo_url, ?), created_at = COALESCE(created_at, ?) WHERE name = ?",
                    (project_repo_url, project_created_at, project),
                )
            if project_thumbnail_path is not None:
                cur.execute(
                    "UPDATE projects SET thumbnail_path = ? WHERE name = ?",
                    (project_thumbnail_path, project),
                )

            cur.execute("SELECT id FROM projects WHERE name = ?", (project,))
            r = cur.fetchone()
            project_id = r['id'] if r else None

        # insert files (batch). file_metadata is a mapping of file_path -> dict
        file_rows = []
        for item in files_found:
            if isinstance(item, tuple):
                display, size, mtime = item
                file_path = display
                file_name = os.path.basename(display.split(':')[-1])
                file_extension = os.path.splitext(file_name)[1]
                file_size = int(size or 0)
                modified_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime)) if mtime else None
                created_at = None
            else:
                file_path = item
                file_name = os.path.basename(item)
                file_extension = os.path.splitext(file_name)[1]
                try:
                    file_size = os.path.getsize(item)
                    created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(item)))
                    modified_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(item)))
                except Exception:
                    file_size = None
                    created_at = None
                    modified_at = None

            # pull owner/metadata if provided
            meta = {}
            if file_metadata and file_path in file_metadata:
                # copy only serializable fields
                try:
                    meta = dict(file_metadata[file_path])
                except Exception:
                    meta = {}

            owner_val = meta.get('owner') if isinstance(meta, dict) else None
            file_rows.append((scan_id, file_name, file_path, file_extension, file_size, created_at, modified_at, owner_val, json.dumps(meta)))

        cur.executemany(
            "INSERT INTO files (scan_id, file_name, file_path, file_extension, file_size, created_at, modified_at, owner, metadata_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            file_rows
        )

        # Fetch inserted file ids to use for linking (simple approach: query files for this scan)
        cur.execute("SELECT id, file_path FROM files WHERE scan_id = ?", (scan_id,))
        file_id_map = {row['file_path']: row['id'] for row in cur.fetchall()}

        # Languages: prefer per-file language from file_metadata; fall back to detected_languages at project-level
        if file_metadata:
            for fp, fid in file_id_map.items():
                meta = file_metadata.get(fp) or {}
                lang = meta.get('language') if isinstance(meta, dict) else None
                if lang:
                    cur.execute("INSERT OR IGNORE INTO languages (name) VALUES (?)", (lang,))
                    cur.execute("SELECT id FROM languages WHERE name = ?", (lang,))
                    lang_id = cur.fetchone()['id']
                    cur.execute("INSERT OR IGNORE INTO file_languages (file_id, language_id) VALUES (?, ?)", (fid, lang_id))
        elif detected_languages:
            for lang in detected_languages:
                if not lang:
                    continue
                cur.execute("INSERT OR IGNORE INTO languages (name) VALUES (?)", (lang,))
                cur.execute("SELECT id FROM languages WHERE name = ?", (lang,))
                lang_id = cur.fetchone()['id']
                for fp, fid in file_id_map.items():
                    cur.execute("INSERT OR IGNORE INTO file_languages (file_id, language_id) VALUES (?, ?)", (fid, lang_id))

        # Skills (project-level)
        if detected_skills and project_id:
            for skill in detected_skills:
                if not skill:
                    continue
                cur.execute("INSERT OR IGNORE INTO skills (name) VALUES (?)", (skill,))
                cur.execute("SELECT id FROM skills WHERE name = ?", (skill,))
                skill_id = cur.fetchone()['id']
                cur.execute("INSERT OR IGNORE INTO project_skills (project_id, skill_id) VALUES (?, ?)", (project_id, skill_id))

        # Contributors: if file-level owner metadata exists, parse & link per-file; else fall back to project-wide contributors
        def _parse_owner_string(s: str):
            # Expected formats: 'individual (Name)' or 'collaborative (A, B)'
            if not s or s == 'unknown':
                return []
            if s.startswith('individual (') and s.endswith(')'):
                return [s[len('individual ('):-1].strip()]
            if s.startswith('collaborative (') and s.endswith(')'):
                inner = s[len('collaborative ('):-1]
                return [p.strip() for p in inner.split(',') if p.strip()]
            # fallback: return the whole string as a single name (cleaned)
            return [s.strip()]

        if file_metadata:
            for fp, fid in file_id_map.items():
                meta = file_metadata.get(fp) or {}
                owner_val = meta.get('owner') if isinstance(meta, dict) else None
                names = _parse_owner_string(owner_val)
                for name in names:
                    if not name:
                        continue
                    cur.execute("INSERT OR IGNORE INTO contributors (name) VALUES (?)", (name,))
                    cur.execute("SELECT id FROM contributors WHERE name = ?", (name,))
                    contrib_id = cur.fetchone()['id']
                    cur.execute("INSERT OR IGNORE INTO file_contributors (file_id, contributor_id) VALUES (?, ?)", (fid, contrib_id))
        elif contributors:
            for contrib in contributors:
                if not contrib:
                    continue
                cur.execute("INSERT OR IGNORE INTO contributors (name) VALUES (?)", (contrib,))
                cur.execute("SELECT id FROM contributors WHERE name = ?", (contrib,))
                contrib_id = cur.fetchone()['id']
                for fp, fid in file_id_map.items():
                    cur.execute("INSERT OR IGNORE INTO file_contributors (file_id, contributor_id) VALUES (?, ?)", (fid, contrib_id))

        conn.commit()
        return scan_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def save_resume(username: str, resume_path: str, metadata: dict = None, generated_at: str = None):
    """Persist a generated resume into the DB.

    - username: GitHub username the resume was generated for
    - resume_path: filesystem path to the written resume markdown
    - metadata: aggregated data used to render the resume (stored as JSON)
    - generated_at: optional timestamp; defaults to current UTC if not provided

    Returns resume_id on success.
    """
    if not username or not resume_path:
        raise ValueError("username and resume_path are required")

    conn = get_connection()
    conn.execute('PRAGMA foreign_keys = ON')
    cur = conn.cursor()
    try:
        cur.execute('BEGIN')
        # Ensure contributor exists for this username
        cur.execute("INSERT OR IGNORE INTO contributors (name) VALUES (?)", (username,))
        cur.execute("SELECT id FROM contributors WHERE name = ?", (username,))
        contrib_row = cur.fetchone()
        contrib_id = contrib_row['id'] if contrib_row else None

        metadata_json = json.dumps(metadata or {}, default=str)
        ts = generated_at or datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')

        cur.execute(
            """
            INSERT INTO resumes (contributor_id, username, resume_path, metadata_json, generated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (contrib_id, username, resume_path, metadata_json, ts)
        )
        resume_id = cur.lastrowid
        conn.commit()
        return resume_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def save_portfolio(username: str, portfolio_path: str, metadata: dict = None, generated_at: str = None):
    """Persist a generated portfolio into the DB.

    - username: GitHub username the portfolio was generated for
    - portfolio_path: filesystem path to the written portfolio markdown
    - metadata: aggregated data used to render the portfolio (stored as JSON)
    - generated_at: optional timestamp; defaults to current UTC if not provided

    Returns portfolio_id on success.
    """
    if not username or not portfolio_path:
        raise ValueError("username and portfolio_path are required")

    conn = get_connection()
    conn.execute('PRAGMA foreign_keys = ON')
    cur = conn.cursor()
    try:
        cur.execute('BEGIN')
        # Ensure contributor exists for this username
        cur.execute("INSERT OR IGNORE INTO contributors (name) VALUES (?)", (username,))
        cur.execute("SELECT id FROM contributors WHERE name = ?", (username,))
        contrib_row = cur.fetchone()
        contrib_id = contrib_row['id'] if contrib_row else None

        metadata_json = json.dumps(metadata or {}, default=str)
        ts = generated_at or datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')

        cur.execute(
            """
            INSERT INTO portfolios (contributor_id, username, portfolio_path, metadata_json, generated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (contrib_id, username, portfolio_path, metadata_json, ts)
        )
        portfolio_id = cur.lastrowid
        conn.commit()
        return portfolio_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_portfolio(portfolio_id: int):
    """Delete a portfolio from the DB by its ID.

    - portfolio_id: ID of the portfolio to delete

    Returns True if deleted successfully, False if not found.
    """
    if not portfolio_id:
        raise ValueError("portfolio_id is required")

    conn = get_connection()
    conn.execute('PRAGMA foreign_keys = ON')
    cur = conn.cursor()
    try:
        cur.execute('BEGIN')
        cur.execute("DELETE FROM portfolios WHERE id = ?", (portfolio_id,))
        deleted = cur.rowcount > 0
        conn.commit()
        return deleted
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
