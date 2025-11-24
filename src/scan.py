import os
import sys
import time
import subprocess
import zipfile
import io
import tempfile
import json
import sqlite3


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from config import load_config, save_config, merge_settings, config_path as default_config_path, is_default_config
from consent import ask_for_data_consent, ask_yes_no
from detect_langs import detect_languages_and_frameworks, LANGUAGE_MAP
from detect_skills import detect_skills
from file_utils import is_valid_format
from db import get_connection, init_db, save_scan
from collab_summary import summarize_project_contributions

# Try to import contribution metrics module; support running as package or standalone
try:
    from contrib_metrics import analyze_repo, pretty_print_metrics
except Exception:
    try:
        from .contrib_metrics import analyze_repo, pretty_print_metrics
    except Exception:
        analyze_repo = None
        pretty_print_metrics = None

# Try to import project_info_output (gather & write summaries)
try:
    from project_info_output import gather_project_info, output_project_info
except Exception:
    try:
        from .project_info_output import gather_project_info, output_project_info
    except Exception:
        gather_project_info = None
        output_project_info = None


def _zip_mtime_to_epoch(dt_tuple):
    """
    Convert ZipInfo.date_time (Y, M, D, h, m, s) to a POSIX timestamp.
    Note: The tuple has no timezone info; treated as local time.
    """
    try:
        y, mo, d, h, mi, s = dt_tuple
        return time.mktime((y, mo, d, h, mi, s, 0, 0, -1))
    except Exception:
        return 0.0


def _is_macos_junk(name: str) -> bool:
    """Return True if the path or filename is a macOS metadata file/dir we should ignore."""
    if not name:
        return False
    base = os.path.basename(name)
    if base == '.DS_Store':
        return True
    if name.split('/')[0] == '__MACOSX':
        return True
    return False


def _scan_zip(zf: zipfile.ZipFile, display_prefix: str, recursive: bool, file_type: str, files_found: list,
              show_collaboration: bool = False, extract_root: str = None):
    """
    Internal: scan an already-open ZipFile and collect/print entries.
    - display_prefix: the accumulated path like "/path/to.zip" or "/path/to.zip:inner.zip"
    - files_found: list of tuples (display_path, size, mtime)
    - show_collaboration: whether to display collaboration info for files
    - extract_root: the root directory where the zip contents are extracted
    """
    for info in zf.infolist():
        # Skip directories
        if hasattr(info, 'is_dir') and info.is_dir():
            continue
        name = info.filename
        # Skip macOS junk files
        if _is_macos_junk(name):
            continue
        # Skip unsupported file formats
        if not is_valid_format(name):
            print(f"Skipping unsupported file format in zip: {name}")
            continue
        # Respect non-recursive by including only root-level entries (no '/')
        if not recursive and ('/' in name or name.endswith('/')):
            continue
        # Record this file if it matches the filter (or no filter)
        display = f"{display_prefix}:{name}"
        if file_type is None or name.lower().endswith(file_type.lower()):
            files_found.append((display, info.file_size, _zip_mtime_to_epoch(info.date_time)))
            print(display)
            if show_collaboration:
                collab = "unknown"
                if extract_root:
                    candidate = os.path.join(extract_root, name)
                    if os.path.exists(candidate):
                        collab = get_collaboration_info(candidate)
                print(f"  Collaboration: {collab}")

        # If recursive and this entry itself is a .zip, descend into it
        if recursive and name.lower().endswith('.zip'):
            try:
                with zf.open(info) as nested_file:
                    nested_bytes = nested_file.read()
                with zipfile.ZipFile(io.BytesIO(nested_bytes)) as nested_zf:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        nested_zf.extractall(tmpdir)
                        _scan_zip(
                            nested_zf,
                            f"{display}",
                            recursive,
                            file_type,
                            files_found,
                            show_collaboration=show_collaboration,
                            extract_root=tmpdir
                        )
            except zipfile.BadZipFile:
                pass


