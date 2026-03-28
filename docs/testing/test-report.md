# Test Report
 
## 1. Overview
 
This project uses a combination of backend integration testing and frontend UI testing to validate system correctness across all major components.
 
Testing focuses on:
 
- File parsing and project extraction
- Database operations and persistence
- API endpoint correctness
- Resume and portfolio generation
- Frontend user interaction and workflows
 
The testing strategy emphasizes realistic system behaviour, simulating actual usage flows rather than relying on isolated unit tests with heavy mocking.
 

## 2. How to Run the Tests
 
### Backend
 
From the repository root:
 
```bash
pytest -v
```
 
Requires Python 3.11 and the dependencies listed in `requirements.txt`. The test suite uses a temporary SQLite database per test class, so no database setup is needed before running.
 
### Frontend
 
```bash
cd frontend
npm test
```
 
Requires dependencies installed via `npm install`. Tests run using Vitest in non-watch mode (`vitest run`).
 
## 3. Test Results
 
### Backend
 
| Result | Count |
|---|---|
| Passed | 288 |
| Skipped | 1 |
| Failed | 0 |
| Total | 289 |
| Duration | 21.6s |
 
### Frontend
 
| Result | Count |
|---|---|
| Passed | 57 |
| Failed | 0 |
| Test Files | 7 |
| Duration | 8.67s |
 
 
### Combined
 
| Suite | Passed | Skipped | Failed | Total |
|---|---|---|---|---|
| Backend (pytest) | 288 | 1 | 0 | 289 |
| Frontend (Vitest) | 57 | 0 | 0 | 57 |
| **Total** | 345 | 1 | 0 | 346 |
 

 
## 4. Backend Testing
 
### Tools
 
- `pytest`
- `FastAPI TestClient`
- Temporary SQLite databases (via `tempfile`)
- Isolated filesystem environments
- `unittest.mock.patch` for external service isolation
 
### Strategy
 
Backend tests are primarily integration tests that validate the full request pipeline:
 
```
HTTP Request -> FastAPI Route -> Business Logic -> SQLite Database -> JSON Response
```
 
Rather than mocking at every layer, tests execute real logic using temporary databases, generated file and directory structures, and realistic seed data. The database path is controlled through the `FILE_DATA_DB_PATH` environment variable, which is overridden per test class via `setUp` and restored in `tearDown`. This ensures tests are fully isolated and reproducible.
 

 
### API Testing
 
The API is tested using `FastAPI TestClient`, which allows HTTP-style testing without running a live server. Each test class creates a fresh `TestClient` instance pointing at a reloaded module with an isolated temporary database, ensuring no state bleeds between tests.
 
The following endpoints are covered:
 
| Endpoint | Method | Test File |
|---|---|---|
| `/privacy-consent` | POST | `test_api.py` |
| `/config` | GET | `test_api.py` |
| `/projects/upload` | POST | `test_api.py` |
| `/projects/scan-plan` | POST | `test_api.py` |
| `/projects/scan-stream` | POST | `test_api.py` |
| `/projects` | GET | `test_api.py` |
| `/projects/{id}` | GET | `test_api.py` |
| `/projects/{id}` | PATCH | `test_api.py` |
| `/projects/{id}` | DELETE | `test_api.py` |
| `/projects/{id}/thumbnail/image` | GET | `test_api.py` |
| `/projects/{id}/evidence` | POST | `test_api.py` |
| `/projects/{id}/evidence/{id}` | PATCH | `test_api.py` |
| `/projects/{id}/evidence/{id}` | DELETE | `test_api.py` |
| `/skills` | GET | `test_api.py` |
| `/resumes` | GET | `test_api.py` |
| `/resume/generate` | POST | `test_api.py` |
| `/resume/{id}` | GET | `test_api.py` |
| `/resume/{id}/edit` | POST | `test_api.py` |
| `/resume/{id}/pdf` | GET | `test_api.py` |
| `/resume/{id}/pdf/info` | GET | `test_api.py` |
| `/resume/{id}` | DELETE | `test_api.py` |
| `/portfolio/generate` | POST | `test_api.py` |
| `/portfolios` | GET | `test_api.py` |
| `/portfolios/{id}` | GET | `test_api.py` |
| `/portfolios/{id}/name` | PATCH | `test_api.py` |
| `/web/portfolio/{id}/timeline` | GET | `test_api.py` |
| `/web/portfolio/{id}/heatmap` | GET | `test_api.py` |
| `/web/portfolio/{id}/showcase` | GET | `test_api.py` |
| `/web/portfolio/{id}/customize` | PATCH | `test_api.py` |
 
