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
