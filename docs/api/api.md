# GitHired API Documentation

This API provides HTTP endpoints for scanning projects, managing privacy/LLM consent, listing project data, generating/editing resumes and portfolios, managing evidence, ranking projects, and powering the web portfolio dashboard.

Base URL (local):

```
http://127.0.0.1:8000
```

## Requirements

- Python 3.9+
- Dependencies:

```
pip install -r requirements.txt
pip install uvicorn
```

## Run the Server

```
uvicorn src.api:app --reload
```

## Consent

The scanner and LLM features require explicit consent. Consent is stored in the user
config file:

- macOS/Linux: `~/.mda/config.json`
- Windows: `%USERPROFILE%\.mda\config.json`

If consent is missing or false, requests that require it return `403`.

---

## Endpoints

### GET /health

Simple readiness/liveness endpoint used by Electron startup checks.

Response:

```json
{
  "status": "ok"
}
```

---

### GET /config

Return the current consent configuration.

Response:

```json
{
  "data_consent": true,
  "llm_summary_consent": false,
  "llm_resume_consent": false
}
```

---

### POST /privacy-consent

Persist data and LLM consent settings.

Request:

```json
{
  "data_consent": true,
  "llm_summary_consent": false,
  "llm_resume_consent": false
}
```

Response:

```json
{
  "data_consent": true,
  "llm_summary_consent": false,
  "llm_resume_consent": false,
  "config_path": "/Users/.../.mda/config.json"
}
```

---

## Projects

### GET /projects

List all projects in the database.

Response:

```json
[
  {
    "id": 1,
    "name": "project",
    "custom_name": null,
    "repo_url": "https://example.com",
    "created_at": "2026-01-01 00:00:00",
    "thumbnail_path": null,
    "latest_scan_at": "2026-01-01 00:05:00"
  }
]
```

---

### GET /projects/{project_id}

Return enriched project data (skills, languages, frameworks, contributors, roles,
scans, evidence, LLM summary, git metrics, and rank score).

Response:

```json
{
  "project": {
    "id": 1,
    "name": "project",
    "custom_name": null,
    "repo_url": "https://example.com",
    "created_at": "2026-01-01 00:00:00",
    "thumbnail_path": null
  },
  "skills": ["SQL", "FastAPI"],
  "languages": ["Python"],
  "frameworks": ["FastAPI"],
  "contributors": ["alice"],
  "contributor_roles": {
    "contributors": [
      {
        "name": "alice",
        "primary_role": "Backend Developer",
        "role_description": "...",
        "confidence": 0.85,
        "secondary_roles": [],
        "contribution_breakdown": { "code": 80, "docs": 20 }
      }
    ],
    "summary": {}
  },
  "scans": [
    {
      "id": 5,
      "scanned_at": "2026-01-01 00:05:00",
      "notes": null
    }
  ],
  "files_summary": {
    "total_files": 42,
    "extensions": {
      ".py": 12,
      ".md": 3
    }
  },
  "evidence": [
    {
      "id": 1,
      "type": "award",
      "description": "demo",
      "value": "winner",
      "source": "internal",
      "url": null,
      "added_by_user": 1,
      "created_at": "2026-01-01 00:05:00"
    }
  ],
  "llm_summary": {
    "text": "...",
    "model": "...",
    "updated_at": "2026-01-01 00:00:00"
  },
  "git_metrics": {},
  "rank_score": 0.87
}
```

---

### POST /projects/upload

Scan a local project directory (filesystem path only) and optionally save to DB.

Requires `data_consent: true`. If `llm_summary` is `true`, also requires
`llm_summary_consent: true`.

Returns `201 Created`.

Request:

```json
{
  "project_path": "/absolute/path/to/project",
  "recursive_choice": false,
  "file_type": ".py",
  "show_collaboration": false,
  "show_contribution_metrics": false,
  "show_contribution_summary": false,
  "save_to_db": true,
  "thumbnail_path": "/absolute/path/to/image.png",
  "llm_summary": false,
  "manual_contributors_by_path": null
}
```

Response:

```json
{
  "project_name": "project",
  "scan_id": 12,
  "saved_to_db": true,
  "output_summary_path": "output/project/project_info_....json"
}
```

