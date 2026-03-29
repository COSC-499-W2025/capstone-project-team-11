# Term 2 Navigation:
- [T2 Week 1](#t2-week-1-january-5th---11th)
- [T2 Week 2](#t2-week-2-logs-january-12th---18th)
- [T2 Week 3](#t2-week-3-january-19th-25th)
- [T2 Week 4 and 5](#t2-week-4-and-5-january-26th--february-8th-2026)
- [T2 Weeks 6–8](#t2--weeks-6-7-and-8-february-9th---march-1st)
- [T2 Week 9](#t2-week-9-march-2nd---march-8th)
- [T2 Week 10](#t2-week-10-march-9th---march-15th)
- [T2 Week 11-12](#t2-week-11--12-march-16th---march-29th)

# Week 3 Personal Log (15th-21st of September)

The main focus of this week was creating some requirements for our project as well as creating the repository. 


<img width="1068" height="619" alt="image" src="https://github.com/user-attachments/assets/6ce78cc8-0eaa-4d5b-995e-cac20ae1a576" />

## Tasks Completed:
I have been involved with the following tasks either alone or helping my other classmates.

- Project requirements doc was created and then printed out for exercise in class.
- Project requirements quiz was completed.
- Established communication platform for group members.
- Weekly log 


# Week 4 Personal Log (22nd-28th of September)

The main focus of this week was creating our system architecture and our project proposal. These are two crucial activities that force us to start thinking about the logistics of the project.

<img width="1594" height="914" alt="image" src="https://github.com/user-attachments/assets/700fc97b-dafb-4f5d-a25f-8117a05e618f" />


## Tasks Completed:
I have been involved with the following tasks either alone or helping my other classmates.

- Project proposal doc was created and finalized.
- Worked on system architecture touch ups.
- Reworked system architecture after receiving and giving feedback to others.
- Personal log.

# Week 5 (September 29th - October 5th)

The main focus of this week was creating our Data Flow Diagram level 1. This is a very important step of designing an application because it demonstrates how the processes will work and flow together. 

<img width="1601" height="939" alt="Screenshot 2025-10-05 140230" src="https://github.com/user-attachments/assets/02317e1a-b0d4-4e90-90b9-a565c9a5c75c" />

## Tasks Completed:
I have been involved with the following tasks either alone or helping my other classmates.

- Providing first draft of DFD level 1 before class to use for reference.
- Gained and gave feedback to other teams on their DFDs.
- Reworked and finalized our DFD.

# Week 6 (October 6th - October 12th)
This week we priotized reworking our system architecture and began starting simple coding in order to perform a scan on files.

<img width="1590" height="918" alt="image" src="https://github.com/user-attachments/assets/dfc6fa88-6be5-49ad-beab-9aef2fc93d22" />

## Tasks completed
I have been involved with the following tasks either alone or helping my other classmates.
- Helped Jaxson with starting an initial scan program which he completed.
- Looked over and tested his code to ensure it was clear and concise.
- Added additional details to the scan which displays details about the files scanned.
- Wrote tests for the scan details.
- Completed week 6 logs.


# Week 7 (October 13th - October 19th)

<img width="814" height="474" alt="image" src="https://github.com/user-attachments/assets/3da688b0-f75c-4a6a-9454-81b2ba3093cc" />

## Tasks Completed
- Reworked and updated the Reamde in order to be more informative and legible for Assignment Repo Readme Content #1.  (issue #68)
- Tested Tanner's user configuration code.  (issue #26)
- Reviewed Jaxson's pull request for adding to the Readme.

## Tasks in progress
- Parse Complicated Zipped Folder (issue #22)

## Planned tasks for next sprint
- Parse Complicated Zipped Folder (issue #22)
- Data access consent (issue #21)
- Return errors for incorrect file types (issue #23)
<img width="1884" height="708" alt="image" src="https://github.com/user-attachments/assets/c9a9e0f4-3801-45ac-9a36-14645505a189" />



# Week 8 (October 20th - October 26th)
<img width="1610" height="924" alt="image" src="https://github.com/user-attachments/assets/44760cb3-06c0-4233-ba64-afbff1311533" />

## Tasks Completed:
- Determine if projects are collaborative or individual. Added code in scan.py that determines if a scanned folder is a git repo, if it is then it lists the authors alongside every file that they worked on which also works on zipped files. If it is an individual folder (ie. not a git repo) then it displayhs unknown author next to each file. (Issue #27)
- Added tests for the collaboration feature.
- Reviewed code for file format validation (Issue #23)
- Completed the team log for week 8
- Completed individual logs for week 8

## Week 9 Plans:
- I will look into issue #29: "Identify Individual Contributions Within a Collaborative Project" alongside Travis by helping him since I started the identification of collaborative projects.
- Look into issue #30: "Extract key contribution metrics within a project"
- Continue to review PRs.
- Help verify system-wide functionality with current features implemented.



# Week 9 (October 27th - November 2nd)

<img width="790" height="466" alt="image" src="https://github.com/user-attachments/assets/c2e0e25d-3b1f-4ca3-ade1-b2a5fab9460c" />


## Tasks Completed
- Added contribution metrics extraction and printing (issue #30)
  - project start/end/duration.
  - total commits and commits-per-author
  - lines added/removed per author
  - activity counts by category (code/test/docs/design)
  - commits-per-week
- Tests for contribution metrics
  - contrib_metrics.py: new/modified logic (parsing, flush at commit boundaries, name normalization)
  - contrib_metrics_test.py: new tests, robust cleanup, resilient assertions
- Reviewed and approved code for extracting skills from a scan (issue #31)
- Individual logs

## Week 10 plans
I will be very busy with several midterms this week so I will be a little limited with the work I can do however, I will continue to improve contribution metrics in order to fix the following bugs:
- Collaboration data does not save from previous scan when user saves info
- Contribution metrics do not save from previous scan when user saves info

I will also continue to help review prs and complete my logs. 


# Week 10 (November 3rd - November 9th)

<img width="1598" height="904" alt="image" src="https://github.com/user-attachments/assets/946eddbb-63f0-4a30-a65b-0fd9b7ce04b4" />

## Tasks completed
- Reworked the contribtuion metrics to try and create a robust consistent naming conventions for users in a github repository.
- Added a function canonical_username which automatically normalizes author identity for any git repo.
- I added a feature which does not display an author of a github repo if they have 0 commits.
- Added more tests for contribution metrics
  -  test_commit_with_no_file_changes: Commits that make no file changes (empty commits)
  -  test_file_categories: Files in different categories: code, test, docs, design
  -  test_zero_commit_user_excluded: Users with zero commits added manually
- Reviewed Tyler's code and pr
- Individual logs


## Reflection
Overall this was less of a productive week for myself and for some other team members due to business from other classes. We communicated well and were honest with what realistic task we could get done this week and we stuck to that plan well. Nevertheless, I probably could have tried to set aside a little more time to work and my pull request was a little last minute on a Sunday. Nonetheless, I think we had a good week considering the factors outside of this course.


## Week 11-12 Plans:
The next sprint will be important going forward since our milestone 1 demo is coming up shortly. During this week I would like to get started working on the ranking of projects based on importance. This will be a big tasks that will need to be done in order to further enhance the project. 



# Week 12 (November 17th - 23rd)
<img width="1602" height="938" alt="image" src="https://github.com/user-attachments/assets/71f38a8c-f0af-4216-a6ae-62b68d05b80a" />

## Tasks Completed
- Added feature that ranks importance of a project based on user contributions. It displays the projects based on the info:
    - Project: project key/name.
    - TotalFiles: total number of files recorded for that project
    - Contributors: number of distinct contributors recorded for files in that project.
    - TopContributor: contributor name with the largest number of files they are linked to within the project.
    - TopFiles: number of files the top contributor is linked to.
    - TopFraction: TopFiles / TotalFiles (a float 0.00–1.00). Shows how concentrated the project's files are with that single contributor (1.00 means the top contributor owns all recorded files).
 
- Created two main contribution functions:
    - rank_projects_contribution_summary: is project-centric, it summarizes, for each project, how contributors are distributed and who the top contributor is. It is useful when you want an at-a-glance view of how contribution is distributed across projects.
    - rank_projects_by_contributor: is specific contributor centric, it summarizes, for each project, the contributions of the specific user for all the projects.
- Added sufficient testing for the feature.
- Reviewed Travis and Tanner's prs
- Individual logs.

## Refelction
After a relaxing week for reading break, we came back as a team and started to gain momentum. Overall, I believe I had a pretty productive week by completing another feature that will contribute towards completing milestone 1. The deadline is rapidly approaching so as a group we have to come together and devise a plan especially for the upcoming presentation.

## Week 13 Plans
There are not a lot of major tasks left to be picked up in the Kanban board and there will be more focus on the quiz and the informational lecture on Monday. Beyond this, I will start working on ideas for the milestone 1 demo that is coming up. I will also be around to review and help others with minor updates and features left to add. 
   
# Week 13 (November 24th - 30th)

<img width="1602" height="928" alt="image" src="https://github.com/user-attachments/assets/0d0e5023-d110-4f94-bd3a-e3d0c0432a9c" />

## Tasks Completed
- Reworked the output of a scan by removing the output of all the files that get scanned.
  - scan.py: main implementation changes that adds a progress load bar during a scan (progress UI,captured detector execution, quiet zip/directory scanning, concise stats).
  - scan_test.py: updated unit tests to assert on returned structured scan results rather than printed filenames; handle zip-style file paths when asserting basenames.
- Worked on the Milestone 1 presentation.
- Reviewed Travis's and Jaxson's pull requests.
- Individual logs.

## Reflection 
As we approach the deadline for Milestone 1, as a team we worked towards finalizing the last deliverables and improve certain features. I  mainly focused on cleaning up the cluttered and noisy output of scans with a loading bar which vastly the readability and iterpredibility. Overall this week was productive for all of us as we transition towards the final week before deadline.

## Week 13 Plans
This is the final week of the semester so we have a lot of tasks that need to be completed. I will be working and helping others with the presentation in class on Wednesday, updating the documentation (DFD, System Architecture, etc.), finalizing project for video demo.


# Week 14 (December 1st - 7th)

<img width="800" height="472" alt="image" src="https://github.com/user-attachments/assets/b6459a8c-aa27-4dbd-997f-83adbdb39976" />

## Tasks completed:
- Worked on the milestone 1 presentation slides
- Presented milestone 1 in front of class
- Reworked the feature to distinguish an individual project vs a collaborative project.
  - Added determine_project_collaboration() function in scan.py that checks git history.
  - Returns "Collaborative" if project has 2+ unique authors, "Individual" otherwise
  - Integrated into scan output to display project type at the end of scanningAdded get_project_collaboration_status() in rank_projects.py to count distinct contributors per project from database
- Fixed the following failing tests
  - test_zip_scan_persists_nested_files
  - test_nested_zip_file_paths_are_recorded_with_zip_colon_format
  - test_cli_saves_resume_to_db
  - test_print_projects_output
- Created the group contract.
- Milestone 1 reflection quiz
- Approved and reviewed PRs
- Individual logs


## Reflection
This is the final week of the semester and the deadline for milestone 1. It was a very stressful week with lots of things that needed to get done such as small bugs for features that were hard to film the demo for, the presentation in front of the class, and all the documentation to update and add. Overall, as a team we worked really hard and collaborated very well. Everyone was around to help out and there were no issues in finishing the final touches of the project for this first milestone. I am very pleased how we worked together and were able to get the work done!

## Winter Break plans
Sleep and relax. Potentially look into APIs and LLMs to integrate.

<br></br>
# Milsestone 2
<br></br>


# T2 Week 1 (January 5th - 11th)
<img width="799" height="466" alt="image" src="https://github.com/user-attachments/assets/749d4e4d-0293-4f1b-9ba3-0804a918cbb7" />

## Tasks completed:
- Worked on identifying key roles of a project
  - Heuristic Role Classification
  - Role Pattern Mapping
  - Contribution Breakdown Analysis
 - Reviewed PRs
 - Team log
 - Individual logs

## Reflection
Overall, this week went pretty well considering we are all coming back from a long break. We all communicated well and were able to push a couple new fetures and lay down the foundation for future improvements. We also took a look at some features from milestone 1 that appeared to lose us some marks which we will address in our weekly checkin this week. This was a positive week for the group as we strive to improve our project.

## Week 2 plans
- Integrate key roles of users into the menu
- Look into APIs and LLMs to improve insights. 


# T2 Week 2 Logs (January 12th - 18th)
<img width="798" height="458" alt="image" src="https://github.com/user-attachments/assets/0920c733-8ab2-4cbb-bf7a-a2dd8f19ce9d" />

## Overview
This week I continued to work on the key roles feature by adding a feature to make it more project centric. Previously it would give a user a role for a combination of all their projects in the database but now there is a feature that shows the role of each user in each project specifically. Additionally, this feature was seperated from the main menu so I added it there with the sufficient menu testing and testing for updates to the key roles feature.

- Closed issue #266

## Refelection
Overall the team was pretty organized and were able to communicate with each other productively. Team members delivered on new features or improved on existing ones and reviews were conducted quickly and professionally. For the most part, all code was pushed and reviewed before late Sunday. 

## Coding Tasks
- Updated key roles to be project centric #267
    - Added load_contributors_per_project_from_db() function to query and analyze contributor roles on a per-project basis
    - Updated [format_roles_report() to accept optional per-project data and display a "PER-PROJECT CONTRIBUTIONS" section
    - Report now shows both overall contributor roles and individual project breakdowns with condensed metrics
    - Added new menu option "11. Analyze Contributor Roles"
    - Updated exit option from 11 to 12

## Testing and Debugging
- Added tests for updated project centric key roles and main menu tests
- Tests validate:
    - Report formatting with/without per-project data
    -  Multiple contributors across projects
    -  Empty project handling
    -   Role differences across projects
    -  Overall analysis without per-project
    -  Per-project breakdown display
    -  Multiple contributors
    -  Metrics display validation

## Reviewing and Collaboration
- Jaxson's FastAPI Integration #264
- Pri's Feature/custom project wording clean #271

## Issues and Blockers
- No main issues

## Planned Tasks for next Sprint
- Fix zip file github project bugs.
- LLM integration

# T2 Week 3 (January 19th-25th)

<img width="802" height="464" alt="image" src="https://github.com/user-attachments/assets/16e6ca72-b49d-44c8-b92a-d59bc53f41c2" />

## Overview 
This week I reworked some features of the scanning logic in order to make it possible to scan nested folders and nested zip files. Before, it would treat zip files as one project although there could be multiple projects inside so I worked on the scan so that if there are multiple projects nested, they will all get scanned individually and be stored in the database individually. This implementation fixes a big flaw in our core scanning process and allows for more coverage if people want to scan multiple things at once. 

- Closed issue #289

## Reflection
Overall the team worked really well together this week. During our checkin we discussed the peer testing coming up and what our priorities should be for that. We all communicated very well and even helped each other out in times of need. I want to give Tanner a big shoutout because he helped me fix a bug with my zip scanning feature and was very helpful, quick to respond, and respectful. We will take this momentum into the next week especially for peer testing. 

## Coding Tasks:
- Reworked Scan to fix nested folder scans PR #292
  - Enhanced zip scanning to use extracted_locations when mapping files to repositories so nested projects are persisted correctly.
  - Updated both zip and directory scans to persist one DB scan per detected project.
  - Reworked all identify_contributions consumers to support the new nested structure.
  - Cleaned summary output, no empty/Unknown entries, authors ordered by commit count
  - Added _find_candidate_project_roots fallback to treat multiple top-level folders as independent projects when .git is absent (e.g., unzipped exports).

 ## Testing and Debugging:
 - With Tanner's help we removed bugs within resume generation caused by the new scan structure and the outputting the JSON and txt data.
      - Removed redundant loop from generate_resume.py's username collection logic
      - Restructured code in both generate_resume.py and generate_portfolio.py to ensure parity between the files, in both code structure, spacing, and comments
      - Added "Unknown" to the list of blacklisted usernames
  
 - Added tests for nested folders #PR 300
      - test_deeply_nested_folders_recursive: Tests recursive scanning through 4 levels of nested folders
      - test_deeply_nested_folders_non_recursive: Ensures non-recursive mode only scans root level
      - test_nested_folders_with_various_file_types: Tests filtering by file type (e.g., .py) across nested folder structure
      - test_nested_zip_with_multiple_levels: Tests zip files nested 3 levels deep (zip within zip within zip)
      - test_nested_zip_preserves_path_structure: Confirms nested zip paths use proper colon-separated notation
      - test_mixed_nested_folders_in_zip: Tests deeply nested folder structures inside zip files (e.g., src/main/java/App.java)
      - test_empty_nested_folders: Handles edge case of deeply nested empty folders
      - test_nested_zip_with_empty_folders: Handles zip files containing empty directory entries

## Reviewing and Collaboration
- Travis' Fix portfolio generation to exclude non-contributor projects #291
- Pri's Add project resume display name editing #294

## Issues and Blockers
No main issues or blockers.

## Plans for next week
- Prepare for peer testing #1.
- Fix existing bugs from Milestone 1 feedback.
- Continue researching LLMs.

# T2 Week 4 and 5  (January 26th – February 8th, 2026)

<img width="798" height="473" alt="image" src="https://github.com/user-attachments/assets/84dbb29b-d80c-4fc6-9095-cfd17d40a7fa" />

## Overview:
For the past two weeks I have been reworking features in preperation for Peer Testing 1 and then reworked features after receiving some feedback from Peer Testing 1. Leading up to the peer testing I looked at some of the suggestions where we lost marks in Milestone 1 and I reworked the way we rank importance of a project by expanding the formula to consider other factors rather than just files touched. I also made the key roles a project more clear by changing the naming conventions, adding descriptions to the roles, and showing the responsibilities of each role. The user has the option to view all the roles with descriptions and responsibilities before getting the real data of users scanned to ensure transparency and make it clear to the user. Lastly, I added a feature that allows a non git project to have a contributor. Previously, we could only extract contributors from git projects however, now the user can assign an existing contributor to a project or create a new contributor to assign to projects. 

Closed issue #358, #305, #320


## Reflection
Overall, the team worked really well these past two weeks and showed professionalism for Peer Testing 1. Leading up to the peer testing we got some last minute feature improvements in that helped us make things clearer to the people who tested our project. During the peer testing we all took solid notes and communicated the issues that we all came across and put that into a list. With that information we spent week 5 fixing some of those issues and integrating new features. All in all, the team was very effective and worked together solidly. 

## Coding Tasks
- Non git contributor (PR #359, Issue #358)
    - This PR introduces adding contributors or assigning existing contributors if the file being scanned is not a git project and doesnt offer git data.
    - Users can select existing contributors by number or name. New contributors can be added with clear duplicate detection and prompts.
    - Updated contributor prompt flow with strict re‑prompting and “Add new contributor.”
    - Applies assigned contributors to file ownership for non‑git scans.

- Reworked key roles of a project to be clearer and more in depth (PR #322, Issue #305)
    - Roles are now designed to be easier to understand for both technical and non-technical users.
    - Each role represents a well-defined area of contribution rather than a vague title, reducing ambiguity in generated reports.
    - Role assignments now include detailed context such as descriptions, responsibilities, and confidence levels.
    - Users can explore all available roles directly from the CLI, helping them understand how the system classifies contributors.
    - Contributor role reports are more readable and informative, surfacing meaningful context instead of just labels.

- Contributor score fix (PR #321, Issue #320)
    - Added TopScore as a composite score (coverage + dominance gap + team-size factor) for project-level contribution summaries.
    - Updated project ranking to sort by TopScore instead of individual metrics, improving consistency and interpretability.
    - Clarified CLI output and help text to explicitly describe TopScore and TopFraction, aligning terminology with contributor-level scoring.
    - Updated contributor ranking tests to match the composite score formula and prevent regressions

## Testing and Debugging
- Updated failing tests due to changes to contributor score formula change
- Updated failing tests due to more in depth changes to key roles of a user.
- `test_contributor_prompt.py`
    - `test_prompt_selects_existing_and_new`: Checks that the prompt correctly returns a combination of selected existing contributors and a newly entered contributor.
    - `test_prompt_selects_existing_only`: Verifies that the prompt returns only the existing contributor chosen by the user.
    - `test_prompt_adds_new_only`: Ensures that the prompt correctly handles the creation of a new contributor when no existing contributor is selected.
 
## Reviewing and collaboration
- Travis' Remove CLI file-extension prompt and fix resume blacklist enforcement #370
- Tyler's Removing depreciated code (9. generate project summary report) #368
- Tyler's Completed Deleting Output Folder Projects On Database Clear #367
- Travis' Improve Evidence of Success naming and clarity #366
- Jaxson's Integrated LLM summary #357
- Tanner's Improved scan progress CLI output#354
- Tanner's Implemented a scanned project TXT summary manager in the CLI #352
- Tanner's Improved error handling based on teammate feedback #351
- Jaxson's Update to main menu #323

## Issues and Blockers
No issues or blockers.

## Plans for week 6
- Add per user filtering for git contributions.
- Work on customizing what information a user wants (ie. being able to customize the order of rankings)


# T2 # Weeks #6, #7, and #8 (February 9th - March 1st)

<img width="797" height="467" alt="image" src="https://github.com/user-attachments/assets/a0b4bc5f-7ba5-4655-b366-476f4f5bb74e" />

## Overview:
The last 3 weeks have been a long haul with plenty of new additions and progress made to the project. In week 6 I spent my time working on the deliverable that allows user to customize what information they see. For this I made a feature in rank projects that allows a user to make their own custoom rankings of projects. They can make a ranking in any order they want and give that ranking a name. An example of this is a user ranking their favourite projects. In week 7 I did not have any code contributions because of reading week. Moving forward to week 8, I worked on getting ready for the Milestone 2 presentation and introducing some basic UI designs for the future. 

Closed issue #232, #393

## Reflection
Overall the team worked pretty well together for the past 3 weeks. Some people were working extra hard especially Jaxson since he was doing some work over the break. The team communicated very well and had several meetings outlining the plans for the week and to coordinate the Milestone 2 presentation. All in all, the team worked hard and collaborated effectively to get to the end of Milestone 2. 

## Coding Tasks
- Added custom rankings [PR #383](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/383)
     - Added support for custom project rankings so users can create their own ordered project lists (e.g., favorites) without affecting existing automated ranking logic.
     - Implemented helper functions to manage rankings, including creating, retrieving, renaming, deleting, listing, and displaying custom rankings. These operate independently from the current ranking systems
     - Users can:
       -  View saved rankings.
       -  Create rankings by specifying project order.
       -  Edit rankings (rename and/or reorder).
       -  Delete rankings with confirmation.
- Added basic main menu UI template [PR #394](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/394)
   - Implemented hash-based page routing in App.jsx (#/main-menu switches between Home and Main Menu)
   - Added Main Menu dashboard layout with:
       - Header: “Capstone MDA Dashboard”
       - Left menu actions: Scan Project, View/Manage Scanned Projects, Generate Resume, Generate Portfolio, Rank Projects, Summarize Contributor Projects
       - “Back to Connection Test” button
       - Right-side overview cards: Scanned Projects, Contributors, Generated Outputs
       - Quick Help, Project Information, and Suggested First Steps panels
    - Added “Go to Main Menu” button on the Home/connection page.
    - Full styling applied in index.css for dashboard layout, including grid layout, sidebar/content cards, buttons, responsive design, and theme/background.
 

## Tests and Debugging

- `App.test.jsx` Navigation tests: 
    -  Navigate to Main Menu when “Go to Main Menu” is clicked
    -  Render Main Menu directly when initial hash is #/main-menu.
    -  Navigate back to Home when “Back to Connection Test” is clicked.
- `test_rank_projects.py:
    -  `test_custom_ranking_save_load_and_list`: Creates a temporary DB, saves a custom ranking, reloads it to verify the order is preserved, and checks that it shows up in the saved rankings list.
    -  `test_custom_ranking_rename_and_delete`: Saves a ranking, renames it and verifies the renamed entry is retrievable, then deletes it and confirms it’s removed.


 
## Reviewing and Collaboration
- Tanner's New scan entry point improvements and bug-fixes [PR #380](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/380)
- Tanner's Updated scan.py test suite to cover new functionalities [PR #381](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/381)
- Pri's Improve CLI username selection retry flow and standardize error output [PR #384](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/384)
- Travis' Frontend: Initial Electron + Vite scaffold + backend connection test [PR #392](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/392)
- Pri's Add toast notifications and active sidebar highlight to dashboard UI [PR #403](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/403)

  
## Issues or Blockers
No issues or blockers

## Plans for Milestone 3
- Continue work on designing the UI
- Integrate the visualization of our backend
- Have a fully functional application 


# T2 Week 9 (March 2nd - March 8th)

<img width="797" height="470" alt="image" src="https://github.com/user-attachments/assets/77185df3-4fc8-41be-8280-6565fdeee29d" />

## Overview
This week I spent my time working on developping some more frontend features on top of our existing backend. Previously I had made a simple UI template for a main menu and this week I decided to implement the rank top projects page. It handles the backend through new API endpoints that I made for getting the ranked projects by importance or chronologically. The UI/UX is pretty simple and plain so that is something that we will work towards making look nicer in the future. For now my goal is to get basic implementation of all our previous features and then improve the styling later before the finishing touches. 

Closed Issue: #414

## Reflection:
Overall the team worked pretty well but all the work was crammed in and finished in the latter portion of the week. Most PRs were being made sometime on the weekend or close to the weekend. Nevertheless, the team communicated well get PRs merged and features were completed. 

## Coding Tasks
- Created Rank Projects Page [PR #419](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/419)
  - New frontend page: RankProjectsPage.jsx with ranking controls, explanation panel, summary cards, and results table.
  - New endpoint GET /contributors: returns sorted contributor names.
  - New endpoint GET /rank-projects: returns ranked project data with filtering and sorting options.
  - Routing updates: Added #/rank-projects hash route and menu navigation in App.jsx.
  - Styling updates: Added ranking page layout and UI styles in index.css.
- Fixed missing } bugs that causes compile error in Development [PR #420](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/420)
  - Fixed tiny error caused by resolving merge conflicts
 
## Tests and Debugging:
`App.test.jsx`:
- Navigation from the main menu to Rank Projects.
- Returning from the ranking page to the main menu.
- Toast messages for unimplemented menu items.

## Reviews and Collaboration
- Travis' Create initial resume generation page [PR #422](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/422)
- Tanner's Initial web portfolio generation functionality [PR #421](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/421)
- Pri's Add scanned projects page and navigation test [PR #418](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/418)
  
## Issues and Blockers
- A couple of merge conflicts when creating PRs.

## Plans for week 10
- Improve ranking feature based on suggestions from team.
- Implement new features for resume generation or viewing,



# T2 Week 10 (March 9th - March 15th)
<img width="871" height="592" alt="Image" src="https://github.com/user-attachments/assets/690cd937-3338-4be9-8fbb-86eac8a4419c" />

## Overview
This week I completed two pull requests that expanded project analysis and ranking features. The first PR added contributor role analysis to project details, including backend role computation and frontend UI updates to display contributor roles, confidence levels, and team composition. The second PR implemented a custom project ranking workflow, allowing users to create, save, view, and delete personalized rankings with a title, description, and ordered project list, supported by new backend API endpoints and UI components.

Closed issue: #414, #413


## Reflection
This week we improved the communication professionalism in terms of getting PRs up and merged. Previously we ran into quite a lot of merge conflicts because we left PRs open too long or would all do work at the end of the week. This week we spaced the work out and communicated well. This helped us make major strides in progressing the project and great.


## Coding Tasks
- Added custom ranking UI [#442](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/442)
  - Save as Custom Ranking section (title + short description)
  - Saved rankings list with view/collapse and delete
  - Expandable saved ranking table view
  - Custom rankings now store name, description, and ordered project list
  - New endpoints:
      - GET /custom-rankings
      - POST /custom-rankings
      - GET /custom-rankings/{name}
      - DELETE /custom-rankings/{name}

- Added key roles UI [#450](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/450)
  - Contributor role analysis is now computed and included in project details.
  - Extended the GET /projects/{project_id} response to include the contributor_roles field.
  - The Scanned Projects details page was refactored to improve layout, readability, and component reuse.
  - Added and updated CSS classes in index.css to support the new layout

 ## Tests and Debugging
`ScannedProjectsPage.test.jsx`
 - Verified the Contributor Roles section renders in the project details panel.
 - Confirmed a contributor’s primary role is displayed correctly.
 - Checked that confidence values (e.g., Confidence: 82%) appear in the UI.
 - Verified the Team Composition summary section is displayed.
 - Ensured existing features like edit and delete project actions still work after the UI refactor.

`RankProjectsPage.test.jsx`
- Verified users can create a custom ranking with a title and description.
- Confirmed projects can be reordered to define ranking order.
- Checked that a ranking is successfully saved and appears in the saved rankings list.
- Verified saved rankings can be expanded/collapsed in the UI.
- Confirmed users can delete a saved ranking and it is removed from the list.

## Reviews and Collaboration
- Tanner's Frontend portfolio generation: Data aggregation & UI reworks [#437](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/437)
- Travis' Redesign App.jsx [#438](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/438)
- Travis' Update frontend tests to match refactored App.jsx [#441](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/441)
- Jaxson's Fixed Scanner Bugs Related to Multi-Project Directories [#443](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/443)
- Travis' Redesign index.css part 1/3: core, base, and shared components [#444](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/444)
- Travis' redesign index.css part 2/3: scan and rank page styles [#445](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/445)
- Jaxson's Delete .DS_Store [#446](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/446)
- Travis' redesign index.css 3/3: portfolio, scanned projects, and responsiveness [#447](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/447)
- Pri's Add project edit endpoint and UI support [#448](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/448)
- Travis' Resume page enhancements [#449](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/449)
- Tanner's Frontend portfolio generation: Project cards (collapsed vs. expanded cards) [#457](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/457)

## Issues and blockers
No issues or blockers.

## Plans for Week 11
- Add activity heatmap and more functionality to the portfolio
- Prep and fix bugs for peer testing

## T2 Week 11-12 (March 16th - March 29th)

<img width="794" height="456" alt="image" src="https://github.com/user-attachments/assets/49db2567-889e-46d9-a817-1d2889a73419" />


## Overview:
This week, I focused on enhancing the portfolio page by implementing a detailed project contribution heatmap. The work included both backend and frontend development, allowing users to visualize weekly commit activity for individual projects or per user. This provides accurate metrics, improves UI responsiveness, and enables toggling between project and user views while ensuring consistent data handling and layout stability. Additionally, I made more edits to the the User Interface by introducing more themes and tried to make the colours less monochrome for users. Alongside that, I added the logo to the header of the app to finalize our UI/UX design.

## Reflection:
This week the team worked pretty well together to complete tasks for peer testing and to get feedback from the session. We communicated and got our goals done in a respectful and professional manner. PRs were made and reviewed in a timely fashion and the team worked really hard to get things done these past two weeks. After the presentation we all met up together to plan who would do what in the final week and people have stuck to their word and have gotten everything done. 

## Coding Tasks:
Added Project Heatmap [PR 469](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/469)
  - Generated weekly heatmap cells with contribution counts, date ranges, and aggregated metrics.
	- Uses Git commit history from git_metrics_json as the primary data source, with a fallback to database scan timestamps and created_at.
	- Normalizes contributions to ISO week format (Monday start) for consistent visualization.
	- Provides metrics such as weekly commits and contribution files via a file_contributors query.
	- Added a project selector dropdown to switch between project heatmaps.
	- Implemented a 7-row heatmap grid (Mon–Sun) with auto-width weekly columns.
	- Contribution intensity is displayed via opacity scaling (0–100%).
	- Displays additional metadata including project duration, peak contribution week, total contributions, active weeks, consistency percentage, and 4-week trend.


Updated Heatmap [PR 473](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/473)
  - Added toggle between Project View and Per User View
	- Introduced a shared horizontal scroll container for aligned heatmap cells and date labels
	- Fixed layout issues to prevent heatmap stretching
	- Added view_scope query parameter to heatmap endpoint
	- Updated both project and per-user heatmaps to return commit counts

Updated menu with scan data [PR #479](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/479)
  - Added new aggregation endpoints:
		- GET /outputs
		- GET /stats/dashboard
	- Implemented aggregation logic for:
		- Total outputs (resumes + portfolios)
		- Latest generated output timestamp
		- Project and contributor statistics
	- Replaced simple count-only cards with contextual insights
	- Added relative-time formatting (e.g., “latest activity”)
	- Consolidated multiple API calls into a single /stats/dashboard request
	- Cards now display meaningful summaries instead of raw numbers
	- Outputs card includes breakdown (resumes vs portfolios)

Updated UI to be less monochrome, added themes, new icons, and transitions across the app [PR #494](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/494)
  - Added Heroicons imports.
  - Updated menu button rendering to use the new icon components.
  - Created ThemeSettingsPage.jsx with four selectable theme presets:
    - Evergreen
    - Harbor
    - Violet Night
    - Sunset
  - Introduced layered background gradients and accent orbs for richer visuals.
  - Improved text, border, and panel contrast across the app.
  - Added @heroicons/react dependency in package.json.
  - Updated package-lock.json.


## Tests and Debugging:

`PortfolioPage.test.jsx`
	
  - Used mock API calls to simulate project and per-user heatmap data without needing the real backend.
	- Tested that the project heatmap loads by default:
		- Checked the API was called with view_scope=project.
		- Confirmed the heatmap and metrics appeared on the page.
	- Tested switching to per-user heatmap:
		- Clicked the “Per User View” button.
		- Checked the API was called with view_scope=user.
		- Confirmed commit data showed correctly in the heatmap.
	- Tested the shared scroll layout:
		- Made sure the scroll container exists.
		- Verified it wraps both the heatmap grid and week labels.

`DashboardStats.test.jsx`

	- Fetches and displays dashboard stats on mount
	- Displays latest project and contributor info
	- Displays outputs breakdown
	- Handles fetch errors without crashing


`test_api.py`

	- Validates that /outputs correctly aggregates resume and portfolio counts and returns the latest
	- Ensures /stats/dashboard returns the correct structure and aggregated data for projects, contributors, and outputs.

  ## Reviews and Collaboration
  - Tanner's Frontend portfolio generation: Expanded project card metrics [PR 468](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/468)
  - Travis' Add delete endpoint and trashcan UI to resume gen [PR #472](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/472)
  - Pri's Add select all / deselect all for project selection in resume and portfolio [PR #491](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/491)
  - Travis' Support education entries in resume generation with collapsible UI [PR #492](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/492)
  - Jaxson's Added multi-page warning before resume PDF export [PR #497](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/497)
  - Travis' Blacklist bot contributors from scanned projects page [PR #498](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/498)
  - Travis' Testing report and external test data documentation [PR #504](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/504)

## Issues and blockers
No issues or blockers.

## Plans going forward
- Project voting
- Bundle application (potentially)
