# Team #11 - Week 3 Team Log (September 15th through September 21st)

Team Members    --> GitHub Username
- Priyanshu Chugh --> priyanshupc04
- Tyler Cummings  --> TylerC-3042
- Tanner Dyck     --> TannerDyck
- Travis Frank    --> travis-frank
- Jaxson Kahl     --> jaxsonkahl
- Daniel Sokic    --> danielsokic

Overview:
This week we focused on completing the following tasks from our Kanban board:
- Create Repository for project
- Create and organize Discord server for communication
- Complete first revision of project requirements
- Hand in project requirements
- Complete Week 1 Logs

Burnup Chart: 
<img width="1022" height="542" alt="Screenshot 2025-09-20 at 2 29 42 PM" src="https://github.com/user-attachments/assets/7f53e5cf-e0f5-48d9-8315-38d45564c5dd" />

Table view of completed tasks on project board (by name):
- Create Repository for project
    - ALL
- Create and organize Discord server for communication
    - ALL
- Complete first revision of project requirements
    - ALL
- Hand in project requirements
    -  ALL
- Complete Week 3 Team Logs
    - Jaxson

Table view of in progress tasks on project board (by which username):
- Complete Week 3 Inidividual Logs
    - ALL

Test Report: 
- N/A For week 3

# Team #11 - Week 4 Team Log (September 22nd through September 28th)

Overview:
This week we focused on completing the following tasks from our Kanban board:
- Project Proposal
- Final Architecture Design

Burnup Chart: 
<img width="994" height="494" alt="Screenshot 2025-09-27 at 12 55 07 PM" src="https://github.com/user-attachments/assets/c3b9c21c-99bb-4ba5-ad06-1e8965b24edb" />

Table view of completed tasks on project board (by name):
- Project Proposal
  - Daniel, Travis, Priyanshu, Tanner, Jaxson
- Final Architecture Design
  - Daniel, Travis, Priyanshu, Tanner, Jaxson

Testing Report:
- N/A For week 4

# Team #11 - Week 5 Team Log (September 29nd through October 5th)

Overview:
This week we focused on completing the following tasks from our Kanban board:
- Project Proposal
- Final Architecture Design

Burnup Chart: 

<img width="1026" height="533" alt="Screenshot 2025-10-04 at 4 25 03 PM" src="https://github.com/user-attachments/assets/efea75cb-c5e4-479d-b235-84a247373c57" />

Table view of completed tasks on project board (by name):
- Data Flow Diagram (Level 0)
    - Tyler
- Initial Data Flow Diagram (Level 1)
    - Tanner, Priyanshu, Travis, Daniel, Jaxson
- Final Data Flow Diagram (Level 1)
    - ALL
- Add Data Flow Diagram to repo
    - Tanner

Testing Report:
- N/A For week 4

# Team #11 - Week 6 Team Log (October 6th through October 12th)

Overview:
This week we focused on completing the following tasks from our Kanban board:
- System diagrams to reflect the final requirements
- File analysis code
- Pull request template
- Setup docker container

Burnup Chart: 

<img width="995" height="505" alt="Capstone Week 6 Burnup Chart" src="https://github.com/user-attachments/assets/674c9dca-bede-4601-bbc2-1a5d5e223455" />

Table view of completed tasks on project board (by name):
- Write code to analyze files in a directory, including size and modification statistics
    - Daniel, Jaxson
- Review Code
    - Tannerc, Tyler, Pri
- Update Repo README to have explanations and links to System Architecture, DFD, WBS
    - Pri, Travis
- Complete Work Breakdown Structure
    - Tanner
- Set up Docker Container
    - Travis

Testing Report:
- All tests for the file scanning script passed successfully on multiple machines.
- The tests thoroughly covers key functionalities, including recursive and non-recursive directory scanning, file type filtering, error handling for invalid paths, and verification of file statistics such as size and modification time.
- Each test is clearly structured with descriptive names and uses temporary directories.
- Overall, tests have strong coverage, clean organization, and validate both normal and edge-case behaviors.

# Team #11 - Week 7 Team Log (October 13th through October 19th)

