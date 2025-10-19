import os
import json

DEFAULTS = {
    "directory": None,
    "recursive_choice": False,
    "file_type": None
}

def normalize_file_type(file_type):
    if not isinstance(file_type, str):
        return None
    file_type = file_type.strip()
    if not file_type:
        return None
    if not file_type.startswith('.'):
        file_type = '.' + file_type
    return file_type.lower()

def config_path():
    home = os.path.expanduser("~")
    return os.path.join(home, ".mda", "config.json")

def load_config(path=None):
    config_file = path or config_path()
    if not os.path.exists(config_file):
        return DEFAULTS.copy()
    
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return DEFAULTS.copy()
    
    config = DEFAULTS.copy()
    config.update(data or {})
    config["file_type"] = normalize_file_type(config.get("file_type"))
    return config

def save_config(data, path=None):
    config_file = path or config_path()
    config_dir = os.path.dirname(config_file)
    os.makedirs(config_dir, exist_ok=True)

    to_save = DEFAULTS.copy()
    to_save.update(data or {})
    to_save["file_type"] = normalize_file_type(to_save.get("file_type"))

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(to_save, f, indent=2)

    try:
        if os.name == 'posix':
            os.chmod(config_file, 0o600)
    except Exception:
        pass

def merge_settings(args_dict, config_dict):
    result = DEFAULTS.copy()
    result.update(config_dict or {})
    for key, value in (args_dict or {}).items():
        if value is not None:
            result[key] = value

    result["file_type"] = normalize_file_type(result.get("file_type"))
    return result