def _persist_scan(scan_source: str, files_found: list, project: str = None, notes: str = None, file_metadata: dict = None,
                  detected_languages: list = None, detected_skills: list = None, contributors: list = None,
                  project_created_at: str = None, project_repo_url: str = None):
    """Persist a scan and its file records to the database using db.save_scan.

    This now also attempts to persist detected languages, skills and contributors
    if they are provided by the caller or can be detected prior to calling.
    """
    # Delegate to db.save_scan which handles transactions and upserts
    # Delegate to db.save_scan which handles transactions and upserts
    return save_scan(
        scan_source,
        files_found,
        project=project,
        notes=notes,
        detected_languages=detected_languages,
        detected_skills=detected_skills,
        contributors=contributors,
        file_metadata=file_metadata,
        project_created_at=project_created_at,
        project_repo_url=project_repo_url,
    )


def list_files_in_zip(zip_path, recursive=False, file_type=None, show_collaboration=False, save_to_db=False):
    """Prints file names inside a zip archive."""
    if not os.path.exists(zip_path) or not zipfile.is_zipfile(zip_path):
        print("Directory does not exist.")
        return

    print(f"\nScanning zip archive: {zip_path}")
    if file_type:
        print(f"Filtering by file type: {file_type}")
    print()

    files_found = []
    with zipfile.ZipFile(zip_path) as zf:
        with tempfile.TemporaryDirectory() as tmpdir:
            zf.extractall(tmpdir)
            _scan_zip(
                zf,
                zip_path,
                recursive,
                file_type,
                files_found,
                show_collaboration=show_collaboration,
                extract_root=tmpdir
            )

            # Optionally persist results to DB (collect metadata first)
            if save_to_db and files_found:
                # prepare placeholder for file metadata in case of failures
                file_meta = {}
                try:
                    # detect languages/skills/contributors from extracted tree
                    langs = detect_languages_and_frameworks(tmpdir).get('languages', [])
                    skills = detect_skills(tmpdir).get('skills', [])
                    metrics = analyze_repo_path(tmpdir) if analyze_repo is not None else None
                    contributors = list(metrics['commits_per_author'].keys()) if metrics and metrics.get('commits_per_author') else None

                    # Build per-file metadata (owner) where possible
                    for item in files_found:
                        display = item[0] if isinstance(item, tuple) else item
                        # display format: zip_path:inner/path
                        inner = display.split(':', 1)[1] if ':' in display else None
                        owner = None
                        if inner:
                            candidate = os.path.join(tmpdir, inner)
                            if os.path.exists(candidate):
                                owner = get_collaboration_info(candidate)
                        # also infer language from filename extension
                        lang = None
                        try:
                            _, ext = os.path.splitext(inner or display)
                            if ext:
                                lang = LANGUAGE_MAP.get(ext.lower())
                        except Exception:
                            lang = None
                        file_meta[display] = {'owner': owner, 'language': lang}

                    # Attempt to detect repo-level info from the extracted tree
                    project_created_at, project_repo_url = _get_repo_info(tmpdir)

                    _persist_scan(
                        zip_path,
                        files_found,
                        project=None,
                        notes=None,
                        file_metadata=file_meta,
                        detected_languages=langs,
                        detected_skills=skills,
                        contributors=contributors,
                        project_created_at=project_created_at,
                        project_repo_url=project_repo_url,
                    )
                except sqlite3.OperationalError:
                    try:
                        init_db()
                        _persist_scan(zip_path, files_found, project=None, notes=None,
                                      file_metadata=file_meta,
                                      detected_languages=langs,
                                      detected_skills=skills,
                                      contributors=contributors)
                    except Exception:
                        print("Warning: failed to persist zip scan results to database.")

    if not files_found:
        print("No files found matching your criteria.")
        return []

    largest = max(files_found, key=lambda t: t[1] or 0)
    smallest = min(files_found, key=lambda t: t[1] or 0)
    newest = max(files_found, key=lambda t: t[2] or 0)
    oldest = min(files_found, key=lambda t: t[2] or 0)

    print("\n=== File Statistics ===")
    print(f"Largest file: {largest[0]} ({largest[1]} bytes)")
    print(f"Smallest file: {smallest[0]} ({smallest[1]} bytes)")
    print(f"Most recently modified: {newest[0]} ({time.ctime(newest[2]) if newest[2] else 'unknown'})")
    print(f"Least recently modified: {oldest[0]} ({time.ctime(oldest[2]) if oldest[2] else 'unknown'})")
    return files_found


