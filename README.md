[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=20510454&assignment_repo_type=AssignmentRepo)

## Project Documentation

### System Architecture
The app combines an Electron and React frontend with a FastAPI(Python) backend to deliver a fast and visual local file scanning system. The frontend built with Vite and Zustand provides a clean interface for selecting directories, filtering results, and viewing interactive charts powered by Chart.js or ECharts.

The backend handles scanning, classification, and reporting through a REST API. It uses SQLite (via SQLModel) for storage, Libmagic for file type detection, and hashlib for hashing and duplicate detection. Reports are generated with Jinja2 and exported to PDF, HTML, or image formats using WeasyPrint and Playwright.

Everything is packaged into cross-platform installers using PyInstaller and electron-builder, with automated testing and performance validation ensuring a reliable desktop experience.

[View the System Architecture Diagram](https://github.com/COSC-499-W2025/capstone-project-team-11/blob/SystemArchitecture/SystemArchitecture.md)


---

### DFD Level 1
The Level 1 Data Flow Diagram illustrates how user interactions flow through the system’s main components from initiating a scan to exporting and viewing reports.

#### Key Components
- **User Interaction**: The user selects directories, preferences, initiate scans, and views or exports reports.
-  **API**: Central controller managing data exchange between the frontend, file system, and database.
-  **Metadata Scanning**: Extracts metadata from selected files and stores it locally.
-  **Database Processes**:
      - D1: Save scan preferences
      - D2: Store scan metadata
      - D3: Maintain scan history
      - D4: Save report drafts or exports
- **Report Generation**: Builds reports using file metadata and scan results.
- **Report Display and Export**: Reports are previewed in the dashboard, formatted into HTML, and exported to user-specified formats (PDF, PNG, etc.).
- **Notification Manager** : Handles system alerts for export failures, access errors, and data inconsistencies.

This diagram effectively captures how user actions trigger backend processes, how data is stored and retrieved, and how final reports and notifications are presented, ensuring clarity in both data movement and component responsibilities.

[View the Level 1 Data Flow Diagram](https://github.com/COSC-499-W2025/capstone-project-team-11/blob/dfd/docs/dfd/dfd1.jpg)



---


### Work Breakdown Structure 

This WBS outlines the major functional modules and implementation tasks for the project, covering everything from user consent to testing and documentation. It ensures that each system component from ethical data access to output generation is thoroughly planned, validated, and testable.

#### Main features of WBS
1. **User Consent & Ethical Access**: Focuses on ensuring ethical data handling and informed consent. The system displays privacy information, prompts for user approval, and logs responses for future use. If consent is denied, a fallback analysis model maintains functionality while respecting user choices.
2. **File Input & Validation**: Handles how files are uploaded and verified. The system supports zipped folders, validates file structure and compression, and extracts metadata such as filenames, extensions, and timestamps. It ensures proper data formatting before any analysis begins.
3. **Project Identification & Classification**: Separates and categorizes scanned content into distinct projects. It distinguishes between individual and collaborative work using metadata (e.g., git authorship) and detects programming languages, frameworks, and other coding attributes within each project.
4. **Contribution & Activity Analysis**: Analyzes how much each contributor participated in a project. This includes parsing commit histories and modification patterns, categorizing activities (coding, testing, documenting, etc.), and identifying key skills based on file types and content.
5. **Data Output & Storage**: Generates and stores project summaries. Metadata and metrics are combined into structured outputs (CSV/JSON) and stored in a database with CRUD operations. Users can retrieve or delete past insights and summaries while maintaining data consistency.
6. **Project Evaluation & Ranking**:Ranks and summarizes projects based on contribution metrics. It produces text-based summaries for portfolios or resumes and allows sorting of projects and skills chronologically by activity date.
7. **System Management & Testing**: Covers the quality assurance and maintenance side. Includes unit and integration testing across all modules, an error-handling and logging framework, and comprehensive documentation updates (schemas, WBS, DFDs, and user guides).

[View the Revised WBS](https://github.com/COSC-499-W2025/capstone-project-team-11/blob/main/docs/WBS%20CAPSTONE.webp)

---
### Src Folder
The src folder is where we will keep our source code for the backend organized by functionality. Its purpose is to group the modules that implement scanning, metadata extraction, database interaction, reporting, and API endpoints. So far we only have a basic scan setup in the file scan.py.

#### scan.py Breakdown:
The program lists files in a specified directory and can optionally:
- Recurse into subdirectories
- Filter by file type
  
After listing the matching files, it computes and displays:
- Largest file
- Smallest file
- Most recently modified file
- Oldest file
If no matching files are found, it notifies the user.

When run directly, it prompts for:
1. Directory path
2. Whether to scan subdirectories
3. File type filter (optional)

This feature is useful as a basic file system utility or a backend helper for metadata scanning, file statistics, or report generation.

[src folder](https://github.com/COSC-499-W2025/capstone-project-team-11/tree/main/src)

---

### Test Folder
The test folder is where we will test the functionality of the source code and is crucial for veryfying if it works and the robustness of our source code. So far we only have one test file scan_test.py for scan.py:

#### scan_test.py Breakdown:
This Python file is a unit test suite for the list_files_in_directory() function defined in scan.py. It uses Python’s built-in unittest framework to automatically verify that the directory scanning tool works correctly under various conditions.

The test class TestListFilesInDirectory:
- Sets up a temporary directory with sample files (.txt, .py, .jpg) and a subdirectory for testing.
- Cleans up by deleting the temporary directory after each test.
- Captures printed output from list_files_in_directory() using redirect_stdout for validation.

The tests check that:
1. Non-recursive scans only list files in the root directory.
2. Recursive scans include files from subdirectories.
3. File type filtering correctly restricts results (e.g., only .txt files).
4. Invalid paths print an appropriate error message.
5. File statistics (largest, smallest, newest, oldest) are correctly reported based on file size and modification time.

This ensures that the directory scanning utility behaves as expected in real-world scenarios, catches regressions, and provides confidence in file handling logic.

#### config.py Breakdown:
Manages simple persistent settings for the scanner: 
- Provides default scan settings and helper functions to read/write/normalize those settings:
- normalize_file_type() formats selected file types to be scanned. It does so by stripping white space around the String, ensuring it starts with a period (eg. ".txt"), and converting String to lowercase. (Essentially converts a submitted String, ex. " JSON " into ".json")
- config_path() returns the default config file location at the User's home directory (~/.mda/config.json) but does not create directories or files.
- load_config() reads/writes JSON config files from local storage (falling back to defalt settings on missing/invalid files)
- merge_settings() sets a precedence in prioritization of saved scan configurations: DEFAULTS < saved config < explicit args (arguments declared at the start of a new scan when not using saved settings)

config.py is useful as it handles all of the logic around saving/storing, locating, and reading/loading scan configuration files.

config_test.py Breakdown:
Unit test suite for config.py and its integration with scan.py using tempfile-based directories so tests are isolated and filesystem-safe. There are 6 unit tests within config_test.py:

Config.py Function Tests
1. Tests that loading a non-existent config file returns the default scan settings.
2. Tests that saving a config and then loading it is functional (also verify formatting of file_type).
3. Tests that if the config file contains invalid JSON, load_config should fall back to the default scan settings.
4. Tests that merge_settings should let explicit arguments override values from the saved config.

scan.py Integration Tests:
1. Tests that when arguments are omitted, run_with_saved_settings should use the saved config values.
2. Tests that explicit arguments passed to run_with_saved_settings should override the saved config values.

These unit tests serve us during development by ensuring the individual components of our larger delivered features continue to be operational as our project scope increases. These tests also help us during bug-fixing by pointing us in the right direction by isolating any broken functionalities.

[test folder](https://github.com/COSC-499-W2025/capstone-project-team-11/tree/main/test)
