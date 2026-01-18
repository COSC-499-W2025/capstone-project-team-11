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
# Week 1 (January 5th - 11th)
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

## Task Completed
This week I continued to work on the key roles feature by adding a feature to make it more project centric. Previously it would give a user a role for a combination of all their projects in the database but now there is a feature that shows the role of each user in each project specifically. Additionally, this feature was seperated from the main menu so I added it there with the sufficient menu testing and testing for updates to the key roles feature.

- Closed issue #266

## Refelection
Overall the team was pretty organized and were able to communicate with each other productively. Team members delivered on new features or improved on existing ones and reviews were conducted quickly and professionally. For the most part, all code was pushed and reviewed before late Sunday. 

## Additions
`detect_roles.py`: 
- Added load_contributors_per_project_from_db() function to query and analyze contributor roles on a per-project basis
- Updated [format_roles_report() to accept optional per-project data and display a "PER-PROJECT CONTRIBUTIONS" section
- Report now shows both overall contributor roles and individual project breakdowns with condensed metrics

`main_menu.py`:
- Added new menu option "11. Analyze Contributor Roles"
- Updated exit option from 11 to 12

## Testing
`test_detect_roles`: Added TestPerProjectAnalysis test class with test cases covering:
- Report formatting with/without per-project data
-  Multiple contributors across projects
-  Empty project handling
-   Role differences across projects

`test_main_menu`: Added new test cases for handle_analyze_roles():
-  Overall analysis without per-project
-  Per-project breakdown display
-  Multiple contributors
-  Metrics display validation

## Reviews
- Jaxson's FastAPI Integration #264
- Pri's Feature/custom project wording clean #271

## In Progress Tasks
Researching and integrating LLMs

## Planned Tasks for next Sprint
- Fix zip file github project bugs.
- LLM integration
