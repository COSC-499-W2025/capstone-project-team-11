import os
import sys
import time
import subprocess
import zipfile
import io
import tempfile
from detect_langs import detect_languages_and_frameworks

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from config import load_config, save_config, merge_settings, config_path as default_config_path
from consent import ask_for_data_consent


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
    """Internal: scan an already-open ZipFile and collect/print entries."""
    for info in zf.infolist():
        if hasattr(info, 'is_dir') and info.is_dir():
            continue
        name = info.filename
        if _is_macos_junk(name):
            continue
        if not recursive and ('/' in name or name.endswith('/')):
            if '/' in name:
                continue

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


def list_files_in_zip(zip_path, recursive=False, file_type=None, show_collaboration=False):
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

    if not files_found:
        print("No files found matching your criteria.")
        return

    largest = max(files_found, key=lambda t: t[1])
    smallest = min(files_found, key=lambda t: t[1])
    newest = max(files_found, key=lambda t: t[2])
    oldest = min(files_found, key=lambda t: t[2])

    print("\n=== File Statistics ===")
    print(f"Largest file: {largest[0]} ({largest[1]} bytes)")
    print(f"Smallest file: {smallest[0]} ({smallest[1]} bytes)")
    print(f"Most recently modified: {newest[0]} ({time.ctime(newest[2])})")
    print(f"Least recently modified: {oldest[0]} ({time.ctime(oldest[2])})")


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


def list_files_in_directory(path, recursive=False, file_type=None, show_collaboration=False):
    """Prints file names in the given directory, or inside a .zip file."""
    if not path:
        print("Directory does not exist.")
        return

    if os.path.isfile(path) and path.lower().endswith('.zip'):
        return list_files_in_zip(path, recursive=recursive, file_type=file_type, show_collaboration=show_collaboration)

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
                if file_type is None or file.lower().endswith(file_type.lower()):
                    full_path = os.path.join(root, file)
                    files_found.append(full_path)
                    print(full_path)
                    if show_collaboration:
                        print(f"  Collaboration: {get_collaboration_info(full_path)}")
    else:
        for file in os.listdir(path):
            full_path = os.path.join(path, file)
            if os.path.isfile(full_path):
                if _is_macos_junk(file):
                    continue
                if file_type is None or file.lower().endswith(file_type.lower()):
                    files_found.append(full_path)
                    print(full_path)
                    if show_collaboration:
                        print(f"  Collaboration: {get_collaboration_info(full_path)}")

    if not files_found:
        print("No files found matching your criteria.")
        return

    largest = max(files_found, key=lambda f: os.path.getsize(f))
    smallest = min(files_found, key=lambda f: os.path.getsize(f))
    newest = max(files_found, key=lambda f: os.path.getmtime(f))
    oldest = min(files_found, key=lambda f: os.path.getmtime(f))

    print("\n=== File Statistics ===")
    print(f"Largest file: {largest} ({os.path.getsize(largest)} bytes)")
    print(f"Smallest file: {smallest} ({os.path.getsize(smallest)} bytes)")
    print(f"Most recently modified: {newest} ({time.ctime(os.path.getmtime(newest))})")
    print(f"Least recently modified: {oldest} ({time.ctime(os.path.getmtime(oldest))})")


def run_with_saved_settings(directory=None, recursive_choice=None, file_type=None, show_collaboration=None, save=False, config_path=None):
    config = load_config(config_path)
    final = merge_settings(
        {
            "directory": directory,
            "recursive_choice": recursive_choice,
            "file_type": file_type,
            "show_collaboration": show_collaboration
        },
        config
    )

    if save:
        save_config(final, config_path)

    list_files_in_directory(
        final["directory"],
        recursive=final["recursive_choice"],
        file_type=final["file_type"],
        show_collaboration=final.get("show_collaboration", False),
    )


if __name__ == "__main__":
    current = load_config(None)
    if current.get("data_consent") is not True:
        consent = ask_for_data_consent(config_path=default_config_path())
        if not consent:
            print("Data access consent not granted, aborting application.")
            sys.exit(0)

    current = load_config(None)
    use_saved = input(
        "Would you like to use the settings from your most recent scan?\n"
        f"  Scanned Directory:      {current.get('directory') or '<none>'}\n"
        f"  Scan Nested Folders:    {current.get('recursive_choice')}\n"
        f"  Only Scan File Type:    {current.get('file_type') or '<all>'}\n"
        "Proceed with these settings? (y/n): "
    ).strip().lower() == 'y'

    if use_saved and current.get("directory"):
        run_with_saved_settings(
            directory=current.get("directory"),
            recursive_choice=current.get("recursive_choice"),
            file_type=current.get("file_type"),
            show_collaboration=current.get("show_collaboration"),
            save=False,
        )
    else:
        directory = input("Enter directory path or zip file path: ").strip()
        recursive_choice = input("Scan subdirectories too? (y/n): ").strip().lower() == 'y'
        file_type = input("Enter file type (e.g. .txt) or leave blank for all: ").strip()
        file_type = file_type if file_type else None

        remember = input("Save these settings for next time? (y/n): ").strip().lower() == 'y'
        show_collab = input("Show collaboration info? (y/n): ").strip().lower() == 'y'
        run_with_saved_settings(
            directory=directory,
            recursive_choice=recursive_choice,
            file_type=file_type,
            show_collaboration=show_collab,
            save=remember
        )
