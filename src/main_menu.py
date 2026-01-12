"""
main_menu.py
---------------------------------
Main menu interface that integrates all project features.

This module provides a unified CLI interface for:
- Scanning directories and zip files
- Inspecting database contents
- Ranking projects
- Summarizing contributor projects
"""

import os
import sys
import sqlite3
import subprocess
from datetime import datetime
import re

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import all feature modules
from scan import run_with_saved_settings
from config import load_config, is_default_config, config_path as default_config_path
from consent import ask_for_data_consent, ask_yes_no
from rank_projects import (
    rank_projects,
    print_projects,
    rank_projects_contribution_summary,
    print_projects_contribution_summary,
    rank_projects_by_contributor,
    print_projects_by_contributor,
    _get_all_contributors
)
from summarize_projects import summarize_top_ranked_projects
from project_info_output import gather_project_info, output_project_info
from db import get_connection, DB_PATH
from file_utils import is_image_file
from project_evidence import handle_project_evidence


def print_main_menu():
    """Display the main menu options."""
    print("\n=== MDA OPERATIONS MENU ===")
    print("1. Run directory scan")
    print("2. Inspect database (projects, scans, skills, etc.)")
    print("3. Rank projects")
    print("4. Summarize contributor projects")
    print("5. Generate Project Summary Report")
    print("6. Manage Project Evidence")
    print("7. Generate Resume")
    print("8. View Resumes")
    print("9. Exit")


def handle_scan_directory():
    """Handle directory/archive scanning."""
    print("\n=== Scan Directory/Archive ===")
    
    # Check data consent first
    current = load_config(None)
    if current.get("data_consent") is True:
        if ask_yes_no("Would you like to review our data access policy? (y/n): ", False):
            consent = ask_for_data_consent(config_path=default_config_path())
            if not consent:
                print("Data access consent not granted, aborting.")
                return
    else:
        consent = ask_for_data_consent(config_path=default_config_path())
        if not consent:
            print("Data access consent not granted, aborting.")
            return
    
    # Check if user wants to use saved settings
    current = load_config(None)
    use_saved = False
    if not is_default_config(current):
        use_saved = ask_yes_no(
            "Would you like to use the settings from your saved scan parameters?\n"
            f"  Scanned Directory:          {current.get('directory') or '<none>'}\n"
            f"  Scan Nested Folders:        {current.get('recursive_choice')}\n"
            f"  Only Scan File Type:        {current.get('file_type') or '<all>'}\n"
            f"  Show Collaboration Info:    {current.get('show_collaboration')}\n"
            f"  Show Contribution Metrics:  {current.get('show_contribution_metrics')}\n"
            f"  Show Contribution Summary:  {current.get('show_contribution_summary')}\n"
            "Proceed with these settings? (y/n): "
        )
    
    if use_saved and current.get("directory"):
        save_db = ask_yes_no("Save scan results to database? (y/n): ", False)
        thumbnail_source = None
        if save_db:
            saved_dir = current.get("directory")
            if saved_dir and not (os.path.isfile(saved_dir) and saved_dir.lower().endswith('.zip')):
                if ask_yes_no("Add a thumbnail image for this project? (y/n): ", False):
                    while True:
                        path = input("Enter path to thumbnail image (or leave blank to skip): ").strip()
                        if not path:
                            break
                        if not os.path.isfile(path):
                            print("Thumbnail path does not point to a file.")
                            continue
                        if not is_image_file(path):
                            print("Unsupported image type. Please use a common image format (e.g., .png, .jpg).")
                            continue
                        thumbnail_source = path
                        break
        run_with_saved_settings(
            directory=current.get("directory"),
            recursive_choice=current.get("recursive_choice"),
            file_type=current.get("file_type"),
            show_collaboration=current.get("show_collaboration"),
            show_contribution_metrics=current.get("show_contribution_metrics"),
            show_contribution_summary=current.get("show_contribution_summary"),
            save=False,
            save_to_db=save_db,
            thumbnail_source=thumbnail_source,
        )
    else:
        directory = input("Enter directory path or zip file path: ").strip()
        if not directory:
            print("No directory provided. Returning to main menu.")
            return
        
        recursive_choice = ask_yes_no("Scan subdirectories too? (y/n): ", False)
        file_type = input("Enter file type (e.g. .txt) or leave blank for all: ").strip()
        file_type = file_type if file_type else None
        show_collab = ask_yes_no("Show collaboration info? (y/n): ")
        show_metrics = ask_yes_no("Show contribution metrics? (y/n): ")
        show_summary = ask_yes_no("Show contribution summary? (y/n): ")
        remember = ask_yes_no("Save these settings for next time? (y/n): ")
        save_db = ask_yes_no("Save scan results to database? (y/n): ")
        thumbnail_source = None
        if save_db and not (os.path.isfile(directory) and directory.lower().endswith('.zip')):
            if ask_yes_no("Add a thumbnail image for this project? (y/n): ", False):
                while True:
                    path = input("Enter path to thumbnail image (or leave blank to skip): ").strip()
                    if not path:
                        break
                    if not os.path.isfile(path):
                        print("Thumbnail path does not point to a file.")
                        continue
                    if not is_image_file(path):
                        print("Unsupported image type. Please use a common image format (e.g., .png, .jpg).")
                        continue
                    thumbnail_source = path
                    break
        
        run_with_saved_settings(
            directory=directory,
            recursive_choice=recursive_choice,
            file_type=file_type,
            show_collaboration=show_collab,
            show_contribution_metrics=show_metrics,
            show_contribution_summary=show_summary,
            save=remember,
            save_to_db=save_db,
            thumbnail_source=thumbnail_source,
        )
    
    selected_dir = current.get("directory") if use_saved else directory
    try:
        info = gather_project_info(selected_dir)
        project_name = info.get("project_name") or os.path.basename(os.path.abspath(selected_dir))
        out_dir = os.path.join("output", project_name)
        os.makedirs(out_dir, exist_ok=True)
        json_path, txt_path = output_project_info(info, output_dir=out_dir)
        print(f"Summary reports saved to: {out_dir}")
    except Exception as e:
        print(f"Failed to generate summary report: {e}")