Validation performed per endpoint includes correct HTTP status codes (200, 201, 400, 403, 404), response JSON structure and field presence, database persistence of side effects, and correct error messages.
 
Notably, `test_scan_stream_includes_structured_multi_project_results` uses `patch.object` to inject a controlled scan result, then reads the streaming response body to assert the `SCAN_DONE::` payload is correctly structured with partial success and failed project lists.
 
---
 
### Core Feature Testing
 
#### Scanning and File Processing
 
**Files:** `test_scan.py`, `test_scan_db.py`, `test_file_utils.py`, `test_relative_paths.py`
 
`test_scan.py` contains four test classes. `TestListFilesInDirectory` validates the `list_files_in_directory` function across recursive and non-recursive traversal, file type filtering, deeply nested directories, zip archive scanning (including nested zips), colon-separated path notation for zip entries, and correct handling of empty folders and macOS junk directories.
 
`TestScanProgressOutput` validates the `ScanProgress` class, confirming that stored scan metrics appear in the completion summary and that `get_scan_progress` behaves as a singleton unless explicitly reset.
 
`TestProjectRootDetection` validates the internal `_find_all_project_roots`, `_find_candidate_project_roots`, and `_map_files_to_repos` helpers, including correct handling of Windows drive letter paths.
 
`TestScanWithCleanOutput` tests the top-level `scan_with_clean_output` entry point, verifying that empty paths return a failure result and that valid single-project directories produce a success result with all expected keys and file counts.
 
`test_scan_db.py` verifies that scan results are persisted to the database, covering directory scans, zip scans with nested files, the `save_to_db=False` flag, the colon-separated path format for nested zip entries, and thumbnail path persistence.
 
---
 
#### Data Extraction and Analysis
 
**Files:** `test_detect_langs.py`, `test_detect_skills.py`, `test_detect_roles.py`, `test_contrib_metrics.py`
 
`test_detect_langs.py` covers language detection from file extensions and content patterns, framework detection from config files, confidence level assignment (high, medium, low), comment stripping for multiple languages, case normalization, and correct skipping of ignored directories such as `node_modules`.
 
`test_detect_roles.py` covers contributor role classification across five test classes: role categorization (Backend Developer, Frontend Developer, QA Tester, UI/UX Designer, Full Stack), role score calculation, confidence scoring, full project role analysis for single and multi-contributor projects, and per-project breakdown formatting.
 
`test_contrib_metrics.py` validates contribution metrics including single and multiple author scenarios, zero-commit user exclusion, file category classification (code vs test vs design vs document), and commits with no file changes.
 
`test_detect_skills.py` validates skill extraction from file content including web development, OOP, recursion, and technical writing detection.
 
---
 
#### Database Operations
 
**Files:** `test_db.py`, `test_db_updates.py`, `test_db_schema_init.py`, `test_db_maintenance.py`, `test_db_clear_and_delete_project.py`, `test_db_clear_output_directory.py`
 
`test_db_schema_init.py` validates schema correctness including all table creation, default values, foreign key constraints, cascade behaviour for scans, files, and project evidence, and join table foreign keys.
 
`test_db.py` validates `save_portfolio` and `delete_portfolio` including correct serialization of `included_project_ids` and `featured_project_ids` as JSON columns, input validation (empty username or portfolio name raises `ValueError`), and correct boolean return values for delete on valid vs. non-existent IDs.
 
`test_db_clear_and_delete_project.py` verifies that `delete_project` removes all related rows (scans, files, file contributors, file languages), that clearing the entire database removes all data, and that invalid or `None` IDs are handled without crashing.
 
`test_db_maintenance.py` validates the pruning logic that removes old scans and their related rows while leaving other projects untouched.
 
---
 
#### Project Aggregation and Ranking
 
**Files:** `test_rank_projects.py`, `test_rank_projects_by_contributor.py`, `test_summarize_projects.py`, `test_collab_summary.py`
 
