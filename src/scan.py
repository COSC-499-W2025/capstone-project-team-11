import os
import sys
import time
import subprocess
import zipfile
import io
import threading
import contextlib
import tempfile
import json
import sqlite3
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from config import load_config, save_config, merge_settings, config_path as default_config_path, is_default_config
from consent import ask_for_data_consent, ask_yes_no
from detect_langs import detect_languages_and_frameworks, LANGUAGE_MAP
from detect_skills import detect_skills
from file_utils import is_valid_format, is_image_file
from db import get_connection, init_db, save_scan
from collab_summary import summarize_project_contributions, identify_contributions
from datetime import datetime
from llm_summary import get_or_generate_summary, summary_timestamp

# =============================================================================
# SCAN PROGRESS OUTPUT MANAGER
# =============================================================================

# Centralized, clean scan output manager for consistent CLI display
class ScanProgress:

    def __init__(self):
        self.results = {}

    # Print a section header
    def header(self, title: str):
        print(f"\n{title}")
        print("-" * 20)

    # Print a real-time progress bar (updates in place)
    def progress(self, current: int, total: int):
        if total <= 0:
            return
        pct = min(100, int((current / total) * 100))
        width = 25
        filled = int((current / total) * width)
        bar = '#' * filled + '-' * (width - filled)
        sys.stdout.write(f'\r    [{bar}] {pct}%')
        sys.stdout.flush()
        if current >= total:
            print()

    # Print a simple item line
    def item(self, text: str):
        print(f"    [-] {text}")

    # Store a result for later display in summary
    def store(self, key: str, value):
        self.results[key] = value

    # Print scan complete summary with moderate detail
    def complete(self, project_name: str, output_dir: str = None):
        self.header("Scan Complete!")
        self.item(f"Project: {project_name}")
        if self.results.get('files_found'):
            self.item(f"Files: {self.results['files_found']} scanned, {self.results.get('files_skipped', 0)} skipped ({self.results['files_found'] + self.results.get('files_skipped', 0)} total)")
        if self.results.get('languages'):
            self.item(f"Languages: {', '.join(self.results['languages'])}")
        if self.results.get('frameworks'):
            self.item(f"Frameworks: {', '.join(self.results['frameworks'])}")
        if self.results.get('skills'):
            self.item(f"Skills: {', '.join(self.results['skills'])}")
        if self.results.get('contributors'):
            self.item(f"Contributors: {', '.join(self.results['contributors'])}")
        if self.results.get('project_type'):
            self.item(f"Project Type: {self.results['project_type']}")
        if output_dir:
            self.item(f"Summary saved to: {output_dir}")

# Global progress instance for use across functions
_scan_progress = None

# Get or create the global scan progress instance (set reset=True to start fresh)
def get_scan_progress(reset: bool = False) -> ScanProgress:
    global _scan_progress
    if _scan_progress is None or reset:
        _scan_progress = ScanProgress()
    return _scan_progress

# Try to import contribution metrics module; support running as package or standalone
try:
    from contrib_metrics import analyze_repo, pretty_print_metrics, canonical_username
except Exception:
    try:
        from .contrib_metrics import analyze_repo, pretty_print_metrics, canonical_username
    except Exception:
        analyze_repo = None
        pretty_print_metrics = None
        canonical_username = None

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


def _print_progress(current: int, total: int, label: str = ""):
    """Single-line filling progress bar.

    - When `total` > 0: shows a fixed-width bar that fills proportionally.
    - When `total` is 0 or unknown: shows a simple counter.
    This intentionally avoids printing individual filenames.
    """
    try:
        # determine basic strings
        if total and total > 0:
            pct = int((current / total) * 100)
            width = 30
            filled = int((current / total) * width)
            if filled > width:
                filled = width
            bar = '[' + ('#' * filled) + ('-' * (width - filled)) + ']'
            msg = f"Scanning {bar} {pct:3d}% ({current}/{total})"
        else:
            msg = f"Scanning: {current} files"

        # Write with carriage return and flush (single-line)
        sys.stdout.write('\r' + msg + ' ' * 10)
        sys.stdout.flush()

        # When complete, terminate the line
        if total and current >= total:
            sys.stdout.write('\n')
            sys.stdout.flush()
    except Exception:
        pass


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


def _normalize_contributor_key(name: str) -> str:
    return _normalize_contributor_name(name)


def _normalize_contributor_name(name: str) -> str:
    if not name:
        return ""
    if canonical_username:
        return canonical_username(name)
    raw = str(name).strip().lower()
    return re.sub(r"[^0-9a-z]+", "", raw)


def _format_owner_from_names(names: list) -> str:
    cleaned = [n.strip() for n in (names or []) if n and n.strip()]
    if not cleaned:
        return "unknown"
    if len(cleaned) == 1:
        return f"individual ({cleaned[0]})"
    return f"collaborative ({', '.join(cleaned)})"


def _get_existing_contributors() -> list:
    try:
        with get_connection() as conn:
            rows = conn.execute("SELECT name FROM contributors ORDER BY name COLLATE NOCASE").fetchall()
            names = [row["name"] for row in rows if row["name"]]
            normalized = [_normalize_contributor_name(n) for n in names if _normalize_contributor_name(n)]
            seen = set()
            unique = [n for n in normalized if not (n in seen or seen.add(n))]
            return sorted(unique)
    except Exception:
        return []


def _prompt_manual_contributors(project_label: str) -> list:
    if not sys.stdin.isatty():
        return []

    prompt = f"No git contributors found for '{project_label}'. Add contributors now? (y/n): "
    try:
        if not ask_yes_no(prompt):
            return []
    except Exception:
        return []

    existing = _get_existing_contributors()
    if existing:
        print("\nDetected candidate usernames:")
        for idx, name in enumerate(existing, 1):
            print(f"  {idx}. {name}")
        print("  0. Add a new contributor")
        print("You may enter numbers (e.g. 1) or exact usernames, comma-separated.")

    existing_map = {_normalize_contributor_key(n): n for n in existing}
    existing_keys = set(existing_map.keys())
    while True:
        raw_input = input(
            "Select contributors (numbers or names, comma-separated): "
        ).strip()
        if not raw_input:
            return []

        tokens = [t.strip() for t in raw_input.split(",") if t.strip()]
        needs_new = any(token in {"0", "new"} for token in tokens)
        selected_keys = set()
        results = []
        invalid = False

        for token in tokens:
            if token in {"0", "new"}:
                continue
            if token.isdigit():
                i = int(token)
                if 1 <= i <= len(existing):
                    name = existing[i - 1]
                    key = _normalize_contributor_key(name)
                    if key in selected_keys:
                        invalid = True
                        print("  Duplicate selection detected. Try again.")
                        break
                    results.append(name)
                    selected_keys.add(key)
                else:
                    invalid = True
                    print(f"  Invalid selection: {token}")
                continue

            name = _normalize_contributor_name(token)
            key = _normalize_contributor_key(name)
            if not key:
                invalid = True
                print("  Invalid name entry. Try again.")
                break
            if key in existing_keys or key in selected_keys:
                invalid = True
                print("  Contributor already exists. Select from the list instead.")
                break
            results.append(name)
            selected_keys.add(key)

        if invalid:
            continue

        if needs_new:
            while True:
                new_raw = input("Enter new contributor names (comma-separated): ").strip()
                if not new_raw:
                    break
                new_tokens = [t.strip() for t in new_raw.split(",") if t.strip()]
                new_invalid = False
                for token in new_tokens:
                    name = _normalize_contributor_name(token)
                    key = _normalize_contributor_key(name)
                    if not key:
                        new_invalid = True
                        print("  Invalid name entry. Try again.")
                        break
                    if key in existing_keys or key in selected_keys:
                        new_invalid = True
                        print("  Contributor already exists. Select from the list instead.")
                        break
                if new_invalid:
                    continue
                for token in new_tokens:
                    name = _normalize_contributor_name(token)
                    key = _normalize_contributor_key(name)
                    results.append(name)
                    selected_keys.add(key)
                break

        return results


