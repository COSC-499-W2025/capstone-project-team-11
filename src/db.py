import sqlite3
import os
import time
import json
from typing import Optional
from collections import Counter
from db_maintenance import prune_old_project_scans
from datetime import datetime

# Allow overriding database path via environment for tests or custom locations
DB_PATH = os.environ.get('FILE_DATA_DB_PATH') or os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'file_data.db')
)


def get_connection():
    """Return a connection to the SQLite database."""
    # Ensure parent folder exists (needed for tests / custom env paths)
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    _ensure_schema(conn)
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
def _ensure_projects_custom_name_column(conn):
    """Ensure the projects table has a custom_name column."""
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(projects)")
    cols = {row['name'] for row in cur.fetchall()}
    if 'custom_name' not in cols:
        cur.execute("ALTER TABLE projects ADD COLUMN custom_name TEXT")
        conn.commit()
def _ensure_projects_column(conn, column_name: str, column_type: str):
    """Ensure the projects table has a specific column."""
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(projects)")
    cols = {row['name'] for row in cur.fetchall()}
    if column_name not in cols:
        cur.execute(f"ALTER TABLE projects ADD COLUMN {column_name} {column_type}")
        conn.commit()
def get_project_display_name(project_name: str):
    if not project_name:
        return None

    conn = None
    try:
        conn = get_connection()
        _ensure_projects_custom_name_column(conn)
        cur = conn.cursor()
        cur.execute("SELECT custom_name FROM projects WHERE name = ?", (project_name,))
        row = cur.fetchone()
        if not row:
            return None
        custom = row["custom_name"]
        return custom.strip() if custom and custom.strip() else None

    except sqlite3.OperationalError:
        return None

    finally:
        if conn:
            conn.close()


def list_projects_for_display():
    """Return projects as rows: id, name, custom_name."""
    conn = get_connection()
    try:
        _ensure_projects_custom_name_column(conn)
        cur = conn.cursor()
        cur.execute("SELECT id, name, custom_name FROM projects ORDER BY name COLLATE NOCASE")
        return cur.fetchall()
    finally:
        conn.close()


def set_project_display_name(project_name: str, custom_name: Optional[str]):
    """
    Set (or clear) the resume display name override for a project.
    If custom_name is None or empty -> clears the override.
    """
    if not project_name:
        raise ValueError("project_name is required")

    custom = (custom_name or "").strip()
    if custom == "":
        custom = None

    conn = get_connection()
    try:
        _ensure_projects_custom_name_column(conn)
        cur = conn.cursor()
        cur.execute(
            "UPDATE projects SET custom_name = ? WHERE name = ?",
            (custom, project_name),
        )
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()







        


def save_scan(scan_source: str, files_found: list, project: str = None, notes: str = None,
              detected_languages: list = None, detected_skills: list = None, contributors: list = None,
              file_metadata: dict = None, project_created_at: str = None, project_repo_url: str = None,
              project_thumbnail_path: str = None, git_metrics: dict = None, tech_summary: dict = None):
    """Persist a scan and related metadata into the DB in a single transaction.

    - files_found: list of filesystem paths OR list of tuples (display_path, size, mtime)
    - detected_languages: list of language strings
    - detected_skills: list of skill strings
    - contributors: list of contributor names (strings)
    - git_metrics: repo contribution metrics dict (stored as JSON)
    - tech_summary: dict of languages/frameworks with confidence tiers (stored as JSON)
    Returns scan_id
    """
    conn = get_connection()
    conn.execute('PRAGMA foreign_keys = ON')
    cur = conn.cursor()

    try:
        if project_thumbnail_path is not None:
            _ensure_projects_thumbnail_column(conn)
           
        _ensure_projects_custom_name_column(conn)
        _ensure_projects_column(conn, "project_path", "TEXT")
        _ensure_projects_column(conn, "git_metrics_json", "TEXT")
        _ensure_projects_column(conn, "tech_json", "TEXT")
           
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


        # link or create project row, and persist project-level metadata
        project_id = None
        project_key = project_name
        if project_key:
            # create row if missing; include repo_url/created_at when present
            if project_repo_url is not None or project_created_at is not None or project_thumbnail_path is not None:
                # Try to insert with provided metadata; INSERT OR IGNORE will skip if exists
                cur.execute(
                    "INSERT OR IGNORE INTO projects (name, repo_url, created_at, thumbnail_path, project_path) VALUES (?, ?, ?, ?, ?)",
                    (project_key, project_repo_url, project_created_at, project_thumbnail_path, scan_source),
                )
            else:
                cur.execute("INSERT OR IGNORE INTO projects (name, project_path) VALUES (?, ?)", (project_key, scan_source))

            # If the row existed but metadata fields are empty, update them non-destructively
            if project_repo_url is not None or project_created_at is not None:
                cur.execute(
                    "UPDATE projects SET repo_url = COALESCE(repo_url, ?), created_at = COALESCE(created_at, ?) WHERE name = ?",
                    (project_repo_url, project_created_at, project_key),
                )
            if project_thumbnail_path is not None:
                cur.execute(
                    "UPDATE projects SET thumbnail_path = ? WHERE name = ?",
                    (project_thumbnail_path, project_key),
                )
            if scan_source:
                cur.execute(
                    "UPDATE projects SET project_path = ? WHERE name = ?",
                    (scan_source, project_key),
                )

            if git_metrics is not None:
                cur.execute(
                    "UPDATE projects SET git_metrics_json = ? WHERE name = ?",
                    (json.dumps(git_metrics, default=str), project_key),
                )
            if tech_summary is not None:
                cur.execute(
                    "UPDATE projects SET tech_json = ? WHERE name = ?",
                    (json.dumps(tech_summary, default=str), project_key),
                )

            cur.execute("SELECT id FROM projects WHERE name = ?", (project_key,))
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