Team Members    --> GitHub Username
- Priyanshu Chugh --> priyanshupc04
- Tyler Cummings  --> TylerC-3042
- Tanner Dyck     --> TannerDyck
- Travis Frank    --> travis-frank
- Jaxson Kahl     --> jaxsonkahl
- Daniel Sokic    --> danielsokic

Overview:
- This week, our focus was on enhancing the project’s usability and configuration management. We updated the repository README to include a more detailed description of the project’s purpose, core features, and technical design overview. In addition a new configuration management system was implemented to streamline user interaction with the file scanning tool.
  
Burnup Chart:
<img width="1041" height="466" alt="Screenshot 2025-10-19 at 9 20 48 PM" src="https://github.com/user-attachments/assets/ababae31-4353-4c4f-92a8-9bc7920fe5ec" />

Table view of completed tasks on project board (by name):
<img width="1110" height="264" alt="Screenshot 2025-10-19 at 9 16 16 PM" src="https://github.com/user-attachments/assets/4dcd1811-59eb-4673-8f43-0a210dcca7a4" />

Testing Report:  
All six unit tests in `config_test.py` passed successfully on multiple systems. The tests validate key behaviors, including:
- Loading a non-existent config file defaults correctly.
- Saving and reloading a valid config file works as intended.
- Invalid JSON gracefully falls back to defaults.
- Explicit arguments correctly override saved settings.
- `run_with_saved_settings()` accurately applies saved configurations.
- Saved settings persist correctly between sessions and can be overwritten or recreated.

Manual testing confirmed successful integration with `scan.py`, ensuring accurate reuse of saved configurations and reliable creation of the `.mda/config.json` file.  
All functionality works as expected on macOS and Linux systems.

Reflection:
- The new configuration feature made the program much more user-friendly, reducing repetitive inputs and improving session persistence.  
- Collaboration and code review were smooth this week, and the README improvements helped clarify the project for new contributors.  
- The testing process showed strong team coordination, and maintaining a clean PR workflow made merging new functionality straightforward.
- We all had a busy week with midterms and will be looking to add more funcionality in the coming weeks

Planning Activities (Week 8):  
- Complete parsing functionality for complicated zipped folders (`#22`).  
- Implement data access consent logic and integrate it into the workflow (`#21`).  
- Add error handling for incorrect file formats (`#23`).  
- Begin preparing for Milestone #1 submission by verifying all current modules meet functional requirements.  
- Continue updating documentation as new features are finalized.


# Team #11 - Week 8 Team Log (October 20th through October 26th)

Team Members    --> GitHub Username
- Priyanshu Chugh --> priyanshupc04
- Tyler Cummings  --> TylerC-3042
- Tanner Dyck     --> TannerDyck
- Travis Frank    --> travis-frank
- Jaxson Kahl     --> jaxsonkahl
- Daniel Sokic    --> danielsokic

Overview:
This week, our team focused on expanding the core functionality of the file scanning system by implementing new modules and improving robustness across the codebase. Several new files were added includint consent.py, detect_langs.py, and file_utils.py which faciltate major enhacnements in order to handle consent validation, language detection, and file format checking. Additionally, scan.py was enhanced to be able to scan complicated zip files as well as determine collaboration in git repositories. The team also began developing a persistent storage system for scan history and file metadata. A new database schema and supporting scripts were introduced to establish the foundation for structured data management within the project.

<img width="1200" height="864" alt="chart (1)" src="https://github.com/user-attachments/assets/619def54-ceae-4942-b708-292e33824582" />


Table view of completed tasks on project board (by name):
- Integrate complicated .zip scanning
    - Jaxson
- Create reusable user consent module
    - Tanner
- Implement functionality to detect programming languages
    - Priyanshu
- Add feature to detect collaborators in a github repository
    - Daniel
- Implement file format validation
    - Travis
- Implement database schema and utilities for scan storage
    - Tyler
- Review Code
    - Jaxson, Tanner, Priyanshu, Daniel, Travis, Tyler
- Update Readme
    - Tanner
 
Testing Report:
All unit tests passed successfully on multiple systems. The test suite was expanded to include new unit and integration tests covering the recently added files:

