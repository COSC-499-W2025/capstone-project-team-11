# MDA API

This API provides HTTP endpoints for scanning projects, managing privacy/LLM consent,
listing project data, generating/editing resumes and portfolios, and powering the
web portfolio dashboard.

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

## Endpoints

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

### POST /projects/upload

Scan a local project directory (filesystem path only) and optionally save to DB.

Requires `data_consent: true`. If `llm_summary` is `true`, also requires
`llm_summary_consent: true`.

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
  "llm_summary": false
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

### GET /projects

List all projects in the database.

Response:

```json
[
  {
    "id": 1,
    "name": "project",
    "repo_url": "https://example.com",
    "created_at": "2026-01-01 00:00:00",
    "thumbnail_path": null,
    "latest_scan_at": "2026-01-01 00:05:00"
  }
]
```

---

### GET /projects/{project_id}

Return enriched project data (skills, languages, contributors, scans, evidence).

Response:

```json
{
  "project": {
    "id": 1,
    "name": "project",
    "repo_url": "https://example.com",
    "created_at": "2026-01-01 00:00:00",
    "thumbnail_path": null
  },
  "skills": ["SQL", "FastAPI"],
  "languages": ["Python"],
  "contributors": ["alice"],
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
      "type": "award",
      "description": "demo",
      "value": "winner",
      "source": "internal",
      "url": null,
      "added_by_user": 1,
      "created_at": "2026-01-01 00:05:00"
    }
  ]
}
```

---

### GET /skills

Return all known skills in the database.

Response:

```json
["SQL", "FastAPI", "Data Analysis"]
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

### POST /resume/generate

Generate a resume from the `output/` directory and optionally store in DB.

If `llm_summary` is `true`, requires `llm_resume_consent: true`.

Request:

```json
{
  "username": "jaxsonkahl",
  "output_root": "output",
  "resume_dir": "resumes",
  "allow_bots": false,
  "save_to_db": false,
  "llm_summary": false
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

### GET /portfolio/{portfolio_id}

Fetch a portfolio by ID, including file contents.

Response:

```json
{
  "id": 4,
  "username": "jaxsonkahl",
  "portfolio_path": "portfolios/portfolio_jaxsonkahl_....md",
  "metadata": {},
  "generated_at": "2026-01-01 00:00:00Z",
  "content": "# Portfolio — jaxsonkahl\n..."
}
```

---

### POST /portfolio/generate

Generate a portfolio from the `output/` directory and optionally store in DB.

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

Response:

```json
{
  "portfolio_id": 4,
  "portfolio_path": "portfolios/portfolio_jaxsonkahl_....md",
  "generated_at": "2026-01-01 00:00:00Z"
}
```

---

### POST /portfolio/{portfolio_id}/edit

Overwrite the portfolio file and update metadata.

Request:

```json
{
  "content": "# Portfolio — jaxsonkahl\nUpdated\n",
  "metadata": {
    "edited": true
  }
}
```

Response matches `GET /portfolio/{portfolio_id}`.

---

### GET /web/portfolio/{portfolio_id}/timeline

Return a skills timeline for the web portfolio dashboard.

Query params:

- `granularity`: `week` or `month` (default: `month`)
- `mode`: `public` or `private` (default: `public`)

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
- `mode`: `public` or `private` (default: `public`)

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

### GET /web/portfolio/{portfolio_id}/showcase

Return top showcase projects for the web portfolio dashboard.

Query params:

- `limit`: integer 1-3 (default: 3)
- `mode`: `public` or `private` (default: `public`)

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

### PATCH /web/portfolio/{portfolio_id}/customize

Customize which projects/skills appear in the web portfolio dashboard.

Request (any subset of fields):

```json
{
  "is_public": true,
  "selected_project_ids": [1, 2],
  "showcase_project_ids": [2],
  "hidden_skills": ["Docker"]
}
```

Response:

```json
{
  "portfolio_id": 4,
  "web_config": {
    "is_public": true,
    "selected_project_ids": [1, 2],
    "showcase_project_ids": [2],
    "hidden_skills": ["Docker"],
    "updated_at": "2026-01-01 00:00:00Z"
  },
  "updated_at": "2026-01-01 00:00:00Z"
}
```

## Notes

- `/projects/upload` supports filesystem paths only (zip upload planned later).
- `resume_id` and `portfolio_id` are `null` unless `save_to_db` is `true`.
- For Windows, ensure JSON paths escape backslashes (e.g., `C:\\Users\\Name\\project`).
