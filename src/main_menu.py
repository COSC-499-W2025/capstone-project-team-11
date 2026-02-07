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

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import sqlite3
import subprocess
from datetime import datetime
import re

from db import list_projects_for_display, set_project_display_name
from cli_validators import prompt_project_path, validate_project_path
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
from summarize_projects import summarize_top_ranked_projects, db_is_initialized
from contrib_metrics import canonical_username
from project_info_output import gather_project_info, output_project_info
from db import get_connection, DB_PATH
from thumbnail_manager import handle_edit_project_thumbnail
from file_utils import is_image_file
from project_evidence import handle_project_evidence
from detect_roles import (
    load_contributors_from_db,
    load_contributors_per_project_from_db,
    analyze_project_roles,
    format_roles_report,
    display_all_roles
)

# Print a standardized error message (message: The main error description | hint: Optional hint for how to resolve the issue)
def print_error(message: str, hint: str = None):
    print(f"\nError: {message}")
    if hint:
        print(f"  Hint: {hint}")

def print_main_menu():
    """Display the main menu options."""
    print("\n=== MDA OPERATIONS MENU ===")
    print("")
    print("SCANNING")
    print("1. Scan Project")
    print("2. View/Manage Scanned Projects")
    print("")
    print("RESUME & PORTFOLIO")
    print("3. Generate Resume")
    print("4. Generate Portfolio")
    print("5. View/Manage Resumes")
    print("6. View/Manage Portfolios")
    print("")
    print("ANALYSIS")
    print("7. Rank Projects")
    print("8. Summarize Contributor Projects")
    print("9. Generate Project Summary Report")
    print("10. Manage Project Evidence")
    print("11. Analyze Contributor Roles")
    print("")
    print("EXTRA")
    print("12. Edit Thumbnail for a Project")
    print("")
    print("ADMIN")
    print("13. Manage Database")
    print("0. Exit")


def handle_scan_directory():
    """Handle directory/archive scanning."""
    print("\n=== Scan Directory/Archive ===")

    # Check data consent first
    current = load_config(None)
    if current.get("data_consent") is True:
        if ask_yes_no("Would you like to review our data access policy? (y/n): "):
            consent = ask_for_data_consent(config_path=default_config_path())
            if not consent:
                print_error("Data access consent not granted.", "You must accept the data policy to scan projects.")
                return
    else:
        consent = ask_for_data_consent(config_path=default_config_path())
        if not consent:
            print_error("Data access consent not granted.", "You must accept the data policy to scan projects.")
            return

    # Check if user wants to use saved settings
    current = load_config(None)
    use_saved = False
    if not is_default_config(current):
        use_saved = ask_yes_no(
            "Would you like to use the settings from your saved scan parameters?\n"
            f"  Scanned Directory:          {current.get('directory') or '<none>'}\n"
            f"  Only Scan File Type:        {current.get('file_type') or '<all>'}\n"
            "Proceed with these settings? (y/n): "
        )

    if use_saved and current.get("directory"):
        llm_summary = bool(current.get("llm_summary_consent"))
        save_db = True
        thumbnail_source = None
        run_with_saved_settings(
            directory=current.get("directory"),
            recursive_choice=True,
            file_type=current.get("file_type"),
            show_collaboration=True,
            show_contribution_metrics=True,
            show_contribution_summary=True,
            save=False,
            save_to_db=save_db,
            thumbnail_source=thumbnail_source,
            generate_llm_summary=llm_summary,
        )
        selected_dir = current.get("directory")
    else:
        while True:
            directory = input("Enter directory path or zip file path: ").strip()
            if not directory:
                print_error("No directory path provided.", "Enter a valid directory or zip file path to scan.")
                continue
            break

        recursive_choice = True
        file_type = input("Enter file type (e.g. .txt) or leave blank for all: ").strip()
        file_type = file_type if file_type else None
        show_collab = True
        show_metrics = True
        show_summary = True
        remember = ask_yes_no("Save these settings for next time? (y/n): ")
        save_db = True
        thumbnail_source = None
        llm_summary = bool(current.get("llm_summary_consent"))

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
            generate_llm_summary=llm_summary,
        )
        selected_dir = directory

    try:
        info = gather_project_info(selected_dir)
        project_name = info.get("project_name") or os.path.basename(os.path.abspath(selected_dir))
        out_dir = os.path.join("output", project_name)
        os.makedirs(out_dir, exist_ok=True)
        json_paths, txt_paths = output_project_info(info, output_dir=out_dir)
        # Display saved report files
        try:
            if isinstance(json_paths, list) and isinstance(txt_paths, list):
                print(f"Summary reports saved to: {out_dir}")
                for jp in json_paths:
                    if jp:
                        print(f"  JSON: {jp}")
                for tp in txt_paths:
                    if tp:
                        print(f"  TXT : {tp}")
            else:
                print(f"Summary reports saved to: {out_dir}")
        except Exception:
            print(f"Summary reports saved to: {out_dir}")
    except Exception as e:
        print_error(f"Failed to generate summary report: {e}", "Check that the directory exists and contains valid project files.")



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
    try:
        import inspect_db
        conn = get_connection()
        inspect_db.inspect_connection(conn, db_label=DB_PATH)
    except Exception as e:
        print_error(f"Failed to inspect database: {e}", "Check that the database file exists and is accessible.")

