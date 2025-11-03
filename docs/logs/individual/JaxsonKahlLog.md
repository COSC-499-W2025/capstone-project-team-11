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

