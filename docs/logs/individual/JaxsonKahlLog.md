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

# Week 14 Personal Logs (December 1st - 7th)

<img width="684" height="493" alt="Screenshot 2025-12-07 at 4 59 34 PM" src="https://github.com/user-attachments/assets/1b281de6-93cc-4d61-bc4e-3513425c7471" />

## Tasks Completed:
This week, I focused on preparing for our Milestone 1 presentation, the individual reflection, and the final deliverable, which was retrieving and deleting generated resume items
- Closed issue #35

### Reflection of the past week:
With exams starting and projects wrapping up in other courses, this was still a good week for our group. All group members completed something to do with the end of milestone 1. We also completed our presentation for Milestone 1, which we had prepared for. We are not too sure what is planned for the week coming back from Christmas break, but we will decide that when classes resume again.


### Additions and Features:
- **`main_menu.py`** wires the scan flow to persist results on demand and, after any scan, immediately derives project info and writes the JSON/TXT reports under an `/output/<project_name>/` folder for easier follow-up. This fixes the empty resume generation problem we encountered.
- **`scan.py`** reinstates database persistence during scans: language/skill detection falls back to empty lists, file metadata is always built, and retries after `init_db()` carry the same project metadata, eliminating the previous UnboundLocalError when saving.
- **`collab_summary.py`** now keeps `identify_contributions()` focused on returning structured data: the JSON file write is suppressed by default and `summarize_project_contributions()` calls it with `write_output=False`, so scans no longer drop contributions artifacts in `/output/`.
- **`init_db.sql`**: adds resumes table plus indexes to store generated resumes linked to contributors.
- **`db.py`**: introduces save_resume helper to persist resume path/metadata with contributor linkage and timestamp.
- **`generate_resume.py`**: adds --save-to-db flag and calls save_resume after writing markdown, with error handling for missing schema.
- **`main_menu.py`**: when inspecting DB, now lists recent resumes; resume generator menu runs with --save-to-db.
- **`main_menu.py`**: Built a full “View Resumes” flow—lists recent resumes, prompts to view or delete, renders Markdown to readable plain text for previews and full paging, and deletes via _delete_resume, which removes the DB row then tries to remove the file with clear messaging. Added helpers for markdown-to-plain rendering, resume listing, previewing, paging, and fixed sqlite3.Row access during deletion.
- **`scan.py`**: 
   - Added `_resolve_extracted_root`, `_prepare_nested_extract_root`, and` _safe_join_extract_root` helpers to safely unpack archives (and nested archives) into real directories so they're scanned exactly once, without leaking temp dirs or allowing path traversal.
   - Updated `_scan_zip` to track the actual extracted path for each zip:path entry, skip macOS junk and nested containers, avoid counting nested zips as files unless the user explicitly filters for .zip, and descend into nested archives using the shared extraction tree.
   - `list_files_in_zip` now keeps a single temp extraction directory, builds accurate file metadata (owner/language) using the tracked real paths, and passes that directory to language/skill detection.
   - `list_files_in_directory` and run_with_saved_settings detect when the target is a zip, extract it once, reuse that path for contributions/metrics/summaries, and clean up afterward.
- **`project_info_output.py`**:  extracts zip targets (outer and nested) before running any detectors so project summaries operate on actual files, not archive placeholders.
- **`collab_summary.py`** ignores .DS_Store, __MACOSX, ._*, and .zip files when summarizing non-git contributions, preventing archive containers and macOS metadata from inflating the “Changed files” list.
- **`detect_langs.py`** and **`detect_skills.py`** share the same artifact filter to keep language/skill stats from counting container zips or macOS junk, ensuring [Filtering Stats] reflect only real files.

### Testing:
- **`test_main_menu.py`**  updated `test_print_main_menu_outputs_correct_text` to reflect new menu options.
- Removed **`test_json_output_file`** since the contribution JSON is no longer needed.
- **`test_generate_resume.py`**: ensures temp DB path applies to subprocess and adds a test verifying resume rows are created.
- **`test_main_menu.py`**: Updated menu output expectations, added coverage for the markdown renderer and preview helper, and added deletion tests that use sqlite3.Row rows to ensure DB rows are removed, files are deleted, and missing files are handled gracefully.

### Reviews: 
- Tyler's Milestone 1 videos (PR #208)
- Daniel's Reworked skipped unsupported file formats (PR #210)
  
## In progress tasks
- No tasks currently in progress

## Planned tasks for next sprint
- Christmas Break

<img width="739" height="495" alt="Screenshot 2025-12-07 at 5 11 10 PM" src="https://github.com/user-attachments/assets/7d882fb9-c604-445b-af30-0e1f3ce73727" />

# T2 Week #1 Personal Logs (Jan 5th - 11th)

<img width="936" height="535" alt="Screenshot 2026-01-11 at 10 22 59 AM" src="https://github.com/user-attachments/assets/6ee6a6ed-f17b-4efb-a2e8-84f77a889b2b" />

## Tasks Completed:
This week, I worked on adding the project thumbnail feature. This feature allows the user to upload an image to be used as a thumbnail for a scanned project. This will be useful for our future frontend UI.
- Closed issue #235

### Reflection of the past week:
This week, we mainly focused on understanding the Milestone 2 deliverables and dividing the tasks among our group members. We have had good communication among our team members and have accomplished our tasks with minimal problems so far. Next week we are planning to dive deeping into a true API integration as well as starting on our LLM route. 


### Additions and Features:
- **`init_db.sql`**: Added `thumbnail_path` column to `projects`
- **`db.py`**: Added `_ensure_projects_thumbnail_column` to migrate existing DBs. `save_scan` now accepts `project_thumbnail_path` and updates the project row when provided.
- **`file_utils.py`**: Added `IMAGE_EXTENSIONS` and `is_image_file` for thumbnail validation
- **`scan.py`**: Added` _prepare_project_thumbnail` to copy the chosen image into `output/<project>/<original_name>.<ext>`. Threaded `project_thumbnail_path` through `_persist_scan`, `list_files_in_directory`, and `run_with_saved_settings`.
- **`main_menu.py`**: Added optional thumbnail prompt when saving scans to the DB

### Testing: 
- **`test_db_updates.py`**: Verified `projects.thumbnail_path` exists in schema. Asserted `save_scan` persists the thumbnail path.
- **`scan_db_test.py`**: Added a thumbnail persistence test using `_prepare_project_thumbnail` and validated the stored path.

### Reviews: 
- Tyler's Incremental resume information (version 1) (PR #245)
- Tyler's Individual Logs (PR #246)
  
## In progress tasks
- API endpoint integration

## Planned tasks for next sprint
- Complete API Integration and start working on LLM integration

<img width="737" height="443" alt="Screenshot 2026-01-11 at 10 35 38 AM" src="https://github.com/user-attachments/assets/ce579866-a307-4f92-96cb-aae78e0cddfc" />
