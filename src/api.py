import json
import mimetypes
import os
import sys
import re
import sqlite3
from io import StringIO
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import subprocess

# Ensure local imports work when running via uvicorn from repo root.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi import APIRouter, Body, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from markdown import markdown as render_markdown_html
from project_evidence import add_evidence, delete_evidence, update_evidence, validate_evidence_type
from pydantic import BaseModel, Field
import contextlib
import queue
import threading
import glob
import tempfile
import zipfile

from config import load_config, save_config, config_path as default_config_path
from cli_username_selection import get_candidate_usernames
from db import get_connection, save_portfolio, update_portfolio, list_portfolios, list_all_portfolios, rename_portfolio, delete_portfolio, save_resume, delete_project_by_id
from generate_portfolio import aggregate_projects_for_portfolio
from generate_resume import (
    collect_projects,
    aggregate_for_user,
    render_markdown,
    maybe_generate_resume_summary,
)
from project_info_output import gather_project_info, output_project_info
from rank_projects import rank_projects, rank_projects_by_importance, list_custom_rankings, get_custom_ranking, save_custom_ranking, delete_custom_ranking
from contrib_metrics import canonical_username, classify_file
from detect_roles import analyze_project_roles
from scan import (
    run_with_saved_settings,
    scan_with_clean_output,
    _find_all_project_roots,
    _find_git_root,
    _resolve_extracted_root,
)
from inspect_db import inspect_connection
from generate_portfolio import build_portfolio

try:
    from weasyprint import HTML  # type: ignore
except Exception:
    HTML = None


app = FastAPI(title="MDA API")
web_router = APIRouter(prefix="/web/portfolio", tags=["web-portfolio"])


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}

# Allow local frontend origins (Vite/Electron dev) to read API responses.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PrivacyConsentRequest(BaseModel):
    data_consent: bool
    llm_summary_consent: Optional[bool] = None
    llm_resume_consent: Optional[bool] = None


class ProjectUploadRequest(BaseModel):
    project_path: str
    recursive_choice: bool = False
    file_type: Optional[str] = None
    show_collaboration: bool = False
    show_contribution_metrics: bool = False
    show_contribution_summary: bool = False
    save_to_db: bool = True
    thumbnail_path: Optional[str] = None
    llm_summary: bool = False
    manual_contributors_by_path: Optional[Dict[str, List[str]]] = None


class ScanPlanProject(BaseModel):
    project_name: str
    project_path: str
    is_git: bool
    requires_contributor_assignment: bool


class ScanPlanResponse(BaseModel):
    root_path: str
    total_projects: int
    is_multi_project: bool
    projects: List[ScanPlanProject]
    existing_contributors: List[str]


class ProjectEditRequest(BaseModel):
    custom_name: Optional[str] = None
    repo_url: Optional[str] = None
    thumbnail_path: Optional[str] = None
    summary_text: Optional[str] = None



class ResumeGenerateRequest(BaseModel):
    username: str
    output_root: str = "output"
    resume_dir: str = "resumes"
    allow_bots: bool = False
    save_to_db: bool = False
    llm_summary: bool = False
    excluded_project_names: List[str] = Field(default_factory=list)
    education: Optional[List[Dict[str, str]]] = None