def analyze_repo_path(path: str):
    """Analyze a filesystem path or zip archive for contribution metrics.

    If path is a zip archive, extract to a temporary directory and run analysis there.
    Returns the metrics dict or None if analysis couldn't run.
    """
    if analyze_repo is None:
        print("Contribution metrics module not available.")
        return None

    if os.path.isfile(path) and path.lower().endswith('.zip'):
        with tempfile.TemporaryDirectory() as td:
            try:
                with zipfile.ZipFile(path) as zf:
                    zf.extractall(td)
            except Exception as e:
                print(f"Failed to extract zip for analysis: {e}")
                return None
            # analyze extracted tree
            try:
                return analyze_repo(td)
            except Exception as e:
                # Don't let analysis errors (e.g., git log on non-repo) crash the scanner
                print(f"Contribution analysis failed: {e}")
                return None
    else:
        try:
            return analyze_repo(path)
        except Exception as e:
            print(f"Contribution analysis failed: {e}")
            return None


def _find_git_root(start_path: str):
    """Return the path to the git repository root for start_path or None."""
    p = os.path.abspath(start_path)
    if os.path.isfile(p):
        p = os.path.dirname(p)
    while True:
        git_path = os.path.join(p, '.git')
        if os.path.exists(git_path):
            return p
        parent = os.path.dirname(p)
        if parent == p:
            break
        p = parent
    return None


