import sys
import os
from typing import Iterable, Optional
from config import save_config, load_config

# Print a short description of the types of data the scan will access. Can be customized via "items" parameter.
def describe_data_access(items: Optional[Iterable[str]] = None) -> None:
    if items is None:
        items = [
            "FILE SYSTEM ACCESS:",
            "  - File names, directory names, and complete directory structure",
            "  - Full absolute file paths (stored in local database)",
            "  - File metadata: sizes, modification times, creation times",
            "  - Complete file contents for code analysis (used during language/framework/skill detection)",
            "  - Any content from files stored in zipped (.zip) folders within a scanned directory",
            "",
            "GIT REPOSITORY DATA (if applicable):",
            "  - Repository remote URL",
            "  - All commit author names (No email addresses are stored)",
            "  - Commit counts, dates, and file-level contribution statistics",
            "  - Lines added/removed per author and per file",
            "  - Repository creation date and activity timelines",
            "  - File collaboration patterns (individual vs collaborative ownership)",
            "",
            "LOCAL DATA STORAGE:",
            "  - All scan results are stored in unencrypted SQLite database (file_data.db)",
            "  - User preferences are written to a file in a hidden folder in the user's home directory (~/.mda/config.json)",
            "  - Generated reports in output/ and resumes/ directories (JSON, TXT, Markdown)",
            "",
            "OPTIONAL LOCAL LLM SUMMARY (ONLY IF ENABLED):",
            "  - Uses a local Ollama model (llama3.2:3b) to summarize the scanned project",
            "  - Reads project metadata and README content (if present) to generate a short summary",
            "  - No data is sent to external services",
            "",
            "WHAT WE DO NOT ACCESS:",
            "  - No network requests or external API calls",
            "  - No data transmission to external services",
            "  - No access to any files outside of user-provided scan directories",
        ]
    print("The scanner can access the following data on your local machine:")
    print()
    for item in items:
        print(f"{item}")
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

    llm_consent = False
    if consent:
        llm_consent = ask_yes_no(
            "Allow local LLM project summary generation (uses Ollama, reads README if present)? (y/n): ",
            default=False
        )

    # Ask whether user wants to save this preference in the config for future runs.
    save_pref = ask_yes_no("Save this preference for future scans? (y/n): ")
    if save_pref:
        # Save the user's preference using config.save_config().
        save_config({"data_consent": consent, "llm_summary_consent": llm_consent}, path=config_path)
        print("Preference saved.")
    else:
        print("Preference not saved.")

    # Returns True if consent granted, False otherwise.
    return consent
