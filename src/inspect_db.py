"""inspect_db.py

Provides a human-friendly, manual inspection utility for the scan database.
Run this script to get a concise summary of scans, files, projects, languages, skills
and contributors.

It is safe to run against a fresh or older schema; missing tables are skipped.
Also provides JSON output for API use, including skills exercised for frontend.
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add src to import path so db.py can be imported
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
)

# Project imports (from src/)
from skill_timeline import print_grouped_skill_timeline
from file_utils import is_image_file

try:
    # Allow overriding DB for inspecting temporary DBs used in tests
    DB_PATH = os.environ.get('FILE_DATA_DB_PATH') or __import__('db').DB_PATH
except Exception:
    DB_PATH = os.environ.get('FILE_DATA_DB_PATH') or os.path.join(os.path.dirname(__file__), '..', 'file_data.db')


def safe_query(cur, sql, params=()):
    try:
        return list(cur.execute(sql, params))
    except sqlite3.OperationalError as e:
        print(f"  (skipped query, missing table or column) - {e}")
        return []


def human_ts(ts):
    if not ts:
        return 'N/A'
    try:
        dt = datetime.fromisoformat(ts)
        return dt.strftime('%Y-%m-%d %H:%M:%S %z') if dt.tzinfo else dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        pass
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S'):
        try:
            dt = datetime.strptime(ts, fmt)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            continue
    return str(ts)


def inspect_connection(conn: sqlite3.Connection, db_label: str = None):
    """CLI inspection function."""
    label = db_label or DB_PATH
    print(f"Inspecting DB: {label}")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Tables
    print('\n' + '='*80)
    print("Tables in database")
    print('='*80)
    tables = safe_query(cur, "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    if tables:
        for r in tables:
            print(' -', r['name'])
    else:
        print(' (no tables found)')

    # Scans summary
    print('\n' + '='*80)
    print("Recent scans")
    print('='*80)
    scans = safe_query(cur, "SELECT id, scanned_at, project, notes FROM scans ORDER BY scanned_at DESC LIMIT 10")
    if not scans:
        print(' No scans found')
    for s in scans:
        print(f"Scan {s['id']}: {human_ts(s['scanned_at'])} | project={s['project'] or '<none>'} | notes={s['notes'] or ''}")

    # Files overview
    print('\n' + '='*80)
    print("Files (recent)")
    print('='*80)
    files = safe_query(cur, "SELECT id, file_name, file_path, file_extension, file_size, modified_at FROM files ORDER BY (modified_at IS NULL), modified_at DESC, id DESC LIMIT 20")
    for f in files:
        size = f['file_size'] if f['file_size'] is not None else 'unknown'
        print(f"[{f['id']}] {f['file_name']} ({f['file_extension'] or ''}) — {size} bytes — modified: {human_ts(f['modified_at'])}\n    path: {f['file_path']}")

    # Projects & skills
    print('\n' + '='*80)
    print("Projects and skills")
    print('='*80)
    projects = safe_query(cur, "SELECT id, name, repo_url, created_at, summary_text FROM projects ORDER BY name")
    for p in projects:
        print(f"Project {p['id']}: {p['name']} (repo: {p['repo_url'] or '<none>'}) created: {human_ts(p['created_at'])}")
        sc = safe_query(cur, "SELECT COUNT(*) AS c FROM scans WHERE project = ?", (p['name'],))
        fc = safe_query(cur, "SELECT COUNT(f.id) AS c FROM files f JOIN scans s ON f.scan_id = s.id WHERE s.project = ?", (p['name'],))
        print(f"  scans: {sc[0]['c'] if sc else 0} | files: {fc[0]['c'] if fc else 0}")
        skills = safe_query(cur, "SELECT sk.name FROM skills sk JOIN project_skills ps ON sk.id = ps.skill_id WHERE ps.project_id = ?", (p['id'],))
        print('  skills:', ', '.join([r['name'] for r in skills]) if skills else '(none)')

        # Summary snippet
        summary = (p['summary_text'] or '').strip()
        if summary:
            clipped = summary[:200] + ("..." if len(summary) > 200 else "")
            print(f"  summary: {clipped}")

    # Thumbnails, languages, contributors
    print('\n' + '='*80)
    print("Project thumbnails, languages, contributors, sample scan")
    print('='*80)

    # Thumbnails
    thumb_rows = safe_query(cur, "SELECT id, name, thumbnail_path FROM projects ORDER BY name")
    for row in thumb_rows:
        thumb_path = row['thumbnail_path']
        if not thumb_path:
            status = 'empty'
        elif not os.path.isfile(thumb_path):
            status = 'missing file'
        elif not is_image_file(thumb_path):
            status = 'not an image'
        else:
            status = 'ok'
        print(f"Project {row['id']}: {row['name']} | thumbnail: {thumb_path or '<none>'} | status: {status}")

    # Languages
    lang_rows = safe_query(cur, "SELECT l.name, COUNT(fl.file_id) AS cnt FROM languages l LEFT JOIN file_languages fl ON l.id = fl.language_id GROUP BY l.id ORDER BY cnt DESC LIMIT 20")
    for r in lang_rows:
        print(f"  {r['name']}: {r['cnt']}")

    # Contributors
    contribs = safe_query(cur, "SELECT id, name FROM contributors ORDER BY name")
    for c in contribs:
        print(f"Contributor {c['id']}: {c['name']}")
        sample_files = safe_query(cur, "SELECT f.file_name, f.file_path FROM files f JOIN file_contributors fc ON f.id = fc.file_id WHERE fc.contributor_id = ? LIMIT 5", (c['id'],))
        for sf in sample_files:
            print(f"   - {sf['file_name']}  ({sf['file_path']})")
        if not sample_files:
            print("   (no linked files)")

    # Sample scan detail
    if scans:
        sid = scans[0]['id']
        print(f"\nDetails for scan id {sid}:")
        frows = safe_query(cur, "SELECT id, file_name, file_path FROM files WHERE scan_id = ? LIMIT 50", (sid,))
        for fr in frows:
            langs = safe_query(cur, "SELECT l.name FROM languages l JOIN file_languages fl ON l.id = fl.language_id WHERE fl.file_id = ?", (fr['id'],))
            conts = safe_query(cur, "SELECT c.name FROM contributors c JOIN file_contributors fc ON c.id = fc.contributor_id WHERE fc.file_id = ?", (fr['id'],))
            print(f" - {fr['file_name']} | langs: {', '.join([r['name'] for r in langs]) or '<none>'} | contribs: {', '.join([r['name'] for r in conts]) or '<none>'}")

    # Skills timeline
    print_grouped_skill_timeline(cur, safe_query, human_ts, lambda t: print('\n' + '='*80 + f"\n{t}\n" + '='*80))

    conn.close()


def inspect_database_json(db_path: str = None):
    """Return all database information as JSON for frontend."""
    import json
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    def q(sql, params=()):
        try:
            return list(cur.execute(sql, params))
        except sqlite3.OperationalError:
            return []

    result = {}

    # Recent scans
    scans = q("SELECT id, scanned_at, project, notes FROM scans ORDER BY scanned_at DESC LIMIT 50")
    result['recent_scans'] = [dict(s) for s in scans]

    # Files
    files = q("SELECT id, file_name, file_path, file_extension, file_size, modified_at, scan_id FROM files ORDER BY id DESC LIMIT 100")
    result['files'] = [dict(f) for f in files]

    # Projects
    projects = q("SELECT id, name, repo_url, created_at, summary_text FROM projects ORDER BY name")
    projects_list = []
    summaries_list = []
    for p in projects:
        sc = q("SELECT COUNT(*) AS c FROM scans WHERE project = ?", (p['name'],))
        fc = q("SELECT COUNT(f.id) AS c FROM files f JOIN scans s ON f.scan_id = s.id WHERE s.project = ?", (p['name'],))
        skills = q("SELECT sk.name FROM skills sk JOIN project_skills ps ON sk.id = ps.skill_id WHERE ps.project_id = ?", (p['id'],))
        projects_list.append({
            "id": p['id'],
            "name": p['name'],
            "repo_url": p['repo_url'],
            "created_at": p['created_at'],
            "scan_count": sc[0]['c'] if sc else 0,
            "file_count": fc[0]['c'] if fc else 0,
            "skills": [s['name'] for s in skills],
            "summary_text": p['summary_text'] or ""
        })
        summaries_list.append({
            "project": p['name'],
            "summary": p['summary_text'] or "<none>"
        })
    result['projects'] = projects_list
    result['project_summaries'] = summaries_list

    # Contributors
    contribs = q("SELECT id, name FROM contributors ORDER BY name")
    contrib_list = []
    for c in contribs:
        sample_files = q("SELECT f.file_name, f.file_path FROM files f JOIN file_contributors fc ON f.id = fc.file_id WHERE fc.contributor_id = ? LIMIT 5", (c['id'],))
        contrib_list.append({
            "id": c['id'],
            "name": c['name'],
            "sample_files": [dict(sf) for sf in sample_files]
        })
    result['contributors'] = contrib_list

    # Languages top
    lang_rows = q("SELECT l.name, COUNT(fl.file_id) AS file_count FROM languages l LEFT JOIN file_languages fl ON l.id = fl.language_id GROUP BY l.id ORDER BY file_count DESC LIMIT 20")
    result['languages'] = [dict(r) for r in lang_rows]

    # Thumbnails
    thumb_rows = q("SELECT id, name, thumbnail_path FROM projects ORDER BY name")
    thumbs_list = []
    for t in thumb_rows:
        thumb_path = t['thumbnail_path']
        if not thumb_path:
            status = 'empty'
        elif not os.path.isfile(thumb_path):
            status = 'missing file'
        elif not is_image_file(thumb_path):
            status = 'not an image'
        else:
            status = 'ok'
        thumbs_list.append({
            "project_id": t['id'],
            "project_name": t['name'],
            "thumbnail_path": t['thumbnail_path'],
            "status": status
        })
    result['thumbnails'] = thumbs_list

    # Skills exercised (timeline)
    skills_rows = []
    timeline_data = q("""
        SELECT sk.name as skill, s.scanned_at as datetime, s.project
        FROM project_skills ps
        JOIN skills sk ON ps.skill_id = sk.id
        JOIN projects p ON ps.project_id = p.id
        JOIN scans s ON s.project = p.name
        ORDER BY s.scanned_at DESC
    """)
    for row in timeline_data:
        skills_rows.append({
            "skill": row['skill'],
            "datetime": row['datetime'],
            "project": row['project']
        })
    result['skills_exercised'] = skills_rows

    # ---------------- RESUMES ----------------
    resume_rows = q("""
        SELECT id, username, resume_path, generated_at
        FROM resumes
        ORDER BY generated_at DESC
    """)

    result['resumes'] = [dict(r) for r in resume_rows]


    # ---------------- PORTFOLIOS ----------------
    portfolio_rows = q("""
        SELECT id, username, portfolio_name, display_name, created_at
        FROM portfolios
        ORDER BY created_at DESC
    """)

    result['portfolios'] = [dict(p) for p in portfolio_rows]

    conn.close()
    return result


def main(db_path: str = None):
    """CLI entry point."""
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    inspect_connection(conn, db_label=path)


if __name__ == "__main__":
    main()