def safe_query(cur, sql, params=()):
    """Safely execute a query, catching operational errors."""
    try:
        return list(cur.execute(sql, params))
    except sqlite3.OperationalError as e:
        print(f"  (skipped query, missing table or column) - {e}")
        return []


def human_ts(ts):
    """Convert timestamp to human-readable format."""
    if not ts:
        return 'N/A'
    # Try strict ISO parse first
    try:
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo:
            return dt.strftime('%Y-%m-%d %H:%M:%S %z')
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        pass

    # Attempt to repair common truncated timezone forms
    try:
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

    # Fallback: try common formats
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S'):
        try:
            dt = datetime.strptime(ts, fmt)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            continue
    return str(ts)


def handle_inspect_database():
    """Handle database inspection."""
    print("\n=== Inspect Database ===")
    print(f"Inspecting DB: {DB_PATH}")
    
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Tables
        print('\n' + '=' * 80)
        print('Tables in database')
        print('=' * 80)
        rows = safe_query(cur, "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        if rows:
            for r in rows:
                print(' -', r['name'])
        else:
            print(' (no tables found)')

        # Scans summary
        print('\n' + '=' * 80)
        print('Recent scans')
        print('=' * 80)
        scans = safe_query(cur, "SELECT id, scanned_at, project, notes FROM scans ORDER BY scanned_at DESC LIMIT 10")
        if not scans:
            print(' No scans found')
        else:
            for s in scans:
                print(f"Scan {s['id']}: {human_ts(s['scanned_at'])} | project={s['project'] or '<none>'} | notes={s['notes'] or ''}")

        # Files overview
        print('\n' + '=' * 80)
        print('Files (recent)')
        print('=' * 80)
        files = safe_query(cur, "SELECT id, file_name, file_path, file_extension, file_size, modified_at FROM files ORDER BY (modified_at IS NULL), modified_at DESC, id DESC LIMIT 20")
        if not files:
            print(' No files recorded')
        else:
            for f in files:
                size = f['file_size'] if f['file_size'] is not None else 'unknown'
                print(f"[{f['id']}] {f['file_name']} ({f['file_extension'] or ''}) — {size} bytes — modified: {human_ts(f['modified_at'])}\n    path: {f['file_path']}")

        # Projects and skills
        print('\n' + '=' * 80)
        print('Projects and skills')
        print('=' * 80)
        projects = safe_query(cur, "SELECT id, name, repo_url, created_at FROM projects ORDER BY name")
        if projects:
            for p in projects:
                print(f"Project {p['id']}: {p['name']} (repo: {p['repo_url'] or '<none>'}) created: {human_ts(p['created_at'])}")
                # count scans and files for this project
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

        # Languages top summary
        print('\n' + '=' * 80)
        print('Top languages (by files)')
        print('=' * 80)
        lang_rows = safe_query(cur, "SELECT l.name, COUNT(fl.file_id) AS cnt FROM languages l LEFT JOIN file_languages fl ON l.id = fl.language_id GROUP BY l.id ORDER BY cnt DESC LIMIT 20")
        if not lang_rows:
            print(' No language information')
        else:
            for r in lang_rows:
                print(f"  {r['name']}: {r['cnt']}")

        # Contributors summary
        print('\n' + '=' * 80)
        print('Contributors & sample files')
        print('=' * 80)
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

        # Resumes summary
        print('\n' + '=' * 80)
        print('Resumes (recent)')
        print('=' * 80)
        resumes = safe_query(cur, """
            SELECT r.id, r.username, r.resume_path, r.generated_at, c.name AS contributor_name
            FROM resumes r
            LEFT JOIN contributors c ON c.id = r.contributor_id
            ORDER BY r.generated_at DESC
            LIMIT 10
        """)
        if not resumes:
            print(' No resumes saved')
        else:
            for r in resumes:
                uname = r['username'] or r['contributor_name'] or '<unknown>'
                print(f"[{r['id']}] user={uname} | generated={human_ts(r['generated_at'])}")
                print(f"    path: {r['resume_path']}")

        # Skills timeline
        print('\n' + '=' * 80)
        print('Skills Exercised (Chronologically — Grouped by Skill)')
        print('=' * 80)
        raw_rows = safe_query(cur, """
            SELECT sk.name AS skill,
                   s.scanned_at AS used_at,
                   p.name AS project
            FROM skills sk
            JOIN project_skills ps ON sk.id = ps.skill_id
            JOIN projects p ON ps.project_id = p.id
            JOIN scans s ON s.project = p.name
            ORDER BY sk.name ASC, used_at ASC
        """)
        if not raw_rows:
            print(" No recorded skills")
        else:
            grouped = {}
            for row in raw_rows:
                skill = row["skill"]
                ts = human_ts(row["used_at"])
                proj = row["project"]
                grouped.setdefault(skill, []).append((ts, proj))
            for skill, entries in grouped.items():
                print(f"\n{skill}:")
                for ts, proj in entries:
                    print(f"   • {ts}  (project: {proj})")

        conn.close()
    except Exception as e:
        print(f"Error inspecting database: {e}")


def handle_rank_projects():
    """Handle project ranking."""
    print("\n=== Rank Projects ===")
    order = input("Order by creation date (asc/desc) [desc]: ").strip().lower()
    if order not in ['asc', 'desc']:
        order = 'desc'
    
    limit_input = input("Limit number of projects (leave blank for all): ").strip()
    limit = int(limit_input) if limit_input.isdigit() else None
    
    try:
        projects = rank_projects(order=order, limit=limit)
        print_projects(projects)
        
        print('\nProject-level contributions summary:')
        contrib_summary = rank_projects_contribution_summary(limit=limit)
        print_projects_contribution_summary(contrib_summary)
    except Exception as e:
        print(f"Error ranking projects: {e}")
        return
    
    # Ask if user wants to see projects ranked by a specific contributor
    # This is outside the try block to ensure it always runs
    try:
        print()  # Add extra line for visibility
        
        # Display available contributors
        contributors = _get_all_contributors()
        if contributors:
            print("=== Available Contributors ===")
            for i, contrib in enumerate(contributors, 1):
                print(f"  {i}. {contrib}")
            print()
        
        name = input('Enter a contributor name to show per-project importance (leave blank to skip): ').strip()
        if name:
            print(f"\nRanking projects by contributor: {name}\n")
            user_projects = rank_projects_by_contributor(name, limit=limit)
            print_projects_by_contributor(user_projects, name)
    except Exception as e:
        print(f"Error ranking projects by contributor: {e}")


def handle_summarize_contributor_projects():
    """Handle generating summary for top-ranked projects by contributor."""
    print("\n=== Summarize Contributor Projects ===")
    contributor_name = input("Enter contributor name: ").strip()
    if not contributor_name:
        print("No contributor name provided.")
        return
    
    limit_input = input("Limit number of top projects (leave blank for all): ").strip()
    limit = int(limit_input) if limit_input.isdigit() else None
    
    try:
        results = summarize_top_ranked_projects(
            contributor_name=contributor_name,
            limit=limit
        )
        print(f"\nProcessed {len(results)} project(s).")
    except Exception as e:
        print(f"Error generating contributor projects summary: {e}")


def handle_generate_project_summary():
    """Handle generating a project summary report."""
    print("\n=== Generate Project Summary Report ===")
    directory = input("Enter project directory path: ").strip()
    if not directory or not os.path.exists(directory):
        print("Invalid directory path.")
        return
    
    try:
        info = gather_project_info(directory)
        project_name = info.get("project_name") or os.path.basename(os.path.abspath(directory))
        out_dir = os.path.join("output", project_name)
        os.makedirs(out_dir, exist_ok=True)
        json_path, txt_path = output_project_info(info, output_dir=out_dir)
        print(f"\nSummary reports saved to: {out_dir}")
        print(f"  JSON: {json_path}")
        print(f"  TXT:  {txt_path}")
    except Exception as e:
        print(f"Error generating project summary: {e}")


def handle_generate_resume():
    """Run the resume generator script for a specified username.

    If the user provides a username here, pass it to the generator to avoid
    a second interactive prompt. If left blank, the generator will prompt.
    """
    print("\n=== Generate Resume ===")
    # Delegate username prompting and candidate listing entirely to the
    # generate_resume script. Do not prompt for username here.
    script_path = os.path.join(os.path.dirname(__file__), 'generate_resume.py')
    if not os.path.exists(script_path):
        print(f"Resume generator script not found at: {script_path}")
        return

    cmd = [sys.executable, script_path, '--save-to-db']
    try:
        # Run the script and inherit stdio so the generator can prompt the user
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"Resume generator exited with code {result.returncode}")
    except Exception as e:
        print(f"Failed to run resume generator: {e}")


