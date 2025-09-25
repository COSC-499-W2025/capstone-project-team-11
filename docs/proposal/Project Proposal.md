# **Features for Project Proposal**

Team 11:  
Daniel Sokic   
Travis Frank   
Tanner Dyck   
Jaxson Kahl   
Priyanshu Chugh   
Tyler Cummings  

## **1	Project Scope and Usage Scenario**

Our project focuses on helping **university students** and **early professionals** who spend much of their time working on computers better understand their digital work history and contributions. Users will be able to scan directories and repositories on their machines to identify important files, projects, and productivity data. Example scenarios include:

* A student preparing job applications, scanning files to highlight completed projects, and generating portfolio content.  
* A student cleaning up duplicate or outdated files to improve file management.  
* A developer discovering and summarizing GitHub repositories stored locally.  
* An employee reviewing their contributions and artifacts ahead of a performance evaluation.  
* A researcher preparing for publication scans their data folders to categorize experiment files, filter results by date ranges, and export a clean report for inclusion in their paper.  
* A team lead auditing a project repo runs the tool to check for outdated or duplicate documents and prepare a status report for management.

The system will serve both **individual learners/job seekers** and **early-career professionals** looking to reflect on and present their digital contributions.

## **2	Proposed Solution**

Our solution is a **local desktop application** (Electron \+ TypeScript frontend with a Node.js backend) that scans directories and repositories to identify work artifacts. The system will:

* **Categorize files** (documents, code, media) and detect duplicates.  
* **Display creation dates** and provide date filtering and sorting.  
* **Generate clear and readable visual outputs** (PDF, HTML, PNG, JPG) for users to keep or share.  
* **Enable project discovery** by summarizing GitHub repositories and related work history.  
* Provide an intuitive UI where users select scan locations, manage results, and export outputs.

**Value proposition:** Unlike generic file explorers, our system emphasizes career and productivity insights, not just storage. We combine technical project scanning with human-readable reporting (exportable formats). Our approach highlights what users have created and contributed, rather than only where files are located.

## **3	Use Cases**

## **Use Case 1:** Select Scan Locations

* **Primary actor:** User  
* **Description:** Choose folders/drives to include or exclude from scanning.  
* **Precondition:** App is running; user has permissions to read selected paths.  
* **Postcondition:** Selected locations are saved for scanning.  
* **Main Scenario:**  
  1. User opens “Scan Locations.”  
  2. User adds/removes directories and sets include/exclude rules.  
  3. User saves the selection.  
* **Extensions:**  
  1. Invalid or inaccessible path → system shows an error and keeps previous valid list.

## **Use Case 2:** Scan Directory

* **Primary actor:** User  
* **Description:** Scan chosen locations for files and gather metadata (name, path, size, creation date, type).  
* **Precondition:** At least one valid scan location is set.  
* **Postcondition:** Scan results are stored in memory/local storage.  
* **Main Scenario:**  
  1. User clicks “Scan.”  
  2. System traverses directories and indexes files.  
  3. System records metadata for each file.  
  4. System displays progress and completion status.  
* **Extensions:**  
  1. Empty directory → system completes with zero results notice.  
  2. Read errors/permissions → system logs and displays non-blocking warnings.

## 

## **Use Case 3:** Categorize Files

* **Primary actor:** System  
* **Description:** Group files by type (e.g., documents, code, media) using extension/MIME.  
* **Precondition:** Scan results exist.  
* **Postcondition:** Results are labeled with categories and shown grouped in UI.  
* **Main Scenario:**  
  1. System infers type from extension/MIME.  
  2. System assigns categories to each file.  
  3. UI updates with grouped views and counts.  
* **Extensions:**  
  1. Unknown/ambiguous type → assign “Other” and allow user override.

## **Use Case 4:** View, Filter, and Sort by Date

* **Primary actor:** User  
* **Description:** Inspect results; filter by single date/range; sort by creation date; verify timezone handling.  
* **Precondition:** Categorized results available.  
* **Postcondition:** UI shows filtered/sorted subset. User can reset filters.  
* **Main Scenario:**  
  1. User opens the results view.  
  2. User sets a date or range and chooses ascending/descending.  
  3. System updates the list and summary stats.  
