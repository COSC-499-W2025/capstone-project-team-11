# Week 3 Personal Log (15th-21st of September)

This weeks focus consisted of created the project requirements and creating a form of communication that works for all group members.  

<img width="790" height="544" alt="Screenshot 2025-09-20 at 2 06 16 PM" src="https://github.com/user-attachments/assets/d6dababb-d765-426a-ab6c-c9a4bd6996dc" />

## Tasks Completed:
I have been involved with the following tasks either alone or helping my other classmates.

- Worked on project requirements doc and give a final format to the doc.
- Project requirements quiz was completed.
- Joined discord server for group communication.
- Individual and team weekly logs

# Week 4 Personal Log (22nd-28th of September)

This weeks focus consisted of created the system architecture design and creating the final project proposal.  

<img width="1047" height="609" alt="Screenshot 2025-09-27 at 12 45 59 PM" src="https://github.com/user-attachments/assets/647452b3-1e3e-48e3-ba6b-1dfed41e4a6f" />

## Tasks Completed:
I have been involved with the following tasks either alone or helping my other classmates.

- Finalizing project proposal (issue #8)
- Worked on system architecture design (issue #9)
- Finalized system architecture design after instructor feedback (issue #9)
- Individual Logs Week 4 (issue #10)
- Team Logs Week 4 (issue #11) 

# Week 4 Personal Log (22nd-28th of September)

This weeks focus consisted of created the system architecture design and creating the final project proposal.  

<img width="1047" height="609" alt="Screenshot 2025-09-27 at 12 45 59 PM" src="https://github.com/user-attachments/assets/647452b3-1e3e-48e3-ba6b-1dfed41e4a6f" />

## Tasks Completed:
I have been involved with the following tasks either alone or helping my other classmates.

- Finalizing project proposal (issue #8)
- Worked on system architecture design (issue #9)
- Finalized system architecture design after instructor feedback (issue #9)
- Individual Logs Week 4 (issue #10)
- Team Logs Week 4 (issue #11) 

# Week 5 Personal Logs (29th - 5th of October)

The week we focused on creating level 1 and 0 data flow diagrams. We then iterated on our design with the feedback we recived to iterate on our final level 1 design.

<img width="940" height="554" alt="Screenshot 2025-10-04 at 4 15 22 PM" src="https://github.com/user-attachments/assets/a36942ec-1059-4d30-9384-a6b70f62feec" />

## Tasks Completed:
- Designed initial level 1 Data flow diagram (issue #16)
- Revised level 1 DFD with peer feedback (issue #17)
- Week 5 Individual Logs (issue #14)
- Week 5 Team Logs (issue #15)

# Week 6 Personal Logs (6th - 12th of October)

The week we focused on updating our system diagrams to reflect the final requirements and started developing code. 

<img width="963" height="559" alt="Screenshot 2025-10-11 at 3 48 25 PM" src="https://github.com/user-attachments/assets/8efa386d-ca76-4021-be94-2c85bb01fdf0" />

## Tasks Completed:
- Developed initial scanning code to scan selected directories and print out the file name based on file type (PR #43)
- Developed tests for initial scanning (PR #43)
- Documented code for other team members (PR #43)
- Advised Team members on Work Breakdown Structure 
- Reviewed final WBS
- Reviewed ScanDetails PR (PR #44)

# Week 7 Personal Logs (13th - 19th of October)
<img width="942" height="555" alt="Screenshot 2025-10-19 at 4 18 32 PM" src="https://github.com/user-attachments/assets/05739b05-e530-488a-8193-aae7c6449684" />

## Tasks Completed:
- Reviewed final version of Assignment Repo README Content #1 (issue #68)
- Tested and reviewed Tanner's user configuration code (issue #26)
- Added User config description to repo README

## In progress tasks
- Parse Complicated Zipped Folder (issue #22)

## Planned tasks for next sprint
- Parse Complicated Zipped Folder (issue #22)
- Data access consent (issue #21)
- Return errors for incorrect file types (issue #23) 

<img width="1884" height="708" alt="Screenshot 2025-10-19 at 4 50 11 PM" src="https://github.com/user-attachments/assets/dd44a6ab-9613-4a34-80e6-26cf662c38b4" />

# Week 8 Personal Logs (20th - 26th of October)
<img width="950" height="555" alt="Screenshot 2025-10-26 at 7 05 29 PM" src="https://github.com/user-attachments/assets/e84d1bb0-86af-47f7-9246-b1f4e32914f6" />

## Tasks Completed:
This week, I focused on expanding the scanner’s capabilities to include .zip and nested .zip file handling while maintaining compatibility with existing directory scans.
- Closed issue #83

Additions and Features:
- Zip File Support: The scanner can now process .zip archives in addition to directories. When a zip file is provided, its contents are listed and analyzed as if they were normal files.
- Nested Zip Handling: With recursive mode enabled, the scanner automatically descends into nested .zip archives (e.g., outer.zip:inner.zip:file.txt) using in-memory extraction via BytesIO.
- File Type Filtering: The existing file type filter (e.g., .py, .txt) now applies uniformly to both directories and zip files, ensuring consistent results.
- macOS Metadata Filtering: Added logic to ignore unnecessary macOS files and folders such as .DS_Store and __MACOSX, both in directories and inside zip archives.
- Timestamps and Metadata: Implemented _zip_mtime_to_epoch() to convert zip entry timestamps into a consistent format for accurate file age and modification tracking.
- CLI Update: The program prompt now accepts either a directory path or a .zip file path, making it easier for users to scan compressed project archives.
- Backward Compatibility: All original directory scanning functionality remains unchanged. Existing workflows, filters, and output formats are preserved.
- Updated README documentation to reflect all changes I have made

Testing:
- Added four new unit tests verifying both recursive and non-recursive zip scanning behavior.
- Confirmed filters, statistics, and metadata exclusion work consistently across all scan types.

Reviews: 
- Pri's Functionality to Detect Programming Languages and Frameworks in Scanned Directories PR #85
- Tanner's Reusable User Consent Module PR #84
- Tylers Sql db creation PR #95
- Tylers Updated documentation PR #97
  
## In progress tasks
- Add functionality for sorting projects chronologically based on their creation or modification dates. This feature will help users view their project history in a clear, time-ordered format (issue #39)

## Planned tasks for next sprint
- Summarize all Key Information for a Project (issue #32)
- Rank Project Importance Based on User's Contributions (issue #36)

<img width="887" height="644" alt="Screenshot 2025-10-26 at 7 20 13 PM" src="https://github.com/user-attachments/assets/9d560cb2-ee9d-4721-a186-4d183f5ccde6" />


# Week 9 Personal Logs (27th Oct - 2nd Nov)

<img width="960" height="565" alt="Screenshot 2025-11-02 at 6 45 09 PM" src="https://github.com/user-attachments/assets/c05cfc35-20aa-49af-b9df-2ffcc9cc9114" />

## Tasks Completed:
This week, I focused on integrating our database into our scanning script and implementing a project ranking feature.
- Closed issue #104

### Reflection of the past week:
This week was very good for our group. Everyone in the group committed some code and reviewed pull requests. We faced some issues with merge conflicts and missing code with our contribution code, but that was solved, and all code and tests run as they should. Next week, we could improve on committing code on time rather than late Sunday night, which would result in less stress and complications merging to main for grading.

### Additions and Features:
- Integrated optional database persistence into the scanner
- Mounted the entire repository into containers
- Updated the Docker setup to make running tests and non-interactive scans inside containers reliable and consistent with local development.
- Displays project name, first scan, last scan, and total scans.
- Supports ordering (--order asc|desc) and limiting results (--limit N).
- Gracefully handles missing or uninitialized databases.
- Uses get_connection() from db.py for consistent DB access

### Testing:
test_rank_projects.py:
- Uses an in-memory SQLite database to verify logic.
- Tests ordering, limiting, and formatted output.
- Patches DB connection to avoid external dependencies.

scan_db_test.py:
- Scans and file records are correctly persisted when save_to_db=True.
- No DB writes occur when save_to_db=False.
- Persisted metadata_json is valid JSON (or {} when NULL).
- File path values are recorded as expected.
- Schema initialization works on first-run (auto-retries once)

### Reviews: 
- Travis's Individual contributions within collaborative project (PR #110)
- Daniel's Added contribution metrics to a repo scan (PR #108)
- Tanner's Bug Fixes From Week 8's Implementations (PR #107)
- Travis's Allowed files (PR #103)
  
## In progress tasks
- Retrieve Previously-Generated Portfolio Information (issue #34)
- Fix bugs found by Travis in Ranking projects chronologically

## Planned tasks for next sprint
- Output all Key Information for a Project (issue #32)
<img width="1151" height="688" alt="Screenshot 2025-11-02 at 6 04 22 PM" src="https://github.com/user-attachments/assets/f0663ecf-ac3f-4a4b-ac12-be4c8a23e0e1" />

# Week 10 Personal Logs (November 3rd - 9th)

<img width="962" height="567" alt="Screenshot 2025-11-09 at 7 15 00 PM" src="https://github.com/user-attachments/assets/b5b82df9-4d4d-44d6-ae0c-6f5279db53a3" />

## Tasks Completed:
This week, I focused on an update for our previous database implementation to accommodate our new additions for the scanner functionality.
- Closed issue #130

### Reflection of the past week:
This was a steady week for our group. Most of us had at least 2 midterms, which made getting in our contributions quite hard, but everyone managed to accomplish what we said we were going to do. Our clarification about contribution and log grades helped us understand what is being asked of us, which was very helpful. Next week, we could improve on improving our time management as all of our group members tend to push code on similar days, creating some merge conflicts that could easily be avoided.

### Additions and Features:
- **`scan.py`**: Integrated database persistence to handle saving scan results. Updated directory and ZIP scanning to capture per-file metadata (owner, language, and metadata JSON) and store it accurately.
- **`db.py`** — Expanded functionality to insert scans, files, contributors, languages, and skills while maintaining previous integrity. Added helper `_get_or_create()` to add new data correctly, makes sure everything stays properly linked, and avoids half-finished saves if something fails.`FILE_DATA_DB_PATH` environment variable for testing.  
- **`init_db.sql`** — Updated schema to include new normalized tables (`projects`, `contributors`, `languages`, `skills`) and linking tables (`file_contributors`, `file_languages`, `project_skills`). Added `owner` and `metadata_json` columns to the `files` table and indices for faster lookups.
- **`inspect_db.py`** — Updated this file that provides a human-readable database inspector. 

### Testing:
- **`test_db_updates.py`** — Added new unit tests to validate database functionality. Tests include table creation, per-file linking for languages and contributors, fallback behavior when per-file metadata is missing, and verification for repeated scans. Uses temporary databases for isolated test runs. This includes:
  - test_tables_created: Confirms schema initialization with all expected tables.
  - test_save_scan_with_file_metadata_and_links: Validates correct insertion and linking of per-file contributors and languages.
  - test_project_level_language_and_contributor_fallback_and_idempotency: Ensures fallback logic and duplicate prevention during repeated saves.

### Reviews: 
- Pri's Add chronological skills timeline to inspect_db output (PR #135)
- Daniel's Contribution metrics name fix (PR #136)
- Tyler's Added scan.py functionality for project_info_output.py file and reorganized output folder structure (PR #139)
- Daniel's personal logs
- Pri's personal logs 
  
## In progress tasks
- Refactor Ranking projects chronologically to use the new database structure

## Planned tasks for next sprint
- Retrieve Previously-Generated Portfolio Information (issue #34)

<img width="889" height="622" alt="Screenshot 2025-11-09 at 7 35 32 PM" src="https://github.com/user-attachments/assets/970ebdde-a4af-4f19-8331-a5232f75cad1" />

# Week 12 Personal Logs (November 17th - 23rd)

<img width="958" height="562" alt="Screenshot 2025-11-23 at 7 59 53 PM" src="https://github.com/user-attachments/assets/211b87d0-b185-45a7-b0b6-b66d8bd5f9f6" />

## Tasks Completed:
This week, I focused on improving and refactoring our “Rank Projects Chronologically” feature to ensure project ordering reflects the true project creation dates rather than just scan timestamps.
- Closed issue #146

### Reflection of the past week:
This was a good week for our group as we have been in a steady flow of each member committing code. Most of our code was committed before Sunday night to avoid merger errors, which has been a problem in the past. For the upcoming week, we plan on preparing for the quiz as well as the presentation for Milestone 1. 

### Additions and Features:
- **`scan.py`**: Added Git-based metadata extraction to detect Git repository root, repo URL, and initial commit timestamp. This passes `project_created_at` and `project_repo_url` into the persistence layer. I also ensured that VCS-derived creation dates are used instead of overwriting them with the latest scan timestamps.
- **`db.py`**: Extended `save_scan()` to store `project_created_at` and `project_repo_url`, which uses non-destructive logic with `INSERT OR IGNORE` + safe `UPDATE` to avoid overwriting valid metadata.
- **`rank_projects.py`**: Updated SQL ordering to use `projects.created_at` (preferred) and a fallback to `MIN(scanned_at)` when missing. I added readable timestamp formatting via `human_ts()` and improved printed output for clarity.
- **`inspect_db.py`**: Improved timestamp normalization and readability, which makes it easier to distinguish between VCS-derived and fallback timestamps. 

### Testing:
- **`test_rank_projects.py`**: Updated to match new chronological ranking logic, which adds a temporary in-memory `projects` table to support JOIN behaviour. Assertions updated to confirm, correct ordering by `created_at`, correct fallback to the earliest scan when needed, and the human-readable formatting

### Reviews: 
- Tanner's Second Round of Revisions to Language/Framework Detection Feature (PR #157)
- Tanner's Detect programming languages revision: Cleaned codebase and updated unit testing suite (PR #159)
  
## In progress tasks
- Retrieve Previously-Generated Portfolio Information (issue #34)
- Quiz 1 preparation 

## Planned tasks for next sprint
- Finalise project outputs for Milestone 1 Presentations

<img width="833" height="496" alt="Screenshot 2025-11-23 at 8 03 50 PM" src="https://github.com/user-attachments/assets/b76ea4d1-ec35-4c93-b49e-1bc6ec8cb98a" />

# Week 13 Personal Logs (November 24th - 30th)

<img width="703" height="492" alt="Screenshot 2025-11-30 at 4 02 48 PM" src="https://github.com/user-attachments/assets/c71c8c83-f0bb-415a-a478-2b8f456f528e" />

## Tasks Completed:
This week, I focused on generating a resume-ready Markdown file for any contributor found in any of the scanned projects
- Closed issue #176

### Reflection of the past week:
This was a good week for our group as we have been in a steady flow of each member committing code. All of our code was committed before Sunday night to avoid merger errors, improving on our problems from the previous weeks. For the upcoming week, we plan on preparing for the presentation and reworking some of our designs to reflect the current system before the term ends. We are also working on the team contract and the final reflections.

### Additions and Features:
- **`generate_resume.py`** Scans output for project info JSONs and repo-level contribution JSONs. Aggregates per-user projects, technologies, and skills. Renders a Markdown resume with a timestamp and writes it to resumes/resume_<username>_<YYYYmmddTHHMMSSZ>.md. Interactive username selection: prints a clean numbered list of detected candidate usernames and accepts either a number or exact username. Blacklists bot accounts (githubclassroombot) by default and offers --allow-bots to override.
- **`main_menu.py`** Added menu entry 6. Generate Resume. Added handle_generate_resume() that delegates to generate_resume.py. Keeps the main menu behavior consistent and non-blocking.

### Testing:
- **`test_generate_resume.py`** Tests included: normalize_project_name() behavior. collect_projects() and aggregate_for_user() return shapes and content. render_markdown() output and generation timestamp. CLI-level behavior: file generation for a user, blacklist enforcement for bots, and override via --allow-bots. Uses temporary output directories in tests to avoid touching repository data.

### Reviews: 
- Daniel's Refactor/skills timeline module (PR #180)
- Travis' Main menu module that acts as a unified CLI interface (PR #181)
- Tyler's Auto Output Key Information On Scan That Includes All New Analysis Info (PR #186)
- Tanner's Updated the unit testing suite for data-access consent feature (PR #187)
  
## In progress tasks
- Presentation preparation
- Updating system architecture and data flow diagrams
- Team contract
- Reflection

## Planned tasks for next sprint
- Christmas Break

<img width="835" height="417" alt="Screenshot 2025-11-30 at 5 33 09 PM" src="https://github.com/user-attachments/assets/997854ef-4b79-4eeb-ba9f-e620a7e3e049" />


