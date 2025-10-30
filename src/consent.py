import sys
import os
from typing import Iterable, Optional
from config import save_config, load_config

# Print a short description of the types of data the scan will access. Can be customized via "items" parameter.
def describe_data_access(items: Optional[Iterable[str]] = None) -> None:
    if items is None:
        items = [
            "file names and directory structure",
            "file metadata (size, modification time)",
            "file contents when opened for scanning/parsing"
        ]
    print("The scanner may access the following data on your machine:")
    for item in items:
        print(f" - {item}")
    print()

# Prompt the user for a yes/no answer. Returns True for yes, False for no.
def ask_yes_no(prompt: str, default: Optional[bool] = None) -> bool:
    # prompt: text to present to the user (should include (y/n) suggestion).
    # default: if provided and user enters empty input, this value is returned.
    # If running in non-interactive mode (e.g. inside CI or docker tests) return the default
    # or False to avoid blocking on input(). The environment variable SCANNER_NONINTERACTIVE
    # can be set to '1' or 'true' to enable this behavior.
    if os.environ.get('SCANNER_NONINTERACTIVE', '').lower() in ('1', 'true'):
        return default if default is not None else False
    while True:
        resp = input(prompt).strip().lower()
        if resp == "" and default is not None:
            return default
        if resp in ("y", "yes"):
            return True
        if resp in ("n", "no"):
            return False
        print("Please answer 'y' or 'n'.")

# Describes what data will be accessed and asks for user consent, optionally saving their consent preferences.
def ask_for_data_consent(config_path: Optional[str] = None) -> bool:
    # Display all possible information we may access during a scan.
    describe_data_access()
    # Prompt user for data access consent.
    consent = ask_yes_no("Do you consent to the scanner accessing the data listed above? (y/n): ")

    # Ask whether user wants to save this preference in the config for future runs.
    save_pref = ask_yes_no("Save this preference for future scans? (y/n): ", default=False)
    if save_pref:
        # Save the user's preference using config.save_config().
        save_config({"data_consent": consent}, path=config_path)
        print("Preference saved.")
    else:
        print("Preference not saved.")

    # Returns True if consent granted, False otherwise.
    return consent