def _display_skipped_files_summary(skipped_files_list):
    """Display skipped files categorized by file extension."""
    if not skipped_files_list:
        return

    # Categorize by extension
    by_extension = {}
    for file_path in skipped_files_list:
        _, ext = os.path.splitext(file_path)
        if not ext:
            ext = "(no extension)"
        by_extension.setdefault(ext, 0)
        by_extension[ext] += 1

    # Display summary
    total = len(skipped_files_list)
    print(f"\n=== Skipped Files ({total} files due to unsupported format) ===")
    for ext in sorted(by_extension.keys()):
        count = by_extension[ext]
        print(f"  {ext}: {count} file(s)")
        
        
def _determine_project_collaboration(path: str) -> str:
    """Determine if a project is collaborative or individual.
    
    Returns 'Collaborative' if the project is a git repo with multiple authors,
    otherwise returns 'Individual'.
    """
    # Detect all git repos under the path; fall back to single-root check.
    repo_roots = _find_all_git_roots(path)
    if not repo_roots:
        solo_root = _find_git_root(path)
        repo_roots = [solo_root] if solo_root else []

    if not repo_roots:
        return "Individual"

    authors = set()
    for repo_root in repo_roots:
        try:
            result = subprocess.run(
                ["git", "log", "--format=%an"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                cwd=repo_root,
                timeout=5,
            )

            if result.returncode != 0 or not result.stdout:
                continue

            authors.update(author.strip() for author in result.stdout.splitlines() if author.strip())
        except Exception:
            continue

    if not authors:
        return "Individual"
    return "Collaborative" if len(authors) > 1 else "Individual"





def _resolve_extracted_root(extract_root: str) -> str:
    """
    Given a directory where an archive was extracted, attempt to pick the actual project root.
    If the extraction produced a single non-junk directory, descend into it so downstream
    detectors operate on the real project folder (rather than the container directory).
    """
    try:
        entries = [entry for entry in os.listdir(extract_root) if not _is_macos_junk(entry)]
        if len(entries) == 1:
            candidate = os.path.join(extract_root, entries[0])
            if os.path.isdir(candidate):
                return candidate
    except Exception:
        pass
    return extract_root


def _find_all_git_roots(base_path: str) -> list:
    """Return all git repository roots under base_path (non-recursive into each repo)."""
    roots = []
    base_abs = os.path.abspath(base_path)
    if not os.path.exists(base_abs):
        return roots

    for root, dirs, _ in os.walk(base_abs):
        if '.git' in dirs:
            roots.append(os.path.abspath(root))
            # Do not descend into this repo to avoid nested duplicates
            dirs[:] = []
            continue
        # Skip macOS junk dirs early
        dirs[:] = [d for d in dirs if not _is_macos_junk(d)]
    return roots


def _prepare_nested_extract_root(parent_root: str, relative_name: str) -> str:
    """
    Create a directory under parent_root where a nested archive should be extracted.
    We suffix with '__unzipped' to avoid collisions with existing directories.
    """
    if not parent_root:
        return None
    rel = relative_name.rstrip('/').replace('\\', '/')
    base, _ = os.path.splitext(rel)
    if not base:
        base = "nested"
    rel_path = f"{base}__unzipped".replace('/', os.sep)
    target = _safe_join_extract_root(parent_root, rel_path)
    os.makedirs(target, exist_ok=True)
    return target


def _safe_join_extract_root(root: str, relative_path: str) -> str:
    """Join root/relative_path while preventing traversal outside the extraction root."""
    combined = os.path.normpath(os.path.join(root, relative_path))
    root_abs = os.path.abspath(root)
    combined_abs = os.path.abspath(combined)
    if os.path.commonpath([root_abs, combined_abs]) != root_abs:
        return root
    return combined


def _scan_zip(zf: zipfile.ZipFile, display_prefix: str, recursive: bool, file_type: str, files_found: list,
              show_collaboration: bool = False, extract_root: str = None, progress: dict = None,
              extracted_paths: dict = None):
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
        # Skip unsupported file formats (track them)
        if not is_valid_format(name):
            if progress is not None:
                progress['skipped'] = progress.get('skipped', 0) + 1
                if 'skipped_files' not in progress:
                    progress['skipped_files'] = []
                progress['skipped_files'].append(f"{display_prefix}:{name}")
            continue
        # Respect non-recursive by including only root-level entries (no '/')
        if not recursive and ('/' in name or name.endswith('/')):
            continue
        display = f"{display_prefix}:{name}"
        actual_rel = name.replace('/', os.sep)
        actual_path = _safe_join_extract_root(extract_root, actual_rel) if extract_root else None

        is_zip_entry = name.lower().endswith('.zip')
        wants_zip_files = bool(file_type and file_type.lower() == '.zip')
        should_record = (file_type is None or name.lower().endswith(file_type.lower()))
        if is_zip_entry and recursive and not wants_zip_files:
            should_record = False

        if should_record:
            files_found.append((display, info.file_size, _zip_mtime_to_epoch(info.date_time)))
            # update progress bar if provided (label with zip basename only)
            if progress is not None:
                progress['current'] = progress.get('current', 0) + 1
                _print_progress(progress['current'], progress.get('total', 0), display_prefix)
            # Do not print per-file collaboration info here to avoid exposing filenames
            if extracted_paths is not None and actual_path and os.path.exists(actual_path):
                extracted_paths[display] = actual_path

        # If recursive and this entry itself is a .zip, descend into it
        if recursive and name.lower().endswith('.zip'):
            try:
                nested_rel = name.replace('/', os.sep)
                nested_zip_path = _safe_join_extract_root(extract_root, nested_rel) if extract_root else None
                nested_extract_root = _prepare_nested_extract_root(extract_root, name) if extract_root else None
                if nested_zip_path and os.path.exists(nested_zip_path):
                    with zipfile.ZipFile(nested_zip_path) as nested_zf:
                        if nested_extract_root:
                            nested_zf.extractall(nested_extract_root)
                        _scan_zip(
                            nested_zf,
                            f"{display}",
                            recursive,
                            file_type,
                            files_found,
                            show_collaboration=show_collaboration,
                            extract_root=nested_extract_root,
                            progress=progress,
                            extracted_paths=extracted_paths
                        )
                else:
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
                                extract_root=tmpdir,
                                progress=progress,
                                extracted_paths=extracted_paths
                            )
            except zipfile.BadZipFile:
                pass


def _persist_scan(scan_source: str, files_found: list, project: str = None, notes: str = None, file_metadata: dict = None,
                  detected_languages: list = None, detected_skills: list = None, contributors: list = None,
                  project_created_at: str = None, project_repo_url: str = None, project_thumbnail_path: str = None,
                  git_metrics: dict = None, tech_summary: dict = None,
                  summary_text: str = None, summary_input_hash: str = None, summary_model: str = None,
                  summary_updated_at: str = None):
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
        project_thumbnail_path=project_thumbnail_path,
        git_metrics=git_metrics,
        tech_summary=tech_summary,
        summary_text=summary_text,
        summary_input_hash=summary_input_hash,
        summary_model=summary_model,
        summary_updated_at=summary_updated_at,
    )


def _run_with_progress(func, args=(), kwargs=None, total_steps: int = 30):
    """Run `func(*args, **kwargs)` in a background thread while showing a filling progress bar.

    Returns (result, captured_stdout, error)
    """
    if kwargs is None:
        kwargs = {}
    buf = io.StringIO()
    result_container = {}

    def _runner():
        try:
            with contextlib.redirect_stdout(buf):
                result_container['result'] = func(*args, **kwargs)
        except Exception as e:
            result_container['error'] = e

    th = threading.Thread(target=_runner)
    th.daemon = True
    th.start()

    progress = get_scan_progress()
    step = 0
    # animate until finished
    while th.is_alive():
        step = (step + 1) % (total_steps + 1)
        if step == 0:
            step = total_steps
        progress.progress(step, total_steps)
        time.sleep(0.08)

    # ensure final 100%
    progress.progress(total_steps, total_steps)

    return result_container.get('result'), buf.getvalue(), result_container.get('error')


