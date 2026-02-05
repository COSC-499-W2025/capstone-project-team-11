import os
import json

# Default scan settings used when no config file is present or values are missing
DEFAULTS = {
    "directory": None,
    "recursive_choice": False,
    "file_type": None,
    "data_consent": False,
    "llm_summary_consent": False,
    "show_collaboration": False,
    "show_contribution_metrics": False,
    "show_contribution_summary": False
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
    # Save scan settings to a JSON config file
    config_file = path or config_path()
    config_dir = os.path.dirname(config_file)
    os.makedirs(config_dir, exist_ok=True)
    
    # Load existing config
    existing = load_config(config_file)
    
    # Create new config with explicit updates from data
    to_save = {}
    
    # First, copy all DEFAULTS keys
    for key in DEFAULTS:
        # If key exists in data (even if None), use that value
        if key in data:
            to_save[key] = data[key]
        # Otherwise use existing value, falling back to DEFAULTS
        else:
            to_save[key] = existing.get(key, DEFAULTS[key])
    
    # Only normalize file_type if it's a non-None string
    if isinstance(to_save.get("file_type"), str):
        to_save["file_type"] = normalize_file_type(to_save["file_type"])

    # Write to file
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(to_save, f, indent=2)

    # Set POSIX permissions if applicable
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
    # Then apply explicit arguments, including "None" values
    if args_dict:
        for key in result:
            if key in args_dict:
                result[key] = args_dict[key]

    # Ensure the chosen file type to scan is in proper format, but only if NOT "None"
    if result.get("file_type") is not None:
        result["file_type"] = normalize_file_type(result.get("file_type"))
    return result

# Check if the user's config.json contains only default values
# This helper function allows us to determine if we should prompt the user to reuse their previous scan settings
# If their config.json only contains default values, we skip the prompt since there's nothing useful to reuse
def is_default_config(config_dict):
    if not config_dict:
        return True
        
    # Compare all fields except data_consent against their default values
    # data_consent needs to be true (not its default value) in order to reach the scan prompt, so we ignore it here.
    scan_settings = ['directory', 'recursive_choice', 'file_type', 'show_collaboration']
    return all(config_dict.get(key) == DEFAULTS[key] for key in scan_settings)
