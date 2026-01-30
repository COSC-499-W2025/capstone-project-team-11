"""
summarize_projects.py
---------------------------------
Generate detailed summaries for top-ranked projects by contributor.

This module provides functionality to:
- Generate summaries for a contributor's top-ranked projects
"""

import os
import sys
import json
import argparse
import sqlite3
from typing import List, Dict, Optional, Set
from datetime import datetime
from collections import defaultdict


src_dir = os.path.abspath(os.path.dirname(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from db import get_connection
from rank_projects import rank_projects_by_contributor
from contrib_metrics import canonical_username
def gather_project_info_from_db(project_name: str) -> dict:
    """Load project metadata from the database in the same shape as gather_project_info."""
    if not project_name:
        raise ValueError("project_name is required")

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, git_metrics_json, tech_json FROM projects WHERE name = ?",
            (project_name,),
        )
        row = cur.fetchone()
        project_id = row["id"] if row else None

        git_metrics = {}
        if row and row["git_metrics_json"]:
            try:
                git_metrics = json.loads(row["git_metrics_json"]) or {}
            except Exception:
                git_metrics = {}

        tech_data = {}
        if row and row["tech_json"]:
            try:
                tech_data = json.loads(row["tech_json"]) or {}
            except Exception:
                tech_data = {}

        frameworks = tech_data.get("frameworks") or []

        cur.execute(
            """
            SELECT DISTINCT l.name
            FROM languages l
            JOIN file_languages fl ON fl.language_id = l.id
            JOIN files f ON f.id = fl.file_id
            JOIN scans s ON s.id = f.scan_id
            WHERE s.project = ?
            ORDER BY l.name COLLATE NOCASE
            """,
            (project_name,),
        )
        languages = [r["name"] for r in cur.fetchall()]

        skills: List[str] = []
        if project_id:
            cur.execute(
                """
                SELECT sk.name
                FROM project_skills ps
                JOIN skills sk ON sk.id = ps.skill_id
                WHERE ps.project_id = ?
                ORDER BY sk.name COLLATE NOCASE
                """,
                (project_id,),
            )
            skills = [r["name"] for r in cur.fetchall()]

        cur.execute(
            """
            SELECT c.name AS contributor, COUNT(DISTINCT f.id) AS file_count
            FROM contributors c
            JOIN file_contributors fc ON fc.contributor_id = c.id
            JOIN files f ON f.id = fc.file_id
            JOIN scans s ON s.id = f.scan_id
            WHERE s.project = ?
            GROUP BY c.name
            """,
            (project_name,),
        )
        contributions: Dict[str, Dict] = {}
        for r in cur.fetchall():
            key = canonical_username(r["contributor"] or "")
            contributions[key] = {
                "commits": 0,
                "files": [],
                "file_count": r["file_count"] or 0,
            }

        commits_per_author = {}
        files_changed_per_author = {}
        if isinstance(git_metrics, dict):
            commits_per_author = git_metrics.get("commits_per_author") or {}
            files_changed_per_author = git_metrics.get("files_changed_per_author") or {}

        for author, commits in commits_per_author.items():
            key = canonical_username(author or "")
            entry = contributions.setdefault(key, {"commits": 0, "files": [], "file_count": 0})
            entry["commits"] = commits or 0

        for author, files_changed in files_changed_per_author.items():
            key = canonical_username(author or "")
            entry = contributions.setdefault(key, {"commits": 0, "files": [], "file_count": 0})
            if isinstance(files_changed, (list, set, tuple)):
                entry["files"] = list(files_changed)
            if entry.get("file_count", 0) == 0:
                entry["file_count"] = len(entry.get("files", []))

        return {
            "project_name": project_name,
            "languages": languages,
            "frameworks": frameworks,
            "skills": skills,
            "contributions": contributions,
            "git_metrics": git_metrics or {},
            "projects_detected": 1,
        }
    finally:
        conn.close()


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
        project_data_list: List of dicts with keys: project, project_info (dict from gather_project_info_from_db)
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
            f.write(f"   Commits: {proj['commits']}\n\n")
        
        # Individual Project Sections
        f.write("=" * 60 + "\n")
        f.write("INDIVIDUAL PROJECT DETAILS\n")
        f.write("=" * 60 + "\n\n")
        
        for i, proj in enumerate(sorted(project_details, key=lambda x: (-x["score"], -x["contrib_files"], x["name"])), 1):
            f.write(f"{'=' * 60}\n")
            f.write(f"PROJECT {i}: {proj['name']}\n")
            f.write(f"{'=' * 60}\n\n")
            f.write(f"Ranking Score: {proj['score']:.2%} ({proj['contrib_files']}/{proj['total_files']} files)\n")
            f.write(f"Commits: {proj['commits']}\n\n")
            
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


def db_is_initialized() -> bool:
    """Return True if the database contains the projects table."""
    try:
        conn = sqlite3.connect(os.environ.get('FILE_DATA_DB_PATH') or os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'file_data.db')
        ))
        cur = conn.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='projects' LIMIT 1"
        )
        row = cur.fetchone()
        return row is not None
    except Exception:
        return False
    finally:
        try:
            conn.close()
        except Exception:
            pass


def summarize_top_ranked_projects(contributor_name: str, limit: Optional[int] = None) -> List[Dict]:
    """Generate a combined summary for a contributor's top-ranked projects.
    
    Args:
        contributor_name: Name of the contributor to rank projects for
        limit: Maximum number of top projects to summarize (None for all)
    
    Returns:
        List of dicts with keys: project, project_info (dict from gather_project_info_from_db),
        and error (if summary generation failed).
    """
    contributor_name = canonical_username(contributor_name or "")

    if not db_is_initialized():
        print("Database not initialized. Run scan before generating summaries.")
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
        
        # Gather project info from DB
        try:
            info = gather_project_info_from_db(project_name)
            print(f"  [SUCCESS] Project info gathered\n")
            results.append({
                "project": project_name,
                "project_info": info,
                "error": None
            })
        except Exception as e:
            print(f"  [ERROR] Failed to gather project info: {e}\n")
            results.append({
                "project": project_name,
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