1. consent_test.py  
    - Simulated user consent prompts to confirm valid/invalid input behavior.
    - Verified that consent decisions are saved and retrieved correctly between sessions.
    - Confirmed that scans cannot proceed without user consent.  
2. files_utils_test.py
    - Verified that is_valid_format() correctly identifies supported file extensions.
    - Tested handling of invalid, hidden, and extensionless files.
    - Confirmed that unsupported formats are skipped gracefully with clear console messages.
3. detect_langs_test.py
    - Verified that language and framework detection correctly identifies common project types              (Python, C++, Java).
    - Ensured accurate detection from directory structures and file contents.
4. scan_test.py
    - Verified that when scanning a ZIP file non-recursively, only top-level files are listed while         nested files are ignored.
    - Confirmed that file-type filters (e.g., .py, .txt) apply correctly inside ZIP archives.
    - Ensured recursive scanning correctly traverses nested ZIPs, displaying inner files with full          hierarchical paths.
    - Verified that in environments without a Git repository (such as a temporary directory), the          "Collaboration: unknown" instead of failing or returning incorrect data.scanner correctly              reports.
  
5. test_db.py
   - Verified that the SQLite database initializes correctly with scans and files tables.
   - Tested insertion of dummy scan and file records to confirm table structure and constraints.
   - Ensured that table data can be retrieved and printed cleanly for debugging and validation.

Reflection:
- Our team made significant progress this week by integrating multiple independent features (consent validation, language detection, file format filtering, ZIP handling, and collaborator detection) into a cohesive and robust scanning workflow.
- The modular design of new components like consent.py, file_utils.py, and detect_langs.py improved overall code organization and testability.
- Handling complex nested ZIPs was a major technical challenge, but successful implementation and testing confirmed that the scanner can now reliably handle recursive archives.
- Adding file format validation increased the system’s safety by preventing unsupported or unsafe files from being processed during scans.
- The addition of the database schema introduced our first persistent data layer, helping us understand how to manage and query scan history efficiently.
- The collaborator detection feature enhanced traceability and transparency by linking scanned files to their respective Git contributors.
- The team demonstrated strong collaboration during pull request reviews, resolving merge conflicts efficiently and maintaining consistent code quality standards.
- Comprehensive testing ensured that all new modules worked seamlessly across platforms, reinforcing the reliability of the codebase.