def _pager(text: str):
    """Display text with paging if available, else print."""
    try:
        import pydoc
        pydoc.pager(text)
    except Exception:
        print(text)


def _list_resumes(cur):
    """Return list of resumes rows ordered by recent generated_at."""
    return safe_query(cur, """
        SELECT r.id, r.username, r.resume_path, r.generated_at, c.name AS contributor_name, r.metadata_json
        FROM resumes r
        LEFT JOIN contributors c ON c.id = r.contributor_id
        ORDER BY r.generated_at DESC
        LIMIT 50
    """)


def _print_resume_list(resumes):
    """Print numbered resume list."""
    if not resumes:
        print(" No resumes saved")
        return
    print("\nAvailable resumes (most recent first):")
    for idx, r in enumerate(resumes, start=1):
        uname = r['username'] or r['contributor_name'] or '<unknown>'
        print(f"  {idx}. user={uname} | generated={human_ts(r['generated_at'])}")
        print(f"     path: {r['resume_path']}")


def _preview_resume(path: str, lines: int = 30):
    """Return a preview (first N lines) of a resume file, lightly rendered."""
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            content = fh.read().splitlines()
    except Exception as e:
        return None, f"Failed to read resume file: {e}"

    preview_lines = content[:lines]
    truncated = len(content) > lines
    rendered = _markdown_to_plain("\n".join(preview_lines))
    return rendered, truncated


