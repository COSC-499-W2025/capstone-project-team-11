[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=20510454&assignment_repo_type=AssignmentRepo)
# Project Documentation

## System Architecture

This project is implemented as a flexibile Python-based backend system that scans directories and ZIP archives, detects programming languages and skills, analyzes contributors, ranks projects, and generates structured summaries and resumes. The system is accessed entirely through a command line interface and stores results in a local SQLite database.



You can view the full architectural diagram here:

 **[Milestone 1 System Architecture Diagram](docs/architecture/Milestone1-SystemArchitectureDiagram.png)**  



### Architectural Responsibilities

- Directory and ZIP scanning (supports nested archives)
- Language and framework detection using extensions + regex patterns
- Skill inference based on file contents and code structure
- Contributor analysis using file authorship and optional git metadata
- Project ranking (recency-based and contributor-based)
- Summary generation (TXT, JSON, combined reports)
- Resume generation (Markdown)
- Database inspection and reporting via the CLI menu

### Technologies

- Python 
- SQLite backend
- Regex-based detection & pattern analysis
- Optional git metadata integration
- Unit tests running in safe, temporary environments

---

## DFD Level 1

The updated Level 1 Data Flow Diagram describes how data moves through the backend system from the user's input in the CLI through scanning, metadata extraction, database storage, analysis, and output generation.  


### Key Components of the Data Flow

#### User Interaction (`main_menu.py`)

User runs the CLI interface.

Actions include:
- Running a scan
- Viewing past scans
- Ranking projects
- Summarizing contributor activity
- Generating reports or resumes

#### Config and Consent (D1)

- `config.py` loads/saves scan preferences.
- `consent.py` prompts for and stores data-access consent.
- Settings passed into scanning pipeline.

#### Scanning Engine (P2)

- Reads directories and ZIP/nested ZIP archives.
- Extracts file paths, metadata, timestamps, sizes.
- Filters files based on user preferences.
- Passes the collected directory data to the modules that use it

#### Language & Framework Detection (P4)

- Reads file contents + extensions.
- Detects languages, frameworks, and assigns confidence levels.
- Output: language + framework metadata.

#### Skill Detection (P5)

- Infers skills from file patterns and project structure.
- Output: per-file and per-project inferred skills.

#### Scan Metadata Storage (P3 -> D2)

Writes:
- scan record
- file metadata
- detected languages/frameworks
- skills
- contributor links

It serves as the main place the system stores and reads data.

#### Project + Contributor Summarization (P6)

Uses DB state to calculate:
- project summaries
- contributor involvement
- rankings and combined summaries

#### Report & Resume Generation (P7 -> D3)

- Produces Markdown, JSON, and TXT outputs.
- Writes generated files back to the local filesystem.
- Sends export paths and summary messages back to the CLI.

[View the Level 1 Data Flow Diagram]  
 **[Level-1 DFD (Milestone 1)](docs/dfd/Updated%20DFD%20level%201%20for%20milestone%201.pdf)**

---

## Work Breakdown Structure

This WBS outlines the major functional modules and implementation tasks for the project, covering everything from user consent to testing and documentation. It ensures that each system component from ethical data access to output generation is thoroughly planned, validated, and testable.

### Main features of WBS


**User Consent & Ethical Access:** Focuses on ensuring ethical data handling and informed consent. The system displays privacy information, prompts for user approval, and logs responses for future use. If consent is denied, a fallback analysis model maintains functionality while respecting user choices.

**File Input & Validation:** Handles how files are uploaded and verified. The system supports zipped folders, validates file structure and compression, and extracts metadata such as filenames, extensions, and timestamps. It ensures proper data formatting before any analysis begins.

**Project Identification & Classification:** Separates and categorizes scanned content into distinct projects. It distinguishes between individual and collaborative work using metadata (e.g., git authorship) and detects programming languages, frameworks, and other coding attributes within each project.

**Contribution & Activity Analysis:** Analyzes how much each contributor participated in a project. This includes parsing commit histories and modification patterns, categorizing activities (coding, testing, documenting, etc.), and identifying key skills based on file types and content.

**Data Output & Storage:** Generates and stores project summaries. Metadata and metrics are combined into structured outputs (CSV/JSON) and stored in a database . Users can retrieve or delete past insights and summaries while maintaining data consistency.