def remove_project_flow(db_path):
    import sqlite3

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM projects;")
    projects = cursor.fetchall()

    if not projects:
        print("No projects found.")
        conn.close()
        return

    print("\nProjects:")
    for pid, name in projects:
        print(f"{pid}: {name}")

    project_id = input("Enter the project ID to delete (or 'q' to cancel): ").strip()

    if project_id.lower() == "q":
        conn.close()
        return

    confirm = input(
        f"⚠️ This will permanently delete project {project_id}. Type 'DELETE' to confirm: "
    )

    if confirm != "DELETE":
        print("Cancelled.")
        conn.close()
        return

    # Delete project (FK cascade should handle related rows)
    cursor.execute("DELETE FROM projects WHERE id = ?;", (project_id,))
    conn.commit()
    conn.close()

    print("✔ Project deleted.")


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
        print_error(f"Failed to rank projects: {e}", "Scan a project first to populate the database.")
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
        
            user_input = input('Enter a contributor name or number to show per-project importance (leave blank to skip): ').strip()
            if user_input:
                # Check if user entered a number
                name = None
                try:
                    index = int(user_input) - 1
                    if 0 <= index < len(contributors):
                        name = contributors[index]
                    else:
                        print_error("Invalid selection.", f"Enter a number between 1 and {len(contributors)}.")
                except ValueError:
                    # User entered a name, not a number
                    name = user_input
                
                if name:
                    print(f"\nRanking projects by contributor: {name}\n")
                    user_projects = rank_projects_by_contributor(name, limit=limit)
                    print_projects_by_contributor(user_projects, name)
    except Exception as e:
        print_error(f"Failed to rank projects by contributor: {e}")