* **Extensions:**  
  1. No matches for the range –  system shows “no results” state with clear reset option.

## **Use Case 5:** Detect Duplicates

* **Primary actor:** System  
* **Description:** Identify duplicate files using size/hash (and optionally name/path heuristics).  
* **Precondition:** Scan results exist.  
* **Postcondition:** Potential duplicate groups are labeled and shown.  
* **Main Scenario:**  
  1. User enables “Find Duplicates.”  
  2. System computes signatures (e.g., hash) and groups matches.  
  3. UI presents duplicate clusters with locations.  
* **Extensions:**  
  1. Large files → system switches to chunked/size-first strategy with progress indicator.  
  2. Permission issues → flagged but scan continues.

## **Use Case 6:** Generate Visual Report

* **Primary actor:** User  
* **Description:** Build a visual summary (charts/tables) of scan results for review.  
* **Precondition:** Results exist; at least one category/date selection made.  
* **Postcondition:** A rendered report view is available for export.  
* **Main Scenario:**  
  1. User clicks “Generate Report.”  
  2. System compiles selected views (by category, by date, duplicates).  
  3. System renders a report preview.  
* **Extensions:**  
  1. Very large dataset → system paginates/summarizes and notes truncation rules.

## **Use Case 7:** Export Results

* **Primary actor:** User  
* **Description:** Export report/results to PDF, HTML, PNG, or JPG.  
* **Precondition:** Report or results view is available.  
* **Postcondition:** Export file saved to user-selected location.  
* **Main Scenario:**  
  1. User selects format (PDF/HTML/PNG/JPG).  
  2. System generates the file.  
  3. System saves and confirms with a link/path.  
* **Extensions:**  
  1. Disk full/permission denied → export fails with actionable error message.

## **Use Case 8:** Clear/Refresh Scan

* **Primary actor:** User  
* **Description:** Clear previous results or re-scan with current locations/preferences.  
* **Precondition:** Results exist (for clear) or locations set (for refresh).  
* **Postcondition:** Cleared state or new results replace old ones.  
* **Main Scenario:**  
  1. User chooses “Clear” or “Refresh.”  
  2. System confirms destructive action (for Clear).  
  3. System clears and/or re-scans; UI updates.  
* **Extensions:**  
  1. Missing locations on refresh → system prompts to set locations first.

## **Use Case 9:** Configure Preferences

* **Primary actor:** User  
* **Description:** Set app-wide options (default export format, category overrides, timezone display, duplicate sensitivity).  
* **Precondition:** App is running.  
* **Postcondition:** Preferences persisted and applied to future scans/exports.  
* **Main Scenario:**  
  1. User opens Settings.  
  2. User edits preferences (e.g., date format, default filters, category rules).  
  3. System saves and applies changes immediately or on the next run as appropriate.  
* **Extensions:**  
  1. Invalid value → inline validation and revert to the last valid setting.

## **4	Requirements, Testing, Requirement Verification**

**Functional Requirements**