**Project Evaluation & Ranking:** Ranks and summarizes projects based on contribution metrics. It produces text-based summaries for portfolios or resumes and allows sorting of projects and skills chronologically by activity date.

**System Management & Testing:** Covers the quality assurance and maintenance side. Includes unit and integration testing across all modules, an error-handling and logging framework, and comprehensive documentation updates (schemas, WBS, DFDs, and user guides).

[View the Revised WBS]
(https://github.com/COSC-499-W2025/capstone-project-team-11/blob/main/docs/WBS%20CAPSTONE.webp)

---

## Src Folder

The `src` directory contains the core backend modules. 

### `scan.py` Breakdown

Handles directory and ZIP scanning (including nested ZIPs).

Extracts:
- file paths
- timestamps
- file sizes
- extension/type

Supports:
- filtering by file type
- capturing metadata for DB storage

### `config.py` Breakdown

- Loads/saves JSON config files
- Normalizes file type formats
- Merges default, saved, and explicit runtime arguments

### `consent.py` Breakdown

- Prints data-access policy
- Asks yes/no prompts (with re-prompting)
- Saves user consent preferences

### `file_utils.py` Breakdown

- Validates file format extensions
- Handles whitespace, case insensitivity, hidden files, and special characters

### `detect_langs.py` Breakdown

Detects:
- programming languages
- frameworks (e.g., Django, Flask, React, Express, Spring Boot)

Uses:
- extension detection
- content regex patterns
- high/medium/low confidence scoring

### `detect_skills.py` Breakdown

Infers high-level skills such as:
- SQL
- async programming
- testing frameworks
- web development

### `db.py` Breakdown

- Initializes all database tables
- Saves scans, files, languages, skills, contributors
- Creates all relationship link tables
- Core persistence layer for all ranking and reporting

### `main_menu.py` Breakdown

CLI interface providing:
- run scan
- inspect DB
- rank projects
- summarize contributor activity
- generate reports/resumes

### `rank_projects.py` Breakdown

Supports:
- recency based ranking
- contributor percentage ranking
- tie breaking rules

### `summarize_projects.py` Breakdown

- Determines project paths
- Generates merged summaries
- Handles missing paths and errors gracefully

### `project_info_output.py` Breakdown

- Creates JSON and TXT summaries
- Aggregates skills,languages, and project metadata

### `generate_resume.py` Breakdown

- Builds Markdown resumes
- Preserves acronyms
- Supports bot filtering

### `skill_timeline.py` Breakdown

- Produces chronological skill development timelines
- Useful for portfolio reconstruction

## Test Folder

The test directory provides full, isolated, and repeatable unit test coverage for the project. All tests use temporary directories, in-memory SQLite databases, or mock objects to ensure they are safe, deterministic, and do not affect the user’s real filesystem or database.

---

### `test_main_menu.py` Breakdown

The test directory provides isolated and repeatable unit tests for the project.
Tests commonly use temporary directories, test-specific SQLite databases, and mock objects to ensure they are safe, deterministic, and do not affect the user’s real filesystem or production data.

#### Key behaviours tested

**1. Menu Output Validation**  
Ensures `print_main_menu()` prints all expected options (scan, inspect DB, ranking, summaries, resume generation, exit).  
This prevents accidental menu regressions.

**2. Timestamp Formatting**  
Tests `human_ts()` on multiple timestamp formats to ensure consistent, readable formatting across:
- ISO timestamps
- SQLite timestamps
- Invalid or missing values

**3. Database Inspection Logic**  
Using an in-memory SQLite database, the test verifies that `handle_inspect_database()` safely:
- Lists tables
- Prints table contents
- Avoids crashing when tables don’t exist
- Uses `safe_query()` to prevent SQL exceptions

This module ensures the CLI remains stable and user-friendly even when the database is empty or partially populated.

---

### `test_detect_langs.py` Breakdown

This module tests all core behaviour of `detect_langs.py`, including language inference, framework detection, and confidence scoring.

#### What the tests verify

**1. Correct Language Detection**  
Checks that common file types (e.g., `.py`, `.js`, `.html`) are correctly detected through:
- extension matching
- regex pattern scanning

**2. Confidence Scoring**  
Validates the logic that determines:
- high confidence (strong matches + known extension)
- medium confidence
- low confidence (few matches or ambiguous content)

**3. Framework Detection from Config Files**  
Ensures frameworks are inferred from common dependency files:
- `requirements.txt` -> Flask, Django, FastAPI
- `package.json` -> React, Express, Next.js, Vue
- `pom.xml` -> Java, Spring Boot

**4. Ignored Directory Handling**  
Ensures directories such as `node_modules`, `.git`, `venv`, and `__pycache__` are excluded from scanning.

**5. Empty or Minimal Projects**  
Tests behaviour when files provide no clear language signals.

This module ensures language and framework identification is accurate.

---

### `test_project_info_output.py` Breakdown

Tests the full behaviour of project summary extraction via `project_info_output.py`.

#### Major behaviours verified

**1. JSON and TXT Output Creation**  
Ensures `output_project_info()` successfully writes:
- a `.json` metadata file
- a `.txt` human-readable summary

**2. Project Path Persistence**  
Validates that the stored `project_path` matches the scanned directory.

**3. End-to-End Aggregation**  
Confirms that `gather_project_info()` returns fully populated dictionaries including:
- languages
- skills
- file summaries
- contributions
- optional git metadata

This ensures that downstream features (resume generation, summaries, ranking) always receive correctly structured project metadata.

---

### `test_rank_projects.py` Breakdown

Tests the behaviour of project ranking logic in `rank_projects.py`.

#### Key behaviours verified

**1. Recency-Based Ranking**  
Ensures ordering by:
- earliest scan
- latest scan
- number of scans  

Works correctly in ascending and descending modes.

**2. Limit Parameter**  
Checks that specifying `limit=N` returns only the top N projects.

**3. Stable Ordering Rules**  
Ensures projects with identical timestamps or counts are handled consistently.

**4. Printable Table Output**  
Tests `print_projects()` to confirm:
- headers print correctly
- column spacing is readable
- project names appear in the output

These tests guarantee reliable ranking accuracy and readable printed reports.

---

### `test_rank_projects_by_contributor.py` Breakdown

Validates contributor-focused project ranking logic.

#### What the tests ensure

**1. Percentage-Based Ranking**  
Correctly computes: contributor_files_touched / total_project_files

**2. Tie-Breaking Logic**  
Uses:
- total file count
- alphabetical order of project names  

when percentages match.

**3. Case-Insensitive Username Matching**  
Ensures `"Alice"` and `"alice"` are treated as the same contributor.

**4. Limit Handling**  
Verifies `limit=N` returns only the top N ranked projects.

This ensures ranking is fair, reproducible, and consistent across all contributors.

---

### `test_skilltimeline.py` Breakdown

Tests the chronological skill-usage timeline generator in `skill_timeline.py`.

#### Behaviours checked

**1. Grouping Logic**  
Skills appearing across multiple projects are grouped under one heading.

**2. Chronological Ordering**  
Ensures timestamps for each skill are listed from earliest -> latest.

**3. Clear Output Formatting**  
Verifies the bullet-style output used in CLI printing.

**4. Empty Dataset Handling**  
When no skills exist, prints a clear fallback message such as:
"No recorded skills.”


This module ensures the timeline is consistently structured and readable.

---

### `test_summarize_projects.py` Breakdown

A comprehensive module validating the contributor summary pipeline in `summarize_projects.py`.

#### Tests cover the full workflow

**1. Project Path Resolution**  
Ensures `get_project_path()` correctly resolves:
- real filesystem paths
- project roots containing `.git` or `README`
- ZIP-based paths like `archive.zip:folder/file.py`
- missing or invalid project names

**2. Summary Generation for Ranked Projects**  
Validates:
- correct ordering
- correct limit behaviour
- correct fallback behaviour when projects lack valid paths

**3. Combined Summary Creation**  
Tests `generate_combined_summary()` for:
- correct text formatting
- inclusion of languages, skills, contributors, and file stats
- proper writing to output files

**4. Error Handling**  
Ensures failures (missing project, I/O problems, exceptions in `gather_project_info`) produce:
- informative error entries
- no crashes in the main pipeline

This module produces complete contributor project summaries ready for actual project data.



[test folder](https://github.com/COSC-499-W2025/capstone-project-team-11/tree/main/test)



##  Milestone 1 Video Demonstration

Our Milestone 1 video demo walks through the installation of our Scanner application and showcases all **20 milestone deliverables including scanning, ranking, summaries, skill extraction, and database storage.**.  

 **Watch the Milestone 1 Video:**  
 https://youtu.be/QVMBRefQHuU
