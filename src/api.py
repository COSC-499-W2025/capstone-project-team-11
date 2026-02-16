import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Ensure local imports work when running via uvicorn from repo root.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi import APIRouter, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from config import load_config, save_config, config_path as default_config_path
from db import get_connection, save_portfolio, save_resume
from generate_portfolio import (
    aggregate_projects_for_portfolio,
    build_portfolio,
)
from generate_resume import (
    collect_projects,
    aggregate_for_user,
    render_markdown,
    maybe_generate_resume_summary,
)
from project_info_output import gather_project_info, output_project_info
from rank_projects import rank_projects_by_importance
from scan import run_with_saved_settings


app = FastAPI(title="MDA API")
web_router = APIRouter(prefix="/web/portfolio", tags=["web-portfolio"])


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


class ResumeGenerateRequest(BaseModel):
    username: str
    output_root: str = "output"
    resume_dir: str = "resumes"
    allow_bots: bool = False
    save_to_db: bool = False
    llm_summary: bool = False


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


class WebPortfolioCustomizeRequest(BaseModel):
    is_public: Optional[bool] = None
    selected_project_ids: Optional[List[int]] = None
    showcase_project_ids: Optional[List[int]] = None
    hidden_skills: Optional[List[str]] = None


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


def _load_portfolio_row_or_404(portfolio_id: int) -> Any:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, username, portfolio_path, metadata_json, generated_at FROM portfolios WHERE id = ?",
            (portfolio_id,),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return row


def _web_cfg_from_row(row: Any) -> Dict[str, Any]:
    metadata = _parse_metadata(row["metadata_json"])
    cfg = metadata.get("web_dashboard")
    return cfg if isinstance(cfg, dict) else {}


def _ensure_mode_allowed(cfg: Dict[str, Any], mode: str) -> None:
    if mode == "public" and not cfg.get("is_public", True):
        raise HTTPException(status_code=403, detail="Portfolio is currently in private mode")


def _resolve_project_names_for_web(
    username: str,
    cfg: Dict[str, Any],
    mode: str,
) -> List[str]:
    all_projects, root_repo_jsons = collect_projects(None)
    portfolio_projects = aggregate_projects_for_portfolio(username, all_projects, root_repo_jsons)
    default_names = [p.get("project_name") for p in portfolio_projects if p.get("project_name")]

    selected_ids = cfg.get("selected_project_ids") or []
    if not isinstance(selected_ids, list) or not selected_ids:
        return default_names

    with get_connection() as conn:
        placeholders = ",".join("?" for _ in selected_ids)
        rows = conn.execute(
            f"SELECT id, name FROM projects WHERE id IN ({placeholders})",
            selected_ids,
        ).fetchall()
    id_to_name = {row["id"]: row["name"] for row in rows}
    selected_names = [id_to_name[item_id] for item_id in selected_ids if item_id in id_to_name]

    # In public mode, show only explicit selected/published projects.
    if mode == "public":
        return selected_names

    # In private mode, use drafts; fallback to generated set when invalid.
    return selected_names or default_names


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

    config = load_config(default_config_path())
    if payload.llm_summary and not config.get("llm_resume_consent"):
        raise HTTPException(status_code=403, detail="LLM resume summary consent not granted")

    projects, root_repo_jsons = collect_projects(payload.output_root)
    agg = aggregate_for_user(username, projects, root_repo_jsons)

    os.makedirs(payload.resume_dir, exist_ok=True)
    ts_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    ts_fname = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    llm_summary = maybe_generate_resume_summary(agg, use_llm=payload.llm_summary)
    md = render_markdown(agg, generated_ts=ts_iso, llm_summary=llm_summary)

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


@web_router.get("/{portfolio_id}/timeline")
def get_web_timeline(
    portfolio_id: int,
    granularity: str = Query("month", pattern="^(week|month)$"),
    mode: str = Query("public", pattern="^(public|private)$"),
):
    row = _load_portfolio_row_or_404(portfolio_id)
    cfg = _web_cfg_from_row(row)
    _ensure_mode_allowed(cfg, mode)
    project_names = _resolve_project_names_for_web(row["username"], cfg, mode)

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

    hidden_skills = set(cfg.get("hidden_skills") or [])
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for item in rows:
        skill_name = item["skill"]
        if skill_name in hidden_skills:
            continue
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
    mode: str = Query("public", pattern="^(public|private)$"),
):
    row = _load_portfolio_row_or_404(portfolio_id)
    cfg = _web_cfg_from_row(row)
    _ensure_mode_allowed(cfg, mode)
    project_names = _resolve_project_names_for_web(row["username"], cfg, mode)

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


@web_router.get("/{portfolio_id}/showcase")
def get_web_showcase(
    portfolio_id: int,
    limit: int = Query(3, ge=1, le=3),
    mode: str = Query("public", pattern="^(public|private)$"),
):
    row = _load_portfolio_row_or_404(portfolio_id)
    cfg = _web_cfg_from_row(row)
    _ensure_mode_allowed(cfg, mode)
    username = row["username"]
    allowed_projects = set(_resolve_project_names_for_web(username, cfg, mode))

    ranked = rank_projects_by_importance(mode="contributor", contributor_name=username, limit=None)
    ranked = [item for item in ranked if item.get("project") in allowed_projects]

    showcase_project_ids = cfg.get("showcase_project_ids") or []
    if isinstance(showcase_project_ids, list) and showcase_project_ids:
        with get_connection() as conn:
            placeholders = ",".join("?" for _ in showcase_project_ids)
            selected_rows = conn.execute(
                f"SELECT id, name FROM projects WHERE id IN ({placeholders})",
                showcase_project_ids,
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
                SELECT type, description, value, source, url, created_at
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
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, metadata_json FROM portfolios WHERE id = ?",
            (portfolio_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        metadata = _parse_metadata(row["metadata_json"])
        web_cfg = metadata.get("web_dashboard")
        if not isinstance(web_cfg, dict):
            web_cfg = {}

        for key, value in payload.model_dump(exclude_none=True).items():
            web_cfg[key] = value
        web_cfg["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
        metadata["web_dashboard"] = web_cfg

        conn.execute(
            "UPDATE portfolios SET metadata_json = ? WHERE id = ?",
            (json.dumps(metadata), portfolio_id),
        )
        conn.commit()

    return {
        "portfolio_id": portfolio_id,
        "web_config": web_cfg,
        "updated_at": web_cfg["updated_at"],
    }


app.include_router(web_router)