`test_rank_projects_by_contributor.py` validates contributor-based ranking including correct ordering, case-sensitive name matching, tie-breaking by file count then name, limit parameter enforcement, and correct handling of contributors with no files.
 
`test_summarize_projects.py` validates the full project summarization pipeline including metric merging from commits and file counts, language and framework and skill aggregation, error handling in the gather step, limit enforcement, and correct handling of unknown contributors.
 
`test_collab_summary.py` validates collaboration detection from both git and non-git projects, including commit detection, changed file tracking, multiple author identification, and error handling for invalid paths.
 
---
 
#### Resume Generation
 
**Files:** `test_generate_resume.py`, `test_regenerate_resume.py`
 
`test_generate_resume.py` has two test classes. `TestGenerateResume` validates the core module functions: `normalize_project_name` correctly preserves acronyms such as TCP and UDP while capitalising other words; `collect_projects` returns the expected dictionary structure; and `aggregate_for_user` plus `render_markdown` produce correctly headed Markdown output with the generation timestamp.
 
`RobustGenerateResumeTests` adds further coverage including exclusion of projects by name from aggregation, inclusion of evidence impact text in the rendered Markdown, CLI subprocess behaviour (correct file creation, bot username blocking and the `--allow-bots` override), and database persistence of generated resumes via `--save-to-db`.
 
`test_regenerate_resume.py` validates the regeneration workflow including missing argument validation, file writing with correct metadata, scan triggering from a zip file using a temporary directory, and the headless scan path.
 
---
 
#### Portfolio Generation
 
**Files:** `test_generate_portfolio.py`, `test_regenerate_portfolio.py`
 
`TestGeneratePortfolio` validates the portfolio module's building blocks. `PortfolioSection.render` is confirmed to respect the `enabled` flag, and `Portfolio.toggle_section` and `render_markdown` are verified to work correctly. `build_overview_section` is tested to aggregate languages and frameworks across projects, and `build_project_section` is verified to label projects as Individual or Collaborative based on contributor counts, with commit metrics, file ownership percentages, lines added and removed, and contributor ranking all included in the output. `build_tech_summary_section` is confirmed to rank technology usage correctly, and `get_filtered_technologies` is tested to apply high, medium, and low confidence thresholds correctly with a fallback for legacy data.
 
`RobustGeneratePortfolioTests` validates the full pipeline from `collect_projects` through `aggregate_projects_for_portfolio` and `build_portfolio`, CLI file creation with expected content, and inclusion of `project_evidence` entries in the rendered portfolio section.
 
`test_regenerate_portfolio.py` validates the regeneration workflow including invalid path handling, directory and zip file scanning, missing argument validation, the overwrite flag, and section rendering output.
 
---
 
#### Configuration and Consent
 
**Files:** `test_config.py`, `test_consent_test.py`
 
`test_config.py` validates configuration loading and saving including missing file fallback to defaults, corrupted JSON fallback, partial config filling with defaults, save-then-load round-trip correctness, and correct precedence when CLI args override config file values.
 
`test_consent_test.py` validates the consent flow including saving a consent preference, leaving config unchanged when consent is declined, the yes/no prompt re-prompting on invalid input, and the data access description output.
 
---
 
#### CLI and User Interaction
 
**Files:** `test_main_menu.py`, `test_cli_validators.py`, `test_cli_username_selection.py`, `test_cli_identity_selection.py`
 
`test_cli_validators.py` validates path normalisation (whitespace stripping, quote removal, absolute path resolution), project path validation (accepts directories and zips, rejects non-existent paths, regular files, and zips when not allowed), and username validation (accepts valid names, rejects empty strings and invalid characters).
 
`test_main_menu.py` covers menu output, timestamp formatting, safe database queries, resume preview and deletion (including missing file handling), and role analysis display with and without per-project data.
 
`test_cli_identity_selection.py` and `test_cli_username_selection.py` validate contributor identity and username selection flows including git-based auto-detection, guest mode fallback, invalid input re-prompting, blank input cancellation, and nested contribution unwrapping.
 
---
 
#### Additional Coverage
 
**Files:** `test_project_evidence.py`, `test_project_display_names.py`, `test_project_info_output.py`, `test_inspect_db_json.py`, `test_skill_timeline.py`, `test_contributor_prompt.py`
 
