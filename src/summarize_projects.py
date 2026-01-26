"""
summarize_projects.py
---------------------------------
Generate detailed summaries for top-ranked projects by contributor.

This module provides functionality to:
- Retrieve project paths from the database
- Generate summaries for a contributor's top-ranked projects
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Optional, Set
from datetime import datetime
from collections import defaultdict


src_dir = os.path.abspath(os.path.dirname(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from db import get_connection
from rank_projects import rank_projects_by_contributor


def get_project_path(project_name: str) -> Optional[str]:
    """Get the project root path from the database for a given project name.
    
    Attempts to infer the project root by:
    1. Getting a file path from the most recent scan for this project
    2. Extracting the project root directory from the file path
    
    Returns None if the project path cannot be determined.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Get a file path from the most recent scan for this project
        cur.execute(
            "SELECT f.file_path FROM files f "
            "JOIN scans s ON f.scan_id = s.id "
            "WHERE s.project = ? "
            "ORDER BY s.scanned_at DESC, f.id ASC "
            "LIMIT 1",
            (project_name,)
        )
        row = cur.fetchone()
        if not row:
            return None
        
        file_path = row[0]
        if not file_path:
            return None

        # Resolve project root directly from file path if project name is in the path
        path_components = os.path.abspath(file_path).split(os.sep)
        if project_name in path_components:
            project_root_index = path_components.index(project_name)
            project_root = os.sep.join(path_components[:project_root_index + 1])
            if os.path.exists(project_root) and os.path.basename(project_root) == project_name:
                return project_root

        # Handle zip file paths (format: "/path/to.zip:inner/path/file.py")
        zip_sep_index = file_path.lower().find(".zip:")
        if zip_sep_index != -1:
            # Extract the zip path portion (including the .zip file itself)
            zip_part = file_path[:zip_sep_index + len(".zip")]
            # Try to find the project root by going up from the zip location
            # For zip files, we'll use the directory containing the zip
            potential_root = os.path.dirname(zip_part)
            if os.path.exists(potential_root):
                return potential_root
            return None
        
        # For regular file paths, find the project root
        # Start from the file path and go up until we find a directory that looks like a project root
        current = os.path.abspath(file_path)
        
        # If it's a file, start from its directory
        if os.path.isfile(current):
            current = os.path.dirname(current)
        elif not os.path.isdir(current):
            # If the path doesn't exist, try to infer from the path structure
            # Assume the project root is the directory containing this file
            current = os.path.dirname(current)
        
        # Try to find a reasonable project root by going up directories
        # Stop at common project root indicators or after a reasonable depth
        max_depth = 10
        depth = 0
        while depth < max_depth:
            if os.path.exists(current) and os.path.isdir(current):
                # Check if this looks like a project root (has common project files)
                common_files = ['.git', 'package.json', 'requirements.txt', 'pom.xml', 
                              'Cargo.toml', 'setup.py', 'Makefile', 'README.md']
                if any(os.path.exists(os.path.join(current, f)) for f in common_files):
                    return current
                # Also check if the directory name matches the project name
                if os.path.basename(current) == project_name:
                    return current
            
            parent = os.path.dirname(current)
            if parent == current:  # Reached filesystem root
                break
            current = parent
            depth += 1
        
        # If we couldn't find a clear project root, return None
        return None
    except Exception as e:
        print(f"[WARNING] Could not determine path for project '{project_name}': {e}")
        return None
    finally:
        # Do not close the connection here for the same reason as in rank_projects.py
        pass


def find_unzipped_project_root(base_path: str, project_name: str) -> Optional[str]:
    """Search for directories matching '<base_path>/<project_name>__unzipped/<project_name>'."""
    if not base_path or not os.path.exists(base_path):
        return None
    for root, dirs, _ in os.walk(base_path):
        for dir_name in dirs:
            if dir_name == f"{project_name}__unzipped":
                potential_path = os.path.join(root, dir_name, project_name)
                if os.path.exists(potential_path):
                    return potential_path
    return None


