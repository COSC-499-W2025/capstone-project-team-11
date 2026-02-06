# Tanner Dyck's Personal Log

### Term 2 (Milestone #2)
- [Weeks #4 and #5 - January 26th-February 2nd](#weeks-4-and-5---january-26th---february-2nd)
- [Week #3 - January 19th-25th](#week-3---january-19th---25th)
- [Week #2 - January 12th-18th](#week-2---january-12th---18th)
- [Week #1 - January 5th-11th](#week-1---january-5th---11th)

### Term 1 (Milestone #1)
- [Week #14 - December 1st-7th](#week-14---december-1st---7th)
- [Week #13 - November 24th-30th](#week-13---november-24th---30th)
- [Week #12 - November 17th-23rd](#week-12---november-17th---23rd)
- [Week #11 - November 10th-16th](#week-11---november-10th---16th)
- [Week #10 - November 3rd-9th](#week-10---november-3rd---9th)
- [Week #9 - October 27th-November 2nd](#week-9---october-27th---november-2nd)
- [Week #8 - October 20th-26th](#week-8---october-20th---october-26th)
- [Week #7 - October 13th-19th](#week-7---october-13th---october-19th)
- [Week #6 - October 6th-12th](#week-6---october-6th---october-12th)
- [Week #5 - September 29th-October 5th](#week-5---september-29th---october-5th)
- [Week #4 - September 22nd-28th](#week-4---september-22nd-28th)
- [Week #3 - September 15th-21st](#week-3---september-15th-21st)

---

# ===== MILESTONE #1 =====

# Week #3 - September 15th-21st

<img width="1078" height="632" alt="TannerDyck-Week3Tasks" src="https://github.com/user-attachments/assets/26dfbdb3-651e-451d-b659-c27fb8ccd9ce" />

## Tasks Completed:
As this was the first week of getting our repository initialized and organzied, we made all decisions as a team and worked collaboratively on all of the following tasks (excluding personal logs and Canvas quizzes):
- Brainstormed project requirements during an in-person team meeting (at Monday's lecture)
- Recorded our project requirements in a shared Google Doc.
- Discussed our team's project requirements with other teams.
- Joined the Capstone GitHub classroom and forked our own project's repository.
- Organized our repository's "docs" file and folder structure
- Completed my "Projects Requirements" Canvas quiz
- Completed my personal log for Week #3
- Helped complete our team log for Week #3
- Merged all changes made on "logs" branch into "main" branch

---

# Week #4 - September 22nd-28th

<img width="733" height="541" alt="TannerDyck-Week4Tasks" src="https://github.com/user-attachments/assets/db92e7a9-cde0-4eec-b413-9ba983c5841e" />

## Tasks Completed:
I have completed the following tasks either alone or in collaboration with my teammates. As we are still in the early stages of our project's development, our team is largely focused on working collaboratively to nail down our project specifications and documents. In the coming weeks, I'm sure our workload and tasks will start to diverge from one another.

- Finalized and submitted project proposal (issue #8)
- Worked on system architecture design (issue #9)
- Finalized system architecture design after instructor feedback (issue #9)
- Filled out peer reviews for week #4
- Completed "project proposal" canvas assignment
- Individual Logs Week 4 (issue #10)
- Team Logs Week 4 (issue #11) 

---

# Week #5 - September 29th - October 5th

<img width="704" height="538" alt="TannerDyck-Week5Tasks" src="https://github.com/user-attachments/assets/d5402613-0622-4328-8677-cb9dd6dd4efe" />

## Tasks Completed:
As our team continues to work through the documentation phase of our project planning, we have been working collaboratively on document designs and revisions. Here is a list of tasks we completed together this week:

- Designed initial Data Flow Diagram (issue #16)
- Met with other project teams to compare DFDs and gather feedback
- Compiled list of feedback/issues with our initial DFD and shared it in our team Discord server
- Revised our DFD to incorporate the changes we decided on based on external feedback (issue #17)
- Completed our individual DFD Level 1 Canvas assignments (issue #18)
- Added our DFD Level 0 and Level 1 diagrams to our GitHub repository under docs/dfd/ (issue #19)
- Completed our individual logs and peer reviews for the week
- Completed our comprehensive team log for the week

---

# Week #6 - October 6th - October 12th

<img width="701" height="539" alt="TannerDyck-Week5Tasks" src="https://github.com/user-attachments/assets/14eb2e92-0138-4850-838a-aa767512d6ac" />

## Tasks Completed:
This marked our first week of largely individual work. We chose to divide and conquer a few tasks this week. Here is what I completed and/or helped complete:

- Attended team meeting at Wednesday's lecture and determined workload for the week
- Converted all 20 milestone #1 deliverables into GitHub issues on our Kanban board
- Built a Work Breakdown Structure document for milestone #1
- Reviewed code contributions and various other PR requests
- Completed my peer reviews for week 6
- Completed my individual logs for week 6

---

# Week #7 - October 13th - October 19th

<img width="546" height="404" alt="week7tasks" src="https://github.com/user-attachments/assets/06eac3b7-489c-4e8c-b57a-59952bab8e23" />

## Tasks Completed:
This was an extremely busy week for our team as midterms stole a lot of our productive hours. I also started a new job, which took up a lot of my usual capstone time.
Regardless, I was able to complete the milestone #1 deliverable #6 (Store user configurations for future use)
- I created two new files in the repo, src/config.py and test/config_test.py
- config.py contains code to handle the creation, reading/writing, locating, and loading of a simple scan config file
- The config.json file is located at the user's home directory in a hidden folder named .mda
- The stored information consists of the most recently scanned and saved: directory (path String), choice to scan nested folders (boolean), and file type filter (file extension String)
- The overall functionality of my files is to allow a user to reuse the parameters from their most recent scan after choosing to save them locally. (Each new scan prompts the user to decide whether or not to save the scan parameters for next time)
I also created config_test.py to act as a suite of unit tests for all of the functions in config.py, as well as testing config.py's integration with scan.py (our main executable file)

This first revision has completed issue #26 from our project board (6. Store user configurations for future use)

In addition to this milestone #1 deliverable, I completed the following non-coding tasks this week:
- Attended Wednesday's Quiz #1 Lecture
- Reviewed other team members' pull requests
- Communicated all of my repository changes in our team's Discord server
- Filmed and edited video demos for my deliverable #6 solution

Below is a screenshot of my assigned issues from our project's Kanban board as of 6:30pm PST on October 19th, 2025.
In week 8, I hope to:
- Complete deliverable #1 (Require the user to give consent for data access before proceeding)
- Reuse code from deliverable #1 to create an early revision/framework for deliverable #4 (Request user permission before using external services (e.g., LLM) and provide implications on data privacy about the user's data)

<img width="1247" height="576" alt="week7kanban" src="https://github.com/user-attachments/assets/c8b89e5c-ee60-4dc3-8950-fe9e16f74855" />

---

# Week #8 - October 20th - October 26th

<img width="715" height="539" alt="week8-tasks" src="https://github.com/user-attachments/assets/6c88dc26-cacb-43c2-b671-58dd2c56cd77" />

## Tasks Completed:
My main focus this week was on creating a reusable Python script that would help us create prompts for users in the terminal. The specific deliverable I hoped to solve with this implementation was 1. Data Access Consent. Here is an overview of what I contributed:

I created consent.py, a file that hosts three main functions:
- describe_data_access() acts as a modifiable template for printing non-interactive material to the console. Currently, it explains to the user what data our scanner has access to on their local machine during a scan. In the future, it will be useful for breaking down all potential data access policies for any third-party services our scanner is dependent on.
- ask_yes_no() is a reusable function that handles all of the logic for printing, reading, and returning a boolean value based on the input from a (y/n)-answer question in the terminal. Currently, our scanner prompts the user with a series of yes/no questions to determine the information they would like to see in their report. This function will simplify and standardize that practice, and hopefully prove useful moving forward.
- ask_for_data_consent() is another modifiable template that utilizes both of the functions above to handle the process of gaining data access consent into one simple, reusable function. It displays the data we have access to, asks for consent, and saves the user's preference to their config.json file using config.py's save_config() function. This ask_for_data_consent() function serves one purpose, but its structure can likely be repurposed for future deliverables.

I also created consent_test.py, which hosts four unit tests for the main functions defined in consent.py:
- Test 1 ensures that describe_data_access() functions correctly by affirming output matches the default items when no parameters are passed in the function call, and that items explicitly passed in the function call are found in the output.
- Test 2 ensures that ask_yes_no() returns the correct boolean for accepted inputs, and re-prompts until a valid input is given
- Test 3 ensures that ask_for_data_consent() correctly saves user preferences to config.json when requested
- Test 4 ensures that ask_for_data_consent() does not save preferences to config.json when the user opts out

In addition to these coding-centric contributions, I performed my usual responsibilities of:
- Attending TA check-in lecture
- Communicating regularly throughout the week in our Discord server and describing my implementations to my teammates
- Reviewing and getting familiar with code contributions made by teammates, and approving team/individual log updates as necessary
- Completing both my individual log and peer review for week 8

## Next Week (Week #9)
Next week, I hope to start work on a simple implementation of an LLM-assisted scan, as well as deliverable 4. Request user permission before using external services (e.g., LLM) and provide implications on data privacy about the user's data (using the framework/functions I created this week in consent.py). It will be a difficult task as I have never worked with an LLM API before, and it may be out of scope for our project in its current state. 

I believe another teammate is planning on getting our database operational next week, which will open up a lot of other deliverables that were previously unable to be completed due to us being unable to store scan information long-term. So the paragraph above is my tentative plan, but I will be ready to adapt if a non-LLM-based deliverable is deemed more important after we have our database functional. 

## Kanban Board at End of Week #8

<img width="2529" height="1193" alt="week8-kanban" src="https://github.com/user-attachments/assets/7a0da033-c9ab-493f-9490-51ad6e736ecf" />

---

# Week #9 - October 27th - November 2nd

<img width="699" height="538" alt="week9-tasks" src="https://github.com/user-attachments/assets/57aebefd-793b-429d-92d6-63f3544df3af" />

## Tasks Completed:
My main focus this week was on fixing bugs and inconsistencies that I found after all of our Week 8 implementations were finalized. I performed thorough testing of our program by running a plethora of scans with unique scan settings across multiple unique projects. I was able to compile the following list of issues to be prioritized:
- Should ask if user wants to save scan settings AFTER user gives response to "show collaboration info", NOT before.
- If a specific file type filter has been saved from a previous scan (.py, .json, .txt, etc.), leaving it blank on the next scan (to not filter by file types) and selecting to save the info, does not overwrite the saved file type filter by making it null/none/empty. (Essentially, config.json's file_type field does not seem to be able to be overwritten back to null, but can be overwritten with new explicit file extensions).
- All yes/no prompts could be remade using the ask_yes_no() function from consent.py for consistency.
- Users should not be prompted to reuse scan settings from last time if they have not scanned before (ie. the config.json has its default values).

I then implemented fixes for a series of similar bugs/inconsistencies that appeared after the implementations from this week (Week 9):
- Show contribution metrics choice does not save from the previous scan when the user chooses to save scan settings (add field to config.json and ensure saving/overwriting works properly).
- Show contribution summary choice does not save from the previous scan when the user chooses to save scan settings (add field to config.json and ensure saving/overwriting works properly).
- Fix if-condition logic on a line within scan.py that reads "if file_type is not None or file_type == None:", essentially always running it's code block. The issue came from an oversight and from being too overcautious with what scan setting values are able to be saved.
- Update config_tests.py unit tests to ensure they cover the two additional fields I added to config.json.
- One complete overpass to ensure that any yes/no prompt asked in the terminal should be asked before the "save settings for next time" prompt, and that each yes/no question has a boolean field in the user's config.

*All implementations of fixes to the bugs listed above are explained more thoroughly in PR templates #107 and #120

In addition to these bug fixes, I performed my usual responsibilities of:
- Attending TA check-in lecture
- Communicating regularly throughout the week in our Discord server and describing my fixes to my teammates
- Reviewing and getting familiar with code contributions made by teammates, and approving team/individual log updates as necessary
- Completing both my individual log and peer review for week 9

## Next Week (Week #10)
In terms of new features, I still need to tackle issue #24: (4. Request User Permission Before Use Of External Services), however, we are still not using any third-party services in our scanner. I have already created an empty template to solve this issue, but in order to make it truly valuable, I hope to look into the implementation of an LLM at least at a basic-level. The group is still unsure if LLM integration is worth it at this point, so in case it is not required, I would like to shift my focus to the following:

We are quickly running out of deliverables to work on for milestone 1. So I think it is important for us to start looking backwards at what we have already implemented and giving our features more depth, accuracy, consistency, and stability. Some of our implementations serve as excellent first revisions, but could become more useful with future revisions. More specifically, I would like to re-examine language and framework identification to see if we can come up with a solution that actively parses files in search of more nuanced words that may be able to provide more accurate results. I also feel I need to get a better handle on how our database implementation works, and potentially add additional fields to the schema to accommodate information we are now able to store after the past two weeks of feature implementations.

## Kanban Board at End of Week #9

<img width="1301" height="1220" alt="week9-kanban" src="https://github.com/user-attachments/assets/d92de0e2-69d1-44bf-bf7c-56d73f8cc2e8" />

---

# Week #10 - November 3rd - 9th

<img width="1075" height="630" alt="week10-tasks" src="https://github.com/user-attachments/assets/d1f6a592-7948-4b61-a728-9b44331182fa" />

## Tasks Completed:
I would like to preface this week's contributions by noting that the majority of the team was busy with midterms and other projects being due, so it was a slower week than usual, myself included. I was rather preoccupied with a game design project worth 40% of my final grade. It is not an excuse; I just hope it helps explain why I contributed less this week than in prior weeks.

Regardless, my main focus this week was on revamping our scanner's ability to detect coding languages/frameworks in coding projects. Our first revision relied solely on file extensions to detect languages, so this week, I implemented file reading in hopes of creating a more comprehensive detection process. I implemented the following changes to work alongside this new infrastructure:

Within detect_langs.py:
a) Programming Language Syntax Patterns:
- Added LANGUAGE_PATTERNS dictionary with regex for 5 initial languages (to be expanded upon later)
- Created scan_file_content() to count pattern matches in files (actually reads files to search for specific language patterns)
- Now uses file extension-checking ALONGSIDE syntax pattern-checking for hopefully, improved accuracy (Still fairly inaccurate at the moment)
- Outputs pattern match counts to the terminal for transparency purposes

b) Detection Confidence Levels:
*My hopes are that these confidence levels will help users weed out any false positives generated by our scanner, as well as just generally provide more transparency and insights around how we are detecting languages and frameworks within coding projects.
- Created calculate_confidence() with a three-tier system (low/medium/high)
- Tracks pattern counts and extension matches per language
- Calculates confidence based on pattern count and extension presence
- Updated output to display confidence levels

c) Expansion of Supported Programming Language Syntax Patterns:
- Added regex patterns for C, C#, Ruby, PHP, Go, Rust, Swift, Kotlin, SQL, Shell Script, HTML, and CSS, to bring it more in-line with our original list of detectable languages
- Each language has 4-5 distinctive syntax patterns

In addition to these bug fixes, I performed my usual responsibilities of:
- Attending TA check-in lecture
- Communicating regularly throughout the week in our Discord server and describing my fixes to my teammates
- Reviewing and getting familiar with code contributions made by teammates, and approving team/individual log updates as necessary
- Completing both my individual log and peer review for week 10

- I also completed the team log for week 10

See my PR "First Round of Revisions to Language/Framework Detection Feature" #134 for more details around the inaccuracies of my changes from this week. But I would like to acknowledge that the "Detect languages/frameworks in coding projects" feature, as it currently stands (after my changes), has numerous issues with accuracy. It is by no means in a finished state, it is stable, and functions withour any critical errors, but due to issues in my REGEX patterns for various coding language syntaxes, many false-positives are discovered. In my PR mentioned above, I suggested fixes for many of these issues that I hope to implement in the next week or two. 

## Reflection Points
I feel like things went well this week. We spoke in the Discord server before our TA check-in meeting this week and touched base about what we planned on working on. Most members mentioned they were going to be swamped this week with other tasks, so we all understood that this would be a lighter week for contributions. We had a good in-person meeting during the TA check-in and were able to organize tasks for the week. We all completed our tasks on the days we said we would have them done by. I have no gripes about how this past sprint went.

## Next Week (Week #11)
Next week is Reading Break, and I have yet to discuss with the team what our planned contributions are for week 11, but I am loosely planning on pushing some additional improvements for the "Detect languages/frameworks" feature I worked on this week (As I have outlined plans for a bunch of potential improvements already, so I will have a good jumping-off point). I will touch base with the team tomorrow and make sure we are all on the same page about what we would like to have done during Reading Break.

## Kanban Board at End of Week #10

<img width="1211" height="886" alt="week10-kanban" src="https://github.com/user-attachments/assets/0b11cf1b-42ad-43b0-97c9-dbb154e63c95" />

---

# Week #11 - November 10th - 16th
During the reading break week, no work was done on our capstone project

---

# Week #12 - November 17th - 23rd

<img width="1065" height="619" alt="week12-tasks" src="https://github.com/user-attachments/assets/1a031ce1-2074-4d22-bcd8-15e5557ca18d" />

## Tasks Completed:
This week, I continued implementing revisions for our scanner's "Detect programming languages/frameworks within coding projects" feature. I left the feature in a stable state last week, but the feature was still highly inaccurate, and the codebase contained a fair amount of redundant/deprecated code. So this week, I implemented another round of changes:

A) Features Implemented (More detailed breakdown can be found in PR #157):
- Added file and directory filtering for language detection
- Added comment stripping to reduce false positives during language detection
- Categorized language detections into primary and secondary detections, and reworked the confidence level thresholds

B) Codebase Refactoring (More detailed breakdown can be found in PR #159):
- Unified LANGUAGE_MAP, CODE_EXTENSIONS, and COMMENT_SYNTAX dictionaries into a single LANGUAGE_CONFIG dictionary that hosts all extension-to-language mappings and comment syntax definitions
- CODE_EXTENSIONS (File extensions directly related to programming languages) and LANGUAGE_MAP (Mapping of file extensions to language names) are now initialized as subsets of LANGUAGE_CONFIG, this eliminates the need to maintain three separate data structures

C) Unit Testing Updates (More detailed breakdown can be found in PR #159):
- Helper function tests:
    - tests that should_scan_file() operates correctly and is returning the proper boolean values when code, text, and unknown file types are passed through it
    - tests that get_extension() normalizes file extensions by stripping them and setting them to lowercase
- Comment Stripping Tests:
    - tests that strip_comments() behaves properly across a variety of file types and languages (comments are removed, and accurate code segments are returned)
- Ignored Directories Tests:
    - tests that some pre-defined "junk" folders such as .git and pycache are not included during language/framework detection in hopes of reducing false positives and other useless detections

In addition to these bug fixes, I performed my usual responsibilities of:
- Communicating regularly throughout the week in our Discord server and describing my fixes to my teammates
- Reviewing and getting familiar with code contributions made by teammates, and approving team/individual log PRs as necessary
- Completing both my individual log and peer review for week 12

*Note: These changes have not fixed all possible inaccuracies with this feature. False positives are still detected, however, the confidence level system helps mitigate the impact of the false positives. Essentially, only "HIGH" confidence languages should be considered, but "MEDIUM" confidence languages can also provide insight into certain coding projects. The framework detection is still in a rudimentary state, and needs to be brought more in line with the current implementation of language detection before I would consider this feature to be "complete".

## Reflection Points
I feel that most of our team has hit a sustainable stride/pace so to speak. We are all checking in with each other through Discord at the beginning of each week to discuss what each of us plans to complete, and by what deadline. We give brief updates throughout the week as we encounter hiccups or push PRs. And we have all hands on deck during the weekend to ensure a smooth merge from our Development branch into main. I feel that our team knows what to expect each week, and we are all trying to pull our weight to ensure we have no more chaotic sprints.

## Next Week (Week #13)
I believe that next week is our final week to commit changes to the repo before milestone #1 comes to a close. I worry about our scanner's ability to produce adequate resumes/portfolios in its current state, but one of our team members was working on that this week, we just haven't seen his implementation yet. I plan to finish my revisions to the detect languages/frameworks section by: revamping framework detection to behave similarly to language detection, and updating the unit testing suite to cover framework detection. Afterwards, I will dedicate any available spare time to working on any last-minute necessary revisions to any other features that significantly impact resume/portfolio generation. 

## Kanban Board at End of Week #12

<img width="1877" height="897" alt="week12-kanban" src="https://github.com/user-attachments/assets/ae65ae28-3af8-4137-9ff6-9ad8562b3625" />

---

# Week #13 - November 24th - 30th

<img width="696" height="542" alt="week13-tasks" src="https://github.com/user-attachments/assets/2e3a21a3-d20e-4115-95c6-8d032c51e23b" />

## Tasks Completed:
This week, I focused on finishing off the necessary revisions to the language and framework detection feature, as well as revamping our scanner's data-access policy:

### Language/Framework Detection (From PR #184):

`detect_langs.py:`
- Added FRAMEWORK_CONFIG dictionary that hosts detection indicators for the 18 most popular frameworks that map to one of our supported languages. (contains framework name, its corresponding programming language, possible config and package file names that may point to its inclusion)
- Added FRAMEWORK_PATTERNS dictionary to hold REGEX patterns for each supported framework, if these REGEX patterns are triggered during file content scanning, it suggests a high likelihood that their corresponding framework is actively being used
- Added scan_file_for_frameworks() to detect frameworks using REGEX patterns found in file content (derived from FRAMEWORK_PATTERNS dictionary)
- Added detect_frameworks_in_config() to find frameworks in config/package/dependency files (derived from FRAMEWORK_CONFIG's "config_files" and "package_names" fields)
- Added calculate_framework_confidence() with 3 confidence thresholds:
    - High: Found in config file AND 1+ pattern matches
    - Medium: Found in config file with 0 pattern matches OR not found in config file but with 5+ pattern matches
    - Low: Not found in config file, <5 pattern matches
- Integrated framework detection into detect_languages_and_frameworks()
    - Runs alongside language detection
    - Tracks pattern counts and config file presence
- Updated terminal output to display detected frameworks within tables (contains the number of pattern matches, and whether or not it is detected in a config/package/dependency file)

`test_detect_langs.py:`
- I removed the 3 pre-existing framework detection unit tests as they relied on deprecated logic that is no longer used
- I added 9 tests to ensure that detect_languages_and_frameworks() is accurately detecting 9 of the 18 supported frameworks by running detections on doctored config/package/dependency files
- I added edge-case tests to ensure:
    - Multiple frameworks can be detected in the same config/package/dependency file
    - No frameworks are detected when no config/package/dependency files exist in the project repository
    - Framework detections are performed case-insensitively (ie. "FLASK==version or flask==version" still detects as "Flask")

### Data-Access Policy (From PRs #185 and #187):

`consent.py:`
- Split data access into three categories
    - Local file system (File/folder names, paths, and content)
    - Git repositories (Any projects with git information: commit histories, collaborative authors, project timelines, etc.)
    - Local data storage (How our scanner may create and store generated files on a user's local machine)
- Included a section to clarify certain data we do not collect or access:
    - No network requests
    - No external services called or used (no LLMs, APIs, Report generation frameworks, etc.)
    - No access to file content outside of the user-provided directories

`consent_test.py:`
- Fixed a unit test that was using deprecated Strings from the previous implementation of our data-access policy (more details in PR #187)

### Other Contributions:

Additionally, I added a few slides to our Google Slides presentation deck that I will be responsible for covering during our in-class presentation on Wednesday, December 3rd, 2025.

In addition to these changes, I performed my usual responsibilities of:
- Communicating regularly throughout the week in our Discord server and describing my changes and implementations to my teammates
- Reviewing and getting familiar with code contributions made by teammates, and approving team/individual log PRs as necessary
- Completing both my individual log and peer review for week 13

## Reflection Points
I was really happy with our progress and collaboration this week. We had a really good team meeting after this weeks' Monday lecture, where we all discussed what still needed to be done, how we should prioritize it, and then who would be doing what. We loosely touched on some policies that will likely be a part of our upcoming team contract, such as when we should be announcing what we plan to do, and how often we should provide updates in our Discord server. Everyone followed these rules fairly well, and all major code contributions for the week had PRs posted by Sunday morning, which is maybe the earliest we have ever had this happen. Overall, no complaints, communication was regular and informative and work was pushed at reasonable times.

## Next Week (Week #14)
Next week is our final opportunity to work on the project before milestone 1's deliverables are all due. My tasks next week will likely include:
- Any final revisions to the project, for any feature, to ensure our scanner is bulletproof before starting on milestone 2, in addition to my individual logs and peer reviews based on the work completed
- Completing our team contract, I will communicate with all of my teammates to ensure we are all happy with our decided-upon policies
- Recording my portion of our scanner's video walkthrough
- Watching other teams' in-class presentations and completing reviews for at least 5 of them
- Completing my milestone 1 self-reflection

## Kanban Board at End of Week #13

I was finally able to mark "Revise Coding Project Language/Framework Detection" (Issue #129) as "Done"
<img width="1874" height="894" alt="week13-kanban" src="https://github.com/user-attachments/assets/f6860480-09fc-4f02-bf95-91e1090f04e4" />

---

# Week #14 - December 1st - 7th

<img width="708" height="539" alt="week14-tasks" src="https://github.com/user-attachments/assets/1788150e-bb17-4d75-82a4-7ad70a01c94f" />

## Tasks Completed:
We came together to discuss this week's task priorities and assignments at the beginning of the week on Monday. We realized we didn't have any major code contributions to push, outside of small bug and inconsistency fixes and a lttle bit of final polish. But we realized we had to redesign the majority of our documentation, create a team contract, and make a video demo for our scanner at the end of milestone 1. So we assigned each team member a larger, single task to complete, while keeping all other teammates informed about changes, and providing everyone an equal opportunity to influence any adjustments made.  

This week I had a number of unique tasks, over the past week I:
- Completed my portion of the in-class presentation slides, performed my section, and answered some related questions afterwards during the Q+A
- Completed my portion of the Milestone 1 Video Demo (intro/outro, deliverable text overlays, recorded footage and voiceovers for deliverables 1 through 10, editing/polish)
- Completed my Milestone #1 Self-Reflection Canvas assignment
- Helped discover/review/fix a small number of last-minute codebase/functionality bugs 

### Other Contributions:
In addition to these changes, I performed my usual responsibilities of:
- Communicating regularly throughout the week in our Discord server and describing my changes and implementations to my teammates
- Reviewing and getting familiar with code contributions made by teammates, and approving team/individual log PRs as necessary
- Completing both my individual log and peer review for week 13

## Reflection Points
I feel like this week was as good as our team has ever worked together. On Monday, we all came together in the Discord to decide on task priorities and assignments, we worked through our list effectively and everyone was happy with the task allocations. Everyone worked hard to get our in-class presentation ready for viewing, and everyone showed up and performed well during our presentation on Wednesday. For the rest of the week, we all grinded out our individual assigned tasks, and I am very impressed with the quality and cohesion of everyone's efforts. All work was completed by Sunday afternoon at the latest, and all PRs and merges went over smoothly. Communication in the Discord was excellent, everyone was bouncing ideas off the rest of the group and looking for feedback, screenshots and recordings were used to showcase task progress and any issues encountered. Overall I could not be happier and it felt like a very cohesive and hardowrking week where everyone was at their best. I hope we can take this momentum/pace into term 2 and hit the ground runnning.

## Next Week (Week #15 and onwards)
By tonight (Sunday, Dec. 7th, 2025) at 11:59pm, we will be completely done with both term 1 and milestone 1. I may push a few changes to our codebase over winter break, but it is more likely that I will take some time off from the project, and revisit it with a fresh attitude and pair of eyes when we start up again at the beginning of January.  

## Kanban Board at End of Week #13

I was able to complete, and mark the following issues as "Done" this week:
- Milestone #1 Video Demonstration (Issue #199)
- Request User permission Before Use of External Services (Issue #24)
- Workaround Analysis if User Denies External Service Permissions (Issue #25)
<img width="1874" height="893" alt="week14-kanban" src="https://github.com/user-attachments/assets/bc6922b4-360c-40da-9114-3505db336c17" />

---

# ===== MILESTONE #2 =====

# Week #1 - January 5th - 11th

<img width="699" height="593" alt="t2week1-tasks" src="https://github.com/user-attachments/assets/dfa38c92-1ed5-4fc5-b52e-722094323c27" />

## Tasks Completed:
This week I focused mainly on implementing an iterable and modifiable portfolio generation feature. This is not an explicit deliverable for milestone 2, but a few of milestone 2's deliverables depend on us having a portfolio generation feature that is distinct from resume generation, something that we had not addressed during milestone 1. This is a sister-feature to Jaxson's `generate_resume.py` file, so I have tried to maintain a level of parity between the two codebases, and resuse logic when possible.
- Added `generate_portfolio.py` to host all of the core logic for portfolio assembly and generation (See PR #253 for more details)
- Integrated portfolio generation script directly into main_menu.py
- Added `test_portfolio_generation` to be a testing suite for portfolio-generation-related functionalities (See PR #253 for more details)
- I also converted milestone 2's 10 deliverables into GitHub issues for our project's Kanban board and added descriptions where necessary

### Other Contributions:
In addition to these changes, I performed my usual responsibilities of:
- Communicating regularly throughout the week in our Discord server and describing my changes and implementations to my teammates
- Reviewing and getting familiar with code contributions made by teammates, and approving team/individual log PRs as necessary
- Completing both my individual log and peer review for T2 Week 1

## Reflection Points
This week went fairly well in my opinion. I feel we lost a bit of momentum over our month-long break, which is to be expected. The start to this week was a little bit slow, we were all processing and trying to come up with development plans for the new set of milestone deliverables. I feel that we had some hesitancy getting started and diving back into our growing codebase. By Wednesday night we had come up with a pretty solid plan, all the teammates assigned themselves to various tasks across our Kanban board, and we had a good amount of code pushed before the weekend. This week was difficult, as the deliverables for this milestone are fairly large-scale, and depend on functionality that we did not have perfectly polished by the end of milestone 1, but we did a good job at pointing out areas we needed to tighten up. Some deliverables are currently unable to be completed due to their reliance on unpolished prior functionality, but my teammates did a great job of communicating stopping points, and build solid foundations for their features that can be finished in the coming weeks. Overall, I am happy with how we started milestone 2, and I imagine it will only improve moving forward!

## Next Week (T2 Week #2)
Next week I hope to continue polishing my "Portfolio generation feature":
- Add database support (Create a portfolio table in the schema to allow for the saving and deletion of portfolios to/from the local database)
- Add a "View Portfolios" option in the main menu, where users will be able to view, delete, or add to their generated portfolios (Ensures parity with current resume functionalities)
- Add useful performance metrics for collaborative projects (user's commits vs total commits percentage, ranked collaborators per project, etc.)
Assuming I have extra time to work on other things, I could take a look at slightly revamping resume generation, so that both file types have a high level of parity between them and are prepared for the deliverables that rely on them. 

## Kanban Board at End of T2 Week #1
I was unable to complete or mark any issues as "Done" this week, as I mainly worked on implementing a feature we should have implemented in milestone 1. However, I picked up a few larger-scale issues that I will have as "In-progress" for a portion of this milestone.
<img width="1875" height="929" alt="t2week1-kanban" src="https://github.com/user-attachments/assets/0d19b401-0ba4-4924-957a-6f9904426e3a" />

---

# Week #2 - January 12th - 18th

<img width="705" height="538" alt="t2week2-tasks" src="https://github.com/user-attachments/assets/9c3fa0b1-8171-40d5-8c10-239d90b671e2" />

## Connection to Last Week
Last week I implemented the core portfolio generation feature (`generate_portfolio.py`) which creates sectional markdown portfolios by aggregating data from scanned projects. I also created `test_generate_portfolio.py` with 9 unit tests covering the core functionality, and converted milestone 2's deliverables into GitHub issues. This week builds on that foundation by adding performance metrics, database integration, and the "View Portfolios" main menu option, which completes the three TODOs I outlined last week.

## Coding Tasks

### Broadened Portfolio Generation Functionality [PR #260](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/260)
- Added additional performance metrics using contribution data from git projects:
    - Commit counts, number of files modified, percentage of total commits made by user
    - Contributor ranking, lines added/removed, file ownership percentage
    - Project timeline, commits per week
- Reworked `detect_skills.py` and `project_info_output.py` to ensure languages/frameworks confidence scoring is included in the locally-saved JSON summaries (we use these JSON files during data aggregation for portfolio generation, and now we can filter out low-confidence languages)
- Updated `generate_portfolio.py` to use the now-supported language/framework confidence filtering (default = show only high-confidence languages/frameworks)

### Database Integration for Portfolios [PR #261](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/261)
- Updated `init_db.sql` to include a table for portfolios (almost identical to the resumes table schema)
- Updated `db.py` to host helper functions `save_portfolio()` and `delete_portfolio()` which help manage both the locally-created portfolio files and their corresponding database entries
- Updated `generate_portfolio.py` to include a `--save-to-db` flag that allows for future functionality for users to choose whether or not they want to save their portfolios to the database

### "View Portfolios" Main Menu Option [PR #261](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/261)
- Updated `main_menu.py` by adding formatting for displaying entries from the database's "portfolios" table within the terminal when using the menu option "2. Inspect Database" (essentially identical to formatting for "resumes" table)
- Updated `main_menu.py` to host functionality for a new menu option "10. View Portfolios" in which generated portfolios can be viewed, deleted, (and in the future, edited or added to) all from within the terminal interface (code largely borrowed from our "9. View Resumes" feature)

## Testing & Debugging Tasks
[PR #260](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/260)
- Updated `test_generate_portfolio.py` to account for the above improvements (a few functions now require additional arguments for the new performance metrics/confidence filtering)
- Renamed `test/detect_skills.py` to `test/test_detect_skills.py` to avoid any potential import conflicts with `src/detect_skills.py`
- Pushed a small fix for `test_project_evidence.py` fixing 4 tests that were failing on Windows due to open SQLite connections preventing temporary file deletion

[PR #261](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/261)
- Updated `test_db.py` to include two new tests: one checks that portfolios can be saved to, and deleted from our database; the second tests that all required fields (arguments for `save_portfolio()`) are verified properly before saving portfolios to the database
- Updated a test within `test_main_menu.py` that was failing due to being out of sync with our updated main menu options

## Reviewing & Collaboration Tasks
- Communicated regularly throughout the week in our Discord server
- Reviewed and approved:
    - Code PRs: [#264](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/264), and [#265](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/265)
    - Log PRs: [#272](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/272), and [#273](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/273)
- Completed individual log and peer review for T2 Week 2
- Caught and proposed fixes for failing tests (on Windows OS machines) introduced in [PR #265](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/265)

## Issues & Blockers
All implementations went smoothly for the most part. The biggest concerns I have mostly revolve around the accuracy and consistency of previously-implemented features from milestone 1. Our language, framework, and skill detection features still leave a bit to be desired in my opinion, and after adding their outputs to the portfolio, I am reminded that we still have fairly limited analyses in these departments. I believe I have hit the ceiling of my programming ability, and worry that LLM-integration may be the only way to deepen our analyses and improve accuracy across a wide array of projects. However, our non-LLM analyses should maintain a level of parity with our LLM analyses which may become an issue. I believe our detections are satisfiable for now, but I will speak with the rest of the team this upcoming week to see what their thoughts are. In summary, I did not run into any major issues this week, just a few minor concerns.

## Reflection Points
Overall I thought we had a solid week, all code additiuons were pushed by Sunday afternoon, and our Discord server was fairly active all week. I pushed all of my code additions early in the week, and my teammates were able to review and approve all of my changes within a day or two. All six of us were present in our Wednesday lecture this week, and it was a great opportunity for us all to meet up and discuss plans for the week. I have no complaints about how this week was handled by our team, and I look forward to next week!

## Goals for Next Week (T2 Week #3)
Currently, I am assigned to two remaining Kanban issues:
- 27. Customize and save information about a portfolio showcase project
- 23. Allow users to choose which information is represented

I have discussed these issues with my team, and we have a clear vision for how we want to implement them, but to do so without a frontend UI will be very difficult. The restrictions of the terminal interface will make our implementation incredibly cumbersome. So I would like to work on these, however I need to come up with a more concrete plan that all my teammates agree with.

Additionally, if I have the time, or if work on the two deliverables above is not possible, I could:
- Rework Kanban board to include all updated milestone 2 deliverables
- Update our README to include recent codebase changes/additions
- Assist Daniel and Travis with LLM-integration
- Assist Jaxson with our continued FastAPI support

## Kanban Board at End of T2 Week #2
This week I was able to tentatively close issue #29. Display textual information about a project as a portfolio showcase (item #238 on GitHub). The wording for the deliverable is fairly vague, and depending on feedback from teaching staff, I may need to re-open it in future weeks to make sure the feature is satisfiably implemented.

<img width="1874" height="895" alt="t2week2-kanban" src="https://github.com/user-attachments/assets/b66b47a7-8b54-4ddf-8646-a204f2d1d4a5" />

---

# Week #3 - January 19th - 25th

<img width="709" height="542" alt="t2week3-tasks" src="https://github.com/user-attachments/assets/072bb361-4a04-46be-86ae-f017ec8aa592" />

## Connection to Last Week
Last week I completed the portfolio generation feature with database integration and the "View Portfolios" menu option. I mentioned a variety of goals I wanted to work towards this week, but most of them didn't pan out as I expected. On Wednesday we met up as a team to discuss our plans, and we decided that pushing forward with new features/integrations was not a priority. As we wanted to ensure we had a bulletproof build of our program for our upcoming peer testing event. We focused largely on bug-fixing, polishing, and small or missing functionalities. I decided I wanted to rework our Docker setup to accomodate our new "API mode" as well as update some outdated dependencies/requirements. I also built some simple documentation for our Docker setup to add to the README to help onboard new users and make using Docker with our program as simple as possible. Additionally, I performed some light refactoring by standardizing our naming scheme for test files. I was also able to rework our Kanban issues to include the updated milestone 2 deliverables, as i mentioned I would last week.     

## Coding Tasks

### Docker and Test Suite Refactoring [PR #288](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/288)
- Renamed all test files within `test/` to follow a consistent naming convention: `test_TESTNAME.py` (previously some files used `TESTNAME_test.py`)
- Reorganized file headers across the test suite to ensure imports (namely pytest) are handled consistently
- Moved `inspect_db.py` from `test/` into `src/` as it was never a testing file
- Updated `Dockerfile` by removing duplicate `RUN apt ...` statements and cleaning up dependency installations
- Updated `docker-compose.yml`:
    - Created an additional "api" image to allow users to choose CLI vs API interaction within Docker
    - Added updated instructions for switching between CLI, API, and Testing modes
    - Updated test discovery to use `test_*.py` instead of the outdated `*_test.py` format
- Updated `requirements.txt` to include pydantic and uvicorn dependencies (required for FastAPI)
- Fixed import ordering in `main_menu.py` that was causing Docker container startup failures
- Added error handling in `project_evidence.py` for when no "projects" table exists in the database (i.e., when no project scans have occurred yet)

### Nested Folder Scan Support [PR #292](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/292)
- Fixed username extraction logic in `generate_resume.py` and `generate_portfolio.py` to properly handle nested JSON dictionary structures (previously failing on nested folder scans)
- Removed redundant loop from `generate_resume.py`'s username collection logic
- Restructured code in both files to ensure parity in code structure, spacing, and comments
- Added "Unknown" to the list of blacklisted usernames to filter out invalid entries

## Testing & Debugging Tasks

### Test Suite Updates [PR #288](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/288)
- Renamed 6 test files to follow the `test_*.py` naming convention:
    - `collab_summary_test.py` → `test_collab_summary.py`
    - `config_test.py` → `test_config.py`
    - `consent_test.py` → `test_consent_test.py`
    - `contrib_metrics_test.py` → `test_contrib_metrics.py`
    - `file_utils_test.py` → `test_file_utils.py`
    - `scan_test.py` → `test_scan.py`
    - `scan_db_test.py` → `test_scan_db.py`
- Updated imports and headers across all 28 modified test files to ensure consistency

### Nested Folder Test Fixes [PR #292](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/292)
- Updated `test_project_info_output.py` to handle the new return type from `output_project_info()` (now returns lists of paths instead of single strings top allow for nested project detection)
- Modified 2 tests to properly unpack lists and access the first element to accommodate the nested folder scanning changes

## Reviewing & Collaboration Tasks
- Communicated regularly throughout the week in our Discord server
- Completed individual log and peer review for T2 Week 3
- Completed the Team Log entry for this week
- Reviewed and approved:
    - Code PRs: 
        - [#291 - Fix portfolio generation to exclude non-contributor projects](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/291),
        - [#292 - Reworked Scan to fix nested folder scans](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/292), 
        - [#298 - Resume/Portfolio tests update after rework](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/298),
        - [#300 - Added tests for nested folders](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/300)
        - [#304 - DB table missing error fixed by auto initialization](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/304)
    - Log PRs:
        - [#303 - Daniel's Individual Log](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/303),
        - [#307 - Tyler's Individual Log](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/307)

- I also helped with polishing touches / quick fixes in the following PRs:
    - [#292](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/292) *My contributions are listed at the bottom of the PR template description + I also reworked test_project_info_output.py to account for a change in the return type of output_project_info().*
    - [#298](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/298) *I loosely suggested some test fixes I found last week. Travis, Jaxson, and Pri are all on Mac, while the other three of us are on Windows. When using temporary DB connections in our testing suite, Windows handles file locks differently than Mac, leading to some accessibility issues between the two operating systems. I found that by reorganizing the tearDown() function, and importing garbage collection to use gc.collect() helps to ensure that all file handles are removed on Windows before temporary connection cleaning begins, stopping the errors we were encountering. I did not specifically commit to this branch, but I suggested some potential fixes in our Discord. Jaxson's commit where he implemented these fixes was titled: "Fix Windows test cleanup by closing TestClient and forcing GC" (811ce7e).*

## Issues & Blockers
I cannot say that we encountered any major issues or blockers this week. We had a few minor hiccups, a few of the PRs ended up introduciong some breaking changes that went unnoticed at the time of posting, but were quickly indentified and rectificed during the code review process. We continue to run into this pesky issue, where file locks are handled differently between Windows and Mac devices, causing issues in any unit tests that rely on temporary directories and SQLite connections. We have identified this as a repeated issue, and have documented a consistent fix that we will need to continue to implement as we continue writing unit tests. We have also set a precedent of ensuring at least one Windows user and one Mac user should be reviewing every PR to ensure no OS-specific issues are slipping into our codebase. Overall, this week went smoothly, and we made a lot of solid progress towards polishing the current build of our program.

## Reflection Points
Everyone worked together really well this week, and we had to rely on collaboration more than ever. Daniel has made his [PR #292](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/292) and ran into a few breaking changes, but as he was busy travelling to and from campus, I fixed a few small issues I encountered during my reviewing of his branch and updated the Discord server with my changes. Similarily, when Daniel encountered the pesky file lock bug mentioned above in Jaxson's [PR #298](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/298), I was able to loosely propose a fix I implemented last week when I encountered a similar issue with Travis' tests, despite being at my place of employment with no access to a computer. As we encountered issues, we documented them in the Discord, often with accompanying screenshots, and we all banded together to suggest fixes whenever possible. I am very proud of how our team worked together this week!

## Goals for Next Week (T2 Week 4)
Next week I want to pick up where we left off at the end of last week. This week was largely focused on bug-fixing and polishing, but next week I'd like to continue implementing larger features:

- I still have a lot to do in terms of getting portfolio generation/editing into it's final state. I want to make portfolios more configurable/editable from the CLI, but I have my doubts about how cumbersome it will become, and whether or not I should wait until we have a frontend to flesh-out this feature. But I will likely do some research early next week to determine what is feasible.
- If I do not feel comfortable further developing the feature above, I would like to assist Daniel with LLM-integration. As it will be a large part of our program's analysis, it will likely need to be retroactively tied into all of our major functionalities included thus far, which will inevitably be a lot of work. I would like to help out with this process if at all possible.
- I would also like to do a better job at staying on top of our documentation this milestone, namely by regularly updating the README. It is not a high-priority task, but if I can find the time I would love to include what we have implemented so far in term 2.

## Kanban Board at End of T2 Week 3

<img width="1875" height="896" alt="t2week3-kanban" src="https://github.com/user-attachments/assets/444a23fe-64d7-4c38-a02b-0bcf253b57a7" />

---

# Weeks #4 and #5 - January 26th - February 2nd

TODO: <img width="" height="" alt="t2weeks4+5-tasks" src="" />

## Connection to T2 Week 3
T2 Week 3 was focused on bug-fixing, polishing, and preparing for peer testing. I mentioned wanting to continue pushing forward with larger features, and that is exactly what I was able to do during these two weeks. The first half of this period was dominated by peer testing preparations: revamping the main menu layout, updating the session outline, and standardizing our error handling across the CLI. The second half shifted towards implementing new functionality: a scanned project TXT summary manager, critical bugfixes after merging, and further error handling improvements based on teammate and peer tester feedback. These two weeks combined saw significant changes to the core CLI experience.

## Coding Tasks

### [T2 Week 4 - January 26th to February 1st]

### 1. Standardized error handling for core functionalities [PR #346](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/346)
- I essentially reworked all error messages I found, that are tied to any of the functionalities that are accessible from the main menu. I just scanned through each file top-to-bottom and replaced any error messages with a new standardized format:
"Error: ERROR_MESSAGE"
"    Hint: HINT_MESSAGE"
- Most of the error handling was able to be handled from within `main_menu.py`, but for all error messages relating to managing project evidence, I had to change the wording directly in the `project_evidence.py` script, as it works as more of an external submenu, so error handling is handled locally.
- I also had to update a failing test in `test_main_menu.py` to accommodate the updated error message format.
*Full transparency: This does not ensure ALL error handling is standardized. I only reworked anything I found in the CORE interaction loop*

### 2. Bugfixes before T2 Week 4 final merge [PR #349](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/349)
*Certain elements of our program broke during the last round of PR merges. This commit includes some hotfixes for the most intrusive of the newly introduced issues:*
- `main_menu.py`:
    - Updated `handle_view_resumes()` to host the same logic as `handle_view_portfolios()`:
        - Added the `action` prompt so users can choose to (v)iew, (a)dd, (d)elete, or (c)ancel
        - Added the `add_path` logic using `prompt_project_path()` when the user chooses "a"
        - Wrapped handle_add_to_resume() in a try/except for improved error handling
    - Reworked a code block at the top that handled scan settings and scan paths. This was a merge conflict issue within PR #346, so I just reverted the changes to what was on Development before.
    - Fixed an issue that arose during the merge that made the main menu options out of sync. Re-wired options 11. Thumbnails and 12. Manage Database and ensured they were functional.
    - Fixed an issue that changed the runtime prompts during a project scan. It has now been set back to its intended structure: review consent policy (y/n) scan project path: filter by file type: save settings for next time (y/n)
    - Changed "Exit" menu option to be activated with number zero instead of thirteen for cleanliness
- `test_main_menu.py`: Updated the first test to accommodate for the updated menu numbering
- `project_evidence.py`: Fixed an issue where the list of current feedback was not re-printed when entering (e)dit or (d)elete submenus.

### [T2 Week 5 - February 2nd to 8th]

### 1. Improved Error Handling Based on Teammate Feedback [PR #351](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/351)
- Addressed 5 issues identified by Jaxson and Pri during review of PR #346:
    1. Removed `default=False` parameter from `ask_yes_no()` in `consent.py` to ensure re-prompting always occurs on invalid/empty inputs
    2. Added while loops with re-prompting in `main_menu.py` for empty scan path inputs (previously sent users back to the main menu)
    3. Added while loops with proper error handling in `generate_portfolio.py` for username selection — both when no candidates are found and when candidates are listed
    4. Applied the same username selection fixes to `generate_resume.py` for parity
    5. Removed the deprecated "(Tip: use option 12 to edit project display names.)" message from resume generation output, as the feature was no longer accessible at that menu number
- Removed deprecated `default=False` arguments from `ask_yes_no()` calls across `main_menu.py`

### 2. Scanned Project TXT Summary Manager [PR #352](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/352)
- Implemented a new main menu option: `2. View/Manage Scanned Projects`
    - Shifted all existing menu options down to accommodate the new entry
- Added `_list_project_summaries()` helper function to locate the `output/` folder, find JSON and TXT summary files for each scanned project, and build a list of project names, paths, and file counts
- Added `_delete_project_output_files()` helper function to delete local JSON and TXT summary files for a project
- Added `handle_manage_scanned_projects()` to host the core logic for the new feature:
    - Lists available project summaries with any custom display names
    - Offers three actions: View (prints TXT summary to CLI), Edit Display Name, and Delete Scanned Project
    - Delete action clears both the database entry and the local output folder
- Updated the "Delete Project" feature within `13. Manage Database` to also clear the project's local `output/` folder when possible

### 3. Improved scan progress CLI output [PR #354](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/354)
I revamped how the scan progress output is formatted within the CLI. We received feedback during our first peer testing event that our CLI got overwhelming during scanning due to the mountain of text, file paths, and metrics that were printed to the CLI. I wanted to improve the user experience when scanning, so I cleaned up the formatting for scan progress updates:
- `scan.py`:
    - Added `ScanProgress` class for centralized, clean CLI output management
    - Added `scan_with_clean_output()` as unified scan entry point with phased/modularized progress display
    - Added helper functions `get_scan_progress()` and `reset_scan_progress()` for global progress instance management
    - Removed label parameter from `_run_with_progress()` calls, now uses ScanProgress to display to the CLI `Updated `if __name__ == "__main__"` block to direct users to main menu
- `main_menu.py`:
    - Replaced `run_with_saved_settings` import with `scan_with_clean_output` in order to use the new CLI scan progress formatting
    - Added `_show_post_scan_menu()` for post-scan action selection (view summary, manage other projects, return to main menu)
    - Added `_view_project_summary()` to display TXT summaries for scanned projects
    - Refactored `handle_scan_directory()` to use new clean scan system with an updated and simplified flow
- `project_info_output.py`:
    - Added quiet parameters to `gather_project_info()` and `output_project_info()` to suppress progress messages (preserves code and logic, but doesn't use it for CLI output)
    - Added confidence categorization (high/medium/low) for languages/frameworks in TXT summary, and during CLI progress reporting
- `detect_langs.py`: Commented out the "Log filtering statistics" code to ensure the new output remains clean

## Testing & Debugging Tasks

### Test Updates
### [T2 Week 4 - January 26th to February 1st]
- [PR #346](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/346): Updated 1 test to accomodate the new standardized `print_error()` message format
- [PR #349](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/349): Updated 1 test to accomodate the new main menu numbering
### [T2 Week 5 - February 2nd to 8th]
- [PR #351](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/351): Updated 6 tests to remove deprecated `default=False` arguments from `ask_yes_no()` calls
- [PR #352](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/352): Updated 1 test to accomodate the new main menu numbering

## Reviewing & Collaboration Tasks
- Communicated regularly throughout the two weeks in our Discord server
- Completed individual log and peer review for T2 Weeks 4 & 5
- Reviewed and approved:
    - Code PRs:
        - [#321 - Contributor score fix](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/321) (Daniel)
        - [#322 - Reworked key roles of a project to be clearer and more in depth](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/322) (Daniel)
        - [#323 - Update to main menu](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/323) (Jaxson)
        - [#347 - Reworked Thumbnail Feature](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/347) (Jaxson)
        - [#348 - Database management](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/348) (Tyler)
        - [#353 - Updated resume summary section](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/353) (Jaxson)
        - [#356 - Refactor username selection into shared helper and update resume/portfolio generation](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/356) (Priyanshu)
        - [#357 - Integrated LLM summary](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/357) (Jaxson)
    - Log PRs:
        - TODO:
- Participated in and helped organize our first peer testing event
- Aggregated peer testing feedback/known bugs/remaining M2 deliverables, and translated them into GitHub issues 

## Issues & Blockers
The biggest challenge these two weeks was dealing with merge conflicts. After the initial round of PRs were merged, several components of the program broke. I spent a bit of time hotfixing these issues in PR [PR #349](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/349) before the final merge could go through. None of the breaking changes were too difficult to fix, and there was only a small handful of critical errors. But still, our program couldn't even be executed on my system without fatal errors. This reinforces the importance of thorough post-merge testing, especially when multiple PRs touch the same files (in our case, `main_menu.py` and `scan.py` are becoming minor bottlenecks for merge conflicts)

## Reflection Points
These two weeks were productive and featured a good mix of polishing and new feature work. The peer testing event went smoothly thanks to the preparation we put in during the first week. We took plenty of notes and were quick to translate feedback into actionable GitHub issues. We spent a lot of time improving the error handling, CLI user experience, and overall polish of our program. We also took a huge step forwards thanks to Jaxson's work on the LLM-assisted project summary implementation in [PR #357](https://github.com/COSC-499-W2025/capstone-project-team-11/pull/357). Our project is becoming more streamlined, more accessible, and more visually appealing every week. Our team vision feels clearer and more aligned than ever before. I'm really proud of our team's work over these two weeks, and I am excited to be closing in on the end of milestone 2! 

## Goals for Next Week (T2 Week 6)
- Continue improving the CLI experience (nested project scanning is currently buggy, and I have fixes planned for next week thanks to PR review feedback from Travis)
- Begin looking into finalizing resume and portfolio functionality (I want them to be customizable and editable, but I fear the restrictions put in place by the CLI interface)
- Assist teammates with LLM integration work if needed, as it is becoming a priority for improving our analysis features (langauges, skills, contributor roles, rankings, etc.)

## Kanban Board at End of T2 Weeks 4 & 5
TODO: <img width="" height="" alt="t2weeks4+5-tasks" src="" />