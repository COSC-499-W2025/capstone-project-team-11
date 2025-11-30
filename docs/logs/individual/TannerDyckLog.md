# Tanner Dyck Personal Log
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

***

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

***

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

***

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

# Week #11 - November 10th - 16th
During the reading break week, no work was done on our capstone project

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