`test_project_evidence.py` provides tests covering evidence operations, type validation, ordering by creation time, formatted output for resume and portfolio rendering, source and timestamp inclusion, partial field updates, and legacy description fallback.
 
`test_skill_timeline.py` validates grouped skill output and correct handling of empty skill sets.
 
`test_contributor_prompt.py` validates the three contributor assignment flows: adding only new contributors, selecting only existing ones, and selecting a mix of existing and new.
 
`test_project_display_names.py` validates setting and retrieving custom display names and that `list_projects_for_display` includes the custom name field.
 
---
 
## 5. Frontend Testing
 
### Tools
 
- `Vitest`
- `@testing-library/react`
- `axios` mocking via `vi.spyOn` and `vi.mock`
 
### Strategy
 
Frontend tests simulate real user interactions by rendering full components and asserting on visible DOM output. Tests use mocked API responses to control component state without a running backend. All 7 test files pass with zero failures.
 
---
 
### Components and What is Validated
 
**`App.test.jsx`**
 
Validates top-level routing and navigation. Tests confirm that the app renders the main menu after the consent check resolves, that the backend connection check button shows a loading state and updates with a pass or fail indicator, and that clicking each navigation button updates the URL hash and renders the correct page heading. Pages covered include Scan Project, Generate Resume, Rank Projects, Scanned Projects, and Database Maintenance.
 
**`DashboardStats.test.jsx`**
 
Validates the dashboard stats panel on the main menu. Tests confirm that project count, contributor information, and output breakdown (number of resumes and portfolios) are fetched from `/stats/dashboard` and rendered correctly, and that a fetch error does not crash the application.
 
**`ResumePage.test.jsx`**
 

Validates the resume generation workflow. Clicking generate triggers a POST to `/resume/generate`, and on success the returned resume content is displayed. API failures are confirmed to show an error message. The PDF download flow is tested end to end, verifying calls to `/resume/{id}/pdf/info` and `/resume/{id}/pdf` and a resulting blob download. A separate test confirms that a multi-page resume shows a warning modal and halts the download if the user cancels. Select all and deselect all checkbox behaviour is also covered.
 
**`PortfolioPage.test.jsx`**
 
Validates the portfolio generation workflow. When fewer than three projects are scanned, a notice is shown and the generate button is hidden. With three or more projects loaded, the contributor selector and generate button appear. Validation errors are tested for missing username and for excluding too many projects. A valid submission is confirmed to transition to the dashboard view with all four section headings present. Additional tests cover the back to setup button, heatmap scope switching between project-wide and per-user views, the shared horizontal scroll container structure, and select all and deselect all checkbox behaviour.
 
**`ScannedProjectsPage.test.jsx`**
 
Validates the project management view. Tests cover the empty state, project list search filtering, and the full tabbed detail view across the Signals, Contributors, Activity, and Evidence tabs. The Contributors tab is specifically checked for role confidence scores and team composition summary. In edit mode, changes to display name, repo URL, thumbnail path, and LLM summary text are verified to reach the correct PATCH endpoint. The Electron file picker integration is tested for thumbnail selection. The Evidence tab tests cover field rendering, formatted type labels, delete button visibility, the in-app confirmation modal, correct deletion endpoint calls, and the ability to delete newly added evidence from local state before a page reload.
 
**`DatabaseMaintenance.test.jsx`**
 
Validates the database management page. Tests confirm that tables load and display row counts, that the refresh button triggers a second API call, that clicking a table header expands its rows, that the clear database button opens a confirmation modal, and that confirming the clear action calls the correct DELETE endpoint.
 
**`modal.test.js`**
 
Validates the shared modal utility. Tests confirm the modal renders with the correct title and message, that confirm resolves the promise as `true`, and that cancel or an outside click resolves it as `false`. Cleanup behaviour is tested to confirm the DOM element is removed after closing. The cancel button is verified to only appear when `cancelText` is provided, and the `danger` type is confirmed to apply the correct CSS class.
 
---
 
## 6. Test Data
 
 The system can be tested using these structured datasets created to satisfy the project requirements and simulate realistic usage scenarios. Scan the incremental set first then the multi-project.

### Incremental Project Dataset

Two folders representing the same collaborative coding project at different points in time are provided to satisfy Requirement 33:

- `test-data-snapshot-1.zip` – earlier version of the capstone project
- `test-data-snapshot-2.zip` – later version with additional and modified files

