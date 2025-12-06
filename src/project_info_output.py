"""
project_info_output.py
---------------------------------
Collects and outputs all key information about a project.

Outputs two files:
  - JSON: structured, machine-readable data for future API/dashboard use
  - TXT : human-readable summary for Milestone #1 evaluation

Expected modules in the same environment:
  - detect_skills.py
  - collab_summary.py
  - contrib_metrics.py
"""

import os
import json
import tempfile
import zipfile
from datetime import datetime

from detect_skills import detect_skills
from collab_summary import identify_contributions, is_git_repo
from contrib_metrics import analyze_repo

OUTPUT_DIR = "output"


def _expand_nested_archives(root_dir: str):
    """
    Recursively extract nested zip archives inside root_dir so that analysis routines
    can inspect their contents like regular directories.
    """
    if not os.path.isdir(root_dir):
        return
    queue = [root_dir]
    visited = set()
    while queue:
        current = queue.pop()
        if current in visited:
            continue
        visited.add(current)
        try:
            entries = os.listdir(current)
        except OSError:
            continue
        for entry in entries:
            path = os.path.join(current, entry)
            if os.path.isdir(path):
                queue.append(path)
                continue
            if not entry.lower().endswith(".zip"):
                continue
            base_name, _ = os.path.splitext(entry)
            target = os.path.join(current, f"{base_name}__unzipped")
            if not os.path.exists(target):
                os.makedirs(target, exist_ok=True)
                try:
                    with zipfile.ZipFile(path) as nested_zf:
                        nested_zf.extractall(target)
                except zipfile.BadZipFile:
                    continue
            if os.path.isdir(target):
                queue.append(target)


def _resolve_extracted_project_root(root_dir: str) -> str:
    """
    When a zip archive is extracted it often produces a single top-level directory.
    Descend into that directory so analyses operate on the actual project files.
    """
    try:
        entries = [entry for entry in os.listdir(root_dir) if entry not in ('.DS_Store', '__MACOSX')]
        if len(entries) == 1:
            candidate = os.path.join(root_dir, entries[0])
            if os.path.isdir(candidate):
                return candidate
    except Exception:
        pass
    return root_dir


def gather_project_info(project_path: str) -> dict:
    """Gather all key project information into a structured dictionary."""
    if not os.path.exists(project_path):
        raise FileNotFoundError(f"Project path '{project_path}' not found")

    print(f"[INFO] Gathering project info for: {project_path}")

    work_path = project_path
    temp_dir = None
    project_name = os.path.basename(os.path.abspath(project_path))
    display_path = os.path.abspath(project_path)

    # Transparently extract zip archives so the downstream detectors can walk real files
    if os.path.isfile(project_path) and project_path.lower().endswith(".zip"):
        temp_dir = tempfile.TemporaryDirectory()
        with zipfile.ZipFile(project_path) as zf:
            zf.extractall(temp_dir.name)
        work_path = _resolve_extracted_project_root(temp_dir.name)
        project_name = os.path.splitext(os.path.basename(project_path))[0] or project_name
    _expand_nested_archives(work_path)

    try:
        # --- Step 1: Detect languages, frameworks, and skills ---
        print("[STEP] Detecting languages, frameworks, and skills...")
        skills_data = detect_skills(work_path)

        # --- Step 2: Analyze contributions (collaborators, commits, etc.) ---
        print("[STEP] Analyzing contributions...")
        contributions = identify_contributions(work_path, output_dir=OUTPUT_DIR)

        # --- Step 3: Git metrics if applicable ---
        git_metrics = {}
        if is_git_repo(work_path):
            try:
                print("[STEP] Extracting detailed Git metrics...")
                git_metrics = analyze_repo(work_path)
            except Exception as e:
                print(f"[WARNING] Could not analyze repo metrics: {e}")

        # --- Step 4: Construct unified project info structure ---
        info = {
            "project_name": project_name,
            "project_path": display_path,
            "detected_type": "coding_project",
            "languages": skills_data.get("languages", []),
            "frameworks": skills_data.get("frameworks", []),
            "skills": skills_data.get("skills", []),
            "contributions": contributions,
            "git_metrics": git_metrics if git_metrics else None,
            "generated_at": datetime.now().isoformat(timespec="seconds")
        }

        # Compute derived metrics for convenience
        if git_metrics and "duration_days" in git_metrics:
            info["duration_days"] = git_metrics["duration_days"]
        if git_metrics and "activity_counts_per_category" in git_metrics:
            info["activity_breakdown"] = git_metrics["activity_counts_per_category"]

        return info
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()


def output_project_info(info: dict, output_dir: str = OUTPUT_DIR):
    """Output project info in both JSON and TXT formats."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # --- JSON output (main structured data) ---
    json_path = os.path.join(output_dir, f"{info['project_name']}_info_{timestamp}.json")
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(info, jf, indent=4, default=str)
    print(f"[INFO] JSON data written to {json_path}")

    # --- TXT output (human-readable summary) ---
    txt_path = os.path.join(output_dir, f"{info['project_name']}_summary_{timestamp}.txt")
    with open(txt_path, "w", encoding="utf-8") as tf:
        tf.write("=============================================\n")
        tf.write("         PROJECT INFORMATION SUMMARY         \n")
        tf.write("=============================================\n\n")
        tf.write(f"Generated at: {info['generated_at']}\n")
        tf.write(f"Project Name: {info['project_name']}\n")
        tf.write(f"Project Path: {info['project_path']}\n\n")

        tf.write("Languages Detected:\n")
        tf.write(", ".join(info.get("languages", [])) or "None found")
        tf.write("\n\nFrameworks Detected:\n")
        tf.write(", ".join(info.get("frameworks", [])) or "None found")
        tf.write("\n\nSkills Detected:\n")
        tf.write(", ".join(info.get("skills", [])) or "None found")

        # Contributions
        tf.write("\n\n=== Contribution Summary ===\n")
        if info.get("contributions"):
            for author, stats in info["contributions"].items():
                commits = stats.get("commits", 0)
                files = stats.get("files", 0)
                tf.write(f"- {author}: {commits} commits, {files} files changed\n")
        else:
            tf.write("No contribution data available.\n")

        # Git metrics
        if info.get("git_metrics"):
            gm = info["git_metrics"]
            tf.write("\n=== Git Metrics ===\n")
            tf.write(f"Project duration: {gm.get('duration_days', 'N/A')} days\n")
            tf.write(f"Total commits: {gm.get('total_commits', 'N/A')}\n")

            if gm.get("activity_counts_per_category"):
                tf.write("Activity by category:\n")
                for cat, count in gm["activity_counts_per_category"].items():
                    tf.write(f"  {cat}: {count}\n")

        tf.write("\n=============================================\n")

    print(f"[INFO] Text summary written to {txt_path}")

    return json_path, txt_path


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Output all key information for a project")
    parser.add_argument("path", help="Path to the project directory")
    args = parser.parse_args()

    project_info = gather_project_info(args.path)
    output_project_info(project_info)


if __name__ == "__main__":
    main()