---

### POST /projects/scan-plan

Preview what projects would be scanned for a given path without actually scanning.
Detects single vs multi-project directories and lists any non-git projects that
require manual contributor assignment.

Requires `data_consent: true`.

Request: same shape as `POST /projects/upload`.

Response:

```json
{
  "root_path": "/absolute/path/to/root",
  "total_projects": 2,
  "is_multi_project": true,
  "projects": [
    {
      "project_name": "project-a",
      "project_path": "/absolute/path/to/project-a",
      "is_git": true,
      "requires_contributor_assignment": false
    }
  ],
  "existing_contributors": ["alice", "bob"]
}
```

---

### POST /projects/scan-stream

Stream scan progress as newline-delimited plain text. Each line is either a raw
log line, a structured event prefixed with `SCAN_EVENT::`, or a final result
prefixed with `SCAN_DONE::`.

Requires `data_consent: true`. If `llm_summary` is `true`, also requires
`llm_summary_consent: true`.

Request: same shape as `POST /projects/upload`.

Response: `text/plain; charset=utf-8` streaming body.

Line format:

```
<raw log line>
SCAN_EVENT::<json event object>
SCAN_DONE::<json result object>
```

`SCAN_DONE` payload:

```json
{
  "success": true,
  "partial_success": false,
  "project_name": "project",
  "project_names": ["project"],
  "project_results": {},
  "failed_projects": [],
  "output_dir": "output/project",
  "error": null,
  "summaries": [
    {
      "project_name": "project",
      "llm_summary": { "text": "...", "model": "...", "updated_at": "..." }
    }
  ]
}
```

---

### PATCH /projects/{project_id}

Update project metadata (custom name, repo URL, thumbnail path, or manual LLM summary text).
All fields are optional; omitted fields are left unchanged.

Request:

```json
{
  "custom_name": "My Renamed Project",
  "repo_url": "https://github.com/user/project",
  "thumbnail_path": "/absolute/path/to/image.png",
  "summary_text": "A short manual description of the project."
}
```

Response:

```json
{
  "project": {
    "id": 1,
    "name": "project",
    "custom_name": "My Renamed Project",
    "repo_url": "https://github.com/user/project",
    "created_at": "2026-01-01 00:00:00",
    "thumbnail_path": "/absolute/path/to/image.png"
  },
  "llm_summary": {
    "text": "A short manual description of the project.",
    "model": null,
    "updated_at": "2026-01-01 00:00:00Z"
  }
}
```

---

### DELETE /projects/{project_id}

Permanently delete a project and all associated data from the database.

Response:

```json
{
  "message": "Project deleted successfully"
}
```

---

### GET /projects/{project_id}/thumbnail/image

Return the raw thumbnail image file for a project.

Response: binary image file (`image/png`, `image/jpeg`, etc.) served via `FileResponse`.

---

### POST /projects/{project_id}/evidence

Add an evidence record to a project.

Returns `201 Created`.

Request:

```json
{
  "type": "award",
  "value": "winner",
  "source": "internal",
  "url": null,
  "added_by_user": true
}
```

Valid `type` values are defined by `validate_evidence_type` in `project_evidence.py`.

Response:

```json
{
  "evidence_id": 7,
  "message": "Evidence added successfully"
}
```

---

### PATCH /projects/{project_id}/evidence/{evidence_id}

Update an existing evidence record. All fields are optional.

Request (any subset):

```json
{
  "type": "award",
  "description": "Updated description",
  "value": "runner-up",
  "source": "external",
  "url": "https://example.com",
  "added_by_user": 1
}
```

Response:

```json
{
  "message": "Evidence updated successfully"
}
```

---

### DELETE /projects/{project_id}/evidence/{evidence_id}

Delete an evidence record from a project.

Response:

```json
{
  "message": "Evidence deleted successfully"
}
```

---

## Skills & Contributors

### GET /skills

Return all known skills in the database.

Response:

```json
["SQL", "FastAPI", "Data Analysis"]
```

---

### GET /contributors

Return all known contributor names, filtered to exclude bots and blank entries.

Response:

```json
["alice", "bob", "carol"]
```