def load_projects_for_generation():
    """Load project data from the DB in the same structure used by resume/portfolio generators."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute("PRAGMA table_info(projects)")
        project_cols = {row['name'] for row in cur.fetchall()}

        select_cols = ["id", "name"]
        if "project_path" in project_cols:
            select_cols.append("project_path")
        if "git_metrics_json" in project_cols:
            select_cols.append("git_metrics_json")
        if "tech_json" in project_cols:
            select_cols.append("tech_json")

        cur.execute(f"SELECT {', '.join(select_cols)} FROM projects ORDER BY name COLLATE NOCASE")
        project_rows = cur.fetchall()

        projects = {}
        commits_counter = Counter()
        lines_counter = Counter()

        for row in project_rows:
            project_id = row["id"]
            project_name = row["name"]
            project_path = row["project_path"] if "project_path" in row.keys() else None

            tech_summary = {}
            if "tech_json" in row.keys() and row["tech_json"]:
                try:
                    tech_summary = json.loads(row["tech_json"])
                except Exception:
                    tech_summary = {}

            git_metrics = None
            if "git_metrics_json" in row.keys() and row["git_metrics_json"]:
                try:
                    git_metrics = json.loads(row["git_metrics_json"])
                except Exception:
                    git_metrics = None

            # Skills (project-level)
            cur.execute(
                """
                SELECT s.name
                FROM project_skills ps
                JOIN skills s ON s.id = ps.skill_id
                WHERE ps.project_id = ?
                ORDER BY s.name COLLATE NOCASE
                """,
                (project_id,),
            )
            skills = [r["name"] for r in cur.fetchall()]

            # Find latest scan_id for this project (pruning keeps only the newest)
            cur.execute(
                "SELECT id FROM scans WHERE project = ? ORDER BY scanned_at DESC, id DESC LIMIT 1",
                (project_name,),
            )
            scan_row = cur.fetchone()
            scan_id = scan_row["id"] if scan_row else None

            # Languages/frameworks (fallback to file_languages if tech summary missing)
            languages = tech_summary.get("languages") or []
            frameworks = tech_summary.get("frameworks") or []
            if (not languages and not frameworks) and scan_id:
                cur.execute(
                    """
                    SELECT DISTINCT l.name
                    FROM file_languages fl
                    JOIN languages l ON l.id = fl.language_id
                    JOIN files f ON f.id = fl.file_id
                    WHERE f.scan_id = ?
                    ORDER BY l.name COLLATE NOCASE
                    """,
                    (scan_id,),
                )
                languages = [r["name"] for r in cur.fetchall()]

            contributions = {}
            if isinstance(git_metrics, dict):
                commits_per_author = git_metrics.get("commits_per_author") or {}
                files_changed_per_author = git_metrics.get("files_changed_per_author") or {}
                lines_added_per_author = git_metrics.get("lines_added_per_author") or {}
                for author, commits in commits_per_author.items():
                    contributions[author] = {
                        "commits": commits or 0,
                        "files": files_changed_per_author.get(author, []) or [],
                    }
                for author, count in commits_per_author.items():
                    if isinstance(count, int):
                        commits_counter[author] += count
                for author, count in lines_added_per_author.items():
                    if isinstance(count, int):
                        lines_counter[author] += count
            elif scan_id:
                # Fallback for non-git projects: build contributions from file ownership
                cur.execute(
                    """
                    SELECT f.file_path, c.name
                    FROM files f
                    JOIN file_contributors fc ON fc.file_id = f.id
                    JOIN contributors c ON c.id = fc.contributor_id
                    WHERE f.scan_id = ?
                    """,
                    (scan_id,),
                )
                for row_fc in cur.fetchall():
                    name = row_fc["name"]
                    contributions.setdefault(name, {"commits": 0, "files": []})
                    contributions[name]["files"].append(row_fc["file_path"])

            projects[project_name] = {
                "project_name": project_name,
                "project_path": project_path,
                "languages": languages,
                "frameworks": frameworks,
                "skills": skills,
                "high_confidence_languages": tech_summary.get("high_confidence_languages", []),
                "medium_confidence_languages": tech_summary.get("medium_confidence_languages", []),
                "low_confidence_languages": tech_summary.get("low_confidence_languages", []),
                "high_confidence_frameworks": tech_summary.get("high_confidence_frameworks", []),
                "medium_confidence_frameworks": tech_summary.get("medium_confidence_frameworks", []),
                "low_confidence_frameworks": tech_summary.get("low_confidence_frameworks", []),
                "contributions": contributions,
                "git_metrics": git_metrics or {},
            }

        root_repo_jsons = {
            "db_aggregate": {
                "commits_per_author": dict(commits_counter),
                "lines_added_per_author": dict(lines_counter),
            }
        }
        return projects, root_repo_jsons
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

def _ensure_schema(conn):
    """Ensure the database schema exists and matches init_db.sql (non-destructive)."""
    cur = conn.cursor()
    
    # --- Core tables ---
    cur.execute("PRAGMA foreign_keys = ON")

    # --- Core tables ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scanned_at TEXT DEFAULT CURRENT_TIMESTAMP,
            project TEXT,
            notes TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            custom_name TEXT,
            repo_url TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            thumbnail_path TEXT,
            project_path TEXT,
            git_metrics_json TEXT,
            tech_json TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_extension TEXT,
            file_size INTEGER,
            created_at TEXT,
            modified_at TEXT,
            owner TEXT,
            metadata_json TEXT,
            FOREIGN KEY (scan_id) REFERENCES scans(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS contributors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS languages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    """)

    # --- Join tables ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS file_contributors (
            file_id INTEGER NOT NULL,
            contributor_id INTEGER NOT NULL,
            PRIMARY KEY (file_id, contributor_id),
            FOREIGN KEY (file_id) REFERENCES files(id),
            FOREIGN KEY (contributor_id) REFERENCES contributors(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS file_languages (
            file_id INTEGER NOT NULL,
            language_id INTEGER NOT NULL,
            PRIMARY KEY (file_id, language_id),
            FOREIGN KEY (file_id) REFERENCES files(id),
            FOREIGN KEY (language_id) REFERENCES languages(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS project_skills (
            project_id INTEGER NOT NULL,
            skill_id INTEGER NOT NULL,
            PRIMARY KEY (project_id, skill_id),
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (skill_id) REFERENCES skills(id)
        )
    """)

    # --- Evidence ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS project_evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            description TEXT,
            value TEXT,
            source TEXT,
            url TEXT,
            added_by_user BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)

    # --- Generated outputs ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contributor_id INTEGER,
            username TEXT NOT NULL,
            resume_path TEXT NOT NULL,
            metadata_json TEXT,
            generated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contributor_id) REFERENCES contributors(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS portfolios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contributor_id INTEGER,
            username TEXT NOT NULL,
            portfolio_path TEXT NOT NULL,
            metadata_json TEXT,
            generated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contributor_id) REFERENCES contributors(id)
        )
    """)

    # --- Indexes ---
    cur.execute("CREATE INDEX IF NOT EXISTS idx_file_path ON files (file_path)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_file_name ON files (file_name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_files_scan_id ON files (scan_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_projects_name ON projects (name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_contributors_name ON contributors (name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_languages_name ON languages (name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_skills_name ON skills (name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_resumes_username ON resumes (username)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_resumes_generated_at ON resumes (generated_at)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_portfolios_username ON portfolios (username)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_portfolios_generated_at ON portfolios (generated_at)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_project_evidence_project_id ON project_evidence (project_id)")

    conn.commit()
