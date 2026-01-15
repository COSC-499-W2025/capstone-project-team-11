# FastAPI Integration

This API provides HTTP endpoints for scanning projects, managing privacy consent,
listing project data, and generating/editing resumes and portfolios.

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

The scanner requires explicit consent. Consent is stored in the user config file:

- macOS/Linux: `~/.mda/config.json`
- Windows: `%USERPROFILE%\.mda\config.json`

If consent is missing or false, `/projects/upload` returns `403`.

## Endpoints

### POST /privacy-consent

Persist data consent for scans.

Request:

```json
{
  "data_consent": true
}
```

Response:

```json
{
  "data_consent": true,
  "config_path": "/Users/.../.mda/config.json"
}
```

---

### POST /projects/upload

Scan a local project directory (filesystem path only) and optionally save to DB.

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
  "thumbnail_path": "/absolute/path/to/image.png"
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

### GET /projects/{id}

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

### POST /resume/generate

Generate a resume from the `output/` directory and optionally store in DB.

Request:

```json
{
  "username": "jaxsonkahl",
  "output_root": "output",
  "resume_dir": "resumes",
  "allow_bots": false,
  "save_to_db": true
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

### GET /resume/{id}

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

### POST /resume/{id}/edit

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

Response matches `GET /resume/{id}`.

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
  "save_to_db": true
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

### GET /portfolio/{id}

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

### POST /portfolio/{id}/edit

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

Response matches `GET /portfolio/{id}`.

## Notes

- `/projects/upload` currently supports filesystem paths only (zip upload planned later).
- `resume_id` and `portfolio_id` only exist when `save_to_db` is `true`.
- For Windows, ensure JSON paths escape backslashes (e.g., `C:\\Users\\Name\\project`).
