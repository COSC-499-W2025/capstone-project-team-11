"""
resume_scan.py

Minimal scanner used ONLY for resume regeneration.
This intentionally avoids config files, menus, prompts,
and legacy scan behaviors.

API-compatible with existing project_info_output.py
"""

import os
import tempfile
import zipfile
import sqlite3
import sys
import time
import threading

from detect_langs import detect_languages_and_frameworks
from detect_skills import detect_skills
from contrib_metrics import analyze_repo
from project_info_output import gather_project_info, output_project_info
from db import init_db, save_scan


# ---------------- Spinner ---------------- #

def _spinner(stop_event, label="Scanning"):
    frames = ["", ".", "..", "..."]
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r{label}{frames[i % len(frames)]} ")
        sys.stdout.flush()
        i += 1
        time.sleep(0.5)
    sys.stdout.write("\r" + " " * (len(label) + 5) + "\r")
    sys.stdout.flush()


# ---------------- Helpers ---------------- #

def _extract_if_zip(path: str):
    """Return (scan_path, temp_ctx) where temp_ctx must be cleaned up."""
    if os.path.isfile(path) and path.lower().endswith(".zip"):
        ctx = tempfile.TemporaryDirectory()
        with zipfile.ZipFile(path) as zf:
            zf.extractall(ctx.name)
        return ctx.name, ctx
    return path, None


# ---------------- Main API ---------------- #

def resume_scan(path: str, save_to_db: bool = True) -> dict:
    """
    Scan a directory or zip for resume usage.

    Returns a dict suitable for resume aggregation.
    """

    if not path or not os.path.exists(path):
        raise ValueError("Invalid scan path")

    scan_root, temp_ctx = _extract_if_zip(path)

    stop_event = threading.Event()
    spinner_thread = threading.Thread(
        target=_spinner, args=(stop_event, "Scanning"), daemon=True
    )
    spinner_thread.start()

    try:
        # --- Lightweight detections for DB bookkeeping only ---
        lang_result = detect_languages_and_frameworks(scan_root) or {}
        languages = lang_result.get("languages", [])

        skill_result = detect_skills(scan_root) or {}
        skills = skill_result.get("skills", [])

        try:
            metrics = analyze_repo(scan_root)
        except Exception:
            metrics = None

        contributors = (
            list(metrics.get("commits_per_author", {}).keys())
            if metrics and metrics.get("commits_per_author")
            else None
        )

        # --- Canonical project info generation ---
        project_info = gather_project_info(scan_root)

        output_project_info(project_info)

        # --- Persist scan (same contract as scan.py) ---
        if save_to_db:
            try:
                save_scan(
                    scan_source=path,
                    files_found=[],
                    project=os.path.basename(scan_root),
                    detected_languages=languages,
                    detected_skills=skills,
                    contributors=contributors,
                    project_created_at=project_info.get("generated_at"),
                )
            except sqlite3.OperationalError:
                init_db()
                save_scan(
                    scan_source=path,
                    files_found=[],
                    project=os.path.basename(scan_root),
                    detected_languages=languages,
                    detected_skills=skills,
                    contributors=contributors,
                )

        return {
            "path": path,
            "languages": project_info.get("languages", []),
            "frameworks": project_info.get("frameworks", []),
            "skills": project_info.get("skills", []),
            "contributors": contributors,
        }

    finally:
        stop_event.set()
        spinner_thread.join()
        if temp_ctx is not None:
            temp_ctx.cleanup()