def list_files_in_zip(zip_path, recursive=False, file_type=None, show_collaboration=False, save_to_db=False,
                      extract_dir=None, generate_llm_summary=False):
    """Prints file names inside a zip archive."""
    if not os.path.exists(zip_path) or not zipfile.is_zipfile(zip_path):
        print("Directory does not exist.")
        return

    # Use only an in-place progress display; avoid printing individual file names

    files_found = []
    temp_extract = None
    tmpdir = None
    try:
        if extract_dir:
            tmpdir = extract_dir
            os.makedirs(tmpdir, exist_ok=True)
        else:
            temp_extract = tempfile.TemporaryDirectory()
            tmpdir = temp_extract.name

        with zipfile.ZipFile(zip_path) as zf:
            # determine total matching entries for progress
            total_entries = 0
            for info in zf.infolist():
                if hasattr(info, 'is_dir') and info.is_dir():
                    continue
                name = info.filename
                if _is_macos_junk(name):
                    continue
                if not is_valid_format(name):
                    continue
                if not recursive and ('/' in name or name.endswith('/')):
                    continue
                if file_type is None or name.lower().endswith(file_type.lower()):
                    total_entries += 1

            progress = {'current': 0, 'total': total_entries, 'skipped': 0}
            # show initial progress line (label with archive basename only)
            _print_progress(0, progress['total'], zip_path)

            zf.extractall(tmpdir)
            extracted_locations = {}
            _scan_zip(
                zf,
                zip_path,
                recursive,
                file_type,
                files_found,
                show_collaboration=show_collaboration,
                extract_root=tmpdir,
                progress=progress,
                extracted_paths=extracted_locations,
            )
        
        # Display skipped files summary
        if progress.get('skipped', 0) > 0:
            _display_skipped_files_summary(progress.get('skipped_files', []))

        # Optionally persist results to DB (collect metadata first)
        if save_to_db and files_found:
            # prepare placeholder for file metadata in case of failures
            file_meta = {}
            try:
                # detect languages/skills/contributors from extracted tree
                # Run language detection under the progress/capture helper to avoid noisy prints
                langs_res, langs_out, langs_err = _run_with_progress(
                    detect_languages_and_frameworks, args=(tmpdir,),  total_steps=40
                )
                langs = langs_res.get('languages', []) if langs_res else []

                # Run skill detection using the same runner so output is captured
                skills_res, skills_out, skills_err = _run_with_progress(
                    detect_skills, args=(tmpdir,),  total_steps=40
                )
                skills = skills_res.get('skills', []) if skills_res else []
                tech_summary = {}
                if skills_res:
                    tech_summary = {
                        "languages": skills_res.get("languages", []),
                        "frameworks": skills_res.get("frameworks", []),
                        "high_confidence_languages": skills_res.get("high_confidence_languages", []),
                        "medium_confidence_languages": skills_res.get("medium_confidence_languages", []),
                        "low_confidence_languages": skills_res.get("low_confidence_languages", []),
                        "high_confidence_frameworks": skills_res.get("high_confidence_frameworks", []),
                        "medium_confidence_frameworks": skills_res.get("medium_confidence_frameworks", []),
                        "low_confidence_frameworks": skills_res.get("low_confidence_frameworks", []),
                    }

                # Build per-file metadata (owner) where possible
                for item in files_found:
                    display = item[0] if isinstance(item, tuple) else item
                    owner = None
                    candidate = extracted_locations.get(display)
                    if candidate and os.path.exists(candidate):
                        owner = get_collaboration_info(candidate)
                    # also infer language from filename extension
                    lang = None
                    try:
                        if candidate and os.path.isfile(candidate):
                            _, ext = os.path.splitext(candidate)
                        else:
                            # fallback: use display name (may include zip metadata)
                            inner = display.split(':')[-1]
                            _, ext = os.path.splitext(inner)
                        if ext:
                            lang = LANGUAGE_MAP.get(ext.lower())
                    except Exception:
                        lang = None
                    file_meta[display] = {'owner': owner, 'language': lang}

                # Detect all project roots (BOTH git repo folders and non-git folders)
                repo_roots = _find_all_project_roots(tmpdir)

                if repo_roots:
                    # Multiple or single repo detected - save per-repo
                    print("\n=== Saving Projects to Database ===")
                    _persist_multi_repo_scans(
                        zip_path,
                        files_found,
                        repo_roots,
                        file_metadata=file_meta,
                        show_progress=True,
                        extracted_locations=extracted_locations,
                        generate_llm_summary=generate_llm_summary,
                    )
                else:
                    # No git repos - save as generic project
                    metrics = analyze_repo_path(tmpdir) if analyze_repo is not None else None
                    contributors = _contributors_from_metrics(metrics)
                    if not contributors:
                        contributors = _prompt_manual_contributors(os.path.basename(zip_path)) or None
                    if contributors:
                        owner_val = _format_owner_from_names(contributors)
                        for meta in file_meta.values():
                            if isinstance(meta, dict):
                                meta['owner'] = owner_val
                    project_created_at, project_repo_url = _get_repo_info(tmpdir)
                    summary_text = None
                    summary_input_hash = None
                    summary_model = None
                    summary_updated_at = None
                    if generate_llm_summary:
                        try:
                            project_name = os.path.basename(os.path.abspath(zip_path))
                            print(f"    [-] LLM summary: generating for {project_name}...")
                            summary_text, summary_input_hash, summary_model, _ = get_or_generate_summary(
                                project_name=project_name,
                                project_root=tmpdir,
                                files_found=files_found,
                                languages=tech_summary.get("languages", []),
                                frameworks=tech_summary.get("frameworks", []),
                                skills=skills,
                            )
                            if summary_text:
                                summary_updated_at = summary_timestamp()
                        except Exception:
                            summary_text = None
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
                        git_metrics=metrics,
                        tech_summary=tech_summary,
                        summary_text=summary_text,
                        summary_input_hash=summary_input_hash,
                        summary_model=summary_model,
                        summary_updated_at=summary_updated_at,
                    )
            except sqlite3.OperationalError:
                try:
                    init_db()
                    repo_roots = _find_all_project_roots(tmpdir)
                    if repo_roots:
                        print("\n=== Saving Projects to Database ===")
                        _persist_multi_repo_scans(zip_path, files_found, repo_roots, file_metadata=file_meta,
                                                 extracted_locations=extracted_locations,
                                                 generate_llm_summary=generate_llm_summary)
                    else:
                        _persist_scan(
                            zip_path,
                            files_found,
                            project=None,
                            notes=None,
                            file_metadata=file_meta,
                            git_metrics=metrics if 'metrics' in locals() else None,
                            tech_summary=tech_summary if 'tech_summary' in locals() else None,
                        )
                except Exception:
                    print("Warning: failed to persist zip scan results to database.")
    finally:
        if temp_extract is not None:
            temp_extract.cleanup()

    if not files_found:
        print("No files found matching your criteria.")
        return []

    largest = max(files_found, key=lambda t: t[1] or 0)
    smallest = min(files_found, key=lambda t: t[1] or 0)
    newest = max(files_found, key=lambda t: t[2] or 0)
    oldest = min(files_found, key=lambda t: t[2] or 0)

    # Concise file statistics (do not show file paths)
    print("\n=== File Statistics ===")
    print(f"Total files found: {len(files_found)}")
    print(f"Largest file size: {largest[1]} bytes")
    print(f"Smallest file size: {smallest[1]} bytes")
    print(f"Most recently modified: {time.ctime(newest[2]) if newest[2] else 'unknown'}")
    print(f"Least recently modified: {time.ctime(oldest[2]) if oldest[2] else 'unknown'}")
    
    # Determine and display collaboration status
    collab_status = _determine_project_collaboration(tmpdir)
    print(f"\nProject Type: {collab_status}")
    return files_found


