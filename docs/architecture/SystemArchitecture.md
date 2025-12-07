![Milestone 1 Architecture Diagram](Milestone1-SystemArchitectureDiagram.png)

## System Architecture Overview

The Milestone 1 system is a local Python CLI application that scans project directories, analyzes code artifacts, stores results in a SQLite database, and generates both project summaries and contributor resumes. The architecture is organized into four functional layers:

---

### User Layer (Blue)

- The user runs the CLI
- Provides actions such as **Scan**, **Ranking**, **Summaries**, and **Resume Generation**.

---

### Presentation / Control Layer – Menu (Green)

- Central controller for all user interactions.
- Prepares scans, routes commands, and provides database inspection.
- Delegates work to scanning, analysis, and resume-generation components.

---

### Data Collection Layer (Orange)

#### Consent/Config
- Handles privacy messaging, consent prompts, and loads/stores user preferences.

#### File & Zip Scanner
- Traverses directories and nested archives.
- Extracts metadata, languages, skills, and contributor info.
- Writes results to the database.

#### Git Metrics Scanner
- Parses git repositories to capture commits, line changes, authorship data, and timestamps.

---

### Processing / Analysis Layer (Purple)

#### Analysis & Aggregation
- Combines scan artifacts with git metrics.
- Computes rankings and metrics.
- Generates project summaries stored in the database.

#### Resume Generator
- Builds Markdown resumes using summaries, skills, languages, and contribution metrics.
- Stores generated resume records in the database.

---

### Data / Output Layer (Yellow)

#### Database (SQLite)
- Stores scans, skills, languages, git metrics, summaries, and resume records.

#### Project/Summary Output
- Exports JSON/TXT project summaries and collaborator reports
