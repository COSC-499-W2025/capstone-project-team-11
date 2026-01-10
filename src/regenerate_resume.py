import os
from datetime import datetime

# Reuse existing logic from generate_resume.py
from generate_resume import collect_projects, aggregate_for_user, render_markdown


def regenerate_resume(
    *,
    username: str,
    resume_path: str,
    output_root: str = "output",
):
    """
    Regenerate (overwrite) an existing resume file for a user using the latest project data.
    
    This version does NOT touch the database.
    """
    if not username:
        raise ValueError("username is required")

    if not resume_path:
        raise ValueError("resume_path is required")

    if not os.path.isdir(output_root):
        raise FileNotFoundError(f"Output folder not found: {output_root}")

    # Ensure target directory exists
    os.makedirs(os.path.dirname(resume_path), exist_ok=True)

    # Aggregate latest project data
    projects, root_repo_jsons = collect_projects(output_root)
    agg = aggregate_for_user(username, projects, root_repo_jsons)

    # Render markdown with timestamp
    ts_iso = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')
    md = render_markdown(agg, generated_ts=ts_iso)

    # OVERWRITE the existing resume file
    with open(resume_path, "w", encoding="utf-8") as fh:
        fh.write(md)

    print(f"[INFO] Resume regenerated and overwritten at: {resume_path}")
    return resume_path