---

## Rankings

### GET /rank-projects

Rank projects by importance or chronology.

Query params:

- `mode`: `project` or `contributor` (default: `project`)
- `contributor_name`: required when `mode` is `contributor`
- `limit`: integer 1–200 (optional)
- `sort_mode`: `importance` or `chronological` (default: `importance`)
- `chronological_order`: `asc` or `desc` (default: `desc`)

Response: array of ranked project objects with importance scores and timeline metadata.

```json
[
  {
    "project": "project-a",
    "top_score": 0.91,
    "score": 0.91,
    "contrib_files": 18,
    "total_files": 30,
    "contributors_count": 2,
    "created_at": "2026-01-01 00:00:00",
    "first_scan": "2026-01-01 00:05:00",
    "last_scan": "2026-01-15 00:05:00",
    "scans_count": 3
  }
]
```

---

### GET /custom-rankings

List all saved custom project rankings.

Response: array of custom ranking objects.

---

### POST /custom-rankings

Create a new custom project ranking.

Returns `201 Created`.

Request:

```json
{
  "name": "My Top Projects",
  "description": "Hand-picked ordering for my portfolio",
  "projects": ["project-a", "project-b", "project-c"]
}
```

Response:

```json
{
  "id": 1,
  "name": "My Top Projects"
}
```

---

### GET /custom-rankings/{name}

Fetch a custom ranking by name.

Response:

```json
{
  "name": "My Top Projects",
  "projects": ["project-a", "project-b", "project-c"]
}
```

---

### DELETE /custom-rankings/{name}

Delete a custom ranking by name.

Response:

```json
{
  "deleted": true
}
```

---

## Resumes

### GET /resumes

List all resumes, optionally filtered by username.

Query params:

- `username`: filter by username (optional)

Response:

```json
[
  {
    "id": 3,
    "username": "jaxsonkahl",
    "generated_at": "2026-01-01 00:00:00Z",
    "llm_used": false
  }
]
```

---

### GET /resume/{resume_id}

Fetch a resume by ID, including file contents.

Response:

```json
{
  "id": 3,
  "username": "jaxsonkahl",
  "resume_path": "resumes/resume_jaxsonkahl_....md",
  "metadata": {},
  "generated_at": "2026-01-01 00:00:00Z",
  "content": "# Resume — jaxsonkahl\n..."
}
```

---

### GET /resume/{resume_id}/pdf/info

Return metadata about the PDF that would be generated for a resume, without
actually streaming the file.

Response:

```json
{
  "filename": "resume_jaxsonkahl_3.pdf",
  "page_count": 1,
  "is_multi_page": false
}
```

---

### GET /resume/{resume_id}/pdf

Download the resume as a formatted PDF file.

Response: `application/pdf` binary download with `Content-Disposition: attachment`.

---

### POST /resume/generate

Generate a resume from the `output/` directory and optionally store in DB.

If `llm_summary` is `true`, requires `llm_resume_consent: true`.

Returns `201 Created`.

Request:

```json
{
  "username": "jaxsonkahl",
  "output_root": "output",
  "resume_dir": "resumes",
  "allow_bots": false,
  "save_to_db": false,
  "llm_summary": false,
  "excluded_project_names": [],
  "education": [
    {
      "institution": "University of Example",
      "degree": "B.Sc. Computer Science",
      "year": "2024"
    }
  ]
}
```

Response:

```json
{
  "resume_id": 3,
  "resume_path": "resumes/resume_jaxsonkahl_....md",
  "generated_at": "2026-01-01 00:00:00Z"
}
```

---

### POST /resume/{resume_id}/edit

Overwrite the resume file and update metadata.

Request:

```json
{
  "content": "# Resume — jaxsonkahl\nUpdated\n",
  "metadata": {
    "edited": true
  }
}
```

Response matches `GET /resume/{resume_id}`.

---

### DELETE /resume/{resume_id}

Delete a resume record and its file from disk.

Response:

```json
{
  "deleted": true
}
```

---

## Portfolios

The portfolio system uses two layers:

