# Week 3 Personal Log (September 15th - 21st)
---
Throughout this week we collaborated on project requirments and the set up of our repo/communication. We'll now look towards system design and acrhitecture. 

<img width="1199" height="561" alt="Screenshot 2025-09-20 at 3 08 42 PM" src="https://github.com/user-attachments/assets/a1dbc1e3-138c-4b37-abbf-51c8fb380f04" />

### Tasks Completed:
---
Been apart of the following tasks:

- Creating project requirements
- Repo initalization and set up
- Weekly and individual log
--- 

# Week 4 Personal Log (September 22nd - 28th)

<img width="1058" height="616" alt="Screenshot 2025-09-28 at 3 31 23 PM" src="https://github.com/user-attachments/assets/0febdbac-efb0-4669-9d92-2fa3bbd5afb0" />

This week we focused lots on polishing our system architecture diagram, and a detailed project proposal document which asked us to go in depth on use cases, functional/non-functional requirements, and how worload will be shared.

### Tasks Completed
Been apart of the following tasks this week:

- Week 4 peer eval
- System Architecture diagram (issue #9)
- Finalized and submitted project proposal document (issue #8)
- Individual Logs Week 4 (issue #10)
- Team Logs Week 4 (issue #11)

---

# Week 5 Personal Log (Sep 29th - Oct 5th)

This weeks focus was on understanding the data flow of our system and making DFD level 0/1 diagrams. After the excercise in clas we got feedback on our design and made necessary revisions.

<img width="1069" height="632" alt="Screenshot 2025-10-05 at 2 03 38 PM" src="https://github.com/user-attachments/assets/221fbbbe-aa4c-4385-889c-d307f923a33f" />

Was apart of the following tasks this week:

- Week 5 indivdual log (issue #14)
- Design Data Flow diagram (issue #16)
- Submit DFD to canvas (issue #17)

---

# Week 6 Personal Log (Oct 6th - Oct 12th)

This week we started to develop code after finilizing changes to system requirements and architecture.

<img width="1094" height="615" alt="Screenshot 2025-10-12 at 6 26 22 PM" src="https://github.com/user-attachments/assets/53e72f19-87f4-4cb6-9c04-8e8c2c59276e" />

## Tasks Completed

- Week 6 individual log
- Inital dockerization (issue #41) PR #55
- Reviewed ScanDetails PR (PR #44)
- Reviewd final WBS 

---

# Week 7 Personal Log (Oct 13th - Oct 19th)

This week, I focused on documentation and progress tracking for our milestone deliverables. I completed the Week 7 team log, ensured that all team activities were properly reflected on our project board, and helped review project updates and PRs to maintain consistency across the repository.

<img width="1096" height="642" alt="Screenshot 2025-10-19 at 9 51 17 PM" src="https://github.com/user-attachments/assets/e67214d6-89dc-4373-ab44-9ec37e93baf3" />

## Tasks Completed

- Completed Week 7 Team Log (#65)  
- Reviewed project documentation and verified milestone progress   
- Participated in PR review discussions with teammates  
- Helped organize the Kanban board and verify completed items
  
<img width="1075" height="115" alt="Screenshot 2025-10-19 at 9 50 34 PM" src="https://github.com/user-attachments/assets/25195b3f-a81a-4fc4-9d81-b370944dbf12" />

## Plans for Week 8

- Finalize and test the “Return Errors for Incorrect File Formats” functionality (#23)  
- Assist with milestone submission documentation and final checks  
- Review the parsing functionality for zipped folders (#22)  
- Ensure consistency between testing outputs and documented requirements  
- Continue supporting integration and testing efforts across modules

---

# Week 8 Personal Log (Oct 20th – Oct 26th)

This week I focused on implementing a new feature that validates file formats during directory and zip file scans. The update integrates the `is_valid_format` function into `scan.py`, ensuring that only supported file types are processed while unsupported ones are skipped with clear messages. I also added unit tests to verify correct behavior across valid, invalid, and edge-case filenames. In addition I continued contributing to code quality by reviewing teammates’ PRs and ensuring consistency across our testing and documentation standards.

<img width="1094" height="630" alt="Screenshot 2025-10-26 at 3 42 39 PM" src="https://github.com/user-attachments/assets/48374d91-4fc0-4e8b-88b7-68e3c7e824ae" />

## Tasks Completed

- Implemented **File Format Validation** feature and tests (Issue #23, PR #92)  
- Reviewed **Reusable User Consent Module** (Issue #21, PR #84)  
- Reviewed **Data Access Consent Updates & Unit Tests** (Issue #21, PR #86)  
- Reviewed **Collaboration Detection Feature** (Issue #27, PR #87)  
- Updated individual log and synced progress with the project board

<img width="1099" height="145" alt="Screenshot 2025-10-26 at 3 48 02 PM" src="https://github.com/user-attachments/assets/efa42e86-171e-4f5a-8be1-d431410d5c8c" />

## Plans for Week 9
- After review of my code is finished and merged, i will look to implement issue #29: "Identify Individual Contributions Within a Collaborative Project"
- Help verify system-wide functionality with current features implemented
- Continue reviewing PRs
- Refine documentation for scanning and validation workflows  

---

# Week 9 Personal Log (Oct 27th – Nov 2nd)

This week I began implementing **Issue #29: Identify Individual Contributions Within a Collaborative Project**, which focuses on mapping file authorship and contributions across Git repositories. I also reviewed **PR #107** (Development bug fixes) and **PR #109** (Issue #19: Solve Projects Chronologically), providing feedback to ensure smooth functionality and consistent testing coverage. In addition, I resolved merge conflicts between the **Contribution Metrics** feature branch and the **Development** branch to maintain alignment across ongoing feature work. Lastly, I completed my individual log for this cycle.

Overall, the week went well, I made pretty good progress on my assigned issue, but had to spend time refacotring after other pushes. All tests ran successfully after the merge. However, resolving the couple merge conflicts highlighted the need for clearer team communication about where and when changes are being made in the repository. Improving coordination will help prevent overlapping edits and make integration smoother in future cycles. I also learned more about how different features interact across modules, which will help with upcoming implementation work.

<img width="1068" height="619" alt="Screenshot 2025-11-02 at 10 38 19 PM" src="https://github.com/user-attachments/assets/e2c6104a-1f3d-4763-8170-597a01b045d6" />

## Tasks Completed

- Implemented **Issue #29: Identify Individual Contributions Within a Collaborative Project**  
- Reviewed **PR #107 (Development bug fixes)**  
- Reviewed **PR #109 (Issue #19 – Solve Projects Chronologically)**  
- Fixed merge conflict between **Contribution Metrics feature** and **Development branch** (PR #109, Issue #10)  
- Completed individual log for this cycle
- Minor bug fixes on my Issue#23 from last week fixing module import error in test suite

<img width="1275" height="154" alt="Screenshot 2025-11-02 at 5 37 15 PM" src="https://github.com/user-attachments/assets/c0f7708f-6d55-4760-85af-184bc3431ca3" />

## Plans for Week 10
- Begin implementation of **Issue #37: Summarize the User’s Top-Ranked Projects**  
- Go over and apply small fixes and refinements in **Issue #29**  
- Add further test cases for collaboration detection and contribution metrics  
- Continue reviewing PRs and verifying system integration before next milestone  
- Contribute to documentation updates for contribution and collaboration modules

---

# Week 10 Personal Log (Nov 3rd – Nov 9th)

This week i had some midterms so I focused on implementing a bug fix for my previous task related to the contribution summary. My fix (PR #133) refined the data handling and ensured that the contribution summary correctly reports the number of files changed and which specific files were modified per contributor. This update aligned the results with the latest database persistence changes and improved overall reporting accuracy. After applying the fix, all related tests passed successfully, confirming stable integration across modules. 

In addition to the bug fix, I participated in peer code reviews for PR #131 (Database persistence integration) and PR #134 (File metadata handling improvements). These reviews focused on verifying data consistency, testing reliability, and adherence to project design standards. Overall, the week was productive in maintaining stability and supporting team progress toward our milestone, as are starting to deepen the analysis of out features

<img width="1109" height="643" alt="Screenshot 2025-11-09 at 4 42 55 PM" src="https://github.com/user-attachments/assets/a8b1a43e-8a3a-4b59-aee6-e606d6a4424f" />

## Tasks Completed
 - Fixed incorrect summary output by ensuring correct reporting of file count and file names per contributor (PR #133) 
- Reviewed **Database Funcionality update** (PR #131)
- Reviewed **FLang/Framework detection revision** (PR #134)
- Verified tests for contribution metrics and database schema compatibility  
- Synced progress with project board and updated individual log  

<img width="1238" height="140" alt="Screenshot 2025-11-09 at 5 47 06 PM" src="https://github.com/user-attachments/assets/638277fa-f83c-4c9a-ae4d-2622aa85b8c3" />


## Plans for Week 11
- Begin planning integration for project summary reporting feature (Issue #37)  
- Continue reviewing teammate PRs ahead of Milestone 1 submission  
- Contribute to documentation updates
- Support final debugging and consistency checks across merged feature

---

# Week 12 Personal Log (Nov 10th – Nov 23rd)

This week I implemented a new contributor-focused project summarization feature. My update (PR #158) added a full implementation of `summarize_projects.py`, which analyzes a contributor’s top-ranked projects from the database, gathers project metadata, and generates one combined summary file. The summary includes languages, skills, frameworks, contribution metrics, ranking breakdowns, and per-project details. The feature resolves project paths, handles missing/invalid paths, aggregates all stats cleanly, and produces a readable multi-section report. It’s completely standalone and can be run manually through the CLI without affecting the main scanning pipeline. I also added a comprehensive test suite covering path resolution, skipping invalid projects, info-gathering behavior, error handling, and limit enforcement. All automated tests passed, and manual runs produced correct summary files.

As a group, I feel we had a solid week. We expanded our reporting tools and kept everything aligned as we move toward the end of Milestone 1. Over the next couple of weeks, we’ll need to come together to tighten up our product for the demo, which I believe we will.

<img width="1107" height="663" alt="Screenshot 2025-11-23 at 5 21 43 PM" src="https://github.com/user-attachments/assets/7b91fd97-37e7-4a08-8ab3-700f9b636ffe" />

## Tasks Completed
- Added full contributor project summarization feature to `summarize_projects.py` (PR #158)  
- Implemented complete test suite in `test_summarize_projects.py`  
- Verified summary reports manually and through pytest  
- Reviewed PR #157  
- Reviewed PR #153   
- Updated project board and personal log  

<img width="1333" height="184" alt="Screenshot 2025-11-23 at 5 43 05 PM" src="https://github.com/user-attachments/assets/6a7ed131-4705-4819-a4de-446b2dbe25a9" />

## Plans for Week 13
- Continue refining contributor/project reporting tools
- **Issue #35 (Retrieve Previously-Generated Résumé Item)** to see if we have good enough reports to support retrieval
- Look into generating résumé/portfolio items **if needed**, depending on how the requirement develops  
- Look into integrating an LLM
- Support upcoming PR reviews ahead of Milestone 1 due date  
- Add documentation for new summary-reporting feature  
- Begin drafting integration notes for contributor-focused analysis

---

# Week 13 Personal Log (Nov 24th – Nov 30th)

This week I implemented the full `main_menu.py` module (PR #181), which now acts as the unified CLI interface for all major MDA features. The menu consolidates scanning, ranking, project summaries, and full database inspection into one consistent entry point. The update includes a complete set of helper utilities, support for per-project and contributor-level reporting, and a much cleaner workflow for interacting with the SQLite database. I also added a full test suite (`test_main_menu.py`) that covers the deterministic logic in the module, including `safe_query()`, `human_ts()`, and the database inspection handler. All tests passed successfully, and the new menu structure should make the user-facing experience much more organized heading into Milestone 1.

As a group, we also spent time preparing and refining our presentation slides for the Milestone 1 demo. We synced our individual logs, reviewed each other's PRs, and made sure the reporting and analysis features aligned well with what we want to showcase. Overall, it was a productive week, and I feel confident with where our project stands heading into the final stretch of Milestone 1.

<img width="1120" height="626" alt="Screenshot 2025-11-30 at 3 49 41 PM" src="https://github.com/user-attachments/assets/28b83416-5787-4393-8eea-84b8077fe217" />

## Tasks Completed
- Implemented full unified CLI interface via `main_menu.py` (PR #181)
- Added complete test suite `test_main_menu.py` with coverage for non-interactive logic
- Reviewed PR #183 (clean noisy scan output)
- Reviewed PR #184 (improved framework detection accuracy)
- Reviewed PR #185 (updated data-access consent policy)
- Helped prepare team slides for Milestone 1
- Updated individual log and project board

<img width="1113" height="155" alt="Screenshot 2025-11-30 at 3 52 20 PM" src="https://github.com/user-attachments/assets/c573d6c0-947a-4676-8307-8d91caba22db" />

## Plans for Week 14
- Continue working on **Issue #35 (Retrieve Previously-Generated Résumé Item)**
- Complete Milestone 1 video demo
- Finalize and submit team contract
- Finish Milestone 1 deliverable
- Complete Milestone 1 self-reflection
- Update system architecture for Milestone 2 requirements

---

# Week 14 Personal Log (Dec 1st – Dec 7th)

This week was busy as our team wrapped up the remaining Milestone 1 tasks and finalized our deliverables. We divided the remaining work across the group, and I focused on a mix of development fixes, architecture updates, and documentation as most of our coding was done.

One of my main contributions was **PR #212**, which fixes a Windows file path issue that caused summary generation to fail. The update standardizes how paths are parsed and makes the summary and reporting tools work consistently across both macOS and Windows environments. I also spent time updating our **system architecture diagram** so it accurately reflects the Milestone 1 implementation. This included organizing the layers, clarifying the flow between the CLI, scanners, detection engine, and database, and adding the resume output and consent/config elements. The updated diagram now gives a clean, accurate overview of how the system behaves end-to-end.

I feel it has been a succecsul milestone/semester and am happy with where our project is at thus far.

<img width="1086" height="645" alt="Screenshot 2025-12-07 at 2 24 57 PM" src="https://github.com/user-attachments/assets/b271c4cc-709a-470b-bc03-3f83f974189e" />

## Tasks Completed
- Submitted **PR #212** fixing Windows file path issues  
- Updated the system architecture diagram to match Milestone 1 functionality  
- Reviewed multiple bug-fix PRs from teammates
- Completed Individual Log
- Completed Team Log for team this week
- Participated in final checks for Milestone 1 deliverables 

<img width="1071" height="159" alt="Screenshot 2025-12-07 at 3 39 31 PM" src="https://github.com/user-attachments/assets/22714fb2-33db-4fbd-8822-9a511b7fe9fa" />

Plans for reading break:
- Begin outlining work for **Milestone 2**
- Improve summary/report generation pipeline based on milestone feedback
