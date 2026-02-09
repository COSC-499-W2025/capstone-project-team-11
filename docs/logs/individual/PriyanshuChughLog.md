# Week 3 Personal Log (15th-21st of September)

The big focus of this week was creating some of the requirements for our project as well and creating the repository. 


<img width="1512" height="982" alt="Screenshot 2025-09-21 at 12 51 56 PM" src="https://github.com/user-attachments/assets/ce22be10-f8f3-423e-929f-4f5996a88a33" />


## Tasks Completed:
I was involved with the following tasks either by myself or helping my peers.

- Helped out think of ideas for capstone requirments specifically usage scenarios and target users 
- Finished the Project requirements quiz 
- Did the Weekly log and individual log  



 # Week 4 Personal Log (22nd-28th of September)

 This weeks focus was creating the system architecture design and making the final project proposal.  

 <img width="1512" height="982" alt="week4logpic" src="https://github.com/user-attachments/assets/c17db5b7-4e4f-48f4-a483-8d12a377040c" />

## Tasks Completed:
I was involved with the following tasks either by myself or helping my classmates.

- Finalizing project proposal (issue #8)
- Worked on system architecture design (issue #9)
- Individual Logs Week 4 (issue #10)


 # Week 5 Personal Log (29th-5th of October)

This week we focused on creating level 1 and 0 data flow diagrams. We then updated our design with the feedback we recived from other teams, and by comparing our diagrams to other teams to see what we could improve/what we were missing
 

<img width="1512" height="982" alt="week5ss" src="https://github.com/user-attachments/assets/080f5072-eaa2-4f89-ba4a-1f39d282d39e" />




#  Tasks Completed:
- Week 5 Individual Logs (issue #14)
- Helped Design level 1 Data flow diagram (issue #16)
- Edidted level 1 DFD with peer/other groups feedback (issue #17)


# Week 6 Personal Log (6th-12th of October)

The week we focused on updating our system diagrams to reflect final requirements and also updating the read me to have links for the diagrams.

<img width="1512" height="982" alt="Screenshot 2025-10-12 at 11 40 08 AM" src="https://github.com/user-attachments/assets/1bcc05da-6ccd-4f76-88fe-d47d8514b1ec" />

## Tasks Completed:
- reviewed with team members on Work Breakdown Structure 
- Reviewed final WBS
-Update Repo README to have explanations and links to System Architecture, DFD, #pr 51
-Added WBS milestone 1 diagram to docs/proposal/wbs #pr 50
- reviwed created basic file scanning script #43



# Week 7 Personal Log (13th-19th of October)


 <img width="1512" height="982" alt="Screenshot 2025-10-19 at 5 36 47 PM" src="https://github.com/user-attachments/assets/513b3a68-25c9-4a02-a890-63a93e22be45" />

## Tasks Completed:
- Tested and reviewed Tanner's user configuration code (issue #26)


## In progress tasks
- Parse Complicated Zipped Folder (issue #22)

## Planned tasks for next sprint
- Parse Complicated Zipped Folder (issue #22)
- Data access consent (issue #21)
- Return errors for incorrect file types (issue #23) 

<img width="1512" height="982" alt="Screenshot 2025-10-19 at 5 41 25 PM" src="https://github.com/user-attachments/assets/780a3abc-7f44-4091-9062-d346928924c8" />

# Week 8 Personal Log (20th-26th of October)

This week, I implemented a new feature to automatically detect programming languages and frameworks within project directories. The new module, detect_langs.py, scans file extensions and configuration files (like package.json and requirements.txt) to identify frameworks such as Express, React, Flask, and more. I also created test_detect_langs.py to validate detection accuracy across multiple cases, including multi-framework projects, empty directories, and invalid inputs.
In addition to development work, I reviewed teammates pull requests,specifically the User Consent Module (PR #84) and Database Schema & Setup (PR #88) , providing feedback on structure, clarity, and integration with the existing system.


<img width="1512" height="982" alt="Screenshot 2025-10-26 at 6 53 00 PM" src="https://github.com/user-attachments/assets/4adfe1e2-ae24-4c8f-8183-99c583afa82c" />

## Tasks Completed

-Implemented Language & Framework Detection feature (detect_langs.py) (Issue #25, PR #91)

-Created unit tests for framework and language detection (test_detect_langs.py)

-Added  documentation and comments for clarity

-Reviewed User Consent Module PR (#84)

-Reviewed Database Schema and Setup PR (#88)

-Updated .gitignore to exclude __pycache__ folders

-Updated individual log and synced progress with the project board


<img width="1097" height="36" alt="Screenshot 2025-10-26 at 7 16 37 PM" src="https://github.com/user-attachments/assets/4176de1b-1b05-4b3f-ad1c-aceec0ca73c0" />


## Next Week (Week #9)

Begin development for Issue #31: Extract Key “Skills” From a Given Project — implement functionality to analyze a project’s outputs (such as code quality, test coverage, or writing accuracy) and infer an individual’s key skills.

Collaborate with teammates to clarify requirements and define measurable indicators for different skill domains (e.g., testing proficiency, documentation quality, or code structure).


# Week 9 (October 27th - November 2nd)


<img width="1056" height="621" alt="Screenshot 2025-11-02 at 8 31 01 PM" src="https://github.com/user-attachments/assets/2e4741ce-f360-4db6-95d7-6d40663d376b" />


## Tasks Completed
-Added skill extraction feature to detect technical and writing-based skills from scanned projects (issue #31).

-Implemented regex pattern matching to identify programming concepts like recursion, OOP, and async, as well as writing-focused skills such as analytical and technical writing.

-Integrated results with detect_langs.py to produce a combined summary of Languages, Frameworks, and Skills.

-Created unit tests in test_detect_skills.py to validate accuracy across mixed project types and ensure no false positives.

-Reviewed and approved code for Individual contributions within collaborative project issue(29) and Added functionality for ranking project scans chronologically issue (39)

-week 9 team log

-individual logs

  ## Week 10 plans

- Sort "Skills Exercised" Chronologically#40
- modify my past features with suggestions left on pull requests
- help the team out with prs and anything they might need help with 



# Week 10 Personal Log (Nov 3rd – Nov 9th)

This week, I implemented the feature for sorting skills exercised chronologically. I updated inspect_db.py so the database can display each detected skill in time order, along with the project where it first appeared. This lets us show how a user’s skills evolve across project scans. I tested the feature by running scans with save_to_db=True and verifying that the chronological output was correct, including edge cases where no skills are present.
I also spent time reviewing team pull requests,” Updated database functionality for all scanning functions” #131
and “Fix: file count always 0 & add per-author file tracking in collaboration summary “#133
Both reviews focused on verifying database consistency, preventing incorrect data in summary features, and making sure the new persistence layer supports upcoming analysis tools like this skills timeline. Overall, the week was productive and helped advance both stability and reporting features for the project.


<img width="1028" height="605" alt="Screenshot 2025-11-09 at 6 16 35 PM" src="https://github.com/user-attachments/assets/affed10e-3fca-47a4-bdc6-b5673e5fb734" />

## Tasks Completed
-Implemented chronological skill tracking by updating inspect_db.py to list skills in the order they first appeared across scans (PR #135)
-Tested new feature using multiple scan runs with save_to_db=True to verify correct ordering and fallback behavior
-Reviewed Updated Database Functionality for All Scanning Functions (PR #131)
-Reviewed Fix: file count always 0 & add per-author file tracking in collaboration summary (PR #133)
-Updated personal log and ensured progress was reflected on project board

<img width="1234" height="51" alt="Screenshot 2025-11-09 at 6 34 47 PM" src="https://github.com/user-attachments/assets/c60f1321-0f6b-4b0e-9373-9405601409a6" />


## Plans for Week 11
- Start modifying and improving past functions with suggestions of peers left on pull requests 
- Continue reviewing teammate PRs 
- Contribute to documentation updates


# Week 12 (November 17th - 23rd)

<img width="1509" height="811" alt="Screenshot 2025-11-23 at 5 01 11 PM" src="https://github.com/user-attachments/assets/fb3e58f8-f501-4e7d-aead-1ab27900300a" />

## Tasks Completed
Implemented the improved Skills Exercised (Chronologically — Grouped by Skill) feature in inspect_db.py.

-Groups duplicate skills under one header
-Sorts occurrences chronologically
-Repositions section for better readability
-Significantly reduces output length for users with many scans

Added code to:
-Build grouped skill dictionaries
-Format readable bullet-point timelines per skill
-Integrate with existing DB queries without breaking prior output
-Ensure timestamps are consistently formatted using human_ts

Reviewed Daniel’s project-importance ranking PR 

-Verified output from both contribution-summary functions
-Pulled the branch and ran tests locally
-Provided feedback on clarity, edge-case handling, and table readability

Reviewed Travis’s summarize_projects.py 

-Verified the manual Test A output
-Ran tests locally
-Provided structured feedback, suggestions, and readability considerations

Completed weekly logs and ensured all GitHub workflow tasks (commits, pushes, reviews) were properly done.

## Refelction
After  reading break we got straight back into the routine of things and did pretty good this week, I implemented some suggestions that were left on a pr from a few weeks ago which i'm pretty satifised with.Since the milestone deadline is coming soon, we should make sure we are all communicating well with each other.


## Week 13 Plans
To be honest not a lot of issues left to picked up and the quiz upcoming this week and some other classes will be taking a lot of time from my week .But I will be helping my peers with reviews or tweaking  functions and helping plan for the demo and making sure we are prepared it for it. 

# Week 13 (November 24th - 30th)

<img width="1511" height="756" alt="Screenshot 2025-11-30 at 8 06 48 PM" src="https://github.com/user-attachments/assets/984de644-8c0c-4bda-8b4b-0eae42dee8d4" />

## Tasks Completed
Refactored the Skills Exercised (Chronologically) logic out of inspect_db.py into a new skill_timeline.py module.
Updated inspect_db.py to use the new skills timeline module.
Added unit tests for the skills timeline feature.
Worked on the Milestone 1 presentation.
Individual logs.

## Reflection 
As a team, we focused on finalizing the remaining deliverables and refining key features. My main contribution was Refactoring the skills exercise chronlogically and adding unit tests for it. Overall, this was a good week as we moved into the final stretch before the deadline.
 
## Week 13 Plans
We are in the final week of the semester so there is a lot of tasks that need to be completed. I will be working on and helping others with updating our documentation and helping complete the  project for video demo. And also working on our presentation that we have in class on Wednesday,



# Week 14 (December 1st - 7th)

<img width="1131" height="640" alt="Screenshot 2025-12-07 at 4 31 28 PM" src="https://github.com/user-attachments/assets/cc2959ca-e380-4324-9b4b-c7b4d705f9b8" />

## Tasks completed:
- Worked on the milestone 1 presentation slides
- Presented milestone 1 in front of class
- Created a new Level 1 Data Flow Diagram that accurately represents the project’s Python CLI architecture, data stores, and workflow.
- Updated the entire README.md, replacing outdated Electron/FastAPI references with the current backend design.
- Added full module breakdowns, detailed test descriptions, and proper Markdown formatting.
- Improved overall documentation clarity and ensured consistency across sections (System Architecture, DFD, Src Folder, Test Folder, etc.).
- Individual logs
- Milestone 1 reflection quiz
- Approved and reviewed PRs

## Reflection
This week was very stressfull but our team managed to pull through, even with last minute bug issues and I was very pleased how we overcame this week 

# Week 1 (January 5th - 11th)

<img width="1058" height="625" alt="Screenshot 2026-01-11 at 5 32 59 PM" src="https://github.com/user-attachments/assets/a5dbd9f1-2d29-4c65-b247-d94722dba05e" />

## Tasks completed:
-worked on Recognize duplicate files and maintain only one in the system
-Designed and implemented a cleanup mechanism to ensure only the most recent scan for a project is kept.
-Added database maintenance logic to remove outdated scans along with their related files, contributors, and language links.
-Wrote and ran unit tests to ensure old scans are correctly removed and the latest scan data remains intact.
- Reviewed PRs
- Individual logs

## Reflection
In conclusion,this week went pretty decent since we all came back from a break and feeling rusty. We communicated well and started some new features.I was really happy with how our communication was this week espically coming back from a break.This was a positive week for the group as we try to improve our project.

## Week 2 plans
- start one of the issues we have in the kanban 
- Look into APIs and LLMs


# T2 Week #2 Personal Logs (Jan 12th - 18th)

<img width="1060" height="624" alt="Screenshot 2026-01-18 at 3 20 38 PM" src="https://github.com/user-attachments/assets/99f1d413-a488-47bb-9279-5894503a9e33" />

## Tasks Completed:
- Implemented support for custom project display names in résumé generation, allowing users to override default folder-based project names with résumé-friendly titles.
- Extended the database schema and access layer to persist and retrieve custom résumé display names without affecting existing project identifiers or file paths.
- Updated the résumé generation logic to dynamically apply the saved display name when rendering project sections.
- Added a CLI workflow that allows users to edit and manage project display names after generating a résumé.
- Wrote and executed unit tests to verify that custom project names are correctly saved, retrieved, and reflected in the résumé output.
- Verified that all existing tests pass and that the new feature does not introduce regressions.
- Closed issue #271.
- Contributed updates reflected in the team log.


### Reflection of the past week:
This week, we worked away on  Milestone 2 deliverables. Our communication was great and no problems there and we also had minimimal problems acomplishing our tasks and most of our code was done before late sunday night. Next week we will probably  plan to start on our LLM integration. 

### Additions and Features:
db.py: Added support for storing and retrieving custom resume display names for projects, including safeguards to ensure database paths are created correctly in test and local environments.

generate_resume.py: Updated resume rendering logic to apply user-defined project display names when generating the Projects section, while preserving existing normalization and fallback behavior.

main_menu.py: Introduced a CLI workflow that allows users to edit and manage project display names after generating a resume, with an option to re-generate the resume to apply changes.

### Testing:

test_generate_resume: Verified that resume aggregation and rendering correctly apply custom project display names, including fallback behavior when no override is set.

test_project_display_names: Added unit tests to ensure project display names can be saved, cleared, and retrieved from the database without affecting other resume or project data.

Regression testing: Ran the full test suite (pytest) to confirm existing resume, portfolio, and database functionality remained unaffected by the changes.

### Reviews: 
-  Jaxson's FastAPI Integration (PR #264)
- Travis's Integrate project evidence into resume/portfolio and update tests (PR #265)
- Daniel's Updated key roles to be project centric (Pr #267)

## In progress tasks
- Researching local LLMs for our project
- Planning on how to add more functionality to allow users to customize additional resume content beyond just project titles (for example, editing bullet points, summaries, or highlighted skills directly from the CLI)

## Planned tasks for next sprint
- add more functionality to allow users to customize additional resume content beyond just project titles (for example, editing bullet points, summaries, or highlighted skills directly from the CLI)

 <img width="1372" height="622" alt="Screenshot 2026-01-18 at 3 45 43 PM" src="https://github.com/user-attachments/assets/8c35c55c-4b72-4f2f-8945-66b0a4103211" />


# T2 Week 3 (January 19th-25th)

<img width="1071" height="608" alt="Screenshot 2026-01-25 at 3 29 37 PM" src="https://github.com/user-attachments/assets/5ad02f7a-2aa3-4be0-a5dd-08384e6f62d4" />

## Overview 
This week I focused on both feature development and peer testing. I merged a resume customization feature that allows users to control how project names appear on resumes, improved the professionalism of resume output, and reviewed and tested several major PRs related to Docker, scanning, and DB backed resume/portfolio generation.

Key contributions this week:

Merged PR #294 Add project resume display name editing

Implemented resume output cleanup to remove non resume friendly metadata

Reviewed and tested multiple high-impact PRs related to Docker, scanning, and generation

Closed issue #293

Closed issue #309

 ## Reflection
The team collaborated really well this week, especially around peer testing and large refactors. A lot of time was spent verifying whether reported issues were reproducible versus already resolved, which helped prevent unnecessary fixes. Communication during reviews was clear and constructive, and the team handled several large changes without breaking existing functionality. Overall, the workflow felt organized and productive.

## Coding Tasks:
Implemented custom resume display names per project by adding a custom_name column to the projects table.

Added a new CLI workflow allowing users to view, set, update, or clear resume facing project names without rescanning.

Updated resume generation to prefer custom names when present, with a safe fallback to default project names.

Ensured the change was non-breaking and backward compatible.

Resume output cleanup :

Removed local filesystem paths from generated resumes, as these are environment specific and not appropriate for a professional resume.

Removed low level Git metrics (commit counts and number of files changed) from individual project bullets to keep resumes focused on skills and contributions rather than raw implementation details.

Ensured resume output emphasizes technologies used, skills demonstrated, and high level contribution descriptions.

## Testing and Debugging:
Ran the full pytest suite locally after resume display name and resume cleanup changes (213 passed, 1 skipped).

Manually tested resume generation to confirm:

Custom project names render correctly

Removed metadata no longer appears in resume output

Resume structure remains unchanged otherwise

Investigated a peer reported issue claiming chronological skills could not generate when the skills table was empty.

Reproduced the setup by scanning a real project, deleting all rows from the skills table, and generating a resume.

Verified that resume generation succeeds and gracefully skips the chronological skills section when no skills are present.

Determined that an earlier crash only occurs when the database has no scans (missing git metrics), not due to an empty skills table.


## Reviewing and Collaboration
Reviewed, tested, and provided feedback on the following PRs:

#288 – Docker updates & test suite refactors
Built Docker containers locally, ran the full test suite inside Docker, verified CLI and API startup, and confirmed test discovery improvements. Suggested adding a reload option for the API container during development.

#291 – Fix portfolio generation to exclude non contributor projects
Ran tests and performed manual scans to confirm portfolios only include projects the selected user contributed to. Verified metadata only projects still appear correctly.

#292 – Reworked scan to fix nested folder scans
Tested nested folder scenarios locally and reviewed changes to multi project detection, contribution summaries, and DB persistence. Confirmed scanning behavior is more reliable for mixed git and non-git directories.

#297 – Reworked resume/portfolio generation to take info from DB
Reset the database, ran scans, and verified resume/portfolio generation no longer depends on filesystem JSON output. Confirmed new DB fields are populated correctly.

#298 – Resume/Portfolio tests update after rework
Verified all tests pass locally (214 passed), confirmed temporary DB seeding works correctly, and ensured generation tests align with the new DB-first flow.

## Issues and Blockers
No main issues or blockers.

## Plans for next week
- Prepare for peer testing #1.
- Fix existing bugs from Milestone 1 feedback.
- Continue researching LLMs.

# T2 Week 4/5 Personal Logs (Jan 26th - Feb 8th)

<img width="1123" height="641" alt="Screenshot 2026-02-08 at 8 22 57 PM" src="https://github.com/user-attachments/assets/f2e07d8c-7244-4454-9647-bef9d9192fb0" />


## Overview
Over the past two weeks, my work focused on fixing and standardizing core CLI input flows, especially around path validation, username/identity selection, and resume/portfolio generation. The goal was to make user input handling predictable, reusable, and consistent across the system, while reducing crashes, silent failures, and confusing control flow. A large part of this effort involved refactoring duplicated logic into shared helpers, tightening validation against database-backed data, and adding tests to lock in correct behavior.


## Coding Tasks
introduced shared CLI path validation helpers to standardize how project paths and zip inputs are checked before scanning (PR #345).

Refactored username selection into a shared helper used by both resume and portfolio generation to prevent invalid or arbitrary usernames from being accepted (PR #356).

Extended CLI input validation to fully align resume and portfolio behavior, including blacklist handling, early failure for invalid usernames, and clearer error messages (PR #360).

Implemented a unified identity selection flow allowing users to:

Select a valid git contributor

Use a local/guest (non-git) mode

Optionally include non-git projects alongside git-based output (PR #361).

Cleaned up control flow and comments across affected files to make validation logic easier to follow and maintain.

Closed issue #336.



## Testing and Debugging
Added targeted unit tests for shared helpers, including:

cli_validators.py path normalization and validation

cli_username_selection logic and edge cases

Ran the full pytest suite locally after each PR to ensure no regressions were introduced.

Manually tested CLI flows through the main menu for:

Resume generation

Portfolio generation

Valid and invalid usernames

Blank inputs and cancel paths

Guest/local-only generation

Verified that invalid input consistently re-prompts instead of crashing or dumping the user back to the main menu.



## Reviewing and Collaboration
Reviewed and provided feedback on the following PRs:

Travis — Refactor summarize_projects.py to use database-backed data only (PR #326)

Tanner — Standardized error handling for core functionalities (PR #346)

Tanner — Reworked Thumbnail Feature (PR #347)

Jaxson — Improved error handling based on teammate feedback (PR #351)

Feedback focused on correctness, control flow consistency, test coverage, and alignment with existing CLI behavior.


## Issues / Blockers
No major blockers during this period.

Some care was required to avoid changing output formats or database structure while refactoring input flows.

Coordinating overlapping CLI changes required frequent rebasing and validation to avoid merge conflicts, especially around main_menu.py


## Plan for Next Week


Build on the identity selection flow to support more granular project selection.

Continue tightening CLI UX edge cases now that a stable validation base is in place.

Assist with final Milestone 2 polish and testing as features converge.
