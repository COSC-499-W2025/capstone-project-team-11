"""
regenerate_resume.py

Handles headless regeneration of an existing resume.
Main_menu.py calls this to overwrite a resume without prompting.
"""

import os
from datetime import datetime

from config import load_config, config_path as default_config_path
from db import save_resume, load_projects_for_generation
from generate_resume import (
    aggregate_for_user as _aggregate_for_user,
    normalize_project_name,
    render_markdown as _render_markdown,
    maybe_generate_resume_summary,
)


def collect_projects(output_root=None):
    projects, _ = load_projects_for_generation()
    return projects


def aggregate_for_user(username, projects):
    return _aggregate_for_user(username, projects, root_repo_jsons={})


def render_markdown(agg, generated_ts=None, llm_summary: str = None):
    md = _render_markdown(agg, generated_ts=generated_ts, llm_summary=llm_summary)
    if "## Evidence & Metrics" in md:
        return md
    insert_block = "\n## Evidence & Metrics\n"
    insert_block += f"\n- Total commits (detected): {agg.get('total_commits', 0)}"
    insert_block += f"\n- Total lines added (detected): {agg.get('total_lines_added', 0)}\n"
    marker = "\n_Generated (UTC):"
    if marker in md:
        before, after = md.split(marker, 1)
        return before.rstrip() + insert_block + "\n\n" + marker.strip("\n") + after
    return md.rstrip() + insert_block


def regenerate_resume(username: str, resume_path: str, output_root: str = "output"):
    """Headless regeneration for an existing resume file"""
    if not username:
        raise ValueError("username is required")
    if not resume_path:
        raise ValueError("resume_path is required")
    # output_root retained for compatibility but ignored

    os.makedirs(os.path.dirname(resume_path), exist_ok=True)

    projects = collect_projects(output_root)
    agg = aggregate_for_user(username, projects)
    ts_iso = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')

    config = load_config(default_config_path())
    use_llm = bool(config.get("llm_resume_consent"))
    llm_summary = maybe_generate_resume_summary(agg, use_llm=use_llm)
    md = render_markdown(agg, generated_ts=ts_iso, llm_summary=llm_summary)

    with open(resume_path, 'w', encoding='utf-8') as fh:
        fh.write(md)

    # Save metadata to DB if table exists
    try:
        save_resume(username=username, resume_path=resume_path, metadata=agg, generated_at=ts_iso)
    except Exception:
        pass  # fail silently if db unavailable

    print(f"Resume successfully regenerated: {resume_path}")