def _markdown_to_plain(text: str) -> str:
    """Lightweight markdown-to-plain renderer for terminal viewing."""
    import re

    lines = []
    for raw in text.splitlines():
        line = raw
        # Headings: remove leading #'s, uppercase
        if line.lstrip().startswith("#"):
            line = re.sub(r"^\s*#+\s*", "", line).strip()
            line = line.upper()
        # Links: [text](url) -> text (url)
        line = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1 (\2)", line)
        # Bold/italic/backticks: strip markers
        line = line.replace("**", "").replace("__", "")
        line = line.replace("*", "").replace("_", "").replace("`", "")
        # Bullets: keep as-is; if nested, normalize spacing
        line = re.sub(r"^\s*[-•]\s*", "- ", line)
        lines.append(line)
    return "\n".join(lines)


def _delete_resume(conn, resume_row):
    """Delete resume row and corresponding file (best-effort for file)."""
    cur = conn.cursor()
    cur.execute("DELETE FROM resumes WHERE id = ?", (resume_row["id"],))
    conn.commit()
    # sqlite3.Row supports key access but not .get
    path = resume_row["resume_path"] if "resume_path" in resume_row.keys() else None
    if path and os.path.exists(path):
        try:
            os.remove(path)
            return True, "Deleted from database and removed file."
        except Exception as e:
            return True, f"Deleted from database but failed to remove file: {e}"
    return True, "Deleted from database; file not found or already removed."