Planning Activities (Week 9):
- Start workaround anaysis if user denies external service permissions (#25).
- Extract key contribution metrics in a project (#30)
- Extract key skills from a given project (#31)
- Output all key information for a project (#32)



 # Team #11 - Week 8 Team Log (October 27th through November 2nd)
Team Members    --> GitHub Username
- Priyanshu Chugh --> priyanshupc04
- Tyler Cummings  --> TylerC-3042
- Tanner Dyck     --> TannerDyck
- Travis Frank    --> travis-frank
- Jaxson Kahl     --> jaxsonkahl
- Daniel Sokic    --> danielsokic

  Overview: This week,our team focused on advancing collaboration features, database integration, and skill analysis within the file scanning system. Several new modules were added, including collab_summary.py, contrib_metrics.py, and rank_projects.py, which collectively enhance collaboration insights and data visibility. These updates enable detection of individual contributions across Git and non-Git projects, commit-level analytics, and chronological project ranking based on scan activity. The detect_skills.py module was also introduced to automatically infer technical and writing-based skills using regex pattern matching, extending the functionality of the language detection system.
In addition, improvements were made to database persistence and Docker reliability, ensuring consistent behavior between local and containerized environments. The team resolved multiple configuration and prompt-related bugs, streamlined scan logic, and refined user interaction flows. Together, these contributions significantly expanded the project’s analytical capabilities—allowing for integrated tracking of languages, skills, collaboration, and scan data persistence within a unified workflow.

<img width="1018" height="518" alt="Screenshot 2025-11-02 at 7 02 27 PM" src="https://github.com/user-attachments/assets/0659f507-7ad2-48f1-af85-949f76d2cf57" />


Table view of completed tasks on project board (by name):

Bug Fixes from Week 8’s Implementations
 -Tanner

Added contribution metrics to a repo scan
- Daniel

Added functionality for ranking project scans chronologically
- Jaxson

Implemented collaboration summary for Git and non-Git projects
- Travis

Extract skills from scanned projects
- Priyanshu

Database integration and persistent storage for scan results
 -Daniel

Implemented output of key information of projects
- Tyler

Code review and verification
 -Tanner, Jaxson, Priyanshu, Daniel, Travis, Tyler


Testing Report:
All new and existing unit tests passed successfully across both local and Docker environments. The testing suite was expanded to cover database persistence, collaboration summaries, skill detection, and ranking functionality. Validation was conducted through both automated and manual testing.

config_test.py
-Verified corrected behavior for None and empty field overwriting in config.json.
-Confirmed that all yes/no prompts now consistently use ask_yes_no() for standardized input handling.
-Ensured users are prompted to reuse settings only after performing an initial scan.

contrib_metrics_test.py
-Validated analyze_repo() accuracy for commit tracking, line changes, and author normalization.
-Confirmed correct aggregation of commits-per-author, categorized activity counts, and commits-per-week.
-Tested isolated Git repositories with both single and multiple authors to ensure reproducibility.

scan_db_test.py
-Verified that scan and file records persist correctly when save_to_db=True.
-Ensured no unintended writes occur when persistence is disabled.
-Confirmed schema auto-initialization, valid JSON formatting, and proper file path recording.

test_rank_projects.py
-Tested ordering and limiting behavior for chronological project ranking (--order, --limit).
-Simulated missing database conditions to confirm graceful handling without crashes.
-Verified accurate aggregation of project names, first/last scan dates, and total scans.

collab_summary_test.py
-Validated contributor detection for both Git-based and non-Git projects.
-Ensured correct JSON export structure for per-author contribution summaries.
-Tested inline Author: tag parsing and commit-based author extraction.

test_detect_skills.py
-Verified accurate detection of programming and writing-based skills using regex pattern matching.
-Tested recursion, OOP, web development, and analytical writing recognition across file types.
-Confirmed no false positives in empty or irrelevant files, with consistent multi-skill output merging.

file_utils_test.py
-Ensured all import paths and module references work across local and Docker environments.
-Validated test discovery and module loading for stable CI/CD test execution.

test_project_info_output.py
-Verifies that a non-Git project correctly generates JSON and TXT outputs with detected languages, skills, and contributions, including placeholder “Unknown” contributors.
-Ensures that a Git project includes proper Git metrics (total commits, contributors, activity breakdown) in both JSON and TXT outputs.

Reflection:

Our team made strong progress this week by introducing several new analytical and collaborative features that expanded the project’s depth and reliability.
The addition of the Collaboration Summary and Contribution Metrics features allowed the scanner to identify and summarize individual contributions across both Git and non-Git projects, giving better insight into team activity.
The new Project Ranking utility added chronological tracking for scans, helping visualize project progress over time.
We also refined database integration to ensure scans and file data are stored persistently, making historical data easy to access and analyze.
The Skill Extraction feature extended our language detection system to recognize both technical and writing-based skills, offering a broader understanding of user expertise.
Alongside these additions, several bug fixes improved configuration handling, prompt sequencing, and cross-platform stability, creating a smoother overall experience.
The team maintained steady collaboration through pull request reviews and testing, confirming that all new modules worked properly in both local and Docker environments.
Overall, this week brought us closer to a polished and feature-complete prototype with more reliable analytics and stronger performance.

Planning Activities (Week 10):
- Retrieve Previously-Generated Résumé #35
- Delete Previously Generated Insights #38
- Sort "Skills Exercised" Chronologically #40
- bug fixes

# Team #11 - Week 10 Team Log (November 2nd through November 9th)
Team Members      --> GitHub Username
- Priyanshu Chugh --> priyanshupc04
- Tyler Cummings  --> TylerC-3042
- Tanner Dyck     --> TannerDyck
- Travis Frank    --> travis-frank
- Jaxson Kahl     --> jaxsonkahl
- Daniel Sokic    --> danielsokic

## Overview:
This week, we focused on completing smaller, more nuanced tasks than in previous weeks, where we have aimed to implement big-ticket scanner features and milestone deliverables.
Everyone has been keeping their own lists of bugs they come across, whether it is within a feature they developed or within features made by others. 
When we met in person for our TA check-in, we took inventory of issues we wanted to address and assigned tasks accordingly.

Our database is more comprehensive and capable than it was last week. Jaxson ensured that all relevant details collected during scans have a home in the database so that they can be accessed later as we improve our scanner's report/summary generation. Daniel made a note of some inconsistencies in the "Display contribution metrics for git projects" feature he developed in week 9, so he dove back into it and reworked how git authors' names are displayed. It was a worthwhile improvement as now we have a canonical naming convention for github usernames, which improves readability and clarity in generated reports. Priyanshu was in a position to implement a new feature, so he allowed for the displaying of chronologically-sorted skills, as they were found in a user's saved scans from the database, which was made easier with Jaxson's recent database revisions. Now users can generate a comprehensive timeline of skills exercised, allowing them to view how their aptitudes have changed/progressed over time, and across projects. I (Tanner) wanted to improve the accuracy and consistency of our "Detect programming languages/frameworks within coding projects" feature. So I added a detection method to be used alongside our first method. detect_langs.py now reads each file in a project and uses a pre-defined set of REGEX syntax patterns for a wide array of languages to find occurrences of unique languages within files. The feature still needs a lot more revision, and I hope to continue to improve it in the coming weeks. Travis, like Daniel, noticed some bugs/inconsistencies in his collaboration summary from last week's sprint, so he made sure it was corrected last week. Now, after his fixes, the collaboration summary is more accurate and comprehensive, and for each GitHub user in the project, it displays how many commits they have made, the total number of files in the project they have contributed to, and the exact files they have worked on. Tyler implemented a new feature: the ability to choose to export a report of a scan in both JSON and .txt formats. This is an excellent addition, as it is a feature that is at the core of the project. We have spent a long time creating the logic for our scanner to operate by, but now we have a tangible exported summary of a scan done on a creative project. Overall, I believe we accomplished a lot this week. We made some necessary improvements to pre-existing features and even programmed a few additional features that our program was lacking. 

## Burnup Chart:
<img width="1025" height="541" alt="week10-burnup" src="https://github.com/user-attachments/assets/0bc2b5ce-8360-44c0-b6b3-04f33c6ad724" />

## Team Member's Completed Tasks:
### Daniel:
- Reworked the contribution metrics to create robust and consistent naming conventions for git authors
### Jaxson:
- Updated database functionality for all scanning functions (Database now correctly stores all relevant information found during scans)
### Priyanshu:
- Added chronologically-sorted skills timeline to inspect_db.py output (Skills found within saved scans are chronologically organized)
### Tanner:
- First pass of revisions on "Detect programming languages/frameworks within coding projects" feature
- Team logs for week 10
### Travis:
- Bug Fixes: file count always displaying 0 & add per-author file tracking in collaboration summary
### Tyler:
- Added scan.py functionality for project_info_output.py file & reorganized output folder structure
### All Members:
- Code reviews and verification
- Completion of individual logs and peer reviews

## Testing Report:
All new and existing unit tests continue to pass successfully across both local and Docker environments. Validation was conducted through a combination of automated and manual testing.

### collab_summary_test.py:
- Added unit test for per-author file tracking in Git repos:
- Git repo should include per-author changed files in the contribution summary
- Creates and commits a file
- Ensures the author appears and the file list contains the changed file

### contrib_metrics_test.py
- Added more tests and a feature that hides any author with zero commits:
- Normalize author identity using email (preferred) or name
- Handles GitHub noreply addresses like 12345+username@users.noreply.github.com
- Automatically normalize author identity for any git repo by stripping away special symbols

### inspect_db.py
- Added chronological skills timeline to inspect_db output:
- Looks at the earliest scan date where each skill was detected in a project
- MIN(scanned_at) gives the first time that the skill appeared in any scan
- Sorting by first_seen shows a "timeline" of when skills were exercised

### test_db_updates.py
- Added new unit tests to validate database functionality. Uses temporary databases for isolated test runs. Tests include:
- table creation
- per-file linking for languages and contributors
- fallback behaviour when per-file metadata is missing
- verification for repeated scans

### test_detect_langs.py
- Creates a temporary Python file and writes some basic Python code within it, uses the new pattern-based detection method to ensure the pre-programmed REGEX patterns are working properly by checking that the pattern match count is greater than 0
- Confirms all 5 confidence scenarios are generating correctly (High - 2 cases, Medium - 2 cases, Low - 1 trivial case)
- Checks that confidence levels are calculated and included in the final output of results by making sure that a Python file (with .py extension) with some basic code returns "high" confidence

## Team Reflection:
Our team worked very well together this week. We all had busy weeks (other projects being due, second-wave midterms, etc.), but we communicated effectively and frequently. 
We made good use of our Discord server to keep each other in the loop when we could not meet in person, and we utilized our TA check-in time wisely by prioritizing tasks to be completed during the busy week ahead. 
Everyone provided their individual timelines and ETAs around when they hoped to have their PRs up and ready for review, and I'm proud to say everyone was pretty accurate. No late-night rushes to merge our Development branch to main; everything was completed in a convenient and timely manner.
We also decided to be proactive and discuss what we hope to accomplish as a team in the upcoming two weeks (weeks 11 *Reading Break*, and 12) ahead of time. Nobody seems to have any complaints about our most recent sprint, and we look forward to the next!

## Planned Activities (Week 11 *Reading Break* & Week 12):
This upcoming week (week 11) is Reading Break, so our contributions may vary between team members depending on individual availability (travelling, visiting family, etc.).
As for week 12, we have discussed it as a team and decided that we hope to:
- Revise "Rank projects chronologically" Issue #146
- Continue revising "Detect programming languages/frameworks used within coding projects" Issue #129
- Implement "Delete Previously Generated Insights" Issue #38 (didn't get to it in week 10 as planned)
- Implement "Rank Project Importance Based on User's Contributions" Issue #36
- Implement "Summarize the User's Top-Ranked Projects" Issue #37
- General bug-fixes that we notice during testing/implementation

# Team #11 - Week 12 Team Log (November 17nd-23rd)
Team Members    --> GitHub Username
- Priyanshu Chugh --> priyanshupc04
- Tyler Cummings  --> TylerC-3042
- Tanner Dyck     --> TannerDyck
- Travis Frank    --> travis-frank
- Jaxson Kahl     --> jaxsonkahl
- Daniel Sokic    --> danielsokic

Overview:
This week the team resumed work after reading break and delivered several major improvements across scanning, ranking, reporting, skill grouping, and project metadata handling. Added/Fixed features such as language detection, contributor summaries, chronological ranking, and skill chronology. The team continued strong collaboration with consistent PR reviews and early commits to avoid merge conflicts.

<img width="1047" height="553" alt="image" src="https://github.com/user-attachments/assets/3a496cca-8ed6-4a7d-b5cd-60da41bec0e1" />


Table view of completed tasks on project board (by name):

Improved language/framework detection with filtering, comment stripping, confidence scoring, config cleanup, expanded tests, PR reviews, and weekly coordination/logs.
- Tanner
  
Added full contribution-ranking feature with project rankings, contributor stats, and contribution fractions.
- Daniel

Refactored chronological project ranking using Git creation timestamps, added Git metadata + DB updates, improved SQL/formatting and continued portfolio-info retrieval
- Jaxson

Implemented full contributor-summary tooling, project/skill summarization improvements and robust path handling.
- Travis

Added interactive menu system to scan.py and view/delete insights
- Tyler

Team Logs
- Tyler

Code Review and Verification
- Tanner, Jaxson, Priyanshu, Daniel, Travis, Tyler

Testing Report:
All new and existing unit tests passed successfully across both local and Docker environments. The testing suite was expanded to cover Chronological Project Ranking, collaboration summaries, Language & Framework Detection, Path Resolution. Validation was conducted through both automated and manual testing.

test_rank_projects.py
- Verified correct ordering for both ascending and descending modes, based on earliest scan timestamps when no entry exists in the projects table.
- Confirmed that limit behavior correctly truncates results without disrupting ordering.
- Ensured ranking logic works with: Multiple projects, Mixed timestamps, Projects with only partial scan history
- Validated fallback behavior when contributor data or projects are missing.
<img width="546" height="102" alt="image" src="https://github.com/user-attachments/assets/43d3a46e-c877-437a-a5fe-c6d444b41b21" />

test_detect_langs.py
- Verified accurate detection for all languages
- Validated proper detection of multiple frameworks in a single package.json (React, Vue, Express).
- Confirmed scan_file_content() detects syntax signatures for Python classes, imports, functions, and block structures.
- Verified complete removal of: Python single-line comments, Python multiline docstrings, JavaScript single and multiline comments, Ensured code integrity remains unchanged.
- Verified Directory & Extension Handling: Ignored directories (node_modules, .git, venv, __pycache__, etc.) are skipped, get_extension() normalizes mixed-case extensions and should_scan_file() distinguishes code, text, and non-scannable file types.
<img width="748" height="767" alt="image" src="https://github.com/user-attachments/assets/63cfede5-53b5-46a6-991f-36ecd8800c5d" />


test_summarize_projects.py
- Validated correct path resolution across several edge cases: Nonexistent or empty projects, returned None when no scans exist and returned None when scans exist but no associated files exist.
- Correctly identified project root using .git directory, even when scanned files were deep in nested subdirectories.
- Verified that a top-level README.md correctly marks the project’s root directory.
- Confirmed correct extraction of base file path when stored paths use archive.zip:/inner/file.py format.
- Ensured the latest scan’s files are used for project path derivation.
- Validated empty result for nonexistent contributor names.
- Confirmed stable behavior even when ranker returns empty lists.
- Verified summaries gracefully degrade with: project_path = None and error = "Project path not found" (No crashes or propagation of invalid paths.)
- Confirmed complete summary generation when: Valid project path exists, README and source files present
- Ensured summaries include: Project name, Project path, Contributor ranking metrics, File counts


Manual testing confirmed:
- Improved language detection accuracy
- Correct metadata extraction from Git
- Correct project summarization outputs
- Correct skill grouping and ordering
- Proper functioning of new scan.py menu

Reflection:
This week was productive and structured. The team successfully reestablished momentum after the break. Several large features were completed or significantly improved, especially around project metadata accuracy, skill grouping, language detection, and contributor-focused summaries. Communication was strong, PR reviews were done early, and merge conflicts were avoided. With Milestone 1 approaching, the team feels confident but aware of the need to finalize demo-related features and polish the pipeline.

Planning Activities (Week 13)
- Prepare for Quiz 1 and Milestone 1 Presentation
- Finalize revisions to Language/framework detection, Chronological ranking and project metadata, Contribution summarization and Skill grouping
- Begin or continue résumé/portfolio generation, Retrieving previously stored résumés/portfolio entries, Completing any remaining Kanban tasks and clean up scan.py for the demo

# Team #11 - Week 13 Team Log (November 24th - November 30th)
Team Members      --> GitHub Username
- Priyanshu Chugh --> priyanshupc04
- Tyler Cummings  --> TylerC-3042
- Tanner Dyck     --> TannerDyck
- Travis Frank    --> travis-frank
- Jaxson Kahl     --> jaxsonkahl
- Daniel Sokic    --> danielsokic

## Overview:
This week, we focused on cleaning up our codebase and outputs before the end of Milestone 1. All group members committed quality PRs on time and contributed quality reviews while providing good feedback and improvements. There was no TA meeting this week, but we managed to stay on schedule as we prepare for the end of the semester. Daniel worked on cleaning up unnecessary outputs and summarising important information when scanning a project. Jaxson implemented our first iteration of the user's resume generation, which summarises all contributions from all scanned projects into a markdown file that will later be used for converting the resume to other formats (PDF, HTML). Priyanshu worked on refactoring skills exercised chronologically. This enhanced our modularity of the codebase by removing this deliverable from the old database test file into its own file. Travis added a big upgrade to the usability of our program by adding a main menu that allows users to select which part of the application they want to use, instead of running different files. Tyler refactored our JSON/TXT output to automatically save to the output folder after performing a new scan. Code reviews were performed by all members. This was a strong week for our group. 

## Burnup Chart:
<img width="901" height="463" alt="Screenshot 2025-11-30 at 8 16 08 PM" src="https://github.com/user-attachments/assets/4468b695-a1fa-492e-b13a-9bcbfd0d3322" />

## Team Member's Completed Tasks:
### Daniel:
- Replaced noisy per-file printing inside of scan.py with a single line and run language/skill detectors via a captured runner so other noisy output is ignored
### Jaxson:
- Full resume generation feature that creates resume-ready Markdown files for a selected contributor by aggregating project exports stored under the output/ directory
- Team Logs for week 12
### Priyanshu:
- Refactored the Skills Exercised (Chronologically) logic out of inspect_db.py into a dedicated module, skill_timeline.py
### Tanner:
- Improved accuracy and coverage of the "detect programming frameworks" feature
- Updated data-access consent policy
### Travis:
- Full main_menu.py module that acts as a unified CLI interface for all major MDA features
### Tyler:
- Auto Output Key Information On Scan That Includes All New Analysis Info
### All Members:
- Code reviews and verification
- Completion of individual logs and peer reviews

## Testing Report:
All new and existing unit tests continue to pass successfully across both local and Docker environments. Validation was conducted through a combination of automated and manual testing.

#### `test_main_menu.py`  
- covers the deterministic and non-interactive portions of the module:
- print_main_menu() output
- safe_query() success and fallback paths
- human_ts() for standard, ISO, invalid, and None timestamps
- handle_inspect_database() using a temporary in-memory database

#### `test_generate_resume.py`
- Tests for normalize_project_name() including acronym preservation
- Tests for collect_projects() and aggregate_for_user() ensuring correct shapes and aggregation
- Tests for render_markdown(), including timestamp insertion and correct formatting

#### `scan_test.py`
- capture_output now returns both printed output and the function return value (output, rv).
- Tests assert on the returned data (rv) to verify which files were found.
- For entries from zip archives, tests split the display_path on ':' and take the last segment before using os.path.basename so comparisons match the new archive:path format.
- The collaboration test now calls get_collaboration_info(file_path) directly and asserts it returns 'unknown' when no git repo is present

#### `test_detect_langs.py`
- Removed the 3 pre-existing framework detection unit tests as they relied on deprecated logic that is no longer used
- Added 9 tests to ensure that detect_languages_and_frameworks() is accurately detecting 9 of the 18 supported frameworks by running detections on doctored config/package/dependency files
- I added 4 edge-case tests to ensure:
- Multiple frameworks can be detected in the same config/package/dependency file
   - No frameworks are detected when no config/package/dependency files exist in the project repository
   - Framework detections are performed case-insensitively (ie, "FLASK==version or flask==version" still detects as "Flask")

#### `consent_test.py`
- Hotfix that fixes a unit test within consent_test.py that was using deprecated Strings from the previous implementation of our data-access policy.
- Test ensures that when no strings are explicitly passed into describe_data_access(), it will return the default Strings that are hardcoded into the function.
- Now it checks that the four main headers from our updated data-access policy are found in the output. 

## Team Reflection:
This week, our team worked very well together. With the upcoming stress of Finals and end-of-semester projects coming to an end, we are making sure to complete our deliverables ahead of time to avoid unwanted stress. All members of the group were sufficiently active in our team's Discord chat and let everyone know what they were working on. All code was delivered in good time, and reviews were quick and with quality improvements and notes. We have been quite proactive with our preparation for the Milestone 1 presentation.

## Planned Activities (Week 14):
For week 14, we have discussed it as a team and decided that we hope to:
- Add finishing touches for Wednesday's Presentation
- Update System Architecture to reflect our current system
- Update Data Flow Diagram to reflect our current system
- Create Team Contract
- Milestone 1 Video Demo
- Milestone 1 Self-Reflection