def _get_repo_info(path: str):
    """Return (created_at_iso, repo_url) for a git repo found at or above path, or (None, None)."""
    repo_root = _find_git_root(path)
    if not repo_root:
        return (None, None)
    try:
        # repo url (remote origin)
        res = subprocess.run(["git", "config", "--get", "remote.origin.url"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, cwd=repo_root, timeout=3)
        repo_url = res.stdout.strip() if res and res.stdout.strip() else None
    except Exception:
        repo_url = None

    try:
        # earliest commit (initial commit) -> committer date in ISO 8601
        res = subprocess.run(["git", "rev-list", "--max-parents=0", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, cwd=repo_root, timeout=3)
        if res and res.stdout.strip():
            first = res.stdout.splitlines()[0].strip()
            res2 = subprocess.run(["git", "show", "-s", "--format=%cI", first], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, cwd=repo_root, timeout=3)
            created_at = res2.stdout.strip() if res2 and res2.stdout.strip() else None
        else:
            created_at = None
    except Exception:
        created_at = None

    return (created_at, repo_url)


def get_collaboration_info(file_path: str) -> str:
    """Return collaboration info for a file using git history when available."""
    def _find_git_root(start_path: str):
        p = os.path.abspath(start_path)
        if os.path.isfile(p):
            p = os.path.dirname(p)
        while True:
            git_path = os.path.join(p, '.git')
            if os.path.exists(git_path):
                return p
            parent = os.path.dirname(p)
            if parent == p:
                break
            p = parent
        return None

    repo_root = _find_git_root(file_path)
    if not repo_root:
        return "unknown"

    rel_path = os.path.relpath(os.path.abspath(file_path), repo_root)
    rel_path_git = rel_path.replace(os.sep, '/')
    try:
        result = subprocess.run(
            ["git", "log", "--pretty=format:%an", "--", rel_path_git],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            cwd=repo_root,
            timeout=5,
        )
    except Exception:
        return "unknown"

    if result.returncode != 0 or not result.stdout:
        return "unknown"

    authors = sorted({a.strip() for a in result.stdout.splitlines() if a.strip()})
    if not authors:
        return "unknown"
    if len(authors) == 1:
        return f"individual ({authors[0]})"
    return f"collaborative ({', '.join(authors)})"


def list_files_in_directory(path, recursive=False, file_type=None, show_collaboration=False, save_to_db=False):
    """
    Prints file names in the given directory, or inside a .zip file.
    If recursive=True, it scans subdirectories (or all nested zip entries).
    If file_type is provided (e.g. '.txt'), only files of that type are shown.
    """
    if not path:
        print("Directory does not exist.")
        return

    # If the path points to a zip file, handle via zip scanning
    if os.path.isfile(path) and path.lower().endswith('.zip'):
        return list_files_in_zip(path, recursive=recursive, file_type=file_type, show_collaboration=show_collaboration, save_to_db=save_to_db)

    if not os.path.exists(path) or not os.path.isdir(path):
        print("Directory does not exist.")
        return

    print(f"\nScanning directory: {path}")
    if file_type:
        print(f"Filtering by file type: {file_type}")
    print()

    files_found = []
    if recursive:
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d != '__MACOSX']
            for file in files:
                if _is_macos_junk(file):
                    continue
                if not is_valid_format(file):
                    print(f"Skipping unsupported file format: {file}")
                    continue
                if file_type is None or file.lower().endswith(file_type.lower()):
                    full_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(full_path)
                    except Exception:
                        size = None
                    try:
                        mtime = os.path.getmtime(full_path)
                    except Exception:
                        mtime = None
                    files_found.append((full_path, size, mtime))
                    print(full_path)
                    if show_collaboration:
                        print(f"  Collaboration: {get_collaboration_info(full_path)}")
    else:
        for file in os.listdir(path):
            full_path = os.path.join(path, file)
            if os.path.isfile(full_path):
                if _is_macos_junk(file):
                    continue
                if not is_valid_format(file):
                    print(f"Skipping unsupported file format: {file}")
                    continue
                if file_type is None or file.lower().endswith(file_type.lower()):
                    try:
                        size = os.path.getsize(full_path)
                    except Exception:
                        size = None
                    try:
                        mtime = os.path.getmtime(full_path)
                    except Exception:
                        mtime = None
                    files_found.append((full_path, size, mtime))
                    print(full_path)
                    if show_collaboration:
                        print(f"  Collaboration: {get_collaboration_info(full_path)}")

    if not files_found:
        print("No files found matching your criteria.")
        return []

    # files_found entries are tuples (path, size, mtime)
    largest = max(files_found, key=lambda t: t[1] or 0)
    smallest = min(files_found, key=lambda t: t[1] or 0)
    newest = max(files_found, key=lambda t: t[2] or 0)
    oldest = min(files_found, key=lambda t: t[2] or 0)

    print("\n=== File Statistics ===")
    print(f"Largest file: {largest[0]} ({largest[1]} bytes)")
    print(f"Smallest file: {smallest[0]} ({smallest[1]} bytes)")
    print(f"Most recently modified: {newest[0]} ({time.ctime(newest[2]) if newest[2] else 'unknown'})")
    print(f"Least recently modified: {oldest[0]} ({time.ctime(oldest[2]) if oldest[2] else 'unknown'})")
    # Optionally persist scan results to the database
    if save_to_db:
        try:
            # Detect project-level metadata and persist with the scan
            try:
                langs = detect_languages_and_frameworks(path).get('languages', [])
            except Exception:
                langs = None
            try:
                skills = detect_skills(path).get('skills', [])
            except Exception:
                skills = None
            try:
                metrics = analyze_repo_path(path) if analyze_repo is not None else None
                contributors = list(metrics['commits_per_author'].keys()) if metrics and metrics.get('commits_per_author') else None
            except Exception:
                contributors = None

            # build file metadata (owner) for each file
            file_meta = {}
            for item in files_found:
                display = item[0] if isinstance(item, tuple) else item
                owner = None
                try:
                    owner = get_collaboration_info(display)
                except Exception:
                    owner = None
                # infer language from extension for filesystem files
                lang = None
                try:
                    _, ext = os.path.splitext(display)
                    if ext:
                        lang = LANGUAGE_MAP.get(ext.lower())
                except Exception:
                    lang = None
                file_meta[display] = {'owner': owner, 'language': lang}

            # Try to detect repo information for the path being scanned
            project_created_at, project_repo_url = _get_repo_info(path)

            _persist_scan(path, files_found, project=os.path.basename(path), notes=None,
                          file_metadata=file_meta,
                          detected_languages=langs,
                          detected_skills=skills,
                          contributors=contributors,
                          project_created_at=project_created_at,
                          project_repo_url=project_repo_url)
        except sqlite3.OperationalError:
            # Try initializing DB and retry once
            try:
                init_db()
                _persist_scan(path, files_found, project=os.path.basename(path), notes=None,
                              file_metadata=file_meta,
                              detected_languages=langs,
                              detected_skills=skills,
                              contributors=contributors)
            except Exception:
                print("Warning: failed to persist scan results to database.")
    return files_found


def run_with_saved_settings(
    directory=None,
    recursive_choice=None,
    file_type=None,
    show_collaboration=None,
    show_contribution_metrics=None,
    show_contribution_summary=None,
    save=False,
    save_to_db=False,
    config_path=None,
):
    config = load_config(config_path)

    # Create settings dict with all provided values
    settings_to_save = {
        "directory": directory,
        "recursive_choice": recursive_choice,
        "file_type": file_type,
        "show_collaboration": show_collaboration,
        "show_contribution_metrics": show_contribution_metrics,
        "show_contribution_summary": show_contribution_summary
    }

    # Save settings if requested
    if save:
        save_config(settings_to_save, config_path)

    # Merge for current run
    final = merge_settings(settings_to_save, config)

    # Run scan
    list_files_in_directory(
        final["directory"],
        recursive=final["recursive_choice"],
        file_type=final["file_type"],
        show_collaboration=final.get("show_collaboration", False),
        save_to_db=save_to_db,
    )

    # After scan, summarize detected skills first
    print("\n=== Detecting Skills ===")
    skills_summary = detect_skills(directory)
    if skills_summary["skills"]:
        print("\n=== Detected Skills Summary ===")
        print(", ".join(skills_summary["skills"]))
    else:
        print("\nNo significant skills detected.")

    # Then show contribution metrics if requested
    if final.get("show_contribution_metrics"):
        try:
            print("\n=== Contribution Metrics ===")
            metrics = analyze_repo_path(final["directory"])
            if metrics and 'pretty_print_metrics' in globals():
                pretty_print_metrics(metrics)
        except Exception as e:
            print(f"Error analyzing contribution metrics: {e}")

    # Show contribution summary if requested
    if final.get("show_contribution_summary"):
        summarize_project_contributions(final["directory"])


if __name__ == "__main__":
    import os
    import sys

    while True:
        print("\n=== Scan Manager ===")
        print("1. Run a new scan")
        print("2. View previous scan insights")
        print("3. Exit")

        choice = input("Select an option (1/2/3): ").strip()

        insights_root = os.path.join("output")

        # EXIT PROGRAM
        if choice == "3":
            print("Exiting program.")
            sys.exit(0)

        # OPTION 2 — VIEW PREVIOUS INSIGHT FILES
        if choice == "2":
            print("\n=== Previous Scan Insights ===")

            if not os.path.exists(insights_root):
                print("No insights found.")
                continue

            # Collect all insight files
            all_files = []
            for root, dirs, files in os.walk(insights_root):
                for f in files:
                    if f.endswith(".json") or f.endswith(".txt"):
                        all_files.append(os.path.join(root, f))

            if not all_files:
                print("No insight files found.")
                continue

            print("\nAvailable Insights:")
            for i, full_path in enumerate(all_files, 1):
                print(f"{i}. {os.path.basename(full_path)}")

            print("\n1. Delete a scan insight")
            print("2. Back to main menu")
            sub_choice = input("Select an option (1/2): ").strip()

            # DELETE AN INSIGHT
            if sub_choice == "1":
                delete_num = input("Enter the number of the insight to delete: ").strip()

                try:
                    idx = int(delete_num) - 1
                    file_to_delete = all_files[idx]
                    os.remove(file_to_delete)
                    print(f"Deleted: {os.path.basename(file_to_delete)}")
                except:
                    print("Invalid selection. No file deleted.")

                continue  # back to main menu

            # BACK TO MAIN MENU
            elif sub_choice == "2":
                continue

            else:
                print("Invalid option. Returning to main menu.")
                continue

        # OPTION 1 — RUN NEW SCAN 
        if choice == "1":
            break  # exits the menu loop and continues to scan logic

        print("Invalid option. Please select 1, 2, or 3.")

    # Handle data consent first
    current = load_config(None)
    # If user previously accepted consent, display an unobtrusive prompt to re-run ask_for_data_consent().
    # This lets users who previously gave consent to view the consent prompt again and change their answer if they wish.
    if current.get("data_consent") is True:
        if ask_yes_no("Would you like to review our data access policy? (y/n): ", False):
            current = load_config(None)
            consent = ask_for_data_consent(config_path=default_config_path())
            if not consent:
                print("Data access consent not granted, aborting application.")
                sys.exit(0)
    else:
        # If user hasn't explicitly accepted, always prompt so they can set or change their preference.
        consent = ask_for_data_consent(config_path=default_config_path())
        if not consent:
            print("Data access consent not granted, aborting application.")
            sys.exit(0)

    # Load current settings
    current = load_config(None)
    
    # Only prompt for reuse of scan settings if config.json has at least one non-default value.
    if not is_default_config(current):
        use_saved = ask_yes_no(
            "Would you like to use the settings from your most recent scan?\n"
            f"  Scanned Directory:          {current.get('directory') or '<none>'}\n"
            f"  Scan Nested Folders:        {current.get('recursive_choice')}\n"
            f"  Only Scan File Type:        {current.get('file_type') or '<all>'}\n"
            f"  Show Collaboration Info:    {current.get('show_collaboration')}\n"
            f"  Show Contribution Metrics:  {current.get('show_contribution_metrics')}\n"
            f"  Show Contribution Summary:  {current.get('show_contribution_summary')}\n"
            "Proceed with these settings? (y/n): "
        )
    else:
        use_saved = False

    if use_saved and current.get("directory"):
        # Use saved settings and only ask about database
        
        save_db = ask_yes_no("Save scan results to database? (y/n): ", False)
        
        run_with_saved_settings(
            directory=current.get("directory"),
            recursive_choice=current.get("recursive_choice"),
            file_type=current.get("file_type"),
            show_collaboration=current.get("show_collaboration"),
            show_contribution_metrics=current.get("show_contribution_metrics"),
            show_contribution_summary=current.get("show_contribution_summary"),
            save=False,
            save_to_db=save_db,
        )
    else:
        # Collect all scan settings first
        directory = input("Enter directory path or zip file path: ").strip()
        directory = directory if directory else None
        recursive_choice = ask_yes_no("Scan subdirectories too? (y/n): ", False)
        file_type = input("Enter file type (e.g. .txt) or leave blank for all: ").strip()
        file_type = file_type if file_type else None
        show_collab = ask_yes_no("Show collaboration info? (y/n): ")
        show_metrics = ask_yes_no("Show contribution metrics? (y/n): ")
        show_summary = ask_yes_no("Show contribution summary? (y/n): ")

        # Ask about saving settings after collecting all of them
        remember = ask_yes_no("Save these settings for next time? (y/n): ")
        
        # Ask about database last
        save_db = ask_yes_no("Save scan results to database? (y/n): ")

        run_with_saved_settings(
            directory=directory,
            recursive_choice=recursive_choice,
            file_type=file_type,
            show_collaboration=show_collab,
            show_contribution_metrics=show_metrics,
            show_contribution_summary=show_summary,
            save=remember,
            save_to_db=save_db,
        )

    try:
        from project_info_output import gather_project_info, output_project_info
    except Exception:
        try:
            from .project_info_output import gather_project_info, output_project_info
        except Exception:
            gather_project_info = None
            output_project_info = None

    selected_dir = current.get("directory") if use_saved else locals().get("directory")

    if selected_dir is None:
        # Nothing to summarize
        pass
    elif gather_project_info is None or output_project_info is None:
        print("Project summary functions not available (couldn't import project_info_output).")
    else:
        if ask_yes_no("Would you like to generate a project summary report (JSON & TXT)? (y/n): ", False):
            try:
                info = gather_project_info(selected_dir)
                project_name = info.get("project_name") or os.path.basename(os.path.abspath(selected_dir))
                out_dir = os.path.join("output", project_name)
                os.makedirs(out_dir, exist_ok=True)
                json_path, txt_path = output_project_info(info, output_dir=out_dir)
                print(f"Summary reports saved to: {out_dir}")
            except Exception as e:
                print(f"Failed to generate summary report: {e}")