def handle_view_resumes():
    """List resumes from the DB and allow viewing content."""
    print("\n=== View Resumes ===")
    try:
        conn = get_connection()
        cur = conn.cursor()
        resumes = _list_resumes(cur)
        _print_resume_list(resumes)
        if not resumes:
            conn.close()
            return

        choice = input("\nEnter number to view/delete (blank to cancel): ").strip()
        if not choice:
            conn.close()
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(resumes)):
            print("Invalid selection.")
            conn.close()
            return
        selected = resumes[int(choice) - 1]
        path = selected['resume_path']
        uname = selected['username'] or selected['contributor_name'] or '<unknown>'
        print(f"\nSelected resume for {uname}: {path}")
        action = input("Choose action: (v)iew, (a)dd, (d)elete, (c)ancel [v]: ").strip().lower() or 'v'
        if action == 'a':
            path = input("\nEnter directory or .zip to add to this resume: ").strip()

            if not path:
                print("No directory entered. Aborting.")
                return

            if not os.path.exists(path):
                print("Path does not exist.")
                return

            handle_add_to_resume(selected, path)
            return
        if action == 'c':
            conn.close()
            return
        if action == 'd':
            confirm = input("Are you sure you want to delete this resume? (y/n): ").strip().lower()
            if confirm != 'y':
                conn.close()
                return
            ok, msg = _delete_resume(conn, selected)
            print(msg)
            conn.close()
            return

        print(f"\nOpening resume for {uname}: {path}")
        preview, truncated_or_error = _preview_resume(path)
        if preview is None:
            print(truncated_or_error)
            conn.close()
            return
        truncated = truncated_or_error is True or (isinstance(truncated_or_error, bool) and truncated_or_error)
        print("\n--- Preview ---\n")
        print(preview)
    except sqlite3.OperationalError as e:
        print(f"Resumes table not available: {e}")
    except Exception as e:
        print(f"Error viewing resumes: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass

from regenerate_resume import regenerate_resume
from regenerate_resume_scan import resume_scan

def handle_add_to_resume(resume_row, path):
    """
    resume_row is the DB row for the currently selected resume
    path is directory or zip to scan
    """
    print("\n=== Scanning new directory ===")
    resume_scan(path, save_to_db=True)

    print("\n=== Regenerating resume ===")
    regenerate_resume(
        username=resume_row["username"],
        resume_path=resume_row["resume_path"],
    )

    print("\nResume successfully updated.")



def main():
    """Main menu loop."""
    while True:
        print_main_menu()
        choice = input("\nSelect an option (1-9): ").strip()
        
        if choice == "1":
            handle_scan_directory()
        elif choice == "2":
            handle_inspect_database()
        elif choice == "3":
            handle_rank_projects()
        elif choice == "4":
            handle_summarize_contributor_projects()
        elif choice == "5":
            handle_generate_project_summary()
        elif choice == "6":
            handle_project_evidence()
        elif choice == "7":
            handle_generate_resume()
        elif choice == "8":
            handle_view_resumes()
        elif choice == "9":
            print("\nExiting program. Goodbye!")
            sys.exit(0)
        else:
            print("\nInvalid option. Please select a number between 1-9.")
        
        # Pause before returning to menu
        input("\nPress Enter to return to main menu...")


if __name__ == "__main__":
    main()
