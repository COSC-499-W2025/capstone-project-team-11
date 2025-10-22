import os
import sys
import time
import zipfile
import io
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from config import load_config, save_config, merge_settings

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
    # Ignore Finder metadata and resource fork directory produced on macOS
    if base == '.DS_Store':
        return True
    # For zip entries or directories, any path starting with __MACOSX
    if name.split('/')[0] == '__MACOSX':
        return True
    return False

def _scan_zip(zf: zipfile.ZipFile, display_prefix: str, recursive: bool, file_type: str, files_found: list):
    """Internal: scan an already-open ZipFile and collect/print entries.
    - display_prefix: the accumulated path like "/path/to.zip" or "/path/to.zip:inner.zip"
    - files_found: list of tuples (display_path, size, mtime)
    """
    for info in zf.infolist():
        # Skip directories
        if hasattr(info, 'is_dir') and info.is_dir():
            continue
        name = info.filename
        # Skip macOS junk files
        if _is_macos_junk(name):
            continue
        # Respect non-recursive by including only root-level entries (no '/')
        if not recursive and ('/' in name or name.endswith('/')):
            if '/' in name:
                continue
        # Record this file if it matches the filter (or no filter)
        display = f"{display_prefix}:{name}"
        if file_type is None or name.lower().endswith(file_type.lower()):
            files_found.append((display, info.file_size, _zip_mtime_to_epoch(info.date_time)))
            print(display)

        # If recursive and this entry itself is a .zip, descend into it
        if recursive and name.lower().endswith('.zip'):
            try:
                with zf.open(info) as nested_file:
                    nested_bytes = nested_file.read()
                with zipfile.ZipFile(io.BytesIO(nested_bytes)) as nested_zf:
                    _scan_zip(nested_zf, display, recursive, file_type, files_found)
            except zipfile.BadZipFile:
                # Ignore corrupt/unsupported nested zips
                pass

def list_files_in_zip(zip_path, recursive=False, file_type=None):
    """
    Prints file names inside a zip archive.
    If recursive=False, only top-level files (no '/') are listed.
    If file_type is provided (e.g. '.txt'), only files of that type are shown.
    """
    if not os.path.exists(zip_path) or not zipfile.is_zipfile(zip_path):
        print("Directory does not exist.")
        return

    print(f"\nScanning zip archive: {zip_path}")
    if file_type:
        print(f"Filtering by file type: {file_type}")
    print()

    files_found = []  # store (display_path, size, mtime)
    with zipfile.ZipFile(zip_path) as zf:
        _scan_zip(zf, zip_path, recursive, file_type, files_found)

    if not files_found:
        print("No files found matching your criteria.")
        return

    # Compute stats based on collected metadata
    largest = max(files_found, key=lambda t: t[1])
    smallest = min(files_found, key=lambda t: t[1])
    newest = max(files_found, key=lambda t: t[2])
    oldest = min(files_found, key=lambda t: t[2])

    print("\n=== File Statistics ===")
    print(f"Largest file: {largest[0]} ({largest[1]} bytes)")
    print(f"Smallest file: {smallest[0]} ({smallest[1]} bytes)")
    print(f"Most recently modified: {newest[0]} ({time.ctime(newest[2])})")
    print(f"Least recently modified: {oldest[0]} ({time.ctime(oldest[2])})")

def list_files_in_directory(path, recursive=False, file_type=None):
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
        return list_files_in_zip(path, recursive=recursive, file_type=file_type)

    if not os.path.exists(path) or not os.path.isdir(path):
        print("Directory does not exist.")
        return

    print(f"\nScanning directory: {path}")
    if file_type:
        print(f"Filtering by file type: {file_type}")
    print()
    
    files_found = []
    # Collect file paths
    if recursive:
        for root, dirs, files in os.walk(path):
            # Prune __MACOSX directories from traversal
            dirs[:] = [d for d in dirs if d != '__MACOSX']
            for file in files:
                if _is_macos_junk(file):
                    continue
                if file_type is None or file.lower().endswith(file_type.lower()):
                    full_path = os.path.join(root, file)
                    files_found.append(full_path)
                    print(full_path)
    # If user does not want to scan subdirectories
    else:
        for file in os.listdir(path):
            full_path = os.path.join(path, file)
            if os.path.isfile(full_path):
                if _is_macos_junk(file):
                    continue
                if file_type is None or file.lower().endswith(file_type.lower()):
                   files_found.append(full_path)
                   print(full_path)
    # If no files found
    if not files_found:
        print("No files found matching your criteria.")
        return

    # Calculate file stats
    largest = max(files_found, key=lambda f: os.path.getsize(f))
    smallest = min(files_found, key=lambda f: os.path.getsize(f))
    newest = max(files_found, key=lambda f: os.path.getmtime(f))
    oldest = min(files_found, key=lambda f: os.path.getmtime(f))

    # Print results
    print("\n=== File Statistics ===")
    print(f"Largest file: {largest} ({os.path.getsize(largest)} bytes)")
    print(f"Smallest file: {smallest} ({os.path.getsize(smallest)} bytes)")
    print(f"Most recently modified: {newest} ({time.ctime(os.path.getmtime(newest))})")
    print(f"Least recently modified: {oldest} ({time.ctime(os.path.getmtime(oldest))})")

# Use saved config as defaults, override with provided settings if given, optionally save the new settings back to config file.
def run_with_saved_settings(directory=None, recursive_choice=None, file_type=None, save=False, config_path=None):
    config = load_config(config_path)
    final = merge_settings({"directory": directory, "recursive_choice": recursive_choice, "file_type": file_type}, config)

    # Optionally save current settings for next time:
    if save:
        save_config(final, config_path)

    # Run the scan:
    list_files_in_directory(
        final["directory"],
        recursive=final["recursive_choice"],
        file_type=final["file_type"]
    )

if __name__ == "__main__":
    # Load current config
    current = load_config(None)
    # Ask the user if they would like to use the same settings from their last scan
    use_saved = input(
        "Would you like to use the settings from your most recent scan?\n"
        f"  Scanned Directory:      {current.get('directory') or '<none>'}\n"
        f"  Scan Nested Folders:    {current.get('recursive_choice')}\n"
        f"  Only Scan File Type:    {current.get('file_type') or '<all>'}\n"
        "Proceed with these settings? (y/n): "
    ).strip().lower() == 'y'

    if use_saved and current.get("directory"):
        # Run with saved settings
        run_with_saved_settings(directory=current.get("directory"), recursive_choice=current.get("recursive_choice"), file_type=current.get("file_type"), save=False)
    else:
        # Ask for new settings
        directory = input("Enter directory path or zip file path: ").strip()
        recursive_choice = input("Scan subdirectories too? (y/n): ").strip().lower() == 'y'
        file_type = input("Enter file type (e.g. .txt) or leave blank for all: ").strip()
        file_type = file_type if file_type else None

        # Ask if we should remember these settings for next time
        remember = input("Save these settings for next time? (y/n): ").strip().lower() == 'y'
        run_with_saved_settings(
            directory=directory,
            recursive_choice=recursive_choice,
            file_type=file_type,
            save=remember
        )