- **`/portfolios`** — manages saved portfolio records in the database (project lists, names, featured projects).
- **`/portfolio/generate`** — generates a markdown portfolio file from scanned output data.
- **`/web/portfolio`** — powers the live web portfolio dashboard views.

---

### GET /portfolios/all

List all portfolio records across all users.

Response: array of portfolio objects (see `GET /portfolios/{portfolio_id}`).

---

### GET /portfolios

List portfolio records for a specific user.

Query params:

- `username`: required

Response: array of portfolio objects.

---

### GET /portfolios/{portfolio_id}

Fetch a portfolio record by ID.

Response:

```json
{
  "id": 4,
  "username": "jaxsonkahl",
  "portfolio_name": "My Portfolio",
  "display_name": "Jaxson Kahl",
  "included_project_ids": [1, 2, 3],
  "featured_project_ids": [2],
  "created_at": "2026-01-01 00:00:00"
}
```

---

### POST /portfolios

Create and save a new portfolio record.

Returns `201 Created`.

Request:

```json
{
  "username": "jaxsonkahl",
  "portfolio_name": "My Portfolio",
  "display_name": "Jaxson Kahl",
  "included_project_ids": [1, 2, 3],
  "featured_project_ids": [2]
}
```

Response matches `GET /portfolios/{portfolio_id}`.

---

### PUT /portfolios/{portfolio_id}

Replace a portfolio record's content.

Request:

```json
{
  "portfolio_name": "Updated Portfolio",
  "display_name": "Jaxson Kahl",
  "included_project_ids": [1, 2, 3, 4],
  "featured_project_ids": [3]
}
```

Response matches `GET /portfolios/{portfolio_id}`.

---

### PATCH /portfolios/{portfolio_id}/name

Rename a portfolio.

Request:

```json
{
  "portfolio_name": "New Name"
}
```

Response matches `GET /portfolios/{portfolio_id}`.

---

### DELETE /portfolios/{portfolio_id}

Delete a portfolio record.

Returns `204 No Content`.

---

### DELETE /portfolios/cleanup-temp

Delete any temporary portfolio rows (those whose name starts with `__temp__`).
Called on app startup to clean up orphaned entries from abrupt closes.

Returns `204 No Content`.

---

### POST /portfolio/generate

Generate a portfolio from the `output/` directory and optionally store in DB.

Returns `201 Created`.

Request:

```json
{
  "username": "jaxsonkahl",
  "output_root": "output",
  "portfolio_dir": "portfolios",
  "confidence_level": "high",
  "save_to_db": false
}
```

Response (without `save_to_db`):

```json
{
  "username": "jaxsonkahl",
  "generated_at": "2026-01-01 00:00:00Z",
  "project_count": 3
}
```

Response (with `save_to_db: true`):

```json
{
  "username": "jaxsonkahl",
  "generated_at": "2026-01-01 00:00:00Z",
  "project_count": 3,
  "portfolio_id": 4,
  "portfolio_path": "portfolios/portfolio_jaxsonkahl_....md"
}
```

---

## Outputs & Stats

### GET /outputs

Return a count of generated outputs (resumes and portfolios) with recent activity.

Response:

```json
{
  "resumes": 2,
  "portfolios": 1,
  "total": 3,
  "latest_generated": "2026-01-15 00:00:00Z"
}
```

---

### GET /stats/dashboard

Return comprehensive dashboard stats covering projects, contributors, and outputs.

Response:

```json
{
  "projects": {
    "count": 5,
    "latest_scan": "2026-01-15 00:05:00",
    "latest_project": "project-a"
  },
  "contributors": {
    "count": 3,
    "top_contributor": "alice",
    "top_contributor_files": 42
  },
  "outputs": {
    "total": 3,
    "resumes": 2,
    "portfolios": 1,
    "latest_generated": "2026-01-15 00:00:00Z"
  }
}
```

---

## Web Portfolio Dashboard

All routes below are prefixed with `/web/portfolio`.

---

### GET /web/portfolio/{portfolio_id}/timeline

Return a skills timeline for the web portfolio dashboard.

Query params:

- `granularity`: `week` or `month` (default: `month`)

Response:

