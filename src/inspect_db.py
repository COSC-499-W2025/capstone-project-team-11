"""inspect_db.py

Provides a human-friendly, manual inspection utility for the scan database.
Run this script to get a concise summary of scans, files, projects, languages, skills
and contributors.

It is safe to run against a fresh or older schema; missing tables are skipped.
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


def print_header(title):
    print('\n' + '=' * 80)
    print(title)
    print('=' * 80)


def human_ts(ts):
    if not ts:
        return 'N/A'
    # Try strict ISO parse first
    try:
        dt = datetime.fromisoformat(ts)
        # Include timezone offset if present
        if dt.tzinfo:
            return dt.strftime('%Y-%m-%d %H:%M:%S %z')
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        pass

    # Attempt to repair common truncated timezone forms like '-08:0' -> '-08:00'
    try:
        import re
        m = re.search(r'([+-]\d{2}:\d)$', ts)
        if m:
            ts2 = ts + '0'
            try:
                dt = datetime.fromisoformat(ts2)
                if dt.tzinfo:
                    return dt.strftime('%Y-%m-%d %H:%M:%S %z')
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                pass
    except Exception:
        pass

    # Fallback: try a couple of common formats, otherwise return raw string
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S'):
        try:
            dt = datetime.strptime(ts, fmt)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            continue
    return str(ts)


def main():
    print(f"Inspecting DB: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Tables
    print_header('Tables in database')
    rows = safe_query(cur, "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    if rows:
        for r in rows:
            print(' -', r['name'])
    else:
        print(' (no tables found)')

    # Scans summary
    print_header('Recent scans')
    scans = safe_query(cur, "SELECT id, scanned_at, project, notes FROM scans ORDER BY scanned_at DESC LIMIT 10")
    if not scans:
        print(' No scans found')
    for s in scans:
        print(f"Scan {s['id']}: {human_ts(s['scanned_at'])} | project={s['project'] or '<none>'} | notes={s['notes'] or ''}")

    # Files overview
    print_header('Files (recent)')
    # Order by modified_at when available, otherwise by id (most recently inserted)
    files = safe_query(cur, "SELECT id, file_name, file_path, file_extension, file_size, modified_at FROM files ORDER BY (modified_at IS NULL), modified_at DESC, id DESC LIMIT 20")
    if not files:
        print(' No files recorded')
    for f in files:
        size = f['file_size'] if f['file_size'] is not None else 'unknown'
        print(f"[{f['id']}] {f['file_name']} ({f['file_extension'] or ''}) — {size} bytes — modified: {human_ts(f['modified_at'])}\n    path: {f['file_path']}")

    # Projects and skills
    print_header('Projects and skills')
    projects = safe_query(cur, "SELECT id, name, repo_url, created_at FROM projects ORDER BY name")
    if projects:
        for p in projects:
            print(f"Project {p['id']}: {p['name']} (repo: {p['repo_url'] or '<none>'}) created: {human_ts(p['created_at'])}")
            # count scans and files for this project if possible
            sc = safe_query(cur, "SELECT COUNT(*) AS c FROM scans WHERE project = ?", (p['name'],))
            fc = safe_query(cur, "SELECT COUNT(f.id) AS c FROM files f JOIN scans s ON f.scan_id = s.id WHERE s.project = ?", (p['name'],))
            sc_cnt = sc[0]['c'] if sc else 0
            f_cnt = fc[0]['c'] if fc else 0
            print(f"  scans: {sc_cnt} | files: {f_cnt}")
            # skills
            skills = safe_query(cur, "SELECT sk.name FROM skills sk JOIN project_skills ps ON sk.id = ps.skill_id WHERE ps.project_id = ?", (p['id'],))
            if skills:
                print('  skills:', ', '.join([r['name'] for r in skills]))
            else:
                print('  skills: (none)')
    else:
        print(' No projects recorded')

    # Thumbnail verification
    print_header('Project thumbnails (path + file check)')
    thumb_rows = safe_query(cur, "SELECT id, name, thumbnail_path FROM projects ORDER BY name")
    if not thumb_rows:
        print(' No projects recorded')
    else:
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
            display_path = thumb_path or '<none>'
            print(f"Project {row['id']}: {row['name']} | thumbnail: {display_path} | status: {status}")

    # Languages top summary
    print_header('Top languages (by files)')
    lang_rows = safe_query(cur, "SELECT l.name, COUNT(fl.file_id) AS cnt FROM languages l LEFT JOIN file_languages fl ON l.id = fl.language_id GROUP BY l.id ORDER BY cnt DESC LIMIT 20")
    if not lang_rows:
        print(' No language information')
    else:
        for r in lang_rows:
            print(f"  {r['name']}: {r['cnt']}")

    # Contributors summary
    print_header('Contributors & sample files')
    contribs = safe_query(cur, "SELECT id, name FROM contributors ORDER BY name")
    if not contribs:
        print(' No contributors recorded')
    else:
        for c in contribs:
            print(f"Contributor {c['id']}: {c['name']}")
            sample_files = safe_query(cur, "SELECT f.file_name, f.file_path FROM files f JOIN file_contributors fc ON f.id = fc.file_id WHERE fc.contributor_id = ? LIMIT 5", (c['id'],))
            if sample_files:
                for sf in sample_files:
                    print(f"   - {sf['file_name']}  ({sf['file_path']})")
            else:
                print('   (no linked files)')

    # Show some joins for a sample scan
    print_header('Sample scan detail (first recent scan)')
    if scans:
        sid = scans[0]['id']
        print(f"Details for scan id {sid}:")
        frows = safe_query(cur, "SELECT id, file_name, file_path FROM files WHERE scan_id = ? LIMIT 50", (sid,))
        for fr in frows:
            langs = safe_query(cur, "SELECT l.name FROM languages l JOIN file_languages fl ON l.id = fl.language_id WHERE fl.file_id = ?", (fr['id'],))
            conts = safe_query(cur, "SELECT c.name FROM contributors c JOIN file_contributors fc ON c.id = fc.contributor_id WHERE fc.file_id = ?", (fr['id'],))
            print(f" - {fr['file_name']} | langs: {', '.join([r['name'] for r in langs]) or '<none>'} | contribs: {', '.join([r['name'] for r in conts]) or '<none>'}")
    else:
        print(' No scans to show details for')

    print_grouped_skill_timeline(cur, safe_query, human_ts, print_header)

    
    
    
    conn.close()


if __name__ == '__main__':
    main()