class ResumeEditRequest(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None


class PortfolioGenerateRequest(BaseModel):
    username: str
    output_root: str = "output"
    portfolio_dir: str = "portfolios"
    confidence_level: str = Field("high", pattern="^(high|medium|low)$")
    save_to_db: bool = False


class PortfolioSaveRequest(BaseModel):
    username: str
    portfolio_name: str
    display_name: Optional[str] = None
    included_project_ids: List[int] = []
    featured_project_ids: List[int] = []


class PortfolioRenameRequest(BaseModel):
    portfolio_name: str


class PortfolioUpdateRequest(BaseModel):
    portfolio_name: str
    display_name: Optional[str] = None
    included_project_ids: List[int] = []
    featured_project_ids: List[int] = []


class WebPortfolioCustomizeRequest(BaseModel):
    selected_project_ids: Optional[List[int]] = None
    featured_project_ids: Optional[List[int]] = None


def _parse_metadata(metadata_json: Optional[str]) -> Dict[str, Any]:
    # Keep metadata parsing resilient to malformed JSON stored in DB.
    if not metadata_json:
        return {}
    try:
        return json.loads(metadata_json)
    except Exception:
        return {}


def _table_exists(conn: Any, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return bool(row)


def _table_has_column(conn: Any, table_name: str, column_name: str) -> bool:
    if not _table_exists(conn, table_name):
        return False
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return any(row["name"] == column_name for row in rows)


def _resume_payload(row: Any) -> Dict[str, Any]:
    # Hydrate response with file contents stored on disk.
    resume_path = row["resume_path"]
    if not os.path.isfile(resume_path):
        raise HTTPException(status_code=404, detail="Resume file not found")
    with open(resume_path, "r", encoding="utf-8") as fh:
        content = fh.read()
    return {
        "id": row["id"],
        "username": row["username"],
        "resume_path": resume_path,
        "metadata": _parse_metadata(row["metadata_json"]),
        "generated_at": row["generated_at"],
        "content": content,
    }


def _portfolio_payload(row: Any) -> Dict[str, Any]:
    # Hydrate response with file contents stored on disk.
    portfolio_path = row["portfolio_path"]
    if not os.path.isfile(portfolio_path):
        raise HTTPException(status_code=404, detail="Portfolio file not found")
    with open(portfolio_path, "r", encoding="utf-8") as fh:
        content = fh.read()
    return {
        "id": row["id"],
        "username": row["username"],
        "portfolio_path": portfolio_path,
        "metadata": _parse_metadata(row["metadata_json"]),
        "generated_at": row["generated_at"],
        "content": content,
    }


def _safe_pdf_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value or "resume")
    return cleaned.strip("_.") or "resume"


def _resume_pdf_html(markdown_text: str) -> str:
    body_html = render_markdown_html(markdown_text or "", extensions=["extra", "sane_lists"])
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
  <style>
    @page {{
      size: letter;
      margin: 0.75in;
    }}

    html, body {{
      margin: 0;
      padding: 0;
      color: #0f172a;
      font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
      font-size: 10.5pt;
      line-height: 1.45;
    }}

    .resume {{
      width: 100%;
    }}

    h1 {{
      margin: 0 0 0.22in;
      font-size: 25pt;
      line-height: 1.15;
      font-weight: 700;
      letter-spacing: 0.01em;
      color: #111827;
    }}

    h2 {{
      margin: 0.2in 0 0.09in;
      padding-bottom: 0.05in;
      border-bottom: 1px solid #cbd5e1;
      font-size: 10.8pt;
      line-height: 1.2;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: #334155;
      font-weight: 700;
    }}

    h3 {{
      margin: 0.14in 0 0.05in;
      font-size: 10.8pt;
      font-weight: 700;
      color: #1f2937;
    }}

    p {{
      margin: 0 0 0.08in;
    }}

    ul {{
      margin: 0.04in 0 0.1in 0.2in;
      padding: 0;
    }}

    li {{
      margin: 0 0 0.055in;
      padding-left: 0.01in;
    }}

    strong {{
      font-weight: 700;
      color: #111827;
    }}

    p > strong:first-child:last-child {{
      display: block;
      margin-top: 0.03in;
      margin-bottom: 0.03in;
      font-size: 10.8pt;
    }}
  </style>
</head>
<body>
  <main class=\"resume\">{body_html}</main>
</body>
</html>
"""


def _render_resume_pdf_with_reportlab(markdown_text: str) -> bytes:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from io import BytesIO

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        leftMargin=0.75*inch, rightMargin=0.75*inch,
        topMargin=0.75*inch, bottomMargin=0.75*inch
    )

    dark = colors.HexColor("#111827")
    mid = colors.HexColor("#334155")
    body_color = colors.HexColor("#0f172a")
    divider_color = colors.HexColor("#cbd5e1")

    style_h1 = ParagraphStyle("h1", fontSize=24, fontName="Helvetica-Bold",
                               textColor=dark, spaceAfter=10, leading=28)
    style_h2 = ParagraphStyle("h2", fontSize=8.5, fontName="Helvetica-Bold",
                               textColor=mid, spaceBefore=16, spaceAfter=2,
                               letterSpacing=1.2)
    style_h3 = ParagraphStyle("h3", fontSize=10.5, fontName="Helvetica-Bold",
                               textColor=dark, spaceBefore=8, spaceAfter=2)
    style_body = ParagraphStyle("body", fontSize=10, fontName="Helvetica",
                                textColor=body_color, spaceAfter=3, leading=14)
    style_bullet = ParagraphStyle("bullet", fontSize=10, fontName="Helvetica",
                                  textColor=body_color, spaceAfter=2, leading=14,
                                  leftIndent=14, firstLineIndent=0)
    style_meta = ParagraphStyle("meta", fontSize=9, fontName="Helvetica-Oblique",
                                textColor=mid, spaceBefore=8)

    story = []
    for line in markdown_text.splitlines():
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 3))
        elif stripped.startswith("# "):
            story.append(Paragraph(stripped[2:], style_h1))
        elif stripped.startswith("## "):
            text = stripped[3:].upper()
            story.append(Spacer(1, 2))
            story.append(Paragraph(text, style_h2))
            story.append(HRFlowable(width="100%", thickness=0.5,
                                    color=divider_color, spaceAfter=5))
        elif stripped.startswith("**") and stripped.endswith("**"):
            story.append(Paragraph(stripped[2:-2], style_h3))
        elif stripped.startswith("- "):
            text = stripped[2:]
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            story.append(Paragraph(f"\u2022\u00a0{text}", style_bullet))
        elif stripped.startswith("_") and stripped.endswith("_"):
            story.append(Paragraph(f"<i>{stripped[1:-1]}</i>", style_meta))
        else:
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', stripped)
            story.append(Paragraph(text, style_body))

    doc.build(story)
    return buf.getvalue()


def _load_portfolio_row_or_404(portfolio_id: int) -> Any:
    with get_connection() as conn:
        row = conn.execute(
            """SELECT id, username, portfolio_name, display_name,
                      included_project_ids, featured_project_ids, created_at
               FROM portfolios WHERE id = ?""",
            (portfolio_id,),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return row


def _portfolio_row_to_dict(row: Any) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "username": row["username"],
        "portfolio_name": row["portfolio_name"],
        "display_name": row["display_name"],
        "included_project_ids": json.loads(row["included_project_ids"] or "[]"),
        "featured_project_ids": json.loads(row["featured_project_ids"] or "[]"),
        "created_at": row["created_at"],
    }


def _resolve_project_names_for_web(row: Any) -> List[str]:
    """Resolve ordered project names from a portfolio row's included_project_ids."""
    included_ids = json.loads(row["included_project_ids"] or "[]")
    if not included_ids:
        return []
    with get_connection() as conn:
        placeholders = ",".join("?" for _ in included_ids)
        rows = conn.execute(
            f"SELECT id, name FROM projects WHERE id IN ({placeholders})",
            included_ids,
        ).fetchall()
    id_to_name = {r["id"]: r["name"] for r in rows}
    return [id_to_name[pid] for pid in included_ids if pid in id_to_name]


def _load_latest_project_summary(project_name: str) -> Optional[Dict[str, Any]]:
    if not project_name:
        return None
    out_dir = os.path.join("output", project_name)
    if not os.path.isdir(out_dir):
        return None
    pattern = os.path.join(out_dir, f"{project_name}_info_*.json")
    candidates = glob.glob(pattern)
    if not candidates:
        return None
    latest = max(candidates, key=lambda p: os.path.getmtime(p))
    try:
        with open(latest, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
            if payload and "high_confidence_skills" not in payload:
                skills = payload.get("skills")
                if isinstance(skills, list):
                    payload["high_confidence_skills"] = skills
            return payload
    except Exception:
        return None


def _load_llm_summary(project_name: str) -> Optional[Dict[str, Any]]:
    if not project_name:
        return None
    with get_connection() as conn:
        row = conn.execute(
            "SELECT summary_text, summary_model, summary_updated_at FROM projects WHERE name = ?",
            (project_name,),
        ).fetchone()
    if not row or not row["summary_text"]:
        return None
    return {
        "text": row["summary_text"],
        "model": row["summary_model"],
        "updated_at": row["summary_updated_at"],
    }


def _list_existing_contributors() -> List[str]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT name FROM contributors WHERE name IS NOT NULL AND TRIM(name) <> '' ORDER BY name COLLATE NOCASE"
        ).fetchall()
    return [row["name"] for row in rows]


def _collect_commit_cells_from_git_log(
    project_path: Optional[str],
    granularity: str,
    target_username: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Collect commit activity cells directly from git log for a repository path."""
    if not project_path or not os.path.isdir(project_path):
        return []

    target_canonical = canonical_username(target_username or "") if target_username else None
    cmd = [
        "git",
        "log",
        "--no-merges",
        "--pretty=format:%an|%ae|%ad",
        "--date=iso",
    ]

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_path,
        )
    except Exception:
        return []

    if proc.returncode != 0:
        return []

    buckets: Dict[str, int] = {}
    for line in proc.stdout.splitlines():
        if not line or "|" not in line:
            continue

        parts = line.split("|", 2)
        if len(parts) < 3:
            continue

        author_name = parts[0].strip()
        author_email = parts[1].strip()
        date_str = parts[2].strip()

        if target_canonical and canonical_username(author_name, author_email) != target_canonical:
            continue

        try:
            dt = datetime.fromisoformat(date_str)
        except Exception:
            try:
                dt = datetime.strptime(date_str[:19], "%Y-%m-%d %H:%M:%S")
            except Exception:
                continue

        if granularity == "day":
            period = dt.date().isoformat()
        elif granularity == "month":
            period = f"{dt.year:04d}-{dt.month:02d}"
        else:
            year, week, _ = dt.isocalendar()
            period = datetime.fromisocalendar(year, week, 1).date().isoformat()

        buckets[period] = int(buckets.get(period, 0)) + 1

    return [
        {"period": period, "value": int(buckets[period])}
        for period in sorted(buckets.keys())
    ]


def _compute_project_contributor_roles(conn: Any, project_name: str) -> Dict[str, Any]:
    """Infer contributor roles for a project from per-file activity in all scans."""
    if not project_name:
        return {"contributors": [], "summary": {}}

    rows = conn.execute(
        """
        SELECT c.name AS contributor_name, f.file_path
        FROM scans s
        JOIN files f ON f.scan_id = s.id
        JOIN file_contributors fc ON fc.file_id = f.id
        JOIN contributors c ON c.id = fc.contributor_id
        WHERE s.project = ?
          AND c.name IS NOT NULL
          AND TRIM(c.name) <> ''
        """,
        (project_name,),
    ).fetchall()

    if not rows:
        return {"contributors": [], "summary": {}}

    contributors_data: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        contributor_name = row["contributor_name"]
        file_path = row["file_path"] or ""

        if contributor_name not in contributors_data:
            contributors_data[contributor_name] = {
                "files_changed": set(),
                "activity_by_category": {
                    "code": 0,
                    "test": 0,
                    "docs": 0,
                    "design": 0,
                    "other": 0,
                },
            }

        file_set = contributors_data[contributor_name]["files_changed"]
        if file_path and file_path not in file_set:
            file_set.add(file_path)
            category = classify_file(file_path)
            activity = contributors_data[contributor_name]["activity_by_category"]
            activity[category] = activity.get(category, 0) + 1

    normalized: Dict[str, Dict[str, Any]] = {}
    for name, data in contributors_data.items():
        files_changed = sorted(data["files_changed"])
        file_count = len(files_changed)
        normalized[name] = {
            "files_changed": files_changed,
            # Keep estimate strategy aligned with detect_roles DB loaders.
            "commits": max(1, file_count),
            "lines_added": file_count * 50,
            "lines_removed": file_count * 10,
            "activity_by_category": data["activity_by_category"],
        }

    return analyze_project_roles(normalized)


@app.post("/privacy-consent")
def update_privacy_consent(payload: PrivacyConsentRequest):
    # Persist consent in the user's config to mirror CLI behavior.
    current = load_config(default_config_path())
    llm_value = payload.llm_summary_consent
    if llm_value is None:
        llm_value = current.get("llm_summary_consent", False)
    resume_llm_value = payload.llm_resume_consent
    if resume_llm_value is None:
        resume_llm_value = current.get("llm_resume_consent", False)
    save_config(
        {
            "data_consent": payload.data_consent,
            "llm_summary_consent": llm_value,
            "llm_resume_consent": resume_llm_value,
        },
        path=default_config_path(),
    )
    return {
        "data_consent": payload.data_consent,
        "llm_summary_consent": llm_value,
        "llm_resume_consent": resume_llm_value,
        "config_path": default_config_path(),
    }


@app.get("/config")
def get_config() -> Dict[str, bool]:
    current = load_config(default_config_path())
    return {
        "data_consent": bool(current.get("data_consent", False)),
        "llm_summary_consent": bool(current.get("llm_summary_consent", False)),
        "llm_resume_consent": bool(current.get("llm_resume_consent", False)),
    }


@app.post("/projects/upload", status_code=201)
def upload_project(payload: ProjectUploadRequest):
    # Enforce the same consent gate used by the CLI scanner.
    config = load_config(default_config_path())
    if not config.get("data_consent"):
        raise HTTPException(status_code=403, detail="Data consent not granted")
    if payload.llm_summary and not config.get("llm_summary_consent"):
        raise HTTPException(status_code=403, detail="LLM summary consent not granted")

    if not os.path.exists(payload.project_path):
        raise HTTPException(status_code=400, detail="project_path not found")

    # Trigger the existing scan pipeline and optionally persist results.
    run_with_saved_settings(
        directory=payload.project_path,
        recursive_choice=payload.recursive_choice,
        file_type=payload.file_type,
        show_collaboration=payload.show_collaboration,
        show_contribution_metrics=payload.show_contribution_metrics,
        show_contribution_summary=payload.show_contribution_summary,
        save=False,
        save_to_db=payload.save_to_db,
        thumbnail_source=payload.thumbnail_path,
        generate_llm_summary=payload.llm_summary,
    )

    project_name = os.path.basename(os.path.abspath(payload.project_path))
    scan_id = None
    if payload.save_to_db:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT id FROM scans WHERE project = ? ORDER BY id DESC LIMIT 1",
                (project_name,),
            ).fetchone()
            scan_id = row["id"] if row else None

    # Attempt to generate a structured project summary alongside the scan.
    output_summary_path = None
    try:
        info = gather_project_info(payload.project_path)
        out_dir = os.path.join("output", project_name)
        os.makedirs(out_dir, exist_ok=True)
        json_path, _ = output_project_info(info, output_dir=out_dir)
        output_summary_path = json_path
    except Exception:
        output_summary_path = None

    return {
        "project_name": project_name,
        "scan_id": scan_id,
        "saved_to_db": payload.save_to_db,
        "output_summary_path": output_summary_path,
    }


@app.post("/projects/scan-plan", response_model=ScanPlanResponse)
def get_project_scan_plan(payload: ProjectUploadRequest):
    config = load_config(default_config_path())
    if not config.get("data_consent"):
        raise HTTPException(status_code=403, detail="Data consent not granted")

    if not os.path.exists(payload.project_path):
        raise HTTPException(status_code=400, detail="project_path not found")

    root_path = os.path.abspath(payload.project_path)
    zip_extract_ctx = None
    scan_target = root_path
    try:
        if os.path.isfile(root_path) and root_path.lower().endswith(".zip"):
            zip_extract_ctx = tempfile.TemporaryDirectory()
            with zipfile.ZipFile(root_path) as zf:
                zf.extractall(zip_extract_ctx.name)
            scan_target = _resolve_extracted_root(zip_extract_ctx.name)

        project_roots = _find_all_project_roots(scan_target)
        if not project_roots:
            project_roots = [scan_target]

        projects = [
            {
                "project_name": os.path.basename(os.path.abspath(project_root)),
                "project_path": os.path.abspath(project_root),
                "is_git": _find_git_root(project_root) is not None,
                "requires_contributor_assignment": _find_git_root(project_root) is None,
            }
            for project_root in project_roots
        ]
    finally:
        if zip_extract_ctx is not None:
            zip_extract_ctx.cleanup()

    return {
        "root_path": root_path,
        "total_projects": len(projects),
        "is_multi_project": len(projects) > 1,
        "projects": projects,
        "existing_contributors": _list_existing_contributors(),
    }


@app.post("/projects/scan-stream")
def stream_project_scan(payload: ProjectUploadRequest):
    # Enforce the same consent gate used by the CLI scanner.
    config = load_config(default_config_path())
    if not config.get("data_consent"):
        raise HTTPException(status_code=403, detail="Data consent not granted")
    if payload.llm_summary and not config.get("llm_summary_consent"):
        raise HTTPException(status_code=403, detail="LLM summary consent not granted")

    if not os.path.exists(payload.project_path):
        raise HTTPException(status_code=400, detail="project_path not found")

    q: "queue.Queue[Optional[str]]" = queue.Queue()

    class StreamWriter:
        def __init__(self):
            self.buffer = ""

        def write(self, data: str) -> int:
            if not data:
                return 0
            # Convert carriage returns (progress updates) into line breaks.
            data = data.replace("\r", "\n")
            self.buffer += data
            while "\n" in self.buffer:
                line, self.buffer = self.buffer.split("\n", 1)
                q.put(line)
            return len(data)

        def flush(self) -> None:
            return None

    def emit_event(event: Dict[str, Any]) -> None:
        q.put(f"SCAN_EVENT::{json.dumps(event)}")

    def run_scan() -> None:
        try:
            writer = StreamWriter()
            with contextlib.redirect_stdout(writer), contextlib.redirect_stderr(writer):
                result = scan_with_clean_output(
                    directory=payload.project_path,
                    recursive=True,
                    file_type=None,
                    save_to_db=True,
                    thumbnail_source=payload.thumbnail_path,
                    generate_llm_summary=payload.llm_summary,
                    manual_contributors_by_path=payload.manual_contributors_by_path or {},
                    prompt_for_manual_contributors=False,
                    prompt_between_projects=False,
                    progress_callback=emit_event,
                )
            if writer.buffer:
                q.put(writer.buffer)

            project_names = result.get("project_names") or []
            if not project_names and result.get("project_name"):
                project_names = [result.get("project_name")]

            summaries: List[Dict[str, Any]] = []
            for name in project_names:
                summary = _load_latest_project_summary(name) or {"project_name": name}
                llm = _load_llm_summary(name)
                if llm:
                    summary["llm_summary"] = llm
                summaries.append(summary)

            summary = {
                "success": bool(result.get("success")),
                "partial_success": bool(result.get("partial_success")),
                "project_name": result.get("project_name"),
                "project_names": result.get("project_names"),
                "project_results": result.get("project_results"),
                "failed_projects": result.get("failed_projects"),
                "output_dir": result.get("output_dir"),
                "error": result.get("error"),
                "summaries": summaries,
            }
            q.put(f"SCAN_DONE::{json.dumps(summary)}")
        except Exception as exc:
            q.put(f"SCAN_DONE::{json.dumps({'success': False, 'error': str(exc)})}")
        finally:
            q.put(None)

    threading.Thread(target=run_scan, daemon=True).start()

    def generate():
        while True:
            item = q.get()
            if item is None:
                break
            yield f"{item}\n"

    return StreamingResponse(generate(), media_type="text/plain; charset=utf-8")


@app.get("/projects")
def list_projects():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT p.id, p.name, p.custom_name, p.repo_url, p.created_at, p.thumbnail_path,
       (SELECT MAX(scanned_at) FROM scans s WHERE s.project = p.name) AS latest_scan_at
FROM projects p
ORDER BY p.id
            """
        ).fetchall()
    return [dict(row) for row in rows]


@app.get("/projects/{project_id}")
def get_project(project_id: int):
    with get_connection() as conn:
        project = conn.execute(
            "SELECT id, name, custom_name, repo_url, created_at, thumbnail_path FROM projects WHERE id = ?",
            (project_id,),
        ).fetchone()

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        scans = conn.execute(
            "SELECT id, scanned_at, notes FROM scans WHERE project = ? ORDER BY scanned_at DESC",
            (project["name"],),
        ).fetchall()

        scan_ids = [row["id"] for row in scans]

        files_summary = {"total_files": 0, "extensions": {}}
        languages: List[str] = []
        contributors: List[str] = []

        if scan_ids:
            placeholders = ",".join("?" for _ in scan_ids)

            files_summary["total_files"] = conn.execute(
                f"SELECT COUNT(*) AS total FROM files WHERE scan_id IN ({placeholders})",
                scan_ids,
            ).fetchone()["total"]

            ext_rows = conn.execute(
                f"""
                SELECT file_extension, COUNT(*) AS count
                FROM files
                WHERE scan_id IN ({placeholders})
                GROUP BY file_extension
                """,
                scan_ids,
            ).fetchall()

            files_summary["extensions"] = {
                (row["file_extension"] or ""): row["count"] for row in ext_rows
            }

            languages_rows = conn.execute(
                f"""
                SELECT DISTINCT l.name
                FROM languages l
                JOIN file_languages fl ON fl.language_id = l.id
                JOIN files f ON f.id = fl.file_id
                WHERE f.scan_id IN ({placeholders})
                """,
                scan_ids,
            ).fetchall()

            languages = [row["name"] for row in languages_rows]

            contributor_rows = conn.execute(
                f"""
                SELECT DISTINCT c.name
                FROM contributors c
                JOIN file_contributors fc ON fc.contributor_id = c.id
                JOIN files f ON f.id = fc.file_id
                WHERE f.scan_id IN ({placeholders})
                """,
                scan_ids,
            ).fetchall()

            contributors = [row["name"] for row in contributor_rows]

        skill_rows = conn.execute(
            """
            SELECT s.name
            FROM skills s
            JOIN project_skills ps ON ps.skill_id = s.id
            WHERE ps.project_id = ?
            ORDER BY s.name
            """,
            (project_id,),
        ).fetchall()

        evidence_rows = conn.execute(
            """
            SELECT id, type, description, value, source, url, added_by_user, created_at
            FROM project_evidence
            WHERE project_id = ?
            ORDER BY created_at DESC
            """,
            (project_id,),
        ).fetchall()

        llm_summary = _load_llm_summary(project["name"])
        contributor_roles = _compute_project_contributor_roles(conn, project["name"])

        git_metrics_row = conn.execute(
            "SELECT git_metrics_json, tech_json FROM projects WHERE id = ?",
            (project_id,),
        ).fetchone()
        git_metrics = _parse_metadata(git_metrics_row["git_metrics_json"]) if git_metrics_row else {}
        tech_summary = _parse_metadata(git_metrics_row["tech_json"]) if git_metrics_row else {}

    # Look up this project's rank score from the project-mode importance ranking.
    rank_score: Optional[float] = None
    try:
        all_ranked = rank_projects_by_importance(mode="project", contributor_name=None, limit=None)
        for item in all_ranked:
            if item.get("project") == project["name"]:
                rank_score = item.get("top_score")
                break
    except Exception:
        pass

    return {
        "project": dict(project),
        "skills": [row["name"] for row in skill_rows],
        "languages": languages,
        "frameworks": tech_summary.get("high_confidence_frameworks") or tech_summary.get("frameworks") or [],
        "contributors": contributors,
        "contributor_roles": contributor_roles,
        "scans": [dict(row) for row in scans],
        "files_summary": files_summary,
        "evidence": [dict(row) for row in evidence_rows],
        "llm_summary": llm_summary,
        "git_metrics": git_metrics,
        "rank_score": rank_score,
    }


@app.patch("/projects/{project_id}/evidence/{evidence_id}")
def update_project_evidence(project_id: int, evidence_id: int, payload: dict = Body(...)):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM project_evidence WHERE id = ? AND project_id = ?",
            (evidence_id, project_id),
        ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Evidence not found")

    updates = {}
    if "type" in payload:
        try:
            updates["type"] = validate_evidence_type(payload.get("type", ""))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
    if "description" in payload:
        updates["description"] = payload.get("description")
    if "value" in payload:
        updates["value"] = payload.get("value")
    if "source" in payload:
        updates["source"] = payload.get("source")
    if "url" in payload:
        updates["url"] = payload.get("url")
    if "added_by_user" in payload:
        updates["added_by_user"] = payload.get("added_by_user")

    updated = update_evidence(evidence_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Evidence not found")

    return {"message": "Evidence updated successfully"}


@app.post("/projects/{project_id}/evidence", status_code=201)
def create_project_evidence(project_id: int, payload: dict = Body(...)):
    with get_connection() as conn:
        project = conn.execute(
            "SELECT id FROM projects WHERE id = ?",
            (project_id,),
        ).fetchone()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        evidence_id = add_evidence(
            project_id,
            {
                "type": validate_evidence_type(payload.get("type", "")),
                "value": payload.get("value"),
                "source": payload.get("source"),
                "url": payload.get("url"),
                "added_by_user": payload.get("added_by_user", True),
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "evidence_id": evidence_id,
        "message": "Evidence added successfully"
    }
    

@app.delete("/projects/{project_id}/evidence/{evidence_id}")
def remove_project_evidence(project_id: int, evidence_id: int):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM project_evidence WHERE id = ? AND project_id = ?",
            (evidence_id, project_id),
        ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Evidence not found")

    deleted = delete_evidence(evidence_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Evidence not found")

    return {"message": "Evidence deleted successfully"}

@app.get("/skills")
def list_skills():
    with get_connection() as conn:
        rows = conn.execute("SELECT name FROM skills ORDER BY name").fetchall()
    return [row["name"] for row in rows]


@app.get("/contributors")
def list_contributors():
    blacklist = {"githubclassroombot", "unknown", "n/a", "none"}
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT name FROM contributors WHERE name IS NOT NULL AND TRIM(name) <> '' ORDER BY name COLLATE NOCASE"
        ).fetchall()
    return sorted(
        row["name"] for row in rows
        if row["name"].lower() not in blacklist
    )


@app.get("/rank-projects")
def get_rank_projects(
    mode: str = Query("project", pattern="^(project|contributor)$"),
    contributor_name: Optional[str] = Query(None),
    limit: Optional[int] = Query(None, ge=1, le=200),
    sort_mode: str = Query("importance", pattern="^(importance|chronological)$"),
    chronological_order: str = Query("desc", pattern="^(asc|desc)$"),
):
    if mode == "contributor" and not (contributor_name and contributor_name.strip()):
        raise HTTPException(status_code=400, detail="contributor_name is required for contributor mode")

    ranked = rank_projects_by_importance(
        mode=mode,
        contributor_name=(contributor_name.strip() if contributor_name else None),
        limit=None,
    )

    # Attach creation/scan chronology metadata for each project.
    timeline_by_project = {
        item.get("project"): item
        for item in rank_projects(order=chronological_order)
        if item.get("project")
    }
    for item in ranked:
        timeline = timeline_by_project.get(item.get("project"), {})
        item["created_at"] = timeline.get("created_at")
        item["first_scan"] = timeline.get("first_scan")
        item["last_scan"] = timeline.get("last_scan")
        item["scans_count"] = timeline.get("scans_count", 0)

    if sort_mode == "chronological":
        ranked.sort(
            key=lambda x: (x.get("created_at") or ""),
            reverse=(chronological_order == "desc"),
        )

    if limit is not None and isinstance(limit, int) and limit > 0:
        return ranked[:limit]

    return ranked


# ── Custom Rankings ────────────────────────────────────────────

class CustomRankingCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str = Field("", max_length=500)
    projects: List[str] = Field(..., min_length=1)


@app.get("/custom-rankings")
def api_list_custom_rankings():
    return list_custom_rankings()


@app.post("/custom-rankings", status_code=201)
def api_create_custom_ranking(body: CustomRankingCreate):
    try:
        ranking_id = save_custom_ranking(body.name.strip(), body.projects, body.description.strip())
        return {"id": ranking_id, "name": body.name.strip()}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/custom-rankings/{name}")
def api_get_custom_ranking(name: str):
    projects = get_custom_ranking(name)
    if not projects:
        raise HTTPException(status_code=404, detail="Custom ranking not found or empty")
    return {"name": name, "projects": projects}


@app.delete("/custom-rankings/{name}")
def api_delete_custom_ranking(name: str):
    deleted = delete_custom_ranking(name)
    if not deleted:
        raise HTTPException(status_code=404, detail="Custom ranking not found")
    return {"deleted": True}


@app.get("/resume/{resume_id}")
def get_resume(resume_id: int):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, username, resume_path, metadata_json, generated_at FROM resumes WHERE id = ?",
            (resume_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Resume not found")
    return _resume_payload(row)


@app.get("/resume/{resume_id}/pdf")
def get_resume_pdf(resume_id: int):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, username, resume_path, metadata_json, generated_at FROM resumes WHERE id = ?",
            (resume_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Resume not found")

    resume_path = row["resume_path"]
    if not resume_path or not os.path.isfile(resume_path):
        raise HTTPException(status_code=404, detail="Resume file not found")

    with open(resume_path, "r", encoding="utf-8") as fh:
        markdown_text = fh.read()

    if HTML is not None:
        pdf_bytes = HTML(string=_resume_pdf_html(markdown_text)).write_pdf()
    else:
        pdf_bytes = _render_resume_pdf_with_reportlab(markdown_text)

    username = row["username"] or "local"
    filename = _safe_pdf_filename(f"resume_{username}_{resume_id}.pdf")
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Cache-Control": "no-store",
    }
    return StreamingResponse(iter([pdf_bytes]), media_type="application/pdf", headers=headers)


@app.get("/resumes")
def list_resumes(username: Optional[str] = Query(default=None)):
    username_filter = (username or "").strip()
    with get_connection() as conn:
        if username_filter:
            rows = conn.execute(
                """
                SELECT id, username, generated_at, metadata_json
                FROM resumes
                WHERE username = ?
                ORDER BY generated_at DESC
                """,
                (username_filter,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, username, generated_at, metadata_json
                FROM resumes
                ORDER BY generated_at DESC
                """
            ).fetchall()

    items = []
    for row in rows:
        metadata = _parse_metadata(row["metadata_json"])
        items.append(
            {
                "id": row["id"],
                "username": row["username"],
                "generated_at": row["generated_at"],
                "llm_used": bool(metadata.get("llm_summary")),
            }
        )
    return items


@app.get("/outputs")
def get_outputs_count():
    """Count generated outputs (resumes and portfolios) with recent activity."""
    with get_connection() as conn:
        resumes_count = conn.execute("SELECT COUNT(*) as count FROM resumes").fetchone()["count"]
        portfolios_count = conn.execute("SELECT COUNT(*) as count FROM portfolios").fetchone()["count"]
        
        # Get most recent output
        latest_resume = conn.execute(
            "SELECT generated_at FROM resumes ORDER BY generated_at DESC LIMIT 1"
        ).fetchone()
        latest_portfolio = conn.execute(
            "SELECT generated_at FROM portfolios ORDER BY generated_at DESC LIMIT 1"
        ).fetchone()
        
        latest_generated = None
        if latest_resume and latest_portfolio:
            latest_generated = max(latest_resume["generated_at"], latest_portfolio["generated_at"])
        elif latest_resume:
            latest_generated = latest_resume["generated_at"]
        elif latest_portfolio:
            latest_generated = latest_portfolio["generated_at"]
    
    return {
        "resumes": resumes_count,
        "portfolios": portfolios_count,
        "total": resumes_count + portfolios_count,
        "latest_generated": latest_generated,
    }


@app.get("/stats/dashboard")
def get_dashboard_stats():
    """Comprehensive dashboard stats with insights."""
    with get_connection() as conn:
        # Projects info
        projects_count = conn.execute("SELECT COUNT(*) as count FROM projects").fetchone()["count"]
        latest_scan = conn.execute(
            "SELECT scanned_at, project FROM scans ORDER BY scanned_at DESC LIMIT 1"
        ).fetchone()
        
        # Contributors info
        contributors_count = conn.execute(
            "SELECT COUNT(DISTINCT name) as count FROM contributors WHERE name IS NOT NULL AND TRIM(name) <> ''"
        ).fetchone()["count"]
        top_contributor = conn.execute(
            """
            SELECT c.name, COUNT(fc.file_id) as file_count
            FROM contributors c
            LEFT JOIN file_contributors fc ON c.id = fc.contributor_id
            WHERE c.name IS NOT NULL AND TRIM(c.name) <> ''
            GROUP BY c.id
            ORDER BY file_count DESC
            LIMIT 1
            """
        ).fetchone()

        # Outputs info. Older local DBs may not yet have these tables/columns.
        resumes_count = 0
        portfolios_count = 0
        latest_output = None

        try:
            if _table_exists(conn, "resumes"):
                resumes_count = conn.execute("SELECT COUNT(*) as count FROM resumes").fetchone()["count"]
            if _table_exists(conn, "portfolios"):
                portfolios_count = conn.execute("SELECT COUNT(*) as count FROM portfolios").fetchone()["count"]

            generated_timestamps: List[str] = []
            if _table_has_column(conn, "resumes", "generated_at"):
                generated_timestamps.extend(
                    row["generated_at"]
                    for row in conn.execute("SELECT generated_at FROM resumes WHERE generated_at IS NOT NULL").fetchall()
                    if row["generated_at"]
                )
            if _table_has_column(conn, "portfolios", "generated_at"):
                generated_timestamps.extend(
                    row["generated_at"]
                    for row in conn.execute("SELECT generated_at FROM portfolios WHERE generated_at IS NOT NULL").fetchall()
                    if row["generated_at"]
                )
            if generated_timestamps:
                latest_output = {"generated_at": max(generated_timestamps)}
        except sqlite3.OperationalError:
            latest_output = None
    
    return {
        "projects": {
            "count": projects_count,
            "latest_scan": latest_scan["scanned_at"] if latest_scan else None,
            "latest_project": latest_scan["project"] if latest_scan else None,
        },
        "contributors": {
            "count": contributors_count,
            "top_contributor": top_contributor["name"] if top_contributor else None,
            "top_contributor_files": top_contributor["file_count"] if top_contributor else 0,
        },
        "outputs": {
            "total": resumes_count + portfolios_count,
            "resumes": resumes_count,
            "portfolios": portfolios_count,
            "latest_generated": latest_output["generated_at"] if latest_output else None,
        },
    }



@app.post("/resume/generate", status_code=201)
def generate_resume(payload: ResumeGenerateRequest):
    # Reuse the resume generator logic used by the CLI.
    # output_root retained for backward compatibility but ignored (DB is used)

    username = payload.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="username is required")

    blacklist = {"githubclassroombot"}
    if username in blacklist and not payload.allow_bots:
        raise HTTPException(
            status_code=400,
            detail=f"Generation disabled for user '{username}'.",
        )

    config = load_config(default_config_path())
    if payload.llm_summary and not config.get("llm_resume_consent"):
        raise HTTPException(status_code=403, detail="LLM resume summary consent not granted")

    projects, root_repo_jsons = collect_projects(payload.output_root)
    agg = aggregate_for_user(
        username,
        projects,
        root_repo_jsons,
        excluded_project_names=payload.excluded_project_names,
    )
    education = payload.education or []

    os.makedirs(payload.resume_dir, exist_ok=True)
    ts_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    ts_fname = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    llm_summary = maybe_generate_resume_summary(agg, use_llm=payload.llm_summary)
    md = render_markdown(agg, generated_ts=ts_iso, llm_summary=llm_summary, education=education)

    out_path = os.path.join(payload.resume_dir, f"resume_{username}_{ts_fname}.md")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(md)

    resume_id = None
    if payload.save_to_db:
        resume_id = save_resume(username=username, resume_path=out_path, metadata=agg, generated_at=ts_iso)

    return {
        "resume_id": resume_id,
        "resume_path": out_path,
        "generated_at": ts_iso,
    }


@app.post("/resume/{resume_id}/edit")
def edit_resume(resume_id: int, payload: ResumeEditRequest):
    # Overwrite the file on disk and update stored metadata.
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, username, resume_path, metadata_json, generated_at FROM resumes WHERE id = ?",
            (resume_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Resume not found")

        resume_path = row["resume_path"]
        os.makedirs(os.path.dirname(resume_path), exist_ok=True)
        with open(resume_path, "w", encoding="utf-8") as fh:
            fh.write(payload.content)

        if payload.metadata is not None:
            conn.execute(
                "UPDATE resumes SET metadata_json = ? WHERE id = ?",
                (json.dumps(payload.metadata), resume_id),
            )
            conn.commit()

        updated = conn.execute(
            "SELECT id, username, resume_path, metadata_json, generated_at FROM resumes WHERE id = ?",
            (resume_id,),
        ).fetchone()

    return _resume_payload(updated)


@app.delete("/resume/{resume_id}")
def delete_resume(resume_id: int):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, resume_path FROM resumes WHERE id = ?",
            (resume_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Resume not found")
        conn.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
        conn.commit()
    resume_path = row["resume_path"]
    if resume_path and os.path.isfile(resume_path):
        try:
            os.remove(resume_path)
        except Exception:
            pass
    return {"deleted": True}


@app.get("/portfolios/all")
def get_all_portfolios():
    return list_all_portfolios()


@app.get("/portfolios")
def get_portfolios(username: str = Query(..., min_length=1)):
    return list_portfolios(username)


@app.get("/portfolios/{portfolio_id}")
def get_portfolio(portfolio_id: int):
    row = _load_portfolio_row_or_404(portfolio_id)
    return _portfolio_row_to_dict(row)


@app.post("/portfolios", status_code=201)
def save_portfolio_endpoint(payload: PortfolioSaveRequest):
    username = payload.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="username is required")
    portfolio_name = payload.portfolio_name.strip()
    if not portfolio_name:
        raise HTTPException(status_code=400, detail="portfolio_name is required")

    portfolio_id = save_portfolio(
        username=username,
        portfolio_name=portfolio_name,
        display_name=payload.display_name,
        included_project_ids=payload.included_project_ids,
        featured_project_ids=payload.featured_project_ids,
    )
    row = _load_portfolio_row_or_404(portfolio_id)
    return _portfolio_row_to_dict(row)


@app.delete("/portfolios/cleanup-temp", status_code=204)
def cleanup_temp_portfolios():
    """Delete any portfolio rows that were created as temporary entries but never saved:
    Temp rows are identified by the prefix "__temp__" flag
    This endpoint is called on PortfolioPage mount to delete orphaned temporary entries left by abrupt app closes
    """
    with get_connection() as conn:
        conn.execute("DELETE FROM portfolios WHERE portfolio_name LIKE '__temp__%'")
        conn.commit()


@app.put("/portfolios/{portfolio_id}")
def update_portfolio_endpoint(portfolio_id: int, payload: PortfolioUpdateRequest):
    portfolio_name = payload.portfolio_name.strip()
    if not portfolio_name:
        raise HTTPException(status_code=400, detail="portfolio_name is required")
    found = update_portfolio(
        portfolio_id,
        portfolio_name=portfolio_name,
        display_name=payload.display_name,
        included_project_ids=payload.included_project_ids,
        featured_project_ids=payload.featured_project_ids,
    )
    if not found:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    row = _load_portfolio_row_or_404(portfolio_id)
    return _portfolio_row_to_dict(row)


@app.delete("/portfolios/{portfolio_id}", status_code=204)
def delete_portfolio_endpoint(portfolio_id: int):
    found = delete_portfolio(portfolio_id)
    if not found:
        raise HTTPException(status_code=404, detail="Portfolio not found")


@app.patch("/portfolios/{portfolio_id}/name")
def rename_portfolio_endpoint(portfolio_id: int, payload: PortfolioRenameRequest):
    portfolio_name = payload.portfolio_name.strip()
    if not portfolio_name:
        raise HTTPException(status_code=400, detail="portfolio_name is required")
    found = rename_portfolio(portfolio_id, portfolio_name)
    if not found:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    row = _load_portfolio_row_or_404(portfolio_id)
    return _portfolio_row_to_dict(row)


@app.post("/portfolio/generate", status_code=201)
def generate_portfolio(payload: PortfolioGenerateRequest):
    username = payload.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="username is required")

    projects, root_repo_jsons = collect_projects(payload.output_root)
    portfolio_projects = aggregate_projects_for_portfolio(username, projects, root_repo_jsons)
    if not portfolio_projects:
        raise HTTPException(status_code=400, detail="No projects found for user")

    ts_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    response = {
        "username": username,
        "generated_at": ts_iso,
        "project_count": len(portfolio_projects),
    }
    if payload.save_to_db:
        os.makedirs(payload.portfolio_dir, exist_ok=True)
        ts_fname = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        portfolio = build_portfolio(username, portfolio_projects, ts_iso, payload.confidence_level)
        out_path = os.path.join(payload.portfolio_dir, f"portfolio_{username}_{ts_fname}.md")
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(portfolio.render_markdown())

        included_project_ids = []
        with get_connection() as conn:
            for project in portfolio_projects:
                project_name = project.get("project_name")
                if not project_name:
                    continue
                row = conn.execute(
                    "SELECT id FROM projects WHERE name = ? ORDER BY id DESC LIMIT 1",
                    (project_name,),
                ).fetchone()
                if row:
                    included_project_ids.append(row["id"])

        portfolio_id = save_portfolio(
            username=username,
            portfolio_name=f"Portfolio for {username}",
            included_project_ids=included_project_ids,
            created_at=ts_iso,
        )
        response["portfolio_id"] = portfolio_id
        response["portfolio_path"] = out_path

    return response


@web_router.get("/{portfolio_id}/timeline")
def get_web_timeline(
    portfolio_id: int,
    granularity: str = Query("month", pattern="^(week|month)$"),
):
    row = _load_portfolio_row_or_404(portfolio_id)
    project_names = _resolve_project_names_for_web(row)

    if not project_names:
        return {
            "portfolio_id": portfolio_id,
            "username": row["username"],
            "granularity": granularity,
            "timeline": [],
        }

    bucket = "%Y-W%W" if granularity == "week" else "%Y-%m"
    placeholders = ",".join("?" for _ in project_names)
    with get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT strftime('{bucket}', s.scanned_at) AS period,
                   sk.name AS skill,
                   COUNT(*) AS occurrences,
                   COUNT(DISTINCT p.id) AS project_count
            FROM scans s
            JOIN projects p ON p.name = s.project
            JOIN project_skills ps ON ps.project_id = p.id
            JOIN skills sk ON sk.id = ps.skill_id
            WHERE p.name IN ({placeholders})
            GROUP BY period, sk.name
            ORDER BY period ASC, sk.name ASC
            """,
            project_names,
        ).fetchall()

    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for item in rows:
        skill_name = item["skill"]
        occ = int(item["occurrences"] or 0)
        project_count = int(item["project_count"] or 0)
        grouped.setdefault(item["period"], []).append(
            {
                "name": skill_name,
                "occurrences": occ,
                "project_count": project_count,
                "expertise_score": round((0.7 * occ) + (0.3 * project_count), 2),
            }
        )

    return {
        "portfolio_id": portfolio_id,
        "username": row["username"],
        "granularity": granularity,
        "timeline": [{"period": period, "skills": skills} for period, skills in grouped.items()],
    }


@web_router.get("/{portfolio_id}/heatmap")
def get_web_heatmap(
    portfolio_id: int,
    granularity: str = Query("day", pattern="^(day|week|month)$"),
    metric: str = Query("files", pattern="^(scans|files)$"),
):
    row = _load_portfolio_row_or_404(portfolio_id)
    project_names = _resolve_project_names_for_web(row)

    if not project_names:
        return {
            "portfolio_id": portfolio_id,
            "granularity": granularity,
            "metric": metric,
            "cells": [],
            "max_value": 0,
        }

    bucket_map = {
        "day": "%Y-%m-%d",
        "week": "%Y-W%W",
        "month": "%Y-%m",
    }
    bucket = bucket_map[granularity]
    placeholders = ",".join("?" for _ in project_names)
    with get_connection() as conn:
        if metric == "scans":
            rows = conn.execute(
                f"""
                SELECT strftime('{bucket}', s.scanned_at) AS period,
                       COUNT(*) AS value
                FROM scans s
                WHERE s.project IN ({placeholders})
                GROUP BY period
                ORDER BY period ASC
                """,
                project_names,
            ).fetchall()
        else:
            rows = conn.execute(
                f"""
                SELECT strftime('{bucket}', s.scanned_at) AS period,
                       COUNT(f.id) AS value
                FROM scans s
                JOIN files f ON f.scan_id = s.id
                WHERE s.project IN ({placeholders})
                GROUP BY period
                ORDER BY period ASC
                """,
                project_names,
            ).fetchall()

    cells = [{"period": item["period"], "value": int(item["value"] or 0)} for item in rows]
    return {
        "portfolio_id": portfolio_id,
        "granularity": granularity,
        "metric": metric,
        "cells": cells,
        "max_value": max((cell["value"] for cell in cells), default=0),
    }


@web_router.get("/{portfolio_id}/heatmap/project")
def get_web_project_heatmap(
    portfolio_id: int,
    project_id: int = Query(..., ge=1),
    granularity: str = Query("week", pattern="^(day|week|month)$"),
    metric: str = Query("contrib_files", pattern="^(scans|files|contrib_files)$"),
    view_scope: str = Query("project", pattern="^(project|user)$"),
):
    row = _load_portfolio_row_or_404(portfolio_id)
    allowed_projects = set(_resolve_project_names_for_web(row))
    with get_connection() as conn:
        project_row = conn.execute(
            "SELECT id, name, git_metrics_json, created_at, project_path FROM projects WHERE id = ?",
            (project_id,),
        ).fetchone()

        if not project_row:
            raise HTTPException(status_code=404, detail="Project not found")

        project_name = project_row["name"]
        if project_name not in allowed_projects:
            raise HTTPException(status_code=403, detail="Project is not available in this portfolio")

        period_expr_map = {
            "day": "date(s.scanned_at)",
            # Normalize each timestamp to the Monday of its week.
            "week": "date(s.scanned_at, '-' || ((CAST(strftime('%w', s.scanned_at) AS INTEGER) + 6) % 7) || ' days')",
            "month": "strftime('%Y-%m', s.scanned_at)",
        }
        period_expr = period_expr_map[granularity]

        git_metrics = None
        if project_row["git_metrics_json"]:
            try:
                git_metrics = json.loads(project_row["git_metrics_json"])
            except Exception:
                git_metrics = None

        range_start = None
        range_end = None
        if isinstance(git_metrics, dict):
            project_start_raw = git_metrics.get("project_start")
            project_end_raw = git_metrics.get("project_end")
            if isinstance(project_start_raw, str) and len(project_start_raw) >= 10:
                range_start = project_start_raw[:10]
            if isinstance(project_end_raw, str) and len(project_end_raw) >= 10:
                range_end = project_end_raw[:10]

        if not range_start or not range_end:
            duration_row = conn.execute(
                """
                SELECT MIN(date(scanned_at)) AS range_start,
                       MAX(date(scanned_at)) AS range_end
                FROM scans
                WHERE project = ?
                """,
                (project_name,),
            ).fetchone()
            if duration_row:
                range_start = range_start or duration_row["range_start"]
                range_end = range_end or duration_row["range_end"]

        project_created = None
        if isinstance(project_row["created_at"], str) and len(project_row["created_at"]) >= 10:
            project_created = project_row["created_at"][:10]

        if project_created and (not range_start or project_created < range_start):
            range_start = project_created

        if range_start and not range_end:
            range_end = datetime.now(timezone.utc).date().isoformat()

        if range_start and range_end and range_end < range_start:
            range_end = range_start

        # For project-wide weekly contribution heatmaps, prefer repository activity from git metrics.
        # This captures the full project history even when there is only one DB scan.
        if metric == "contrib_files" and granularity == "week":
            if view_scope == "project":
                week_cells: List[Dict[str, Any]] = []
                if isinstance(git_metrics, dict):
                    commits_per_week = git_metrics.get("commits_per_week") or {}
                    if isinstance(commits_per_week, dict):
                        for key, value in commits_per_week.items():
                            try:
                                year_str, week_str = key.split("-W", 1)
                                year = int(year_str)
                                week = int(week_str)
                                monday = datetime.fromisocalendar(year, week, 1).date().isoformat()
                                week_cells.append({"period": monday, "value": int(value or 0)})
                            except Exception:
                                continue

                if not week_cells:
                    week_cells = _collect_commit_cells_from_git_log(project_row["project_path"], "week")

                week_cells.sort(key=lambda item: item["period"])
                return {
                    "portfolio_id": portfolio_id,
                    "project_id": project_row["id"],
                    "project_name": project_name,
                    "granularity": granularity,
                    "metric": metric,
                    "view_scope": view_scope,
                    "range_start": range_start,
                    "range_end": range_end,
                    "value_unit": "commits",
                    "cells": week_cells,
                    "max_value": max((cell["value"] for cell in week_cells), default=0),
                }

            # Per-user weekly heatmap should also be commit-based.
            # Prefer precomputed per-author weekly stats when available; otherwise derive from git log.
            user_week_cells: List[Dict[str, Any]] = []
            if isinstance(git_metrics, dict):
                commits_per_week_per_author = git_metrics.get("commits_per_week_per_author") or {}
                if isinstance(commits_per_week_per_author, dict):
                    user_key = canonical_username(row["username"])
                    author_weekly = commits_per_week_per_author.get(user_key) or {}
                    if isinstance(author_weekly, dict):
                        for key, value in author_weekly.items():
                            try:
                                year_str, week_str = key.split("-W", 1)
                                year = int(year_str)
                                week = int(week_str)
                                monday = datetime.fromisocalendar(year, week, 1).date().isoformat()
                                user_week_cells.append({"period": monday, "value": int(value or 0)})
                            except Exception:
                                continue

            if not user_week_cells:
                user_week_cells = _collect_commit_cells_from_git_log(
                    project_row["project_path"],
                    "week",
                    target_username=row["username"],
                )

            user_week_cells.sort(key=lambda item: item["period"])
            return {
                "portfolio_id": portfolio_id,
                "project_id": project_row["id"],
                "project_name": project_name,
                "granularity": granularity,
                "metric": metric,
                "view_scope": view_scope,
                "range_start": range_start,
                "range_end": range_end,
                "value_unit": "commits",
                "cells": user_week_cells,
                "max_value": max((cell["value"] for cell in user_week_cells), default=0),
            }

        if metric == "scans":
            rows = conn.execute(
                f"""
                  SELECT {period_expr} AS period,
                       COUNT(*) AS value
                FROM scans s
                WHERE s.project = ?
                GROUP BY period
                ORDER BY period ASC
                """,
                (project_name,),
            ).fetchall()
        elif metric == "files":
            rows = conn.execute(
                f"""
                  SELECT {period_expr} AS period,
                       COUNT(f.id) AS value
                FROM scans s
                JOIN files f ON f.scan_id = s.id
                WHERE s.project = ?
                GROUP BY period
                ORDER BY period ASC
                """,
                (project_name,),
            ).fetchall()
        else:
            if view_scope == "user":
                # Fallback metric: files linked to the portfolio owner over time.
                rows = conn.execute(
                    f"""
                    SELECT {period_expr} AS period,
                           COUNT(fc.file_id) AS value
                    FROM scans s
                    JOIN files f ON f.scan_id = s.id
                    JOIN file_contributors fc ON fc.file_id = f.id
                    JOIN contributors c ON c.id = fc.contributor_id
                    WHERE s.project = ?
                      AND LOWER(c.name) = LOWER(?)
                    GROUP BY period
                    ORDER BY period ASC
                    """,
                    (project_name, row["username"]),
                ).fetchall()
            else:
                # Fallback metric: all contributor-file links over time.
                rows = conn.execute(
                    f"""
                    SELECT {period_expr} AS period,
                           COUNT(fc.file_id) AS value
                    FROM scans s
                    JOIN files f ON f.scan_id = s.id
                    JOIN file_contributors fc ON fc.file_id = f.id
                    WHERE s.project = ?
                    GROUP BY period
                    ORDER BY period ASC
                    """,
                    (project_name,),
                ).fetchall()

    cells = [{"period": item["period"], "value": int(item["value"] or 0)} for item in rows]
    return {
        "portfolio_id": portfolio_id,
        "project_id": project_row["id"],
        "project_name": project_name,
        "granularity": granularity,
        "metric": metric,
        "view_scope": view_scope,
        "range_start": range_start,
        "range_end": range_end,
        "value_unit": "contrib_files",
        "cells": cells,
        "max_value": max((cell["value"] for cell in cells), default=0),
    }


@web_router.get("/{portfolio_id}/showcase")
def get_web_showcase(
    portfolio_id: int,
    limit: int = Query(3, ge=1, le=3),
):
    row = _load_portfolio_row_or_404(portfolio_id)
    username = row["username"]
    allowed_projects = set(_resolve_project_names_for_web(row))

    ranked = rank_projects_by_importance(mode="contributor", contributor_name=username, limit=None)
    ranked = [item for item in ranked if item.get("project") in allowed_projects]

    featured_project_ids = json.loads(row["featured_project_ids"] or "[]")
    if featured_project_ids:
        with get_connection() as conn:
            placeholders = ",".join("?" for _ in featured_project_ids)
            selected_rows = conn.execute(
                f"SELECT id, name FROM projects WHERE id IN ({placeholders})",
                featured_project_ids,
            ).fetchall()
        selected_names = [item["name"] for item in selected_rows]
        selected_set = set(selected_names)
        ranked_map = {item["project"]: item for item in ranked}
        ordered = [ranked_map[name] for name in selected_names if name in ranked_map]
        for item in ranked:
            if item["project"] not in selected_set:
                ordered.append(item)
        ranked = ordered

    top = ranked[:limit]
    projects_payload = []
    with get_connection() as conn:
        for item in top:
            name = item["project"]
            project_row = conn.execute(
                "SELECT id, name, thumbnail_path FROM projects WHERE name = ?",
                (name,),
            ).fetchone()
            if not project_row:
                continue

            evidence_rows = conn.execute(
                """
                SELECT id, type, description, value, source, url, created_at
                FROM project_evidence
                WHERE project_id = ?
                ORDER BY created_at DESC
                LIMIT 3
                """,
                (project_row["id"],),
            ).fetchall()
            scan_rows = conn.execute(
                """
                SELECT id, scanned_at, notes
                FROM scans
                WHERE project = ?
                ORDER BY scanned_at ASC
                """,
                (name,),
            ).fetchall()
            projects_payload.append(
                {
                    "project_id": project_row["id"],
                    "name": project_row["name"],
                    "thumbnail_path": project_row["thumbnail_path"],
                    "score": round(float(item.get("score") or 0.0), 4),
                    "contrib_files": int(item.get("contrib_files") or 0),
                    "total_files": int(item.get("total_files") or 0),
                    "role": "collaborative" if int(item.get("contributors_count") or 0) > 1 else "individual",
                    "evidence": [dict(row_item) for row_item in evidence_rows],
                    "evolution": [dict(row_item) for row_item in scan_rows],
                }
            )

    return {
        "portfolio_id": portfolio_id,
        "username": username,
        "projects": projects_payload,
    }


@web_router.patch("/{portfolio_id}/customize")
def patch_web_customize(portfolio_id: int, payload: WebPortfolioCustomizeRequest):
    row = _load_portfolio_row_or_404(portfolio_id)
    updates = payload.model_dump(exclude_none=True)

    # Map customize fields to the new schema columns
    with get_connection() as conn:
        if "featured_project_ids" in updates:
            conn.execute(
                "UPDATE portfolios SET featured_project_ids = ? WHERE id = ?",
                (json.dumps(updates["featured_project_ids"]), portfolio_id),
            )
        if "selected_project_ids" in updates:
            conn.execute(
                "UPDATE portfolios SET included_project_ids = ? WHERE id = ?",
                (json.dumps(updates["selected_project_ids"]), portfolio_id),
            )
        conn.commit()

    updated_row = _load_portfolio_row_or_404(portfolio_id)
    return _portfolio_row_to_dict(updated_row)

from inspect_db import inspect_database_json

@app.get("/database/inspect")
def api_inspect_database():
    return inspect_database_json()

@app.delete("/database/clear")
def clear_database():
    from db import get_connection

    conn = get_connection()
    cur = conn.cursor()

    # Disable FK checks
    cur.execute("PRAGMA foreign_keys = OFF;")

    tables = cur.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%';
    """).fetchall()

    for (table,) in tables:
        cur.execute(f"DELETE FROM {table};")

    # reset autoincrement ids
    cur.execute("DELETE FROM sqlite_sequence;")

    conn.commit()

    # Re-enable FK checks
    cur.execute("PRAGMA foreign_keys = ON;")

    conn.close()

    return {"message": "Database cleared successfully"}

app.include_router(web_router)

@app.delete("/projects/{project_id}")
def delete_project(project_id: int):
    result = delete_project_by_id(project_id)

    if not result:
        raise HTTPException(status_code=404, detail="Project not found")

    return {"message": "Project deleted successfully"}

@app.patch("/projects/{project_id}")
def update_project(project_id: int, payload: ProjectEditRequest):
    with get_connection() as conn:
        existing = conn.execute(
            """
            SELECT id, name, custom_name, repo_url, created_at, thumbnail_path,
                   summary_text, summary_model, summary_updated_at
            FROM projects
            WHERE id = ?
            """,
            (project_id,),
        ).fetchone()

        if not existing:
            raise HTTPException(status_code=404, detail="Project not found")

        next_custom_name = payload.custom_name if payload.custom_name is not None else existing["custom_name"]
        next_repo_url = payload.repo_url if payload.repo_url is not None else existing["repo_url"]
        next_thumbnail_path = payload.thumbnail_path if payload.thumbnail_path is not None else existing["thumbnail_path"]

        if payload.summary_text is not None:
            next_summary_text = payload.summary_text.strip()
            next_summary_updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
        else:
            next_summary_text = existing["summary_text"]
            next_summary_updated_at = existing["summary_updated_at"]

        conn.execute(
            """
            UPDATE projects
            SET custom_name = ?, repo_url = ?, thumbnail_path = ?, summary_text = ?, summary_updated_at = ?
            WHERE id = ?
            """,
            (
                next_custom_name,
                next_repo_url,
                next_thumbnail_path,
                next_summary_text,
                next_summary_updated_at,
                project_id,
            ),
        )
        conn.commit()

        updated = conn.execute(
            """
            SELECT id, name, custom_name, repo_url, created_at, thumbnail_path,
                   summary_text, summary_model, summary_updated_at
            FROM projects
            WHERE id = ?
            """,
            (project_id,),
        ).fetchone()

    return {
        "project": {
            "id": updated["id"],
            "name": updated["name"],
            "custom_name": updated["custom_name"],
            "repo_url": updated["repo_url"],
            "created_at": updated["created_at"],
            "thumbnail_path": updated["thumbnail_path"],
        },
        "llm_summary": {
            "text": updated["summary_text"],
            "model": updated["summary_model"],
            "updated_at": updated["summary_updated_at"],
        } if updated["summary_text"] else None,
    }


@app.get("/projects/{project_id}/thumbnail/image")
def get_project_thumbnail_image(project_id: int):
    with get_connection() as conn:
        project = conn.execute(
            "SELECT thumbnail_path FROM projects WHERE id = ?",
            (project_id,),
        ).fetchone()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    thumbnail_path = project["thumbnail_path"]
    if not thumbnail_path:
        raise HTTPException(status_code=404, detail="Project thumbnail not found")
    if not os.path.isfile(thumbnail_path):
        raise HTTPException(status_code=404, detail="Thumbnail file not found")

    media_type = mimetypes.guess_type(thumbnail_path)[0] or "application/octet-stream"
    return FileResponse(thumbnail_path, media_type=media_type)