```json
{
  "portfolio_id": 4,
  "username": "jaxsonkahl",
  "granularity": "month",
  "timeline": [
    {
      "period": "2026-01",
      "skills": [
        {
          "name": "Python",
          "occurrences": 12,
          "project_count": 2,
          "expertise_score": 9.0
        }
      ]
    }
  ]
}
```

---

### GET /web/portfolio/{portfolio_id}/heatmap

Return scan/file activity heatmap data for the web portfolio dashboard.

Query params:

- `granularity`: `day`, `week`, or `month` (default: `day`)
- `metric`: `scans` or `files` (default: `files`)

Response:

```json
{
  "portfolio_id": 4,
  "granularity": "day",
  "metric": "files",
  "cells": [
    {
      "period": "2026-01-01",
      "value": 10
    }
  ],
  "max_value": 10
}
```

---

### GET /web/portfolio/{portfolio_id}/heatmap/project

Return a per-project contribution heatmap. Supports filtering by user vs project-wide
scope and falls back to git log data for commit-based metrics.

Query params:

- `project_id`: integer, required
- `granularity`: `day`, `week`, or `month` (default: `week`)
- `metric`: `scans`, `files`, or `contrib_files` (default: `contrib_files`)
- `view_scope`: `project` or `user` (default: `project`)

Response:

```json
{
  "portfolio_id": 4,
  "project_id": 1,
  "project_name": "project",
  "granularity": "week",
  "metric": "contrib_files",
  "view_scope": "user",
  "range_start": "2025-09-01",
  "range_end": "2026-01-15",
  "value_unit": "commits",
  "cells": [
    {
      "period": "2025-09-01",
      "value": 4
    }
  ],
  "max_value": 4
}
```

---

### GET /web/portfolio/{portfolio_id}/showcase

Return top showcase projects for the web portfolio dashboard. Featured projects
(set via `PUT /portfolios/{portfolio_id}`) are surfaced first.

Query params:

- `limit`: integer 1–3 (default: 3)

Response:

```json
{
  "portfolio_id": 4,
  "username": "jaxsonkahl",
  "projects": [
    {
      "project_id": 1,
      "name": "project",
      "thumbnail_path": null,
      "score": 0.9234,
      "contrib_files": 12,
      "total_files": 20,
      "role": "collaborative",
      "evidence": [
        {
          "id": 1,
          "type": "award",
          "description": "demo",
          "value": "winner",
          "source": "internal",
          "url": null,
          "created_at": "2026-01-01 00:05:00"
        }
      ],
      "evolution": [
        {
          "id": 1,
          "scanned_at": "2026-01-01 00:05:00",
          "notes": null
        }
      ]
    }
  ]
}
```

---

### GET /web/portfolio/{portfolio_id}/export-html

Generate and download a self-contained HTML export of the web portfolio. The file
embeds all project data, thumbnails (as base64), heatmaps, and a skills timeline
into a single downloadable `.html` file with no external dependencies beyond
Google Fonts.

Response: `text/html` download with `Content-Disposition: attachment`.

---

### PATCH /web/portfolio/{portfolio_id}/customize

Update which projects are included or featured in the web portfolio dashboard.
All fields are optional.

Request (any subset of fields):

```json
{
  "selected_project_ids": [1, 2],
  "featured_project_ids": [2]
}
```

Response matches `GET /portfolios/{portfolio_id}`.

---

## Database

### GET /database/inspect

Return a full structural and data inspection of the database.

Response: JSON object from `inspect_database_json()`.

---

### DELETE /database/clear

Permanently delete all rows from every table and reset auto-increment sequences.
Foreign key checks are disabled for the duration of the operation.

**Irreversible. Use with caution.**

Response:

```json
{
  "message": "Database cleared successfully"
}
```

---

## Notes

- `/projects/upload` and `/projects/scan-stream` support filesystem paths only (zip upload planned).
- `resume_id` and `portfolio_id` are `null` in generate responses unless `save_to_db` is `true`.
- For Windows, ensure JSON paths escape backslashes (e.g., `C:\\Users\\Name\\project`).
- The old `/portfolio/{portfolio_id}` (singular) GET/edit endpoints have been superseded by the `/portfolios` collection routes.
- PDF generation uses WeasyPrint if available, falling back to ReportLab.