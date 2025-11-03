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
