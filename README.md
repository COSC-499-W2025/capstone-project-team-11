

# Capstone Project Team 11

A Python project scanner with CLI and FastAPI modes that detects languages and skills, ranks projects, and generates summaries, resumes, and portfolios backed by SQLite.

## Table Of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Documentation](#documentation)
4. [Repo Layout](#repo-layout)
5. [Local Setup](#local-setup)
6. [Docker Setup](#docker-setup)
7. [Usage](#usage)
8. [Testing](#testing)
9. [Configuration And Consent](#configuration-and-consent)
10. [Outputs](#outputs)

## Project Overview
This project scans directories or ZIP archives, detects languages, frameworks, and skills, analyzes contributors, ranks projects, and produces structured summaries. It runs as either:
1. A CLI application (`python -m src.main_menu`)
2. A FastAPI server (`uvicorn src.api:app`)

## Features
- Directory and ZIP scanning (including nested archives)
- Language and framework detection with confidence scoring
- Skill inference from file contents and project structure
- Contributor analysis and project ranking
- Resume and portfolio generation
- SQLite persistence for scans and summaries
- Optional LLM integration via `OLLAMA_HOST`

## Documentation
- API documentation: [`docs/api/api.md`](docs/api/api.md)
- Architecture docs: [`docs/architecture/`](docs/architecture/)
- Data Flow Diagrams: [`docs/dfd/`](docs/dfd/)
- Team contract: [`docs/contract/`](docs/contract/)
- Project proposal: [`docs/proposal/`](docs/proposal/)
- Team logs: [`docs/logs/`](docs/logs/)
- Work Breakdown Structure: [`docs/WBS CAPSTONE.webp`](docs/WBS%20CAPSTONE.webp)

## Repo Layout
- `src/` core application and CLI/API code
- `test/` backend unit tests (see [`test/`](test/))
- `docs/` documentation and artifacts (see [`docs/`](docs/))
- `frontend/` Electron UI (optional, see [`frontend/`](frontend/))
- `output/` generated project summaries
- `resumes/` generated resumes
- `portfolios/` generated portfolios (created on demand)
- `file_data.db` local SQLite database
- `init_db.sql` DB schema bootstrap

## Local Setup
1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. LLM setup (optional, for local Ollama):
4. Run the Ollama application (start the app or run `ollama serve` in a separate terminal).
5. In a terminal inside the project, pull the model:

```bash
ollama pull llama3.2:3b
```

6. Confirm the model installed:

```bash
ollama list
```

7. Run the CLI:

```bash
python -m src.main_menu
```

8. Update data consent to `YES` for LLM use.
9. Scan a project.
10. Inspect the database to see the generated summary.
11. Run the API (separate terminal):

```bash
uvicorn src.api:app --reload
```

## Docker Setup
1. Docker Desktop -> Settings -> Resources -> File Sharing
2. Ensure `/Users` is listed (Add if missing)
3. Apply & Restart
4. Windows Setup (Windows Only)
   - Run `setx HOST_ROOT "C:\Users"` before Docker Compose so the mount is picked up:
   -  This will set the host-path mount configurable via an environment variable (e.g., `HOST_ROOT`) so Mac and Windows can both use the same file paths style without changing the compose file
5. Build Images

```bash
docker compose build
```

6. Start Ollama + API

```bash
docker compose up -d ollama api
```

7. Pull Model (FIRST TIME ONLY)

```bash
docker exec -it capstone-ollama ollama pull llama3.2:3b
```

8. Run CLI (from interactive app container)

```bash
docker compose run --rm app
```

9. Run a scan on a local project

**IMPORTANT**: you must include `/host` in the path to scan a local project.  
Example: `/host/jaxsonkahl/Desktop/capstone-project-team-11`  
NOTE: `/Users/` is no longer needed in the file path when using Docker.

10. Run Tests (Test Container)

```bash
docker compose up --exit-code-from tests tests
```

11. Run an API Test

```bash
curl -s http://localhost:8000/docs > /dev/null && echo "API OK"
```

12. Stop Everything

```bash
docker compose down
```

## Usage
CLI:

```bash
python -m src.main_menu
```

API:

```bash
uvicorn src.api:app --reload
```

API docs live at `http://127.0.0.1:8000/docs` (see `docs/api/api.md` for full payloads).

## Testing
Backend tests live in `test/` (see [`test/`](test/)).

Local:

```bash
python -m pytest test/
```

Docker:

```bash
docker compose up --exit-code-from tests tests
```

Frontend (optional):

```bash
cd frontend
npm install
npm test
```

## Configuration And Consent
The scanner requires explicit consent. Consent is stored in:
- macOS/Linux: `~/.mda/config.json`
- Windows: `%USERPROFILE%\.mda\config.json`

If consent is missing or false, API scans via `/projects/upload` return `403`.

## Outputs
- `output/` project summaries (JSON/TXT)
- `resumes/` generated resume files
- `portfolios/` generated portfolio files