def handle_summarize_contributor_projects():
    """Handle generating summary for top-ranked projects by contributor."""
    print("\n=== Summarize Contributor Projects ===")
    
    if not db_is_initialized():
        print("Database not initialized. Run scan before generating summaries.")
        return
    
    BLACKLIST = {"githubclassroombot", "unknown"}
    
    # Query contributors from the database
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT name FROM contributors;")
        raw_contributors = [row[0] for row in cur.fetchall()]
    except Exception as e:
        print_error(f"Failed to fetch contributors: {e}", "Scan a project first to populate the database.")
        return
    finally:
        cur.close()
    
    canonical_usernames = sorted(
        set(canonical_username(name) for name in raw_contributors if canonical_username(name) not in BLACKLIST)
    )
    
    if not canonical_usernames:
        print("No contributors found in database.")
        input("\nPress Enter to return to main menu...")
        return
    
    # Display canonical usernames
    if canonical_usernames:
        print("\nDetected candidate usernames:")
        for idx, username in enumerate(canonical_usernames, 1):
            print(f"  {idx}. {username}")
        print("Press Enter to manually type a username.")
    
    # Prompt for contributor selection
    contributor_name = input("\nSelect a username by number or type it manually: ").strip()
    if contributor_name.isdigit():
        contributor_index = int(contributor_name) - 1
        if 0 <= contributor_index < len(canonical_usernames):
            contributor_name = canonical_usernames[contributor_index]
        else:
            print_error("Invalid selection.", f"Enter a number between 1 and {len(canonical_usernames)}, or type a username.")
            return

    if not contributor_name:
        print_error("No username provided.", "Enter a contributor number or type a username.")
        return
    
    # Prompt for optional project limit
    limit_input = input("Limit number of top projects (leave blank for all): ").strip()
    limit = int(limit_input) if limit_input.isdigit() else None
    
    # Call summarize_top_ranked_projects
    try:
        results = summarize_top_ranked_projects(
            contributor_name=contributor_name,
            limit=limit
        )
        print(f"\nProcessed {len(results)} project(s).")
    except Exception as e:
        print_error(f"Failed to generate contributor projects summary: {e}")


def handle_generate_project_summary():
    """Handle generating a project summary report."""
    print("\n=== Generate Project Summary Report ===")
    directory = input("Enter project directory path: ").strip()
    if not directory:
        print_error("No directory path provided.", "Enter a valid project directory path.")
        return
    if not os.path.exists(directory):
        print_error("Directory does not exist.", "Check the path and try again.")
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
        print_error(f"Failed to generate project summary: {e}", "Check that the directory contains valid project files.")


def handle_generate_resume():
    """Run the resume generator script for a specified username.

    Delegates username prompting and candidate listing entirely to the
    generate_resume script.
    """
    print("\n=== Generate Resume ===")

    script_path = os.path.join(os.path.dirname(__file__), 'generate_resume.py')
    if not os.path.exists(script_path):
        print_error(f"Resume generator script not found at: {script_path}", "Ensure the application is installed correctly.")
        return

    cmd = [sys.executable, script_path, '--save-to-db']

    try:
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print_error(f"Resume generator exited with code {result.returncode}.", "Check the output above for details on what went wrong.")
            return

        print("\nResume generated successfully.")

    except Exception as e:
        print_error(f"Failed to run resume generator: {e}", "Check that Python is configured correctly and try again.")


        
def handle_edit_project_display_name():
    """Allow user to edit custom resume display names for projects."""
    print("\n=== Edit Project Resume Display Names ===")

    projects = list_projects_for_display()
    if not projects:
        print_error("No projects found in the database.", "Run a directory scan first (Option 1) to populate the database.")
        return

    print("\nProjects:")
    for idx, p in enumerate(projects, start=1):
        custom = (p["custom_name"] or "").strip()
        default = p["name"]
        display = custom or default

        if custom:
         print(f"  {idx}. {display}  [custom | default: {default}]")
        else:
         print(f"  {idx}. {display}  (default)")


    choice = input(
    "\nEnter the project number from the list above to edit (blank to cancel): "
).strip()

    if not choice:
        return

    if not choice.isdigit() or not (1 <= int(choice) <= len(projects)):
        print_error("Invalid selection.", f"Enter a number between 1 and {len(projects)}.")
        return

    project = projects[int(choice) - 1]
    project_name = project["name"]

    print(f"\nSelected project: {project_name}")
    print("Enter a new display name for resumes.")
    print("Leave blank to clear the custom name and use the default.")

    new_name = input("New display name: ").strip()
    set_project_display_name(project_name, new_name or None)

    if new_name:
        print(f"✔ Resume display name updated to: {new_name}")
    else:
        print("✔ Custom resume name cleared (using default).")

    input("\nPress Enter to continue...")