def analyze_repo_path(path: str):
    """Analyze a filesystem path or zip archive for contribution metrics.

    If path is a zip archive, extract to a temporary directory and run analysis there.
    Returns the metrics dict for a single repo, a list of metrics dicts for multiple repos,
    or None if analysis couldn't run.
    """
    if analyze_repo is None:
        print("Contribution metrics module not available.")
        return None

    def _analyze_roots(roots: list):
        results = []
        for repo_root in roots:
            try:
                metrics = analyze_repo(repo_root)
                results.append(metrics)
            except Exception as e:
                print(f"Contribution analysis failed for {repo_root}: {e}")
        if not results:
            return None
        return results[0] if len(results) == 1 else results

    if os.path.isfile(path) and path.lower().endswith('.zip'):
        with tempfile.TemporaryDirectory() as td:
            try:
                with zipfile.ZipFile(path) as zf:
                    zf.extractall(td)
            except Exception as e:
                print(f"Failed to extract zip for analysis: {e}")
                return None
            repo_roots = _find_all_git_roots(td)
            if not repo_roots:
                solo = _find_git_root(td)
                repo_roots = [solo] if solo else []
            return _analyze_roots(repo_roots)

    # Directory or repo path
    repo_roots = []
    if os.path.isdir(path):
        repo_roots = _find_all_git_roots(path)
        if not repo_roots:
            solo = _find_git_root(path)
            repo_roots = [solo] if solo else []
    else:
        root = _find_git_root(path)
        if root:
            repo_roots = [root]

    return _analyze_roots(repo_roots)


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


def _contributors_from_metrics(metrics):
    """Return a unique list of contributors from metrics (single or multi-repo)."""
    if not metrics:
        return None
    if isinstance(metrics, list):
        names = set()
        for m in metrics:
            try:
                names.update(m.get('commits_per_author', {}).keys())
            except Exception:
                continue
        return list(names) if names else None
    return list(metrics.get('commits_per_author', {}).keys()) if metrics.get('commits_per_author') else None


def _map_files_to_repos(file_list: list, repo_roots: list) -> dict:
    """Map each file to its parent git repo root. Returns dict[repo_root] -> files."""
    mapping = {root: [] for root in repo_roots}
    unmapped = []

    for item in file_list:
        file_path = item[0] if isinstance(item, tuple) else item
        # Extract inner part for zip display paths, use as-is for normal filesystem paths
        if ':' in file_path:
            # Skip Windows drive letter colons (position 1), only split on zip-style colons
            colon_pos = file_path.find(':', 2)
            resolved_path = file_path if colon_pos == -1 else file_path[:colon_pos]
        else:
            resolved_path = file_path
        matched = False
        for repo_root in repo_roots:
            try:
                abs_file = os.path.abspath(resolved_path)
                abs_repo = os.path.abspath(repo_root)
                common = os.path.commonpath([abs_file, abs_repo])
                if common == abs_repo:
                    mapping[repo_root].append(item)
                    matched = True
                    break
            except (ValueError, TypeError):
                continue
        if not matched:
            unmapped.append(item)

    # Assign unmapped files to the first repo (as fallback)
    if unmapped and repo_roots:
        mapping[repo_roots[0]].extend(unmapped)

    # Remove empty repos from mapping
    return {k: v for k, v in mapping.items() if v}


def _map_files_to_repos_with_locations(file_list: list, repo_roots: list, extracted_locations: dict) -> dict:
    """Map files to repos using actual extracted filesystem paths from extracted_locations dict."""
    mapping = {root: [] for root in repo_roots}
    unmapped = []
    
    for item in file_list:
        display = item[0] if isinstance(item, tuple) else item
        actual_path = extracted_locations.get(display)
        
        if not actual_path:
            unmapped.append(item)
            continue
        
        matched = False
        for repo_root in repo_roots:
            try:
                abs_file = os.path.abspath(actual_path)
                abs_repo = os.path.abspath(repo_root)
                common = os.path.commonpath([abs_file, abs_repo])
                if common == abs_repo:
                    mapping[repo_root].append(item)
                    matched = True
                    break
            except (ValueError, TypeError):
                continue
        
        if not matched:
            unmapped.append(item)
    
    # Assign unmapped files to the first repo (as fallback)
    if unmapped and repo_roots:
        mapping[repo_roots[0]].extend(unmapped)
    
    # Remove empty repos from mapping
    return {k: v for k, v in mapping.items() if v}


def _find_candidate_project_roots(base_path: str) -> list:
    """Return immediate subdirectories under base_path that contain at least one file."""
    candidates = []
    if not base_path or not os.path.isdir(base_path):
        return candidates
    try:
        for entry in os.scandir(base_path):
            if not entry.is_dir():
                continue
            if _is_macos_junk(entry.name):
                continue
            # check if the subtree has any files
            has_files = False
            for _, _, files in os.walk(entry.path):
                if files:
                    has_files = True
                    break
            if has_files:
                candidates.append(entry.path)
    except Exception:
        return candidates
    return candidates

# Find ALL project roots under base_path: git repos AND non-git project directories
# Combines `_find_all_git_roots()` with `_find_candidate_project_roots()` to catch non-git subdirectories
def _find_all_project_roots(base_path: str) -> list:

    git_roots = _find_all_git_roots(base_path)
    candidate_roots = _find_candidate_project_roots(base_path)

    if not candidate_roots:
        return git_roots
    if not git_roots:
        # Only treat as multi-project if >1 candidates
        return candidate_roots if len(candidate_roots) > 1 else []

    abs_git_roots = [os.path.abspath(g) for g in git_roots]

    all_roots = list(git_roots)
    for candidate in candidate_roots:
        abs_candidate = os.path.abspath(candidate)

        # Determine candidate's relationship to known git roots
        is_inside_git = False
        contains_git = False
        for abs_git in abs_git_roots:
            try:
                common = os.path.commonpath([abs_candidate, abs_git])
                if common == abs_git:
                    # Candidate is inside a git root, skip
                    is_inside_git = True
                    break
                if common == abs_candidate:
                    # Candidate is a parent of a git root, scan subdirs for non-git siblings instead
                    contains_git = True
            except (ValueError, TypeError):
                continue

        if is_inside_git:
            continue

        if contains_git:
            # Container directory, check immediate subdirs for non-git project folders
            try:
                for entry in os.scandir(candidate):
                    if not entry.is_dir() or _is_macos_junk(entry.name):
                        continue
                    abs_sub = os.path.abspath(entry.path)
                    # Skip if this subdir is already a known git root
                    if abs_sub in abs_git_roots:
                        continue
                    # Skip subdirs inside any git root
                    inside = False
                    for abs_git in abs_git_roots:
                        try:
                            if os.path.commonpath([abs_sub, abs_git]) == abs_git:
                                inside = True
                                break
                        except (ValueError, TypeError):
                            continue
                    if inside:
                        continue
                    # Only add if subdir contains files
                    has_files = False
                    for _, _, files in os.walk(entry.path):
                        if files:
                            has_files = True
                            break
                    if has_files:
                        all_roots.append(entry.path)
            except Exception:
                pass
        else:
            # Standalone non-git directory, add it
            all_roots.append(candidate)

    return all_roots


