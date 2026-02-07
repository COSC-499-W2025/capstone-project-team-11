import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Ensure local imports work when running via uvicorn from repo root.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from config import load_config, save_config, config_path as default_config_path
from db import get_connection, save_portfolio, save_resume
from generate_portfolio import (
    aggregate_projects_for_portfolio,
    build_portfolio,
)
from generate_resume import collect_projects, aggregate_for_user, render_markdown
from project_info_output import gather_project_info, output_project_info
from scan import run_with_saved_settings


app = FastAPI(title="MDA API")


class PrivacyConsentRequest(BaseModel):
    data_consent: bool
    llm_summary_consent: Optional[bool] = None


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


class ResumeGenerateRequest(BaseModel):
    username: str
    output_root: str = "output"
    resume_dir: str = "resumes"
    allow_bots: bool = False
    save_to_db: bool = False


class ResumeEditRequest(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None


class PortfolioGenerateRequest(BaseModel):
    username: str
    output_root: str = "output"
    portfolio_dir: str = "portfolios"
    confidence_level: str = Field("high", pattern="^(high|medium|low)$")
    save_to_db: bool = False


class PortfolioEditRequest(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None


def _parse_metadata(metadata_json: Optional[str]) -> Dict[str, Any]:
    # Keep metadata parsing resilient to malformed JSON stored in DB.
    if not metadata_json:
        return {}
    try:
        return json.loads(metadata_json)
    except Exception:
        return {}


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


@app.post("/privacy-consent")
def update_privacy_consent(payload: PrivacyConsentRequest):
    # Persist consent in the user's config to mirror CLI behavior.
    current = load_config(default_config_path())
    llm_value = payload.llm_summary_consent
    if llm_value is None:
        llm_value = current.get("llm_summary_consent", False)
    save_config(
        {"data_consent": payload.data_consent, "llm_summary_consent": llm_value},
        path=default_config_path(),
    )
    return {
        "data_consent": payload.data_consent,
        "llm_summary_consent": llm_value,
        "config_path": default_config_path(),
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


@app.get("/projects")
def list_projects():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT p.id, p.name, p.repo_url, p.created_at, p.thumbnail_path,
                   (SELECT MAX(scanned_at) FROM scans s WHERE s.project = p.name) AS latest_scan_at
            FROM projects p
            ORDER BY p.id
            """
        ).fetchall()
    return [dict(row) for row in rows]


@app.get("/projects/{project_id}")
def get_project(project_id: int):
    # Aggregate enriched project data from related tables.
    with get_connection() as conn:
        project = conn.execute(
            "SELECT id, name, repo_url, created_at, thumbnail_path FROM projects WHERE id = ?",
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
            # Build dynamic IN clauses only when scans exist.
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
            SELECT type, description, value, source, url, added_by_user, created_at
            FROM project_evidence
            WHERE project_id = ?
            ORDER BY created_at DESC
            """,
            (project_id,),
        ).fetchall()

    return {
        "project": dict(project),
        "skills": [row["name"] for row in skill_rows],
        "languages": languages,
        "contributors": contributors,
        "scans": [dict(row) for row in scans],
        "files_summary": files_summary,
        "evidence": [dict(row) for row in evidence_rows],
    }


@app.get("/skills")
def list_skills():
    with get_connection() as conn:
        rows = conn.execute("SELECT name FROM skills ORDER BY name").fetchall()
    return [row["name"] for row in rows]


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

    projects, root_repo_jsons = collect_projects(payload.output_root)
    agg = aggregate_for_user(username, projects, root_repo_jsons)

    os.makedirs(payload.resume_dir, exist_ok=True)
    ts_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    ts_fname = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    md = render_markdown(agg, generated_ts=ts_iso)

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


@app.get("/portfolio/{portfolio_id}")
def get_portfolio(portfolio_id: int):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, username, portfolio_path, metadata_json, generated_at FROM portfolios WHERE id = ?",
            (portfolio_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Portfolio not found")
    return _portfolio_payload(row)


@app.post("/portfolio/generate", status_code=201)
def generate_portfolio(payload: PortfolioGenerateRequest):
    # Reuse the portfolio generator logic used by the CLI.
    # output_root retained for backward compatibility but ignored (DB is used)

    username = payload.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="username is required")

    projects, root_repo_jsons = collect_projects(payload.output_root)
    portfolio_projects = aggregate_projects_for_portfolio(username, projects, root_repo_jsons)
    if not portfolio_projects:
        raise HTTPException(status_code=400, detail="No projects found for user")

    os.makedirs(payload.portfolio_dir, exist_ok=True)
    ts_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    ts_fname = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    portfolio = build_portfolio(username, portfolio_projects, ts_iso, payload.confidence_level)

    md = portfolio.render_markdown()
    out_path = os.path.join(payload.portfolio_dir, f"portfolio_{username}_{ts_fname}.md")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(md)

    portfolio_id = None
    if payload.save_to_db:
        metadata = {
            "username": username,
            "project_count": len(portfolio_projects),
            "sections": list(portfolio.sections.keys()),
            "confidence_level": payload.confidence_level,
            "projects": [
                {
                    "name": p.get("project_name"),
                    "path": p.get("path"),
                    "user_commits": p.get("user_commits", 0),
                }
                for p in portfolio_projects
            ],
        }
        portfolio_id = save_portfolio(username, out_path, metadata, ts_iso)

    return {
        "portfolio_id": portfolio_id,
        "portfolio_path": out_path,
        "generated_at": ts_iso,
    }


@app.post("/portfolio/{portfolio_id}/edit")
def edit_portfolio(portfolio_id: int, payload: PortfolioEditRequest):
    # Overwrite the file on disk and update stored metadata.
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, username, portfolio_path, metadata_json, generated_at FROM portfolios WHERE id = ?",
            (portfolio_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        portfolio_path = row["portfolio_path"]
        os.makedirs(os.path.dirname(portfolio_path), exist_ok=True)
        with open(portfolio_path, "w", encoding="utf-8") as fh:
            fh.write(payload.content)

        if payload.metadata is not None:
            conn.execute(
                "UPDATE portfolios SET metadata_json = ? WHERE id = ?",
                (json.dumps(payload.metadata), portfolio_id),
            )
            conn.commit()

        updated = conn.execute(
            "SELECT id, username, portfolio_path, metadata_json, generated_at FROM portfolios WHERE id = ?",
            (portfolio_id,),
        ).fetchone()

    return _portfolio_payload(updated)