| Requirement | Description | Test Cases (Pos and Neg) | Who | H / M / E |
| :---- | :---- | :---- | :---- | :---- |
| The system must be able to display information based on file creation dates.  | Users can choose to view artifacts within a certain date range to filter their preferred data. <br> **Steps:** 1. Collect file metadata 2. Store and index the dates 3. Provide filtering for data 4. Process the data 5. Display the data to user <br> **Possible difficulties:**  Inconsistent file creation Large dataset performance User privacy  | **Test Case 1:** Verify system can display all artifacts sorted by file creation date <br>  **Preconditions:** System has completed a scan and stored artifacts with creation dates <br> **Test Steps:**          1\. Open dashboard 2\. 2\. Select “Sort by Creation Date (Ascending)”<br>  **Expected result:** Work displayed from oldest to newest based on its creation date <br>  **Test Case 2:** Verify filtering by date range returns correct results. <br> **Preconditions**: System has work spanning multiple months. <br>  **Test Steps:**              1\. Open dashboard  2\. Select date filter 3\. Apply filter <br> **Expected result:** Only artifacts created between the date range are displayed.    | Daniel | Medium  |
| The system must be able to categorize files by type (e.g., documents, code, media). | This feature allows the system to categorize work into file type categories such as code, documents, media, and design files.<br>**Steps:**  1. Scan files Identify file type 2. Store category in database 3. Display categorised results.<br>**Possible difficulties**  Ambiguous file types Custom formats Scalabality  | **Test Case 1:** Verify code files are categorised correctly. <br>  **Preconditions:** System scanned folders with .py, .java, .cpp files.<br>  **Test Steps:**             1\. Open dashboard 2\. Filter by “code” <br> **Expected Result:** Only code files are displayed. **Test Case 2:** Verify document files are categorised correctly.<br>  **Preconditions:** System scanned folders with .docx, .pdf, .txt. <br> **Test Steps:**             1\. Open dashboard  2\. Filter by “document” <br> **Expected Result:** Only document files are displayed. <br> **Test Case 3:** Verify media files are categorised correctly. <br>  **Preconditions:** System scanned folders with .jpg, .png, and .mp4. <br> **Test Steps:**             1\. Open dashboard  2\. Filter by “media”<br>  **Expected Result:** Only media files are displayed.  | Travis | Medium |
| The system must present scan results visually in clear, human-readable formats such as PDF, HTML (printable webpage), PNG, or JPG. | The user can select between several output formats such as PDF, JPG, PNG, or HTML. <br>  **Steps:** 1. Generate report data Render visuals such as charts, tables, summary counts, and key metrics. 2.Export to desired format. 3. Present to user <br> **Possible difficulties:** Formatting consistency  Chart rendering for exports Cross-platform file generation |  **Test Case 1:** Verify export type works with summary data. <br> **Preconditions:** Scan completed with results. <br>  **Test Steps:**             1\. Go to dashboard  2\. Click export as desired format        3\. Save file              4\. Open file <br>  **Expected Result:** Desired file format contains correctly formatted summary, charts, and tables.<br>  **Test Case 2:** Verify export respects filters.<br>  **Preconditions:** User applied category/dates filter. **Test Steps:**             1\. Apply filter         2\. Export report      <br>  **Expected Result:** Report only contains filtered data.  | Tyler | Hard |
| The system must be able to scan user-selected directories to locate relevant work artifacts. | The system must be able to scan user-selected directories to locate relevant work artifacts. <br> **Steps:** 1. User selects directories to include. 2. System validates path accessibility. 3. System traverses the directories. 4. Metadata (name, size, type, creation date) is collected. 5. Results are stored and displayed. <br> **Possible difficulties:** Handling inaccessible or permission-restricted folders Large dataset traversal performance Ensuring the scan is non-blocking for the UI | **Test Case 1:** Verify system scans a valid directory. <br> **Preconditions:** User has selected a valid directory with files.<br>  **Test Steps:** Open application. Select directory containing files. Start scan.<br>  **Expected Result:** All files in the directory are scanned and displayed with metadata. <br> **Test Case 2:** Verify system handles empty directory.<br>  **Preconditions:** User selects an empty directory. <br> **Test Steps:** Open application. Select empty directory. Start scan. <br> **Expected Result:** System completes scan with “no files found” message, no crash. <br> **Test Case 3:** Verify invalid or inaccessible directory. <br> **Preconditions:** User selects an invalid or restricted path.<br>  **Test Steps:** Open application. Select directory without access. Start scan. <br> **Expected Result:** System shows error notification, does not crash, and continues to function. | Jaxson | Medium |
| The system must allow users to clear, refresh, or re-scan their data. | Able to completely remove scanned work and start fresh, refresh previously scanned work to update metadata, and perform a full scan of selected work with new possible selections <br> **Steps:** 1. Provide data management options 2. Clear data (delete stored data from database) 3. Refresh data (retrieve list of previously scanned directories and reprocess file metadata and categories). 4. Re-scan (allow user to re-select directories and perform full scanning process again).5. Display status <br>  **Possible difficulties:**  Accidental data loss Partial refresh issues Handling deleted directories  | **Test Case 1:** Verify clear data removes all previous data. <br> **Precondition:** Scan completed and result stored. <br> **Test Steps:**             1\. Select clear data  2\. Confirm action <br> **Expected Results:** All stored results are deleted, dashboard is empty. <br> **Test Case 2:** Verify refresh updates modified files <br> **Precondition:** Directory contains updated files.<br>  **Test Steps:**             1\. Modify a file in the scanned folder.  2\. Select refresh <br> **Expected Results:** Dashboard updates with new metadata. **Test Case 3:** Verify re-scan reprocesses all files. <br> **Precondition:** Previous scan exists. <br> **Test Steps:**             1\. Select re-scan     2\. Keep the same folder selection<br>  **Expected Results:** Dashboard is fully updated with current state of directories.                          | Priyanshu | Hard |
| The system must provide a simple user interface for selecting scan locations and setting preferences. | Users can easily choose one or more folders to scan and set basic options.<br>  **Steps:** 1\. Click <br>  **Select Location**. 2\. Pick one or more folders and confirm. 3\. Open <br> **Preferences**. 4\. Choose options (ignore certain folders, file types to include, date range, “only changed since last scan”). 5\. Click **Save** — the app **remembers** these settings next time. 6\. Click **Start Scan**. <br> **Possible difficulties:** \- Folder picker works a bit differently on Windows/Mac/Linux. \- Some folders may be locked or not available. \- Users may choose a folder that no longer exists.. | **Test Case 1:** Pick a folder and save preferences <br> **Preconditions:** App is installed with default settings. <br> **Steps:**  1\) Select /documents → Start Scan.           2\) Open Preferences, turn on “Only changed since last scan”, Save. 3\) Close and reopen the app. <br> **Expected:** Settings are remembered; the option is still on. <br> **Test Case 2:** Multiple folders and one missing <br> **Preconditions:** /Projects/A and /Projects/B exist; /USB1 is not connected. <br> **Test Steps:**                  1\) Select A, B, and /USB1.                2\) Start Scan.<br>  **Expected Result:** App scans A and B; shows a clear message that /USB1 can’t be scanned; no crash. | Tanner | Medium |
| Detect duplicates via SHA-256 hashing. | The system must be able to detect duplicate files. <br> **Steps:** 1\. Collect file metadata and hashes (e.g., SHA-256). 2\. Compare files based on size \+ hash. 3\. Group identical files into duplicate sets. 4\. Display duplicates to the user.<br>  **Possible difficulties:** \- Large file hashing may slow performance. \- Files with the same size but different contents. \- Handling permission-denied or corrupted files. | Case 1:**Verify** system detects two identical files with different names. <br> **Preconditions:** Two files with identical content but different file names exist in the directory.<br>  **Test Steps:** 1\. Run a scan. 2\. Open duplicate groups panel. <br> **Expected Result:** Both files appear in the same duplicate group Case 2:Verify system does not mark different files of the same size as duplicates.<br>  **Preconditions:** Two files with same size but different content exist.<br>  **Test Steps:** 1\. Run a scan. 2\. Check duplicate groups.<br>  **Expected Result:** Files are not marked as duplicates.  | Priyanshu | Medium/Hard |

