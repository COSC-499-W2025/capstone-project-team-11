import os
import json

# Default scan settings used when no config file is present or values are missing
DEFAULTS = {
    "directory": None,
    "recursive_choice": False,
    "file_type": None,
    "data_consent": None
}

# Guards against invalid file_type inputs and normalizes/formats them properly
def normalize_file_type(file_type):
    if not isinstance(file_type, str):
        return None
    # Remove leading/trailing whitespace which can cause mismatches
    file_type = file_type.strip()
    if not file_type:
        return None
    # Ensure a leading dot for consistent comparisons elsewhere in the app
    if not file_type.startswith('.'):
        file_type = '.' + file_type
    return file_type.lower()

# Generates a path to a hidden .mda (Mining Digital Artifacts) directory and config.json file in the user's home directory (directory/file are not created here)
def config_path():
    home = os.path.expanduser("~")
    return os.path.join(home, ".mda", "config.json")

# Handles logic around loading a config file from the user's local machine
def load_config(path=None):
    config_file = path or config_path()
    # If the file does not exist, return default settings to ensure predictable behavior 
    if not os.path.exists(config_file):
        return DEFAULTS.copy()
    
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return DEFAULTS.copy()
    
    # Start from the default settings template, then overwrite using values from the local config file
    config = DEFAULTS.copy()
    config.update(data or {})
    # Normalize the file_type value for consistent comparisons elsewhere.
    config["file_type"] = normalize_file_type(config.get("file_type"))
    return config

# Saves the provided scan settings to a local JSON file on the user's machine
def save_config(data, path=None):
    # Determine config file path
    config_file = path or config_path()
    config_dir = os.path.dirname(config_file)
    # Ensure the directory exists so the file can be written to
    os.makedirs(config_dir, exist_ok=True)
    
    # Load existing config to preserve any settings not being updated now
    existing = load_config(config_file)

    # Start from the existing saved settings, then overwrite using new values
    to_save = existing.copy()
    to_save.update(data or {})

    # Normalize file_type before saving
    to_save["file_type"] = normalize_file_type(to_save.get("file_type"))

    # Write settings to local JSON config file
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(to_save, f, indent=2)

    # On POSIX systems, restrict file permissions to owner read/write only
    try:
        if os.name == 'posix':
            os.chmod(config_file, 0o600)
    except Exception:
        pass

# Merges runtime arguments and saved config onto default scan settings
def merge_settings(args_dict, config_dict):
    result = DEFAULTS.copy()
    # Overwrite default settings with saved config values first
    result.update(config_dict or {})
    # Then apply explicit arguments, but only when value is not empty/None
    for key, value in (args_dict or {}).items():
        if value is not None:
            result[key] = value

    # Ensure the chosen file type to scan is in proper format
    result["file_type"] = normalize_file_type(result.get("file_type"))
    return result