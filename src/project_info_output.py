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


def _find_all_git_roots(path: str) -> list:
    """Find all git repository roots under the given path."""
    roots = []
    if not os.path.isdir(path):
        return roots
    
    for root, dirs, files in os.walk(path):
        # Don't descend into .git directories
        dirs[:] = [d for d in dirs if d != '.git']
        
        if '.git' in dirs:
            roots.append(root)
            # Don't descend into subdirectories of a git repo to avoid nested repos
            dirs[:] = []
    
    return roots


def _find_candidate_project_roots(base_path: str) -> list:
    """Return immediate subdirectories under base_path that contain at least one file."""
    candidates = []
    if not base_path or not os.path.isdir(base_path):
        return candidates
    try:
        for entry in os.scandir(base_path):
            if not entry.is_dir():
                continue
            # Skip macOS junk
            if entry.name in ('.DS_Store', '__MACOSX'):
                continue
            # Check if the subtree has any files
            has_files = False
            for _, _, files in os.walk(entry.path):
                if files:
                    has_files = True
                    break
            if has_files:
                candidates.append(entry.path)
    except Exception:
        return candidates
    return candidates


def gather_project_info(project_path: str) -> dict:
    """Gather all key project information into a structured dictionary.
    
    If multiple projects are detected, separates skills, languages, and frameworks per-project.
    """
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
        # --- Step 1: Analyze contributions (collaborators, commits, etc.) ---
        print("[STEP] Analyzing contributions...")
        contributions = identify_contributions(work_path, output_dir=OUTPUT_DIR)

        # --- Step 2: Check if this is a multi-project structure based on contributions ---
        is_multi_project = False
        multi_repos = []
        if isinstance(contributions, dict) and contributions.get("type") == "multi_git":
            multi_repos = contributions.get("repos", [])
            is_multi_project = len(multi_repos) > 1
        
        # --- Step 3: Handle single vs multiple projects ---
        if is_multi_project:
            # Multiple projects detected - gather info per project
            print(f"[INFO] Found {len(multi_repos)} projects, gathering skills per project...")
            projects = []
            
            # Try to match repo_roots to subdirectories in work_path and detect skills for each
            for i, repo_info in enumerate(multi_repos, 1):
                repo_root = repo_info.get("repo_root", "")
                repo_name = os.path.basename(repo_root) if repo_root else f"Project-{i}"
                
                print(f"[STEP] Processing project {i}/{len(multi_repos)}: {repo_name}")
                
                try:
                    # Try to find the repo subdirectory within work_path
                    repo_subdir = None
                    
                    # First, try direct match if path still exists
                    if repo_root and os.path.exists(repo_root) and os.path.isdir(repo_root):
                        repo_subdir = repo_root
                    else:
                        # Search for matching subdirectory in work_path by name
                        target_name = os.path.basename(repo_root)
                        for root, dirs, files in os.walk(work_path):
                            if os.path.basename(root) == target_name and '.git' in dirs:
                                repo_subdir = root
                                break
                            # Also try without .git check
                            if os.path.basename(root) == target_name and any(files):
                                repo_subdir = root
                    
                    project_skills_data = {}
                    project_git_metrics = {}
                    
                    if repo_subdir:
                        print(f"[INFO] Found project at: {repo_subdir}")
                        try:
                            project_skills_data = detect_skills(repo_subdir)
                            if is_git_repo(repo_subdir):
                                try:
                                    project_git_metrics = analyze_repo(repo_subdir)
                                except Exception as e:
                                    print(f"[WARNING] Could not analyze repo metrics: {e}")
                        except Exception as e:
                            print(f"[WARNING] Could not detect skills: {e}")
                    else:
                        print(f"[WARNING] Could not locate project directory for {repo_name}")
                    
                    project_info = {
                        "project_name": repo_name,
                        "project_path": repo_root,
                        "languages": project_skills_data.get("languages", []),
                        "frameworks": project_skills_data.get("frameworks", []),
                        "skills": project_skills_data.get("skills", []),
                        "high_confidence_languages": project_skills_data.get("high_confidence_languages", []),
                        "medium_confidence_languages": project_skills_data.get("medium_confidence_languages", []),
                        "low_confidence_languages": project_skills_data.get("low_confidence_languages", []),
                        "high_confidence_frameworks": project_skills_data.get("high_confidence_frameworks", []),
                        "medium_confidence_frameworks": project_skills_data.get("medium_confidence_frameworks", []),
                        "low_confidence_frameworks": project_skills_data.get("low_confidence_frameworks", []),
                        "git_metrics": project_git_metrics if project_git_metrics else None,
                        "contributions": repo_info.get("contributions", {}),
                    }
                    
                    projects.append(project_info)
                except Exception as e:
                    print(f"[WARNING] Failed to gather info for project {repo_name}: {e}")
            
            # Construct multi-project info structure
            info = {
                "project_name": project_name,
                "project_path": display_path,
                "detected_type": "multi_coding_project",
                "num_projects": len(projects),
                # Per-project details only
                "projects": projects,
                # Contributions analysis
                "contributions": contributions,
                "generated_at": datetime.now().isoformat(timespec="seconds")
            }
        else:
            # Single project - gather info as before
            print("[STEP] Single project detected, gathering full info...")
            
            # Detect languages, frameworks, and skills
            print("[STEP]  languages, frameworks, and skills...")
            skills_data = detect_skills(work_path)

            # Git metrics if applicable
            git_metrics = {}
            if is_git_repo(work_path):
                try:
                    print("[STEP] Extracting detailed Git metrics...")
                    git_metrics = analyze_repo(work_path)
                except Exception as e:
                    print(f"[WARNING] Could not analyze repo metrics: {e}")

            # Construct single project info structure
            info = {
                "project_name": project_name,
                "project_path": display_path,
                "detected_type": "coding_project",
                # Unfiltered lists
                "languages": skills_data.get("languages", []),
                "frameworks": skills_data.get("frameworks", []),
                "skills": skills_data.get("skills", []),
                # Confidence-categorized lists
                "high_confidence_languages": skills_data.get("high_confidence_languages", []),
                "medium_confidence_languages": skills_data.get("medium_confidence_languages", []),
                "low_confidence_languages": skills_data.get("low_confidence_languages", []),
                "high_confidence_frameworks": skills_data.get("high_confidence_frameworks", []),
                "medium_confidence_frameworks": skills_data.get("medium_confidence_frameworks", []),
                "low_confidence_frameworks": skills_data.get("low_confidence_frameworks", []),
                # Additional metadata
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
    """Output project info in both JSON and TXT formats.
    
    Returns a tuple of (json_paths, txt_paths), where each is a list of file paths.
    For multi-project outputs: one entry per project. For single project: one entry.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    json_paths = []
    txt_paths = []
    
    # Handle multi-project output - create separate files for each project
    if info.get("detected_type") == "multi_coding_project" and info.get("projects"):
        print("\n[INFO] Generating separate files for each project...")
        
        for project in info["projects"]:
            project_name = project["project_name"]
            
            # Create separate JSON for this project
            json_path = os.path.join(output_dir, f"{project_name}_info_{timestamp}.json")
            with open(json_path, "w", encoding="utf-8") as jf:
                json.dump(project, jf, indent=4, default=str)
            print(f"[INFO] JSON data written to {json_path}")
            json_paths.append(json_path)
            
            # Create separate TXT for this project
            txt_path = os.path.join(output_dir, f"{project_name}_summary_{timestamp}.txt")
            with open(txt_path, "w", encoding="utf-8") as tf:
                tf.write("=============================================\n")
                tf.write("         PROJECT INFORMATION SUMMARY         \n")
                tf.write("=============================================\n\n")
                tf.write(f"Generated at: {info['generated_at']}\n")
                tf.write(f"Project Name: {project_name}\n")
                tf.write(f"Project Path: {project['project_path']}\n\n")
                
                tf.write("Languages Detected:\n")
                tf.write(", ".join(project.get("languages", [])) or "None found")
                tf.write("\n\nFrameworks Detected:\n")
                tf.write(", ".join(project.get("frameworks", [])) or "None found")
                tf.write("\n\nSkills Detected:\n")
                tf.write(", ".join(project.get("skills", [])) or "None found")
                
                # Git metrics if available
                if project.get("git_metrics"):
                    gm = project["git_metrics"]
                    tf.write("\n\n=== Git Metrics ===\n")
                    tf.write(f"Project duration: {gm.get('duration_days', 'N/A')} days\n")
                    tf.write(f"Total commits: {gm.get('total_commits', 'N/A')}\n")

                    if gm.get("activity_counts_per_category"):
                        tf.write("Activity by category:\n")
                        for cat, count in gm["activity_counts_per_category"].items():
                            tf.write(f"  {cat}: {count}\n")
                
                # Contributions for this project
                if project.get("contributions"):
                    tf.write("\n=== Contribution Summary ===\n")
                    contribs = project.get("contributions", {})
                    if contribs and isinstance(contribs, dict):
                        for author, stats in contribs.items():
                            if isinstance(stats, dict):
                                commits = stats.get("commits", 0)
                                files = stats.get("files", [])
                                file_count = len(files) if isinstance(files, list) else 0
                                tf.write(f"- {author}: {commits} commits, {file_count} files changed\n")
                    else:
                        tf.write("No contribution data available.\n")
                
                tf.write("\n=============================================\n")
            
            print(f"[INFO] Text summary written to {txt_path}")
            txt_paths.append(txt_path)
    else:
        # Single project output - create one JSON and one TXT
        json_path = os.path.join(output_dir, f"{info['project_name']}_info_{timestamp}.json")
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump(info, jf, indent=4, default=str)
        print(f"[INFO] JSON data written to {json_path}")
        json_paths.append(json_path)

        # --- TXT output (human-readable summary) ---
        txt_path = os.path.join(output_dir, f"{info['project_name']}_summary_{timestamp}.txt")
        with open(txt_path, "w", encoding="utf-8") as tf:
            tf.write("=============================================\n")
            tf.write("         PROJECT INFORMATION SUMMARY         \n")
            tf.write("=============================================\n\n")
            tf.write(f"Generated at: {info['generated_at']}\n")
            tf.write(f"Project Name: {info['project_name']}\n")
            tf.write(f"Project Path: {info['project_path']}\n\n")

            # Single project output
            tf.write("Languages Detected:\n")
            tf.write(", ".join(info.get("languages", [])) or "None found")
            tf.write("\n\nFrameworks Detected:\n")
            tf.write(", ".join(info.get("frameworks", [])) or "None found")
            tf.write("\n\nSkills Detected:\n")
            tf.write(", ".join(info.get("skills", [])) or "None found")

            # Contributions
            tf.write("\n\n=== Contribution Summary ===\n")
            if info.get("contributions"):
                contrib_data = info["contributions"]
                
                # Handle multi-repo contributions structure
                if isinstance(contrib_data, dict) and contrib_data.get("type") == "multi_git":
                    repos = contrib_data.get("repos", [])
                    for repo_data in repos:
                        repo_root = repo_data.get("repo_root", "Unknown")
                        tf.write(f"\nRepository: {os.path.basename(repo_root)}\n")
                        tf.write("-" * 40 + "\n")
                        
                        contribs = repo_data.get("contributions", {})
                        if contribs and isinstance(contribs, dict):
                            for author, stats in contribs.items():
                                if isinstance(stats, dict):
                                    commits = stats.get("commits", 0)
                                    files = stats.get("files", [])
                                    file_count = len(files) if isinstance(files, list) else 0
                                    tf.write(f"- {author}: {commits} commits, {file_count} files changed\n")
                        else:
                            tf.write("No contribution data available.\n")
                else:
                    # Handle single repo contributions
                    if isinstance(contrib_data, dict) and "contributions" in contrib_data:
                        contribs = contrib_data.get("contributions", {})
                    else:
                        contribs = contrib_data
                    
                    if contribs and isinstance(contribs, dict):
                        for author, stats in contribs.items():
                            if isinstance(stats, dict):
                                commits = stats.get("commits", 0)
                                files = stats.get("files", [])
                                file_count = len(files) if isinstance(files, list) else 0
                                tf.write(f"- {author}: {commits} commits, {file_count} files changed\n")
                    else:
                        tf.write("No contribution data available.\n")
            else:
                tf.write("No contribution data available.\n")

            # Git metrics for single projects
            if info.get("git_metrics") and info.get("detected_type") != "multi_coding_project":
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
        txt_paths.append(txt_path)

    return (json_paths, txt_paths)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Output all key information for a project")
    parser.add_argument("path", help="Path to the project directory")
    args = parser.parse_args()

    project_info = gather_project_info(args.path)
    output_project_info(project_info)


if __name__ == "__main__":
    main()
