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

## Plans for Week 11
- Start modifying and improving past functions with suggestions of peers left on pull requests 
- Continue reviewing teammate PRs 
- Contribute to documentation updates