def generate_combined_summary(
    contributor_name: str,
    ranked_projects: List[Dict],
    project_data_list: List[Dict],
    output_dir: str = "output"
) -> str:
    """Generate a combined summary file for all top-ranked projects.
    
    Args:
        contributor_name: Name of the contributor
        ranked_projects: List of ranked project dicts from rank_projects_by_contributor
        project_data_list: List of dicts with keys: project, project_path, project_info (dict from gather_project_info)
        output_dir: Directory where the combined summary should be saved
    
    Returns:
        Path to the generated combined summary file
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_path = os.path.join(output_dir, f"{contributor_name}_top_projects_summary_{timestamp}.txt")
    
    # Aggregate data from all projects
    all_languages: Set[str] = set()
    all_frameworks: Set[str] = set()
    all_skills: Set[str] = set()
    total_contrib_files = 0
    total_files = 0
    project_details = []
    
    # Create a mapping of project name to ranking info
    ranking_map = {p["project"]: p for p in ranked_projects}
    
    # Process project data directly (no JSON file loading needed)
    for result in project_data_list:
        if result.get("error") or not result.get("project_info"):
            continue
        
        project_name = result["project"]
        project_data = result["project_info"]
        
        # Aggregate languages, frameworks, skills
        all_languages.update(project_data.get("languages", []))
        all_frameworks.update(project_data.get("frameworks", []))
        all_skills.update(project_data.get("skills", []))
        
        # Get ranking info
        ranking_info = ranking_map.get(project_name, {})
        contrib_files = ranking_info.get("contrib_files", 0)
        total_proj_files = ranking_info.get("total_files", 0)
        score = ranking_info.get("score", 0.0)
        
        total_contrib_files += contrib_files
        total_files += total_proj_files
        
        # Get contribution info for this contributor
        contributions = project_data.get("contributions", {})
        contrib_info = contributions.get(contributor_name, {})
        
        # Compute contributor-specific commit count
        commits = 0
        git_metrics = project_data.get("git_metrics", {})
        commits_per_author = git_metrics.get("commits_per_author", {})
        if contributor_name in commits_per_author:
            commits = commits_per_author[contributor_name]
        elif "commits" in contrib_info:
            commits = contrib_info["commits"]
        
        project_details.append({
            "name": project_name,
            "path": result.get("project_path", "N/A"),
            "languages": project_data.get("languages", []),
            "frameworks": project_data.get("frameworks", []),
            "skills": project_data.get("skills", []),
            "contrib_files": contrib_files,
            "total_files": total_proj_files,
            "score": score,
            "commits": commits,
            "git_metrics": git_metrics
        })
    
    # Write combined summary
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write(f"  TOP-RANKED PROJECTS FOR {contributor_name.upper()}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Generated at: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write(f"Total Projects: {len(project_details)}\n\n")
        
        # Overall Statistics
        f.write("=" * 60 + "\n")
        f.write("OVERALL STATISTICS\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total Files Contributed To: {total_contrib_files}\n")
        f.write(f"Total Files Across Projects: {total_files}\n")
        f.write(f"Overall Contribution Score: {total_contrib_files / total_files if total_files > 0 else 0:.2%}\n\n")
        
        # Overall Skill Coverage
        f.write("=" * 60 + "\n")
        f.write("OVERALL SKILL COVERAGE\n")
        f.write("=" * 60 + "\n")
        if all_skills:
            f.write(", ".join(sorted(all_skills)) + "\n\n")
        else:
            f.write("No skills detected.\n\n")
        
        # Total Languages
        f.write("=" * 60 + "\n")
        f.write("TOTAL LANGUAGES ACROSS ALL PROJECTS\n")
        f.write("=" * 60 + "\n")
        if all_languages:
            f.write(", ".join(sorted(all_languages)) + "\n\n")
        else:
            f.write("No languages detected.\n\n")
        
        # Frameworks
        if all_frameworks:
            f.write("=" * 60 + "\n")
            f.write("FRAMEWORKS DETECTED\n")
            f.write("=" * 60 + "\n")
            f.write(", ".join(sorted(all_frameworks)) + "\n\n")
        
        # Contribution Breakdown
        f.write("=" * 60 + "\n")
        f.write("CONTRIBUTION BREAKDOWN ACROSS ALL PROJECTS\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"{'Project':<30} {'Contrib Files':<15} {'Total Files':<15} {'Score':<10} {'Commits':<10}\n")
        f.write("-" * 80 + "\n")
        for proj in sorted(project_details, key=lambda x: x["score"], reverse=True):
            f.write(f"{proj['name']:<30} {proj['contrib_files']:<15} {proj['total_files']:<15} "
                   f"{proj['score']:<10.2f} {proj['commits']:<10}\n")
        f.write("\n")
        
        # Ranking Weights
        f.write("=" * 60 + "\n")
        f.write("RANKING WEIGHTS\n")
        f.write("=" * 60 + "\n")
        f.write("Projects are ranked by:\n")
        f.write("  1. Contribution Score (contrib_files / total_files)\n")
        f.write("  2. Number of Files Contributed (tie-breaker)\n")
        f.write("  3. Project Name (alphabetical, final tie-breaker)\n\n")
        f.write("Ranking Details:\n")
        f.write("-" * 60 + "\n")
        for i, proj in enumerate(sorted(project_details, key=lambda x: (-x["score"], -x["contrib_files"], x["name"])), 1):
            f.write(f"{i}. {proj['name']}\n")
            f.write(f"   Score: {proj['score']:.2%} ({proj['contrib_files']}/{proj['total_files']} files)\n")
            f.write(f"   Commits: {proj['commits']}\n")
            f.write(f"   Path: {proj['path']}\n\n")
        
        # Individual Project Sections
        f.write("=" * 60 + "\n")
        f.write("INDIVIDUAL PROJECT DETAILS\n")
        f.write("=" * 60 + "\n\n")
        
        for i, proj in enumerate(sorted(project_details, key=lambda x: (-x["score"], -x["contrib_files"], x["name"])), 1):
            f.write(f"{'=' * 60}\n")
            f.write(f"PROJECT {i}: {proj['name']}\n")
            f.write(f"{'=' * 60}\n\n")
            f.write(f"Ranking Score: {proj['score']:.2%} ({proj['contrib_files']}/{proj['total_files']} files)\n")
            f.write(f"Commits: {proj['commits']}\n")
            f.write(f"Path: {proj['path']}\n\n")
            
            if proj['languages']:
                f.write(f"Languages: {', '.join(proj['languages'])}\n")
            if proj['frameworks']:
                f.write(f"Frameworks: {', '.join(proj['frameworks'])}\n")
            if proj['skills']:
                f.write(f"Skills: {', '.join(proj['skills'])}\n")
            
            if proj.get('git_metrics'):
                gm = proj['git_metrics']
                f.write(f"\nGit Metrics:\n")
                if gm.get('duration_days'):
                    f.write(f"  Duration: {gm['duration_days']} days\n")
                if gm.get('total_commits'):
                    f.write(f"  Total Commits: {gm['total_commits']}\n")
            
            f.write("\n")
        
        f.write("=" * 60 + "\n")
    
    print(f"[SUCCESS] Combined summary generated: {summary_path}")
    return summary_path


def summarize_top_ranked_projects(contributor_name: str, limit: Optional[int] = None) -> List[Dict]:
    """Generate a combined summary for a contributor's top-ranked projects.
    
    Args:
        contributor_name: Name of the contributor to rank projects for
        limit: Maximum number of top projects to summarize (None for all)
    
    Returns:
        List of dicts with keys: project, project_path, project_info (dict from gather_project_info),
        and error (if summary generation failed).
    """
    # Try to import project_info_output function
    try:
        from project_info_output import gather_project_info
    except ImportError:
        try:
            from .project_info_output import gather_project_info
        except ImportError:
            print("[ERROR] Could not import project_info_output module. Summaries cannot be generated.")
            return []
    
    # Get top-ranked projects for the contributor (reuse existing ranking logic)
    top_projects = rank_projects_by_contributor(contributor_name, limit=limit)
    
    if not top_projects:
        print(f"No projects found for contributor '{contributor_name}'.")
        return []
    
    results = []
    print(f"\nAnalyzing top {len(top_projects)} project(s) for '{contributor_name}'...\n")
    
    for i, project_info in enumerate(top_projects, 1):
        project_name = project_info["project"]
        print(f"[{i}/{len(top_projects)}] Processing: {project_name}")
        
        # Get the project path
        project_path = get_project_path(project_name)
        
        # Attempt to resolve extracted zip project root
        resolved_path = find_unzipped_project_root(project_path, project_name)
        if resolved_path:
            project_path = resolved_path
        
        if not project_path or not os.path.exists(project_path):
            print(f"  [SKIP] Could not find project path for '{project_name}'")
            results.append({
                "project": project_name,
                "project_path": None,
                "project_info": None,
                "error": "Project path not found"
            })
            continue
        
        print(f"  [INFO] Project path: {project_path}")
        
        # Gather project info (but don't output individual files)
        try:
            info = gather_project_info(project_path)
            
            # Enforce single-project invariant
            if info.get("projects_detected", 1) > 1:
                raise ValueError(
                    f"Refusing to summarize multi-project directory: {project_path}"
                )
            
            print(f"  [SUCCESS] Project info gathered\n")
            results.append({
                "project": project_name,
                "project_path": project_path,
                "project_info": info,
                "error": None
            })
        except Exception as e:
            print(f"  [ERROR] Failed to gather project info: {e}\n")
            results.append({
                "project": project_name,
                "project_path": project_path,
                "project_info": None,
                "error": str(e)
            })
    
    # Generate combined summary
    successful_results = [r for r in results if not r.get("error") and r.get("project_info")]
    if successful_results:
        print(f"\nGenerating combined summary for {len(successful_results)} project(s)...")
        try:
            combined_path = generate_combined_summary(
                contributor_name=contributor_name,
                ranked_projects=top_projects,
                project_data_list=successful_results,
                output_dir="output"
            )
            print(f"[SUCCESS] Combined summary: {combined_path}\n")
        except Exception as e:
            print(f"[WARNING] Could not generate combined summary: {e}\n")
    else:
        print("[WARNING] No successful project analyses to summarize.\n")
    
    return results


def main():
    """CLI entry point for summarize_projects."""
    parser = argparse.ArgumentParser(
        description="Generate detailed summaries for a contributor's top-ranked projects"
    )
    parser.add_argument(
        "contributor_name",
        help="Name of the contributor to generate summaries for"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of top projects to summarize (default: all)"
    )
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        default="output",
        help="Directory where summary files should be saved (default: output)"
    )
    args = parser.parse_args()
    
    summarize_top_ranked_projects(
        contributor_name=args.contributor_name,
        limit=args.limit
    )


if __name__ == "__main__":
    main()
