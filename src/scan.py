import os

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

    if recursive:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file_type is None or file.lower().endswith(file_type.lower()):
                    print(os.path.join(root, file))
    else:
        for file in os.listdir(path):
            full_path = os.path.join(path, file)
            if os.path.isfile(full_path):
                if file_type is None or file.lower().endswith(file_type.lower()):
                    print(full_path)

if __name__ == "__main__":
    directory = input("Enter directory path: ").strip()
    recursive_choice = input("Scan subdirectories too? (y/n): ").strip().lower() == 'y'
    file_type = input("Enter file type (e.g. .txt) or leave blank for all: ").strip()
    file_type = file_type if file_type else None
    list_files_in_directory(directory, recursive_choice, file_type)