def handle_generate_portfolio():
    """Run the portfolio generator script."""
    print("\n=== Generate Portfolio ===")
    script_path = os.path.join(os.path.dirname(__file__), 'generate_portfolio.py')
    if not os.path.exists(script_path):
        print_error(f"Portfolio generator script not found at: {script_path}", "Ensure the application is installed correctly.")
        return

    cmd = [sys.executable, script_path, '--save-to-db']
    try:
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print_error(f"Portfolio generator exited with code {result.returncode}.", "Check the output above for details on what went wrong.")
            return
    except Exception as e:
        print_error(f"Failed to run portfolio generator: {e}", "Check that Python is configured correctly and try again.")


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
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        resumes = _list_resumes(cur)
        _print_resume_list(resumes)
        if not resumes:
            return

        choice = input("\nEnter number to view/delete (blank to cancel): ").strip()
        if not choice:
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(resumes)):
            print_error("Invalid selection.", f"Enter a number between 1 and {len(resumes)}.")
            conn.close()
            return

        selected = resumes[int(choice) - 1]
        path = selected["resume_path"]
        uname = selected["username"] or selected["contributor_name"] or "<unknown>"
        print(f"\nSelected resume for {uname}: {path}")

        action = input("Choose action: (v)iew, (a)dd, (d)elete, (c)ancel [v]: ").strip().lower() or 'v'

        if action == "a":
            add_path = prompt_project_path(
                "Enter directory or zip to add to this resume (blank to cancel): ",
                allow_zip=True
            )
            if not add_path:
                print_error("No directory path provided.", "Enter a valid directory or zip file path.")
                return
            if not os.path.exists(add_path):
                print_error("Path does not exist.", "Check the path and try again.")
                return

            try:
                handle_add_to_resume(selected, add_path)
            except Exception as e:
                print_error(f"Failed to update resume: {e}")
            return

        if action == "c":
            return

        if action == "d":
            confirm = input("Are you sure you want to delete this resume? (y/n): ").strip().lower()
            if confirm != "y":
                return
            ok, msg = _delete_resume(conn, selected)
            print(msg)
            return

        # Default: view
        print(f"\nOpening resume for {uname}: {path}")
        preview, truncated_or_error = _preview_resume(path)
        if preview is None:
            print(truncated_or_error)
            return

        truncated = truncated_or_error is True
        print("\n--- Preview ---\n")
        print(preview)
        if truncated:
            print(f"\n... [Preview truncated - full file at: {path}]")

    except sqlite3.OperationalError as e:
        print_error(f"Resumes table not available: {e}", "Run a scan first to initialize the database.")
    except Exception as e:
        print_error(f"Failed to view resumes: {e}")
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def _list_portfolios(cur):
    """Return list of portfolios rows ordered by recent generated_at."""
    return safe_query(cur, """
        SELECT p.id, p.username, p.portfolio_path, p.generated_at, c.name AS contributor_name, p.metadata_json
        FROM portfolios p
        LEFT JOIN contributors c ON c.id = p.contributor_id
        ORDER BY p.generated_at DESC
        LIMIT 50
    """)


def _print_portfolio_list(portfolios):
    """Print numbered portfolio list."""
    if not portfolios:
        print(" No portfolios saved")
        return
    print("\nAvailable portfolios (most recent first):")
    for idx, p in enumerate(portfolios, start=1):
        uname = p['username'] or p['contributor_name'] or '<unknown>'
        print(f"  {idx}. user={uname} | generated={human_ts(p['generated_at'])}")
        print(f"     path: {p['portfolio_path']}")


def _delete_portfolio_with_file(conn, portfolio_row):
    """Delete portfolio row and corresponding file (best-effort for file)."""
    from db import delete_portfolio
    portfolio_id = portfolio_row["id"]
    delete_portfolio(portfolio_id)
    path = portfolio_row["portfolio_path"] if "portfolio_path" in portfolio_row.keys() else None
    if path and os.path.exists(path):
        try:
            os.remove(path)
            return True, "Deleted from database and removed file."
        except Exception as e:
            return True, f"Deleted from database but failed to remove file: {e}"
    return True, "Deleted from database; file not found or already removed."


