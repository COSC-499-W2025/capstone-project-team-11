import os

# Default scan settings used when no config file is present or values are missing
DEFAULTS = {
    "directory": None,
    "recursive_choice": False,
    "file_type": None,
    "data_consent": False,
    "show_collaboration": False,
    "show_contribution_metrics": False,
    "show_contribution_summary": False,
    # LLM settings (opt-in)
    "llm_enabled": False,
    "llm_consent": False,
    "llm_consent_asked": False,
    "llm_provider": "ollama",
    "llm_model": "llama3.2:3b",
    "llm_base_url": "http://localhost:11434",
    "llm_api_key": None
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
    return os.path.join(home, ".mda", ".env")

# Handles logic around loading a config file from the user's local machine
def _parse_env_value(value):
    if value is None:
        return None
    v = str(value).strip()
    if v.lower() in ("true", "1", "yes", "y"):
        return True
    if v.lower() in ("false", "0", "no", "n"):
        return False
    if v == "":
        return None
    return v


def _format_env_value(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _read_env_file(path):
    if not path or not os.path.exists(path):
        return {}
    data = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw in f.readlines():
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                data[key.strip()] = _parse_env_value(val)
    except Exception:
        return {}
    return data


def _write_env_file(path, data):
    lines = []
    for key in sorted(data.keys()):
        val = _format_env_value(data[key])
        lines.append(f"{key}={val}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def load_config(path=None):
    config_file = path or config_path()
    # Start from defaults, then apply .env, then env vars.
    config = DEFAULTS.copy()

    env_file_data = _read_env_file(config_file)
    for key in DEFAULTS:
        env_key = f"MDA_{key.upper()}"
        if env_key in env_file_data:
            config[key] = env_file_data.get(env_key)

    for key in DEFAULTS:
        env_key = f"MDA_{key.upper()}"
        if env_key in os.environ:
            config[key] = _parse_env_value(os.environ.get(env_key))

    # Normalize the file_type value for consistent comparisons elsewhere.
    config["file_type"] = normalize_file_type(config.get("file_type"))
    return config

# Saves the provided scan settings to a local JSON file on the user's machine
def save_config(data, path=None):
    # Save scan settings to a .env config file
    config_file = path or config_path()
    config_dir = os.path.dirname(config_file)
    os.makedirs(config_dir, exist_ok=True)

    # Load existing config (from .env + env vars)
    existing = load_config(config_file)

    # Create new config with explicit updates from data
    to_save = {}

    for key in DEFAULTS:
        if key in data:
            to_save[key] = data[key]
        else:
            to_save[key] = existing.get(key, DEFAULTS[key])

    # Only normalize file_type if it's a non-None string
    if isinstance(to_save.get("file_type"), str):
        to_save["file_type"] = normalize_file_type(to_save["file_type"])

    env_out = {}
    for key in DEFAULTS:
        env_out[f"MDA_{key.upper()}"] = to_save.get(key)

    _write_env_file(config_file, env_out)

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
