# GitHired / Capstone Project Team 11

GitHired is a local-first project analysis toolkit that scans source code repositories or ZIP archives, stores structured project data in SQLite, and turns that data into ranked project views, resumes, and web portfolios.

The recommended way to use this project is the Electron desktop application. It provides the primary user workflow and automatically starts the local FastAPI backend for you.

The repository currently includes three primary surfaces:

- An Electron + React desktop frontend that drives the backend through a local API
- A Python CLI for interactive scanning and project management
- A FastAPI backend for scanning, ranking, resume generation, portfolio generation, and database operations

## Table of Contents
1. [Project Overview](#project-overview)
2. [Current Feature Set](#current-feature-set)
3. [Repository Layout](#repository-layout)
4. [Requirements](#requirements)
5. [Recommended Setup and Usage](#recommended-setup-and-usage)
6. [Alternative Workflows](#alternative-workflows)
7. [Docker Workflow](#docker-workflow)
8. [Configuration and Consent](#configuration-and-consent)
9. [Generated Data and Outputs](#generated-data-and-outputs)
10. [Testing](#testing)
11. [Documentation](#documentation)

## Project Overview
GitHired analyzes local software projects and extracts:

- languages and frameworks
- inferred technical skills
- contributors and contribution metrics
- project summaries and evidence
- ranked project views
- contributor-focused resume content
- web portfolio content and visualizations

Scans can target a single project, a directory that contains multiple projects, or a ZIP archive. Results are persisted to a local SQLite database and can then be reviewed and edited through the Electron desktop app, the CLI, or the API.

## Current Feature Set
- Scan directories and ZIP archives, including multi-project roots
- Detect languages, frameworks, and skills from file contents and project structure
- Inspect Git history and derive contributor metrics when a project is a Git repository
- Support manual contributor assignment for non-Git projects
- Persist scan results, summaries, resumes, portfolios, and evidence in SQLite
- Generate project summaries and optional local LLM summaries through Ollama
- Rank projects by importance or for a specific contributor
- Save and reload custom rankings
- Generate, edit, list, delete, and export resumes
- Generate, save, rename, delete, customize, and export portfolios
- Manage project thumbnails, display names, evidence entries, and database contents
- Provide dashboard statistics and portfolio visualizations through the API
- Run from local Python, Docker, or the Electron desktop application

## Repository Layout
- `src/`: Python backend, CLI flows, scan logic, ranking, DB access, resume generation, and portfolio generation
- `frontend/`: Electron + React desktop app with pages for consent, scanning, scanned projects, ranking, resumes, portfolios, and database maintenance
- `test/`: backend test suite
- `docs/`: API docs, architecture diagrams, DFDs, proposal, contract, and other project artifacts
- `init_db.sql`: base SQLite schema
- `Dockerfile`: backend image definition
- `docker-compose.yml`: local CLI, API, test, and Ollama services

## Requirements

### Backend
- Python 3.9+
- `pip`
- Git installed if you want contributor data from repository history

### Frontend
- Node.js and npm

### Optional LLM Support
- [Ollama](https://ollama.com/) running locally or reachable through `OLLAMA_HOST`
- A pulled local model such as `llama3.2:3b`

## Recommended Setup and Usage
Use the Electron app first unless you are developing against the backend directly.

1. Install backend dependencies from the repository root:

```bash
pip install -r requirements.txt
```

2. Install frontend dependencies:

```bash
cd frontend
npm install
```

3. Optional: start Ollama and pull a model if you want local LLM summaries:

```bash
ollama serve
ollama pull llama3.2:3b
```

4. Start the Electron app:

```bash
npm start
```

Notes:

- Run `npm start` from the [`frontend/`](/Users/jaxsonkahl/Desktop/capstone-project-team-11/frontend) directory.
- The Electron main process attempts to start the FastAPI backend automatically on `http://127.0.0.1:8000`.
- If needed, set `BACKEND_PYTHON` to point Electron at a specific Python executable.
- The desktop UI is the primary interface for consent management, scanning, project management, ranking, resume generation, portfolio generation, theme settings, and database maintenance.

The application creates its SQLite database automatically on first use. By default the database file is `file_data.db` in the repository root.

## Alternative Workflows

### CLI
Run the interactive menu directly if you want a terminal-driven workflow:

```bash
python3 -m src.main_menu
```

The CLI includes flows for:

- scanning projects
- viewing and managing scanned projects
- generating resumes
- generating portfolios
- ranking projects
- summarizing contributor projects
- managing project evidence
- analyzing contributor roles
- editing project thumbnails
- managing the database

### FastAPI Backend
Start the API directly if you want to work against the backend without Electron:

```bash
uvicorn src.api:app --reload
```

Local API URLs:

- App base: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

The backend exposes endpoints for:

- consent and configuration
- project scanning and scan streaming
- project listing, editing, deletion, thumbnails, and evidence
- contributor and skill lookup
- project ranking and custom rankings
- resume generation, editing, listing, deletion, and PDF export
- portfolio generation, persistence, customization, and HTML export
- portfolio timeline, heatmap, and showcase visualizations
- database inspection and clearing
- dashboard stats and generated output listing

See `docs/api/api.md` for request and response examples.

## Docker Workflow
The repository includes containerized workflows for the CLI, API, tests, and Ollama.

### Build
```bash
docker compose build
```

### Start the API and Ollama
```bash
docker compose up -d ollama api
```

### Run the interactive CLI in Docker
```bash
docker compose run --rm app
```

### Run tests in Docker
```bash
docker compose up --exit-code-from tests tests
```

### Pull the Ollama model in Docker
```bash
docker exec -it capstone-ollama ollama pull llama3.2:3b
```

### Stop containers
```bash
docker compose down
```

Docker path notes:

- The compose file mounts the repository at `/app`
- Host user directories are mounted at `/host`
- When scanning a host machine path from inside Docker, use the `/host/...` form
- On Windows, set `HOST_ROOT` before running Docker Compose if your user directory is not under the default mount root

## Configuration and Consent
Scanning and some generation features require explicit consent.

Consent is stored in:

- macOS/Linux: `~/.mda/config.json`
- Windows: `%USERPROFILE%\.mda\config.json`

Current consent fields include:

- `data_consent`
- `llm_summary_consent`
- `llm_resume_consent`

If required consent is missing, API requests that depend on it will fail, typically with `403`.

Useful environment variables:

- `OLLAMA_HOST`: override the Ollama endpoint used for local LLM calls
- `FILE_DATA_DB_PATH`: override the SQLite database location
- `BACKEND_PYTHON`: Python executable used by Electron when auto-starting the backend

## Generated Data and Outputs
Common generated and persisted artifacts:

- `file_data.db`: SQLite database for projects, scans, contributors, skills, resumes, portfolios, rankings, and evidence
- `output/`: generated project summaries and project information output
- `resumes/`: generated resume markdown and related artifacts
- `portfolios/`: generated portfolio markdown/html artifacts

The database schema includes tables for:

- projects and scans
- files and file metadata
- contributors, languages, and skills
- project evidence
- resumes
- portfolios
- custom rankings

## Testing

### Backend tests
```bash
python -m pytest test/
```

### Frontend tests
```bash
cd frontend
npm test
```

The backend suite covers scanning, DB behavior, ranking, summaries, API routes, resume generation, portfolio generation, contributor logic, and supporting utilities. The frontend suite covers the Electron/React app pages and dashboard flows with Vitest.

## Documentation
- API documentation: `docs/api/api.md`
- Architecture: `docs/architecture/`
- Data flow diagrams: `docs/dfd/`
- Project proposal: `docs/proposal/`
- Team contract: `docs/contract/`
- Work breakdown artifact: `docs/WBS CAPSTONE.webp`