def handle_view_portfolios():
    """List portfolios from the DB and allow viewing or updating content."""
    print("\n=== View Portfolios ===")
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        portfolios = _list_portfolios(cur)
        _print_portfolio_list(portfolios)
        if not portfolios:
            return

        choice = input("\nEnter number to view/delete (blank to cancel): ").strip()
        if not choice:
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(portfolios)):
            print_error("Invalid selection.", f"Enter a number between 1 and {len(portfolios)}.")
            return

        selected = dict(portfolios[int(choice) - 1])  # Ensure dict
        portfolio_file_path = selected.get("portfolio_path")
        if isinstance(portfolio_file_path, dict):
            portfolio_file_path = portfolio_file_path.get("portfolio_path") or portfolio_file_path.get("path")
        if not isinstance(portfolio_file_path, str):
            raise TypeError(f"Expected portfolio path as string, got {type(portfolio_file_path)}")

        uname = selected.get('username') or selected.get('contributor_name') or '<unknown>'
        print(f"\nSelected portfolio for {uname}: {portfolio_file_path}")

        action = input("Choose action: (v)iew, (a)dd, (d)elete, (c)ancel [v]: ").strip().lower() or 'v'

        if action == "a":
            add_path = prompt_project_path(
                "Enter directory or zip to add to this portfolio (blank to cancel): ",
                allow_zip=True
            )
            if not add_path:
                print_error("No directory path provided.", "Enter a valid directory or zip file path.")
                return
            if not os.path.exists(add_path):
                print_error("Path does not exist.", "Check the path and try again.")
                return

            try:
                handle_add_to_portfolio(selected, add_path)
            except Exception as e:
                print_error(f"Failed to update portfolio: {e}")
            return


        if action == "d":
            confirm = input("Are you sure you want to delete this portfolio? (y/n): ").strip().lower()
            if confirm != 'y':
                return
            ok, msg = _delete_portfolio_with_file(conn, selected)
            print(msg)
            return

        if action == "c":
            return

        # Default: view
        print(f"\nOpening portfolio for {uname}: {portfolio_file_path}")
        preview, truncated_or_error = _preview_resume(portfolio_file_path, lines=500)
        if preview is None:
            print(truncated_or_error)
            return

        truncated = truncated_or_error is True or (isinstance(truncated_or_error, bool) and truncated_or_error)
        print("\n--- Preview ---\n")
        print(preview)
        if truncated:
            print(f"\n... [Preview truncated - full file at: {portfolio_file_path}]")

    except sqlite3.OperationalError as e:
        print_error(f"Portfolios table not available: {e}", "Run a scan first to initialize the database.")
    except Exception as e:
        print_error(f"Failed to view portfolios: {e}")
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

from regenerate_portfolio_scan import portfolio_scan
from regenerate_portfolio import regenerate_portfolio

def handle_add_to_portfolio(portfolio_row, path):
    """
    portfolio_row is the DB row for the currently selected portfolio
    path is directory or zip to scan
    """
    scan_path = validate_project_path(path, allow_zip=True)

    print("\n=== Scanning new directory ===")
    portfolio_scan(scan_path, save_to_db=True)


    # --- Add project summary output to output/<project_name>/ ---
    try:
        info = gather_project_info(scan_path)
        project_name = info.get("project_name") or os.path.basename(os.path.abspath(scan_path))
        out_dir = os.path.join("output", project_name)
        os.makedirs(out_dir, exist_ok=True)
        json_path, txt_path = output_project_info(info, output_dir=out_dir)
        print(f"Summary reports saved to: {out_dir}")
        print(f"  JSON: {json_path}")
        print(f"  TXT:  {txt_path}")
    except Exception as e:
        print(f"Failed to generate project summary output: {e}")

    print("\n=== Regenerating portfolio ===")
    regenerate_portfolio(
        username=portfolio_row["username"],
        portfolio_path=portfolio_row["portfolio_path"],  # overwrite existing
        output_root="output",  # now includes the new project JSON
        confidence_level="high"
    )

    print("\nPortfolio successfully updated.")