def _persist_multi_repo_scans(scan_source: str, file_list: list, repo_roots: list,
                               detected_languages: list = None, detected_skills: list = None,
                               file_metadata: dict = None, show_progress: bool = True,
                               extracted_locations: dict = None,
                               generate_llm_summary: bool = False):
    """Persist scans for multiple git repositories, one scan per repo.
    
    Detects languages, frameworks, and skills per-project to avoid aggregating them.
    """
    if not repo_roots or not file_list:
        return
    
    # Use extracted_locations if provided (for zip files), otherwise use standard mapping
    if extracted_locations:
        repo_file_map = _map_files_to_repos_with_locations(file_list, repo_roots, extracted_locations)
    else:
        repo_file_map = _map_files_to_repos(file_list, repo_roots)
    
    for repo_root in repo_roots:
        if repo_root not in repo_file_map or not repo_file_map[repo_root]:
            continue
        
        files_for_repo = repo_file_map[repo_root]
        project_name = os.path.basename(os.path.abspath(repo_root))
        
        try:
            # Get repo-specific info
            created_at, repo_url = _get_repo_info(repo_root)
            
            # Analyze this repo
            metrics = analyze_repo_path(repo_root) if analyze_repo is not None else None
            contributors = _contributors_from_metrics(metrics)
            
            # Detect languages, frameworks, and skills PER PROJECT
            try:
                project_langs_res, _, _ = _run_with_progress(
                    detect_languages_and_frameworks, args=(repo_root,), total_steps=40
                )
                project_langs = project_langs_res.get('languages', []) if project_langs_res else []
            except Exception:
                project_langs = []

            try:
                project_skills_res, _, _ = _run_with_progress(
                    detect_skills, args=(repo_root,), total_steps=40
                )
                project_skills = project_skills_res.get('skills', []) if project_skills_res else []
            except Exception:
                project_skills = []
                project_skills_res = None

            tech_summary = {}
            if project_skills_res:
                tech_summary = {
                    "languages": project_skills_res.get("languages", []),
                    "frameworks": project_skills_res.get("frameworks", []),
                    "high_confidence_languages": project_skills_res.get("high_confidence_languages", []),
                    "medium_confidence_languages": project_skills_res.get("medium_confidence_languages", []),
                    "low_confidence_languages": project_skills_res.get("low_confidence_languages", []),
                    "high_confidence_frameworks": project_skills_res.get("high_confidence_frameworks", []),
                    "medium_confidence_frameworks": project_skills_res.get("medium_confidence_frameworks", []),
                    "low_confidence_frameworks": project_skills_res.get("low_confidence_frameworks", []),
                }
            
            summary_text = None
            summary_input_hash = None
            summary_model = None
            summary_updated_at = None
            if generate_llm_summary:
                try:
                    print(f"    [-] LLM summary: generating for {project_name}...")
                    summary_text, summary_input_hash, summary_model, _ = get_or_generate_summary(
                        project_name=project_name,
                        project_root=repo_root,
                        files_found=files_for_repo,
                        languages=tech_summary.get("languages", project_langs),
                        frameworks=tech_summary.get("frameworks", []),
                        skills=project_skills,
                    )
                    if summary_text:
                        summary_updated_at = summary_timestamp()
                except Exception:
                    summary_text = None

            # Persist this repo's scan with its OWN detected languages and skills
            _persist_scan(
                repo_root,
                files_for_repo,
                project=project_name,
                notes=None,
                file_metadata=file_metadata,
                detected_languages=project_langs,
                detected_skills=project_skills,
                contributors=contributors,
                project_created_at=created_at,
                project_repo_url=repo_url,
                git_metrics=metrics,
                tech_summary=tech_summary,
                summary_text=summary_text,
                summary_input_hash=summary_input_hash,
                summary_model=summary_model,
                summary_updated_at=summary_updated_at,
            )
            if show_progress:
                print(f"  Saved project: {project_name}")
        except Exception as e:
            print(f"  Warning: failed to save project {project_name}: {e}")


def _get_repo_info(path: str):
    """Return (created_at_iso, repo_url) for a git repo found at or above path, or (None, None)."""
    repo_root = _find_git_root(path)
    if not repo_root:
        # If multiple repos exist, this function returns no single source of truth
        multi_roots = _find_all_git_roots(path) if os.path.isdir(path) else []
        if len(multi_roots) != 1:
            return (None, None)
        repo_root = multi_roots[0]
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


def list_files_in_directory(path, recursive=False, file_type=None, show_collaboration=False, save_to_db=False,
                            zip_extract_dir=None, project_thumbnail_path=None, generate_llm_summary=False):
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
        return list_files_in_zip(
            path,
            recursive=recursive,
            file_type=file_type,
            show_collaboration=show_collaboration,
            save_to_db=save_to_db,
            extract_dir=zip_extract_dir,
            generate_llm_summary=generate_llm_summary,
        )

    if not os.path.exists(path) or not os.path.isdir(path):
        print("Directory does not exist.")
        return

    print(f"\nScanning directory: {path}")
    if file_type:
        print(f"Filtering by file type: {file_type}")
    print()

    files_found = []
    # determine total files to scan for progress display
    total_files = 0
    if recursive:
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d != '__MACOSX']
            for file in files:
                if _is_macos_junk(file):
                    continue
                if not is_valid_format(file):
                    continue
                if file_type is None or file.lower().endswith(file_type.lower()):
                    total_files += 1
    else:
        try:
            for file in os.listdir(path):
                full_path = os.path.join(path, file)
                if os.path.isfile(full_path):
                    if _is_macos_junk(file):
                        continue
                    if not is_valid_format(file):
                        continue
                    if file_type is None or file.lower().endswith(file_type.lower()):
                        total_files += 1
        except Exception:
            total_files = 0

    progress = {'current': 0, 'total': total_files, 'skipped': 0, 'skipped_files': []}
    _print_progress(0, total_files, path)

    if recursive:
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d != '__MACOSX']
            for file in files:
                if _is_macos_junk(file):
                    continue
                if not is_valid_format(file):
                    # track skipped files
                    progress['skipped'] = progress.get('skipped', 0) + 1
                    full_path = os.path.join(root, file)
                    progress['skipped_files'].append(full_path)
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
                    progress['current'] += 1
                    # Update progress every 10 files to avoid too many redraws
                    if progress['current'] % 10 == 0:
                        _print_progress(progress['current'], progress['total'], path)
                    # do not print per-file collaboration info during scan
    else:
        for file in os.listdir(path):
            full_path = os.path.join(path, file)
            if os.path.isfile(full_path):
                if _is_macos_junk(file):
                    continue
                if not is_valid_format(file):
                    progress['skipped'] = progress.get('skipped', 0) + 1
                    progress['skipped_files'].append(full_path)
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
                    progress['current'] += 1
                    # Update progress every 10 files to avoid too many redraws
                    if progress['current'] % 10 == 0:
                        _print_progress(progress['current'], progress['total'], path)
                    # do not print per-file collaboration info during scan
    

    # Ensure final progress bar is shown at 100%
    _print_progress(progress['current'], progress['total'], path)
    
    # Display skipped files summary before final statistics
    if progress.get('skipped', 0) > 0:
        _display_skipped_files_summary(progress.get('skipped_files', []))

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
    
    # Determine and display collaboration status
    collab_status = _determine_project_collaboration(path)
    print(f"\nProject Type: {collab_status}")
    # Optionally persist scan results to the database
    if save_to_db:
        # Detect project-level metadata and persist with the scan
        try:
            langs_res, langs_out, langs_err = _run_with_progress(
                detect_languages_and_frameworks, args=(path,),  total_steps=40
            )
            langs = langs_res.get('languages', []) if langs_res else []
        except Exception:
            langs = []

        try:
            skills_res, skills_out, skills_err = _run_with_progress(
                detect_skills, args=(path,),  total_steps=40
            )
            skills = skills_res.get('skills', []) if skills_res else []
        except Exception:
            skills = []
            skills_res = None

        tech_summary = {}
        if skills_res:
            tech_summary = {
                "languages": skills_res.get("languages", []),
                "frameworks": skills_res.get("frameworks", []),
                "high_confidence_languages": skills_res.get("high_confidence_languages", []),
                "medium_confidence_languages": skills_res.get("medium_confidence_languages", []),
                "low_confidence_languages": skills_res.get("low_confidence_languages", []),
                "high_confidence_frameworks": skills_res.get("high_confidence_frameworks", []),
                "medium_confidence_frameworks": skills_res.get("medium_confidence_frameworks", []),
                "low_confidence_frameworks": skills_res.get("low_confidence_frameworks", []),
            }

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

        # Check for multiple project roots (git repos + non-git project folders)
        repo_roots = _find_all_project_roots(path)

        try:
            if repo_roots and len(repo_roots) > 1:
                # Multiple repos/projects detected - save each separately
                print("\n=== Saving Projects to Database ===")
                _persist_multi_repo_scans(
                    path,
                    files_found,
                    repo_roots,
                    file_metadata=file_meta,
                    show_progress=True,
                    generate_llm_summary=generate_llm_summary,
                )
            else:
                # Single repo or no repo - save as before
                project_name = os.path.basename(os.path.abspath(path))
                metrics = analyze_repo_path(path) if analyze_repo is not None else None
                contributors = _contributors_from_metrics(metrics)
                if not contributors and (not repo_roots):
                    contributors = _prompt_manual_contributors(project_name) or None
                if contributors and (not repo_roots):
                    owner_val = _format_owner_from_names(contributors)
                    for meta in file_meta.values():
                        if isinstance(meta, dict):
                            meta['owner'] = owner_val
                project_created_at, project_repo_url = _get_repo_info(path)
                
                summary_text = None
                summary_input_hash = None
                summary_model = None
                summary_updated_at = None
                if generate_llm_summary:
                    try:
                        print(f"    [-] LLM summary: generating for {project_name}...")
                        summary_text, summary_input_hash, summary_model, _ = get_or_generate_summary(
                            project_name=project_name,
                            project_root=path,
                            files_found=files_found,
                            languages=tech_summary.get("languages", []),
                            frameworks=tech_summary.get("frameworks", []),
                            skills=skills,
                        )
                        if summary_text:
                            summary_updated_at = summary_timestamp()
                    except Exception:
                        summary_text = None

                _persist_scan(
                    path,
                    files_found,
                    project=project_name,
                    notes=None,
                    file_metadata=file_meta,
                    detected_languages=langs,
                    detected_skills=skills,
                    contributors=contributors,
                    project_created_at=project_created_at,
                    project_repo_url=project_repo_url,
                    project_thumbnail_path=project_thumbnail_path,
                    git_metrics=metrics,
                    tech_summary=tech_summary,
                    summary_text=summary_text,
                    summary_input_hash=summary_input_hash,
                    summary_model=summary_model,
                    summary_updated_at=summary_updated_at,
                )
        except sqlite3.OperationalError:
            # Try initializing DB and retry once
            try:
                init_db()
                if repo_roots and len(repo_roots) > 1:
                    print("\n=== Saving Projects to Database ===")
                    _persist_multi_repo_scans(path, files_found, repo_roots, file_metadata=file_meta,
                                             generate_llm_summary=generate_llm_summary)
                else:
                    project_name = os.path.basename(os.path.abspath(path))
                    _persist_scan(
                        path,
                        files_found,
                        project=project_name,
                        notes=None,
                        file_metadata=file_meta,
                        detected_languages=langs,
                        detected_skills=skills,
                        project_thumbnail_path=project_thumbnail_path,
                        git_metrics=metrics if 'metrics' in locals() else None,
                        tech_summary=tech_summary if 'tech_summary' in locals() else None,
                    )
            except Exception:
                print("Warning: failed to persist scan results to database.")
    return files_found

