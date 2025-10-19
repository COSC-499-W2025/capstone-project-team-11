import os
import sys
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from config import load_config, save_config, merge_settings

def list_files_in_directory(path, recursive=False, file_type=None):
    """
    Prints file names in the given directory.
    If recursive=True, it scans subdirectories.
    If file_type is provided (e.g. '.txt'), only files of that type are shown.
    """
    if not os.path.exists(path):
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
            for file in files:
                if file_type is None or file.lower().endswith(file_type.lower()):
                    full_path = os.path.join(root, file)
                    files_found.append(full_path)
                    print(full_path)
    # If user does not want to scan subdirectories
    else:
        for file in os.listdir(path):
            full_path = os.path.join(path, file)
            if os.path.isfile(full_path):
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

def run_with_saved_settings(directory=None, recursive_choice=None, file_type=None, save=False, config_path=None):
    config = load_config(config_path)
    final = merge_settings({"directory": directory, "recursive_choice": recursive_choice, "file_type": file_type}, config)

    if save:
        save_config(final, config_path)

    list_files_in_directory(
        final["directory"],
        recursive=final["recursive_choice"],
        file_type=final["file_type"]
    )

if __name__ == "__main__":
    current = load_config(None)
    use_saved = input(
        "Would you like to use the settings from your most recent scan?\n"
        f"  Scanned Directory:      {current.get('directory') or '<none>'}\n"
        f"  Scan Nested Folders:    {current.get('recursive_choice')}\n"
        f"  Only Scan File Type:    {current.get('file_type') or '<all>'}\n"
        "Proceed with these settings? (y/n): "
    ).strip().lower() == 'y'

    if use_saved and current.get("directory"):
        run_with_saved_settings(directory=current.get("directory"), recursive_choice=current.get("recursive_choice"), file_type=current.get("file_type"), save=False)
    else:
        directory = input("Enter directory path: ").strip()
        recursive_choice = input("Scan subdirectories too? (y/n): ").strip().lower() == 'y'
        file_type = input("Enter file type (e.g. .txt) or leave blank for all: ").strip()
        file_type = file_type if file_type else None

        remember = input("Save these settings for next time? (y/n): ").strip().lower() == 'y'
        run_with_saved_settings(
            directory=directory,
            recursive_choice=recursive_choice,
            file_type=file_type,
            save=remember
        )