from regenerate_resume import regenerate_resume
from regenerate_resume_scan import resume_scan

def handle_add_to_resume(resume_row, path):
    """
    resume_row is the DB row for the currently selected resume
    path is directory or zip to scan
    """
    scan_path = validate_project_path(path, allow_zip=True)

    print("\n=== Scanning new directory ===")
    resume_scan(scan_path, save_to_db=True)

    print("\n=== Regenerating resume ===")
    regenerate_resume(
        username=resume_row["username"],
        resume_path=resume_row["resume_path"],
    )

    print("\nResume successfully updated.")

from db import clear_database, delete_project_by_id

# ============================================================
# MANAGE SCANNED PROJECTS
# ============================================================

# Scan output/ directory and return list of project summary info (Returns list of dicts with keys: project_name, txt_path, json_path, folder_path)
def _list_project_summaries():

    output_root = os.path.join(os.path.dirname(__file__), '..', 'output')
    output_root = os.path.abspath(output_root)

    if not os.path.isdir(output_root):
        return []

    projects = []
    for folder_name in sorted(os.listdir(output_root)):
        folder_path = os.path.join(output_root, folder_name)
        if not os.path.isdir(folder_path):
            continue

        # Find TXT and JSON files in the output/ folder
        txt_files = []
        json_files = []
        for fname in os.listdir(folder_path):
            fpath = os.path.join(folder_path, fname)
            if fname.endswith('_summary_') or '_summary_' in fname and fname.endswith('.txt'):
                txt_files.append(fpath)
            elif fname.endswith('.txt') and '_summary_' in fname:
                txt_files.append(fpath)
            elif fname.endswith('.json') and '_info_' in fname:
                json_files.append(fpath)

        # Sort by modification time, most recent first
        txt_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        json_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

        # Add the found files to the projects list to be returned and listed
        projects.append({
            'project_name': folder_name,
            'folder_path': folder_path,
            'txt_path': txt_files[0] if txt_files else None,
            'json_path': json_files[0] if json_files else None,
            'txt_files': txt_files,
            'json_files': json_files,
        })

    return projects

# Deletes all output files for a project (TXT, JSON, and project folder within output/ if empty)
def _delete_project_output_files(project_name: str):

    output_root = os.path.join(os.path.dirname(__file__), '..', 'output')
    output_root = os.path.abspath(output_root)
    folder_path = os.path.join(output_root, project_name)

    # Delete all files in the project's output folder
    deleted_files = []
    if os.path.isdir(folder_path):
        for fname in os.listdir(folder_path):
            fpath = os.path.join(folder_path, fname)
            if os.path.isfile(fpath):
                try:
                    os.remove(fpath)
                    deleted_files.append(fpath)
                except Exception as e:
                    print(f"Warning: Could not delete {fpath}: {e}")

        # Remove project's output folder if empty
        try:
            if not os.listdir(folder_path):
                os.rmdir(folder_path)
                deleted_files.append(folder_path)
        except Exception as e:
            print(f"Warning: Could not remove folder {folder_path}: {e}")

    return deleted_files

