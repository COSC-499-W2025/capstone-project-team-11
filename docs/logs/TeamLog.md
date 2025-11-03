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

Code review and verification
 -Tanner, Jaxson, Priyanshu, Daniel, Travis


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