def run_headless_scan(
    path: str,
    *,
    recursive: bool = True,
    file_type: str = None,
    save_to_db: bool = True,
    zip_extract_dir: str = None,
    generate_llm_summary: bool = False,
):
    """
    Headless, programmatic scan entrypoint.

    This function performs the exact same scan as scan.py's
    interactive/CLI path, but without prompts, menus, or config.

    Intended for internal callers (e.g. resume regeneration).
    """

    return list_files_in_directory(
        path,
        recursive=recursive,
        file_type=file_type,
        show_collaboration=False,
        save_to_db=save_to_db,
        zip_extract_dir=zip_extract_dir,
        generate_llm_summary=generate_llm_summary,
    )



def run_with_saved_settings(
    directory=None,
    recursive_choice=None,
    file_type=None,
    show_collaboration=None,
    show_contribution_metrics=None,
    show_contribution_summary=None,
    save=False,
    save_to_db=False,
    thumbnail_source=None,
    generate_llm_summary=False,
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

    scan_path_input = final.get("directory")
    zip_extract_ctx = None
    zip_extract_path = None
    if scan_path_input and os.path.isfile(scan_path_input) and scan_path_input.lower().endswith('.zip'):
        zip_extract_ctx = tempfile.TemporaryDirectory()
        zip_extract_path = zip_extract_ctx.name
    project_thumbnail_path = None
    if save_to_db and thumbnail_source and scan_path_input and not zip_extract_path:
        if not os.path.isfile(thumbnail_source):
            print("Warning: thumbnail path does not point to a file; skipping.")
        elif not is_image_file(thumbnail_source):
            print("Warning: unsupported thumbnail type; skipping.")
        else:
            project_thumbnail_path = thumbnail_source

    # Run scan
    try:
        list_files_in_directory(
            final["directory"],
            recursive=final["recursive_choice"],
            file_type=final["file_type"],
            show_collaboration=final.get("show_collaboration", False),
            save_to_db=save_to_db,
            zip_extract_dir=zip_extract_path,
            project_thumbnail_path=project_thumbnail_path,
            generate_llm_summary=generate_llm_summary,
        )

        scan_target = _resolve_extracted_root(zip_extract_path) if zip_extract_path else scan_path_input

        # Detect multiple projects/repos in the scan target
        repo_roots = _find_all_git_roots(scan_target)
        if not repo_roots:
            candidate_roots = _find_candidate_project_roots(scan_target)
            if len(candidate_roots) > 1:
                repo_roots = candidate_roots
        
        # After scan, run language detection and then summarize detected skills
        if repo_roots and len(repo_roots) > 1:
            # Multiple projects detected - show detection results per project
            print("\n=== Detecting Languages and Skills Per Project ===")
            
            for i, repo_root in enumerate(repo_roots, 1):
                project_name = os.path.basename(os.path.abspath(repo_root))
                
                print(f"\n--- PROJECT {i}: {project_name} ---")
                
                # Detect languages for this project
                langs_res, langs_out, langs_err = _run_with_progress(
                    detect_languages_and_frameworks, args=(repo_root,), total_steps=40
                )
                langs_summary = langs_res or {}

                if langs_summary.get("languages"):
                    print("Languages Detected:")
                    if langs_summary.get("high_confidence"):
                        print("  High confidence:", ", ".join(langs_summary.get("high_confidence")))
                    if langs_summary.get("medium_confidence"):
                        print("  Medium confidence:", ", ".join(langs_summary.get("medium_confidence")))
                    if langs_summary.get("low_confidence"):
                        print("  Low confidence:", ", ".join(langs_summary.get("low_confidence")))
                    if langs_summary.get("frameworks"):
                        print("  Frameworks:", ", ".join(langs_summary.get("frameworks")))
                else:
                    print("No languages detected.")

                # Detect skills for this project
                skills_res, skills_out, skills_err = _run_with_progress(
                    detect_skills, args=(repo_root,), total_steps=40
                )
                skills_summary = skills_res or {}
                
                if skills_summary.get("skills"):
                    print("Skills Detected:", ", ".join(skills_summary.get("skills")))
                else:
                    print("No significant skills detected.")
        else:
            # Single project - detect as before
            print("\n=== Detecting Languages ===")
            langs_res, langs_out, langs_err = _run_with_progress(
                detect_languages_and_frameworks, args=(scan_target,),  total_steps=40
            )
            langs_summary = langs_res or {}
            if langs_summary.get("languages"):
                print("\n=== Detected Languages Summary ===")
                if langs_summary.get("high_confidence"):
                    print("High confidence:", ", ".join(langs_summary.get("high_confidence")))
                if langs_summary.get("medium_confidence"):
                    print("Medium confidence:", ", ".join(langs_summary.get("medium_confidence")))
                if langs_summary.get("low_confidence"):
                    print("Low confidence:", ", ".join(langs_summary.get("low_confidence")))
                if langs_summary.get("frameworks"):
                    print("Frameworks:", ", ".join(langs_summary.get("frameworks")))
            else:
                print("\nNo languages detected.")

            print("\n=== Detecting Skills ===")
            skills_res, skills_out, skills_err = _run_with_progress(
                detect_skills, args=(scan_target,),  total_steps=40
            )
            skills_summary = skills_res or {}

            
            if skills_summary.get("skills"):
                print("\n=== Detected Skills Summary ===")
                print(", ".join(skills_summary.get("skills")))
            else:
                print("\nNo significant skills detected.")

        # Then show contribution metrics if requested
        if final.get("show_contribution_metrics"):
            try:
                print("\n=== Contribution Metrics ===")
                metrics = analyze_repo_path(scan_target)
                if metrics and 'pretty_print_metrics' in globals():
                    if isinstance(metrics, list):
                        for m in metrics:
                            print()
                            pretty_print_metrics(m)
                    else:
                        pretty_print_metrics(metrics)
            except Exception as e:
                print(f"Error analyzing contribution metrics: {e}")

        # Show contribution summary if requested
        if final.get("show_contribution_summary"):
            summarize_project_contributions(scan_target)
    finally:
        if zip_extract_ctx is not None:
            zip_extract_ctx.cleanup()


# =============================================================================
# PER-PROJECT SCAN HELPERS [used by scan_with_clean_output()]
# =============================================================================

def _scan_single_project_phases(project_root: str, progress: ScanProgress) -> dict:
    """Run language/skill/contributor detection for a single project root.

    Returns dict with detection results for CLI display and DB persistence.
    """
    # Phase: Detecting Languages & Frameworks
    progress.header("Detecting Languages & Frameworks")
    langs_res, _, _ = _run_with_progress(
        detect_languages_and_frameworks, args=(project_root,), total_steps=25
    )
    langs_summary = langs_res or {}

    high_conf_langs = langs_summary.get('high_confidence', [])
    languages_all = langs_summary.get('languages', [])
    high_conf_frameworks = langs_summary.get('high_confidence_frameworks', [])
    frameworks_all = langs_summary.get('frameworks', [])

    if high_conf_langs:
        progress.item(f"Languages: {', '.join(high_conf_langs[:5])}")
    elif languages_all:
        progress.item(f"Languages: {', '.join(languages_all[:3])} (low confidence)")
    else:
        progress.item("Languages: None detected")
    if high_conf_frameworks:
        progress.item(f"Frameworks: {', '.join(high_conf_frameworks[:5])}")
    elif frameworks_all:
        progress.item(f"Frameworks: {', '.join(frameworks_all[:3])} (low confidence)")

    # Phase: Detecting Skills
    progress.header("Detecting Skills")
    skills_res, _, _ = _run_with_progress(
        detect_skills, args=(project_root,), total_steps=25
    )
    skills_summary = skills_res or {}
    skills = skills_summary.get('skills', [])
    if skills:
        progress.item(", ".join(skills[:5]))
    else:
        progress.item("None detected")

    # Phase: Analyzing Project
    progress.header("Analyzing Project")
    metrics = None
    contributors = []
    collab_status = "Individual"

    try:
        contrib_data = identify_contributions(project_root, write_output=False)
        if contrib_data:
            if contrib_data.get('type') == 'multi_git':
                all_contribs = set()
                for repo in contrib_data.get('repos', []):
                    all_contribs.update(repo.get('contributions', {}).keys())
                contributors = list(all_contribs)
            elif 'contributions' in contrib_data:
                contributors = list(contrib_data['contributions'].keys())

        if analyze_repo is not None:
            metrics = analyze_repo_path(project_root)

        collab_status = _determine_project_collaboration(project_root)
    except Exception:
        pass

    # Prompt manual contributor assignment for non-git projects
    has_real_contributors = contributors and contributors != ['Unknown']
    if not has_real_contributors and _find_git_root(project_root) is None:
        manual = _prompt_manual_contributors(os.path.basename(os.path.abspath(project_root)))
        if manual:
            contributors = manual

    for i in range(25):
        progress.progress(i + 1, 25)
        time.sleep(0.02)

    if contributors:
        progress.item(f"Contributors: {len(contributors)} found")
    else:
        progress.item("Contributors: None detected")
    progress.item(f"Project Type: {collab_status}")

    return {
        'langs_res': langs_res,
        'skills_res': skills_res,
        'high_conf_langs': high_conf_langs,
        'languages_all': languages_all,
        'high_conf_frameworks': high_conf_frameworks,
        'frameworks_all': frameworks_all,
        'skills': skills,
        'contributors': contributors,
        'collab_status': collab_status,
        'metrics': metrics,
    }

# Persist a single project's scan results to the database
def _persist_single_project(repo_root: str, project_name: str, files_for_repo: list, proj_result: dict, file_meta: dict, generate_llm_summary: bool, project_thumbnail_path: str = None):
    
    skills_res = proj_result.get('skills_res')
    tech_summary = {}
    if skills_res:
        tech_summary = {
            "languages": skills_res.get("languages", []),
            "frameworks": skills_res.get("frameworks", []),
            "high_confidence_languages": skills_res.get("high_confidence_languages", []),
            "medium_confidence_languages": skills_res.get("medium_confidence_languages", []),
            "low_confidence_languages": skills_res.get("low_confidence_languages", []),
            "high_confidence_frameworks": skills_res.get("high_confidence_frameworks", []),
            "medium_confidence_frameworks": skills_res.get("medium_confidence_frameworks", []),
            "low_confidence_frameworks": skills_res.get("low_confidence_frameworks", []),
        }

    project_created_at, project_repo_url = _get_repo_info(repo_root)

    summary_text = summary_input_hash = summary_model = summary_updated_at = None
    if generate_llm_summary:
        try:
            print(f"\nGenerating LLM Summary")
            print("-" * 20)
            print(f"    [-] Generating summary for {project_name}...")
            summary_text, summary_input_hash, summary_model, _ = get_or_generate_summary(
                project_name=project_name,
                project_root=repo_root,
                files_found=files_for_repo,
                languages=tech_summary.get("languages", []),
                frameworks=tech_summary.get("frameworks", []),
                skills=proj_result['skills'],
            )
            if summary_text:
                summary_updated_at = summary_timestamp()
        except Exception:
            summary_text = None

    try:
        _persist_scan(
            repo_root, files_for_repo, project=project_name, notes=None,
            file_metadata=file_meta,
            detected_languages=proj_result['languages_all'],
            detected_skills=proj_result['skills'],
            contributors=proj_result['contributors'],
            project_created_at=project_created_at,
            project_repo_url=project_repo_url,
            project_thumbnail_path=project_thumbnail_path,
            git_metrics=proj_result['metrics'],
            tech_summary=tech_summary,
            summary_text=summary_text, summary_input_hash=summary_input_hash,
            summary_model=summary_model, summary_updated_at=summary_updated_at,
        )
    except Exception:
        init_db()
        _persist_scan(repo_root, files_for_repo, project=project_name)


# =============================================================================
# CLEAN SCAN ORCHESTRATOR (New unified entry point)
# =============================================================================

def scan_with_clean_output(
    directory: str,
    recursive: bool = True,
    file_type: str = None,
    save_to_db: bool = True,
    thumbnail_source: str = None,
    generate_llm_summary: bool = False,
) -> dict:
    
    # Unified scan entry point with clean CLI output (returns dict with scan results)
    progress = get_scan_progress(reset=True)

    if not directory:
        print("Error: No directory provided.")
        return {'success': False, 'error': 'No directory provided'}

    # Handle zip files
    zip_extract_ctx = None
    zip_extract_path = None
    if os.path.isfile(directory) and directory.lower().endswith('.zip'):
        zip_extract_ctx = tempfile.TemporaryDirectory()
        zip_extract_path = zip_extract_ctx.name

    # Validate thumbnail
    project_thumbnail_path = None
    if save_to_db and thumbnail_source and not zip_extract_path:
        if os.path.isfile(thumbnail_source) and is_image_file(thumbnail_source):
            project_thumbnail_path = thumbnail_source

    scan_target = directory
    project_name = os.path.basename(os.path.abspath(directory))

    try:
        # PHASE 1: Scanning Files
        progress.header("Scanning Files")

        # Count files for progress display
        if zip_extract_path:
            # Extract zip contents first
            with zipfile.ZipFile(directory) as zf:
                zf.extractall(zip_extract_path)
            scan_target = _resolve_extracted_root(zip_extract_path)

        # Collect files with progress bar
        total_to_scan = sum(1 for r, _, fs in os.walk(scan_target) for f in fs if not _is_macos_junk(f) and is_valid_format(f) and (file_type is None or f.lower().endswith(file_type.lower())))
        files_found, skipped_count, scan_count = [], 0, 0
        for root, dirs, files in os.walk(scan_target):
            dirs[:] = [d for d in dirs if d != '__MACOSX']
            for file in files:
                if _is_macos_junk(file):
                    continue
                if not is_valid_format(file):
                    skipped_count += 1
                    continue
                if file_type is None or file.lower().endswith(file_type.lower()):
                    full_path = os.path.join(root, file)
                    size = os.path.getsize(full_path) if os.path.exists(full_path) else None
                    mtime = os.path.getmtime(full_path) if os.path.exists(full_path) else None
                    files_found.append((full_path, size, mtime))
                    scan_count += 1
                    progress.progress(scan_count, total_to_scan)
        progress.item(f"{len(files_found)} files found, {skipped_count} skipped")

        progress.store('files_found', len(files_found))
        progress.store('files_skipped', skipped_count)

        if not files_found:
            print("\nNo files found matching your criteria.")
            return {'success': False, 'error': 'No files found'}

        # Detect project roots early so we can branch to either the single or multi-project path
        repo_roots = _find_all_project_roots(scan_target)
        is_multi = repo_roots and len(repo_roots) > 1

        if is_multi:
            progress.item(f"Multiple projects detected ({len(repo_roots)})! Scan times may vary.")

        # Build file metadata shared by single and multi-project paths
        file_meta = {}
        for item in files_found:
            display = item[0] if isinstance(item, tuple) else item
            owner = get_collaboration_info(display) if os.path.exists(display) else None
            _, ext = os.path.splitext(display)
            lang = LANGUAGE_MAP.get(ext.lower()) if ext else None
            file_meta[display] = {'owner': owner, 'language': lang}

        if not is_multi:
            # =================================================================
            # SINGLE PROJECT PATH
            # =================================================================
            result_data = _scan_single_project_phases(scan_target, progress)

            # Store results for progress.complete() summary
            progress.store('languages', result_data['high_conf_langs'] or result_data['languages_all'])
            progress.store('frameworks', result_data['high_conf_frameworks'] or result_data['frameworks_all'])
            progress.store('skills', result_data['skills'])
            progress.store('contributors', result_data['contributors'])
            progress.store('project_type', result_data['collab_status'])

            if save_to_db:
                _persist_single_project(
                    scan_target, project_name, files_found,
                    result_data, file_meta, generate_llm_summary,
                    project_thumbnail_path=project_thumbnail_path,
                )

            output_dir = os.path.join("output", project_name)

            # Generate TXT/JSON summary
            if output_project_info is not None:
                try:
                    skills_res = result_data.get('skills_res') or {}
                    contrib_data = identify_contributions(scan_target, write_output=False)
                    proj_info = {
                        "project_name": project_name,
                        "project_path": os.path.abspath(scan_target),
                        "detected_type": "coding_project",
                        "languages": skills_res.get("languages", []),
                        "frameworks": skills_res.get("frameworks", []),
                        "skills": skills_res.get("skills", []),
                        "high_confidence_languages": skills_res.get("high_confidence_languages", []),
                        "medium_confidence_languages": skills_res.get("medium_confidence_languages", []),
                        "low_confidence_languages": skills_res.get("low_confidence_languages", []),
                        "high_confidence_frameworks": skills_res.get("high_confidence_frameworks", []),
                        "medium_confidence_frameworks": skills_res.get("medium_confidence_frameworks", []),
                        "low_confidence_frameworks": skills_res.get("low_confidence_frameworks", []),
                        "contributions": contrib_data,
                        "git_metrics": result_data.get('metrics'),
                        "generated_at": datetime.now().isoformat(timespec="seconds"),
                    }
                    os.makedirs(output_dir, exist_ok=True)
                    output_project_info(proj_info, output_dir=output_dir, quiet=True)
                except Exception:
                    pass

            progress.complete(project_name, output_dir)

            return {
                'success': True,
                'is_multi_project': False,
                'project_name': project_name,
                'project_names': [project_name],
                'output_dir': output_dir,
                'files_found': len(files_found),
                'languages': result_data['high_conf_langs'] or result_data['languages_all'],
                'frameworks': result_data['high_conf_frameworks'] or result_data['frameworks_all'],
                'skills': result_data['skills'],
                'contributors': result_data['contributors'],
                'project_type': result_data['collab_status'],
            }

        else:
            # =================================================================
            # MULTI-PROJECT PATH
            # =================================================================

            # Map files to their project roots
            repo_file_map = _map_files_to_repos(files_found, repo_roots)

            detected_project_names = []

            for idx, repo_root in enumerate(repo_roots):
                proj_name = os.path.basename(os.path.abspath(repo_root))
                files_for_repo = repo_file_map.get(repo_root, [])

                # Print project banner
                print(f"\n{'=' * 50}")
                print(f"  Project {idx + 1}/{len(repo_roots)}: {proj_name}")
                print(f"{'=' * 50}")
                progress.item(f"{len(files_for_repo)} files in this project")

                # Run language/skill/contributor detection for this project
                proj_result = _scan_single_project_phases(repo_root, progress)

                # Update file ownership for non-git projects with manual contributors
                if proj_result['contributors'] and _find_git_root(repo_root) is None:
                    owner_val = _format_owner_from_names(proj_result['contributors'])
                    for f_item in files_for_repo:
                        f_display = f_item[0] if isinstance(f_item, tuple) else f_item
                        if f_display in file_meta and isinstance(file_meta[f_display], dict):
                            file_meta[f_display]['owner'] = owner_val

                detected_project_names.append(proj_name)

                # Save this project to DB
                if save_to_db:
                    _persist_single_project(
                        repo_root, proj_name, files_for_repo,
                        proj_result, file_meta, generate_llm_summary,
                    )
                    progress.item(f"Saved to database: {proj_name}")

                # Generate TXT/JSON summary
                if output_project_info is not None:
                    try:
                        skills_res = proj_result.get('skills_res') or {}
                        contrib_data = identify_contributions(repo_root, write_output=False)
                        proj_info = {
                            "project_name": proj_name,
                            "project_path": os.path.abspath(repo_root),
                            "detected_type": "coding_project",
                            "languages": skills_res.get("languages", []),
                            "frameworks": skills_res.get("frameworks", []),
                            "skills": skills_res.get("skills", []),
                            "high_confidence_languages": skills_res.get("high_confidence_languages", []),
                            "medium_confidence_languages": skills_res.get("medium_confidence_languages", []),
                            "low_confidence_languages": skills_res.get("low_confidence_languages", []),
                            "high_confidence_frameworks": skills_res.get("high_confidence_frameworks", []),
                            "medium_confidence_frameworks": skills_res.get("medium_confidence_frameworks", []),
                            "low_confidence_frameworks": skills_res.get("low_confidence_frameworks", []),
                            "contributions": contrib_data,
                            "git_metrics": proj_result.get('metrics'),
                            "generated_at": datetime.now().isoformat(timespec="seconds"),
                        }
                        proj_output_dir = os.path.join("output", proj_name)
                        os.makedirs(proj_output_dir, exist_ok=True)
                        output_project_info(proj_info, output_dir=proj_output_dir, quiet=True)
                        progress.item(f"Summary files written to output/{proj_name}/")
                    except Exception:
                        pass

                # Prompt before next project (skip after the last one)
                if idx < len(repo_roots) - 1:
                    next_name = os.path.basename(os.path.abspath(repo_roots[idx + 1]))
                    if not ask_yes_no(f"\nReady to proceed with next project? ({next_name}) (y/n): ", default=True):
                        progress.item("Remaining projects skipped by user.")
                        break

            # Print overall completion summary
            progress.header("All Scans Complete!")
            progress.item(f"{len(detected_project_names)} of {len(repo_roots)} projects scanned")
            for pn in detected_project_names:
                progress.item(pn)

            return {
                'success': True,
                'is_multi_project': True,
                'project_name': project_name,
                'project_names': detected_project_names,
                'output_dir': None,
                'files_found': len(files_found),
                'languages': [],
                'frameworks': [],
                'skills': [],
                'contributors': [],
                'project_type': 'Multiple Projects',
            }

    finally:
        if zip_extract_ctx is not None:
            zip_extract_ctx.cleanup()

if __name__ == "__main__":
    print("Run 'python -m src.main_menu' to access scanning features.")