# List project summaries from output/ and allow viewing, name editing, and deletion
def handle_manage_scanned_projects():
    
    print("\n=== Manage Scanned Projects ===")
    projects = _list_project_summaries()

    if not projects:
        print("No project summaries found in output/ directory.")
        print("Run a project scan first (Option 1) to generate summaries.")
        return

    # Get custom display names from database for showing status
    db_projects = {}
    try:
        db_project_list = list_projects_for_display()
        for p in db_project_list:
            db_projects[p["name"]] = p
    except Exception:
        pass

    print("\nAvailable project summaries:")
    for idx, p in enumerate(projects, start=1):

        # Check if project has custom name in database
        db_entry = db_projects.get(p['project_name'])
        custom_name = db_entry["custom_name"] if db_entry and "custom_name" in db_entry.keys() and db_entry["custom_name"] else None
        if custom_name:
            name_display = f"{custom_name} (was: {p['project_name']})"
        else:
            name_display = p['project_name']

        print(f"  {idx}. {name_display}")

    choice = input("\nEnter number to manage (blank to cancel): ").strip()
    if not choice:
        return

    if not choice.isdigit() or not (1 <= int(choice) <= len(projects)):
        print_error("Invalid selection.", f"Enter a number between 1 and {len(projects)}.")
        return

    selected = projects[int(choice) - 1]
    project_name = selected['project_name']

    # Get the current custom name (if any)
    db_entry = db_projects.get(project_name)
    current_custom_name = db_entry["custom_name"] if db_entry and "custom_name" in db_entry.keys() and db_entry["custom_name"] else None

    print(f"\nSelected project: {project_name}")
    if current_custom_name:
        print(f"  Display name: {current_custom_name}")
    print(f"  Folder: {selected['folder_path']}")
    if selected['txt_path']:
        print(f"  TXT summary: {os.path.basename(selected['txt_path'])}")

    print("\nChoose an action:")
    print("1. View summary")
    print("2. Edit display name")
    print("3. Delete project")
    print("4. Cancel")

    action = input("\nSelect an option (1-4): ").strip()

    if action == '4' or not action:
        return

    if action == '2':
        # Check if project exists in database
        if not db_entry:
            print_error(f"Project '{project_name}' not found in database.", "The project must be in the database to edit its display name. Consider rescanning the project first.")
            return

        print(f"\nCurrent display name: {current_custom_name or project_name} {'(custom)' if current_custom_name else '(default)'}")
        print("Enter a new display name for resumes/portfolios.")
        print("Leave blank to clear the custom name and use the default.")

        new_name = input("New display name: ").strip()
        set_project_display_name(project_name, new_name or None)

        if new_name:
            print(f"Success. Display name updated to: {new_name}")
        else:
            print("Success. Custom display name cleared (reverted to original).")
        return

    if action == '3':
        print(f"\nThis will permanently delete:")
        print(f"    - Project '{project_name}' from the database (if it exists)")
        print(f"    - All summary files in {selected['folder_path']}")

        confirm = input("\nType 'DELETE' to confirm: ").strip()
        if confirm != 'DELETE':
            print("Cancelled.")
            return

        # Delete from database
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id FROM projects WHERE name = ?", (project_name,))
            row = cur.fetchone()
            conn.close()

            if row:
                project_id = row['id']
                delete_project_by_id(project_id)
                print(f"Success. Removed '{project_name}' from database.")
            else:
                print(f"  (Project '{project_name}' not found in database - skipping DB deletion)")
        except Exception as e:
            print(f"Warning: Database deletion error: {e}")

        # Delete local output/ files
        deleted = _delete_project_output_files(project_name)
        if deleted:
            print(f"Success. Deleted {len(deleted)} output file(s)/folder(s).")
        else:
            print("(No output files found to delete)")

        print(f"Success. Project '{project_name}' has been removed.")
        return

    if action == '1':
        # View project TXT summary
        if not selected['txt_path']:
            print_error("No TXT summary file found for this project.")
            return

        print(f"\n--- Viewing Summary for {project_name} ---\n")
        try:
            with open(selected['txt_path'], 'r', encoding='utf-8') as f:
                content = f.read()
            print(content)
        except Exception as e:
            print_error(f"Failed to read summary file: {e}")
        return

    print_error("Invalid selection.", "Enter a number between 1 and 4.")


def database_management_menu():
    while True:
        print("\n=== DATABASE MANAGEMENT ===")
        print("1. Inspect database")
        print("2. Clear database (REMOVE ALL DATA)")
        print("3. Remove a project")
        print("4. Go back")

        choice = input("Select an option (1-4): ").strip()

        if choice == "1":
            handle_inspect_database()

        elif choice == "2":
            confirm = input(
                "**This will DELETE ALL DATA. Type 'CLEAR' to confirm**: "
            )
            if confirm == "CLEAR":
                clear_database()
                print("✔ Database cleared.")
            else:
                print("Cancelled.")

        elif choice == "3":
            remove_project_menu()

        elif choice == "4":
            return

        else:
            print("Invalid selection.")

