<img width="1102" height="530" alt="Screenshot 2025-09-24 at 11 15 12 AM" src="https://github.com/user-attachments/assets/e98c9700-5f6c-4118-a474-868d9a2cac18" />

# Frontend (Desktop UI)

- **Electron** – wraps React app as a cross-platform desktop program.  
- **React + JavaScript** – builds the user interface with type safety and reusable components.  
- **Vite** – fast development server and bundler for React.  
- **Zustand** – simple state manager for keeping track of app state (scan status, filters, etc.).  
- **Chart.js / Apache ECharts** – makes interactive charts for insights dashboards.  
- **Features**:
  - Directory picker (user-selected scan paths), preferences, and controls (Scan, Re-scan, Clear).  
  - Filters for date ranges and file categories; results tables; project/repo views.  
  - Visuals (timeline, category bars/pies) and print-friendly report preview.  

**Why**: Gives a simple interface that directly satisfies *“simple UI,” “visual results,” and “user-selected scan”* requirements.  

---

# Backend (Local API & Logic)

- **Python 3.11+** – main backend language.  
- **FastAPI + Uvicorn** – runs the REST API that the UI talks to.  
- **SQLModel (SQLAlchemy)** – ORM layer to talk to the database in Python classes.  

**Endpoints**:
- `POST /scan` (start a scan)  
- `GET /scans/{id}` (status)  
- `GET /artifacts?from=&to=&type=&project=…` (date/category filters)  
- `GET /stats/summary` (counts by category, date histograms)  
- `GET /export?format=html|pdf|png`  
- `POST /overrides` (persist user category overrides)  
- `POST /clear` (wipe local data)  

**Why**: Clean separation between UI and logic; easy to test; future-proof for Term-2 front-end/API milestones.  

---

# Data & Storage

- **SQLite** – lightweight, embedded database stored in a single file.  
- **Alembic** – manages schema changes over time (migrations).  
- **Libmagic (python-magic)** – detects file type/MIME from content or extension.  
- **hashlib (SHA-256)** – generates file hashes to detect duplicates.  

**What’s stored**:
- Artifacts  
- Projects (repos)  
- Scan jobs  
- User overrides  

**Why SQLite now**:
- Simple & portable for a desktop-style MVP.  
- Good performance at your expected scale (tens to low hundreds of thousands of files).  
- Keeps everything local-only for privacy by default.  

---

# Reporting & Export

- **Jinja2** – templating engine to generate HTML reports.  
- **WeasyPrint** – converts HTML/CSS reports into PDFs.  
- **Playwright / Headless Chromium** – optional export to PNG/JPG by rendering pages off-screen.  
- **Pillow** – image processing (e.g., thumbnails).  

**Outputs**:
- Readable English reports with charts, legends, and summaries.  
- Export formats: **PDF / HTML / PNG / JPG**.  

**Why**: Directly meets your *“visual, human-readable outputs”* requirement and enables portfolio/resumé artifacts.  

---

# DevOps & Packaging

- **PyInstaller** – bundles backend Python code into a single binary.  
- **electron-builder** – packages the whole Electron + backend into installers (`.exe`, `.dmg`, `.AppImage`).  
- **pytest + Hypothesis** – testing libraries for backend logic and edge cases.  
- **Playwright** – automated tests for UI flows.  
- **k6** – load testing tool to check performance under heavy scans.  