**Non-Functional Requirements**

| Requirement | Description | Test Cases | Who | H / M / E |
| :---- | :---- | :---- | :---- | :---- |
| Scalability  | The system should handle increasing number of files and larger directory structure | Test with nested folders 10+ levels deep and ensure scanning does not fail.  | Daniel | Medium |
| Performance | The system must scan and categorise the work in a reasonable amount of time.  | Run a scan on a folder with \<1GB of mixed files and verify it can be done within 30 seconds Run scan on a folder with 10,000+ small files and make sure results are still generated without timeouts or crashes. | Travis | Medium |
| Usability | The interface must be intuitive for users that range from experts to people who rarely use computers. | Check that buttons and controls are labeled clearly and produce expected outcomes. | Jaxson | Easy |
| Reliability  | The system should handle unexpected shutdowns or incomplete scans gracefully without crashing. | Simulate system shut down during scan and verify that on restart, system doesn’t lose previous results and can resume scanning.  | Tanner | Hard |
| Security and Privacy | User data must remain private and only accessible locally unless explicitly shared.  | Attempt unauthorized access to stored results and verify results are access-controlled. | Tyler | Medium |
| Maintainability  | Codebase must be modular and well-documented to support future API and front-end integration. | Conduct code review and verify that code follows naming conventions, is commented, and uses modular functions/classes. | Priyanshu | Easy |