Scanning both datasets into the system and comparing results exercises incremental update handling, duplicate file detection across scans, and timeline accuracy. When scanning either snapshot, use `tannerdyck` as the contributor name to see meaningful per-user metrics.

---

### Multi-Project Dataset

A dataset containing multiple project types is provided to satisfy Requirement 34:

- `test-data-multi.zip`

This dataset exercises project classification (individual vs. collaborative), contributor extraction from git history, non-git project handling, language and skill detection across multiple codebases, and project ranking with mixed contribution levels. When scanning BilletBlaze, Firebreak, Hangman, and UBCForums, use `tannerdyck` as the contributor name to see individual contribution data extracted from git history. HangmanNoGit has no git history so contributor assignment is prompted manually during the scan (use tannerdyck).

---

### File Access

The test data files are hosted externally. 

Google Drive Folder:  
[Google Drive Test Data](https://drive.google.com/drive/folders/1_16KMI63oGM1S2aKTIPLqQlAY_IaduFn)

A reference file is included in `/docs/test-data/` within the repository. These datasets are sufficient to validate both system functionality and robustness across varying project structures.

---
 
## 7. Testing Strategy Summary
 
The project follows an integration-heavy testing strategy. Backend tests validate full system behaviour from HTTP request through to database state. Frontend tests validate user workflows against mocked API responses. Real file structures and seeded database rows are used throughout. Mocking is limited to external services such as LLM calls and, in the frontend, all HTTP requests.
 
Key principles applied across the test suite:
 
- Isolation via temporary databases and filesystems reset between tests
- Deterministic outputs wherever possible (timestamps injected rather than read from the system clock)
- End-to-end validation of all critical user-facing features
- Subprocess testing of CLI entry points to validate the full execution path including argument parsing and file output
 
---
 
## 8. Coverage Summary
 
Coverage includes the following areas:
 
- API endpoints and backend route handling
- File scanning, zip parsing, and path normalization
- Language, framework, skill, and contributor role detection
- Contribution metrics and project aggregation
- Database schema validation, CRUD operations, and cascade deletion
- Project ranking and summarization
- Resume and portfolio generation workflows
- Configuration and consent flows
- CLI validation and user interaction flows
- Evidence management, display names, and timeline-related features
- Frontend navigation, form submission, dashboard rendering, and modal behaviour
 
---
 
## 9. Known Limitations
 
**Environment-dependent test skip.** `test_real_git_project_metrics` in `test_project_info_output.py` requires a local repository clone at a specific absolute path. It is automatically skipped on any machine where that path does not exist. This test validates real git command output against a live repository and cannot be made fully portable without mocking the git layer, which would reduce its diagnostic value. It is documented here rather than removed.
 
**LLM non-determinism.** LLM-generated summaries produce different output on each call. All tests that touch the LLM path either patch the LLM call to return a fixed value or assert only on structure (e.g. that a summary field is present and non-null) rather than on exact content. Tests of downstream rendering that depend on summary text use seeded database rows with known values.
 
**Windows teardown behaviour.** Several test classes include explicit `gc.collect()` calls in `tearDown`. This is required on Windows to release SQLite file handles before the temporary directory can be deleted. Tests pass on all platforms but this is a known friction point when running the suite on Windows.
 
**jsdom navigation warning.** The frontend test suite produces a console warning (`Not implemented: navigation (except hash changes)`) on tests that involve clicking navigation buttons. This is a jsdom limitation and does not affect test correctness since the application uses hash-based routing throughout. The warning can be suppressed by adding a jsdom configuration option but has been left visible as it accurately reflects a real environmental constraint.
 
**Electron file picker.** The thumbnail file picker in `ScannedProjectsPage` relies on `window.api.openThumbnailDialog`, an Electron IPC bridge. In tests this is mocked via `window.api = { openThumbnailDialog: vi.fn() }`. The mock cannot verify that the actual native file dialog opens correctly or that the file type filter works on each OS. This path requires manual testing in the Electron environment.
 
---
 
## 10. Conclusion
 
This project uses a comprehensive testing approach that combines backend integration testing with frontend UI validation. The use of realistic datasets, temporary isolated databases, and full-system test flows ensures that the application behaves correctly under real-world conditions and satisfies the project requirements across all milestones.