def remove_project_menu():
    """
    Show projects, prompt user to select one, then delete it.
    """

    projects = list_projects_for_display()
    if not projects:
        print("No projects found.")
        return

    print("\nSelect the project you wish to remove:")
    for idx, p in enumerate(projects, start=1):
        name = p["custom_name"] or p["name"]
        print(f"{idx}. {name}")

    choice = input("\nEnter project number (or 'q' to cancel): ").strip()
    if choice.lower() == "q":
        return

    if not choice.isdigit() or not (1 <= int(choice) <= len(projects)):
        print("Invalid selection.")
        return

    project = projects[int(choice) - 1]

    confirm = input(
        f"⚠️ Permanently delete '{project['name']}'? Type 'DELETE' to confirm ⚠️: "
    )

    if confirm != "DELETE":
        print("Cancelled.")
        return

    project_name = project["name"]
    delete_project_by_id(project["id"])
    print("✔ Project removed from database.")

    # Also delete output files
    deleted = _delete_project_output_files(project_name)
    if deleted:
        print(f"✔ Deleted {len(deleted)} output file(s)/folder(s).")




def handle_analyze_roles():
    """Handle contributor role analysis."""
    print("\n=== Analyze Contributor Roles ===")

    # Ask if user wants to see all available roles first
    show_roles = ask_yes_no("\nWould you like to see all available contributor roles and their descriptions? (y/n): ")

    if show_roles:
        print(display_all_roles())

    # Load overall contributor data
    print("Loading contributors from database...")
    contributors_data = load_contributors_from_db()

    if not contributors_data:
        print_error("No contributor data found in the database.", "Run a directory scan first (Option 1) to populate the database.")
        return

    print(f"Found {len(contributors_data)} contributors")

    # Analyze overall roles
    print("Analyzing overall contributor roles...")
    overall_analysis = analyze_project_roles(contributors_data)

    # Ask if user wants per-project breakdown
    show_per_project = ask_yes_no("\nInclude per-project breakdown? (y/n): ")
    
    per_project_analysis = None
    if show_per_project:
        print("\nLoading per-project contributor data...")
        per_project_raw = load_contributors_per_project_from_db()
        
        if per_project_raw:
            print(f"Found {len(per_project_raw)} projects")
            print("Analyzing roles for each project...")
            per_project_analysis = {}
            for project_name, project_contributors in per_project_raw.items():
                per_project_analysis[project_name] = analyze_project_roles(project_contributors)
        else:
            print("No per-project data found.")
    
    # Generate and display report
    print("\n" + "="*70)
    report = format_roles_report(overall_analysis, per_project_analysis)
    print(report)


def main():
    """Main menu loop."""
    while True:
        print_main_menu()
        choice = input("\nSelect an option (0-13): ").strip()

        if choice == "1":
            handle_scan_directory()
        elif choice == "2":
            handle_manage_scanned_projects()
        elif choice == "3":
            handle_generate_resume()
        elif choice == "4":
            handle_generate_portfolio()
        elif choice == "5":
            handle_view_resumes()
        elif choice == "6":
            handle_view_portfolios()
        elif choice == "7":
            handle_rank_projects()
        elif choice == "8":
            handle_summarize_contributor_projects()
        elif choice == "9":
            handle_generate_project_summary()
        elif choice == "10":
            handle_project_evidence()
        elif choice == "11":
            handle_analyze_roles()
        elif choice == "12":
            handle_edit_project_thumbnail()
        elif choice == "13":
            database_management_menu()
        elif choice == "0":
            print("\nExiting program. Goodbye!")
            sys.exit(0)
        else:
            print("\nInvalid option. Please select 0-13.")

        input("\nPress Enter to return to main menu...")

if __name__ == "__main__":
    main()
