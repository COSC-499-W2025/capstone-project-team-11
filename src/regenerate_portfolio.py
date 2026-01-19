"""
regenerate_portfolio.py

Headless regeneration of an existing portfolio Markdown.
Overwrites the specified file, including any newly scanned projects.
"""

import os
from collections import OrderedDict
from datetime import datetime, timezone

from generate_portfolio import (
    collect_projects,
    aggregate_projects_for_portfolio,
    build_portfolio
)
from db import save_portfolio


def regenerate_portfolio(username: str, portfolio_path: str, output_root: str = "output",
                         confidence_level: str = "high", save_to_db: bool = False):
    """
    Headless regeneration for an existing portfolio file.
    Ensures all projects for this user are included (including newly scanned ones).

    Args:
        username: GitHub username
        portfolio_path: Full path to overwrite
        output_root: Path to scanned project JSON files
        confidence_level: 'high', 'medium', or 'low' for tech confidence filtering
        save_to_db: If True, save portfolio metadata to DB
    """
    if not username:
        raise ValueError("username is required")
    if not portfolio_path:
        raise ValueError("portfolio_path is required")
    if not os.path.isdir(output_root):
        raise ValueError(f"output_root not found: {output_root}")

    os.makedirs(os.path.dirname(portfolio_path), exist_ok=True)

    # --- 1. Collect all projects for this user from output_root ---
    all_projects, root_repo_jsons = collect_projects(output_root)
    portfolio_projects = aggregate_projects_for_portfolio(username, all_projects, root_repo_jsons)

    if not portfolio_projects:
        raise ValueError(f"No projects found for user '{username}' in {output_root}")

    # --- 2. Build portfolio object ---
    ts_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    portfolio = build_portfolio(username, portfolio_projects, generated_ts=ts_iso, confidence_level=confidence_level)

    # --- 3. Render Markdown and overwrite existing portfolio ---
    md = portfolio.render_markdown()
    with open(portfolio_path, 'w', encoding='utf-8') as f:
        f.write(md)

    print(f"Portfolio successfully regenerated at: {portfolio_path}")
    print(f"  {len(portfolio_projects)} project(s) included")
    print(f"  {len(portfolio.sections)} section(s) generated")
    print(f"  Confidence filter: {confidence_level}")

    # --- 4. Save metadata to DB if requested ---
    if save_to_db:
        try:
            portfolio_metadata = {
                'username': username,
                'project_count': len(portfolio_projects),
                'sections': list(portfolio.sections.keys()),
                'confidence_level': confidence_level,
                'projects': [
                    {
                        'name': p.get('project_name'),
                        'path': p.get('path'),
                        'user_commits': p.get('user_commits', 0)
                    }
                    for p in portfolio_projects
                ]
            }
            save_portfolio(username, portfolio_path, portfolio_metadata, ts_iso)
            print(f"  Portfolio metadata saved to database.")
        except Exception as e:
            print(f"  Warning: Failed to save portfolio metadata to DB: {e}")


# Optional CLI entry point
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Regenerate an existing portfolio (overwrites file).")
    parser.add_argument("--username", "-u", required=True, help="GitHub username")
    parser.add_argument("--portfolio-path", "-p", required=True, help="Path to the existing portfolio file to overwrite")
    parser.add_argument("--output-root", "-r", default="output", help="Path to output folder with project JSONs")
    parser.add_argument("--confidence", "-c", choices=["high", "medium", "low"], default="high", help="Confidence filter for languages/frameworks")
    parser.add_argument("--save-to-db", action="store_true", help="Save portfolio metadata to DB")

    args = parser.parse_args()

    regenerate_portfolio(
        username=args.username,
        portfolio_path=args.portfolio_path,
        output_root=args.output_root,
        confidence_level=args.confidence,
        save_to_db=args.save_to_db
    )
