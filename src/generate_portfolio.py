# Generates a project-centric portfolio Markdown file using scanned project summaries
# The script reads project data from the local database and aggregates project-level details
# It then writes the generated portfolio to: portfolios/portfolio_<username>_<timestamp>.md
"""
TODO: Once we have a frontend UI, I expect this to be a two column window: 
        left-column: shows all portfolio sections next to: checkboxes for enabling/disabling them & edit buttons
        right-column: live preview of the generated markdown file, where users can view and edit before final export
        *For now, this is a CLI-only tool that generates a static markdown file, but I have built in the infrastructure for section toggling
"""

import argparse
import os
import sys
from collections import OrderedDict
from datetime import datetime, timezone
# Import shared functions from generate_resume.py
from generate_resume import collect_projects, normalize_project_name
# Import database functions
from db import save_portfolio
# Evidence integration: import helpers for user-provided project evidence
from project_evidence import get_project_id_by_name, get_evidence_for_project, format_evidence_for_portfolio

# ============================================================================
# Portfolio Structure & Helper Functions
# ============================================================================

# Helper function to filter languages/frameworks by confidence level
def get_filtered_technologies(project_data, confidence_level='high'):
    """
    Extract languages and frameworks from project data, filtered by confidence level.

    Args:
        project_data: Project dict with language/framework data
        confidence_level: Filter level for language/framework confidence ('high', 'medium', 'low')
    Returns:
        Tuple of (languages, frameworks) filtered by confidence
    """
    # Only high confidence
    if confidence_level == 'high': 
        languages = project_data.get('high_confidence_languages', [])
        frameworks = project_data.get('high_confidence_frameworks', [])
    # High + medium confidence
    elif confidence_level == 'medium':
        languages = list(set(
            project_data.get('high_confidence_languages', []) +
            project_data.get('medium_confidence_languages', [])
        ))
        frameworks = list(set(
            project_data.get('high_confidence_frameworks', []) +
            project_data.get('medium_confidence_frameworks', [])
        ))
    # High + medium + low confidence (All confidence levels)
    elif confidence_level == 'low': 
        languages = list(set(
            project_data.get('high_confidence_languages', []) +
            project_data.get('medium_confidence_languages', []) +
            project_data.get('low_confidence_languages', [])
        ))
        frameworks = list(set(
            project_data.get('high_confidence_frameworks', []) +
            project_data.get('medium_confidence_frameworks', []) +
            project_data.get('low_confidence_frameworks', [])
        ))
    else: # Any other value, use unfiltered list
        languages = project_data.get('languages', [])
        frameworks = project_data.get('frameworks', [])

    # Fallback to full lists if confidence data not available
    if not languages and not frameworks:
        languages = project_data.get('languages', [])
        frameworks = project_data.get('frameworks', [])

    return languages, frameworks

# Represents a configurable section of a portfolio (three main section types: overview, project(s), tech summary)
class PortfolioSection:

    def __init__(self, section_id, title, content, enabled=True, metadata=None):
        """
        Args:
            section_id: Unique identifier (e.g., 'overview', 'project_1', etc.)
            title: Display title for the section (project name)
            content: Markdown content (String)
            enabled: Whether to include in final output (defaults to True)
            metadata: Optional dict to host additional project metadata
        """
        self.section_id = section_id
        self.title = title
        self.content = content
        self.enabled = enabled
        self.metadata = metadata or {}
    
    # Render a portfolio section (if section is disabled, returns empty string | if enabled, returns markdown format)
    def render(self):
        if not self.enabled:
            return ""
        return f"## {self.title}\n\n{self.content}\n"

# Initializes a portfolio with multiple sections
class Portfolio:

    def __init__(self, username, sections, metadata=None):
        """
        Args:
            username: Portfolio owner's username
            sections: Ordered dict of sections
            metadata: Optional dict for portfolio-level metadata
        """
        self.username = username
        self.sections = sections
        self.metadata = metadata or {}

    # Generate final markdown from enabled sections
    def render_markdown(self):
        lines = [f"# Portfolio — {self.username}\n"]

        for section in self.sections.values():
            if section.enabled:
                lines.append(section.render())

        # Footer with generation timestamp
        timestamp = self.metadata.get('generated_at', datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ'))
        lines.append(f"\n---\n_Generated: {timestamp}_\n")

        return '\n'.join(lines) # Returns complete portfolio in markdown format

    # Retrieve specific section by section_id
    def get_section(self, section_id):
        return self.sections.get(section_id) # Returns PortfolioSection or None if not found

    # Enable/disable a section
    def toggle_section(self, section_id):
        if section_id in self.sections:
            self.sections[section_id].enabled = not self.sections[section_id].enabled

# ============================================================================
# Section Builders
# ============================================================================

# Build portfolio 'overview' section
def build_overview_section(projects_data, username, confidence_level='high'):
    """
    Args:
        projects_data: List of project dicts
        username: Portfolio owner's GitHub username
        confidence_level: Filter level for language/framework confidence ('high', 'medium', 'low')
    """
    total_projects = len(projects_data)
    all_techs = set()
    all_skills = set()

    for proj in projects_data:
        # Use confidence-filtered technologies
        languages, frameworks = get_filtered_technologies(proj, confidence_level)
        all_techs.update(languages)
        all_techs.update(frameworks)
        all_skills.update(proj.get('skills', []))

    content_lines = [f"This portfolio showcases **{total_projects} project(s)** developed by {username}.", "",]

    if all_techs:
        content_lines.append(f"**Technologies:** {', '.join(sorted(all_techs))}")
        content_lines.append("")

    if all_skills:
        content_lines.append(f"**Skills Demonstrated:** {', '.join(sorted(all_skills))}")
        content_lines.append("")

    return PortfolioSection(
        section_id='overview',
        title='Overview',
        content='\n'.join(content_lines),
        metadata={'project_count': total_projects}
    )

# Build detailed section for a single project
def build_project_section(project_data, index, username, confidence_level='high'):
    """
    Args:
        project_data: Project dict from aggregated data
        index: Project number (for section_id)
        username: Portfolio owner's username (for calculating user-specific metrics)
        confidence_level: Filter level for language/framework confidence ('high', 'medium', 'low')
    """
    # Gathers and formats project details, includes fallbacks for missing data
    name = project_data.get('project_name', 'Unnamed Project')
    normalized_name = normalize_project_name(name, project_data.get('path'))
    path = project_data.get('path', 'N/A')

    # Use confidence-filtered technologies
    languages, frameworks = get_filtered_technologies(project_data, confidence_level)
    skills = project_data.get('skills', [])
    git_metrics = project_data.get('git_metrics', {})

    # Determine project type (individual vs collaborative)
    authors = git_metrics.get('commits_per_author', {}) if git_metrics else {}
    project_type = "Collaborative" if len(authors) > 1 else "Individual"

    content_lines = [
        f"_({project_type} Project)_",
        "",
        f"**Project Path:** `{path}`",
        ""
    ]

    # Build 'Languages' summary
    if languages:
        content_lines.append(f"**Languages:** {', '.join(languages)}")
        content_lines.append("")

    # Build 'Frameworks' summary
    if frameworks:
        content_lines.append(f"**Frameworks:** {', '.join(frameworks)}")
        content_lines.append("")

    # Build 'Skills Demonstrated' summary
    if skills:
        content_lines.append(f"**Skills Demonstrated:** {', '.join(skills)}")
        content_lines.append("")

    # Incorporate Git metrics if available
    if git_metrics:
        total_commits = git_metrics.get('total_commits', 0)
        duration = git_metrics.get('duration_days', 0)
        authors = git_metrics.get('commits_per_author', {})

        if total_commits or duration or authors:
            content_lines.append("**Project Metrics:**")

            if total_commits:
                content_lines.append(f"- Total commits: {total_commits}")

            if duration:
                content_lines.append(f"- Development duration: {duration} days")

            if len(authors) > 1:
                content_lines.append(f"- Contributors: {', '.join(authors.keys())}")

            content_lines.append("")

    # Build 'User-Specific Contributions' summary with performance metrics
    user_commits = project_data.get('user_commits', 0)
    user_files = project_data.get('user_files', [])

    if user_commits and git_metrics:
        content_lines.append("**My Contributions:**")

        # === COMMIT METRICS ===
        # My commits
        content_lines.append(f"- {user_commits} commit(s)")

        # Percentage of total commits
        total_commits = git_metrics.get('total_commits', 0)
        if total_commits > 0:
            commit_percentage = (user_commits / total_commits) * 100
            content_lines.append(f"- {commit_percentage:.1f}% of total commits")

        # Commit frequency per week
        project_start = git_metrics.get('project_start')
        project_end = git_metrics.get('project_end')
        if project_start and project_end:
            duration_days = git_metrics.get('duration_days', 0)
            if duration_days > 0:
                weeks = max(1, duration_days / 7)
                avg_commits_per_week = user_commits / weeks
                content_lines.append(f"- {avg_commits_per_week:.1f} commit(s)/week")

        # === FILE METRICS ===
        # Files modified
        content_lines.append(f"- {len(user_files)} file(s) modified")

        # File ownership percentage
        files_per_author = git_metrics.get('files_changed_per_author', {})
        all_files = set()
        for files_list in files_per_author.values():
            all_files.update(files_list)
        if all_files and user_files:
            file_ownership = (len(user_files) / len(all_files)) * 100
            content_lines.append(f"- {file_ownership:.1f}% file ownership")

        # === CODE CONTRIBUTION METRICS ===
        # Lines added/removed
        lines_added = git_metrics.get('lines_added_per_author', {}).get(username, 0)
        lines_removed = git_metrics.get('lines_removed_per_author', {}).get(username, 0)
        if lines_added or lines_removed:
            content_lines.append(f"- Lines: +{lines_added} / -{lines_removed}")

        # Contributor ranking
        authors = git_metrics.get('commits_per_author', {})
        if len(authors) > 1:
            sorted_authors = sorted(authors.items(), key=lambda x: x[1], reverse=True)
            user_rank = next((i+1 for i, (name, _) in enumerate(sorted_authors) if name == username), None)
            if user_rank:
                total_contributors = len(authors)
                content_lines.append(f"- Ranked #{user_rank} of {total_contributors} contributor(s) _*by commit count_")

        # Active period
        if project_start and project_end:
            start_str = project_start.strftime('%Y-%m-%d') if hasattr(project_start, 'strftime') else str(project_start)[:10]
            end_str = project_end.strftime('%Y-%m-%d') if hasattr(project_end, 'strftime') else str(project_end)[:10]
            content_lines.append(f"- My first/last commit: {start_str} to {end_str}")

        content_lines.append("")
    elif user_commits:
        # Fallback for projects without full git metrics
        content_lines.append("**My Contributions:**")
        content_lines.append(f"- {user_commits} commit(s)")
        content_lines.append(f"- {len(user_files)} file(s) modified")
        content_lines.append("")

    # Evidence integration: Add optional "Evidence of Success" section if user-provided evidence exists
    # This follows the same optional-section pattern used for Languages, Frameworks, and Skills.
    # Evidence is treated as user-provided input and is NOT inferred, scored, or ranked.
    try:
        project_id = get_project_id_by_name(name)
        if project_id:
            evidence = get_evidence_for_project(project_id)
            evidence_content = format_evidence_for_portfolio(evidence)
            if evidence_content:
                content_lines.append("**Evidence of Success:**")
                content_lines.append(evidence_content)
                content_lines.append("")
    except Exception:
        # Gracefully skip evidence if DB not available or any error occurs
        pass

    return PortfolioSection(
        section_id=f'project_{index}',
        title=normalized_name,
        content='\n'.join(content_lines),
        metadata={'project_name': name, 'path': path}
    )

# Build 'Technology Summary' section
def build_tech_summary_section(projects_data, confidence_level='high'):
    """
    Args:
        projects_data: List of project dicts
        confidence_level: Filter level for language/framework confidence ('high', 'medium', 'low')
    """
    tech_usage = {}

    # Aggregate language/framework usage across all included projects
    for proj in projects_data:
        proj_name = proj.get('project_name', 'Unknown')

        # Use confidence-filtered technologies
        languages, frameworks = get_filtered_technologies(proj, confidence_level)

        for tech in languages + frameworks:
            if tech not in tech_usage:
                tech_usage[tech] = []
            tech_usage[tech].append(proj_name)

    # Sort by usage frequency (most used first)
    sorted_techs = sorted(tech_usage.items(), key=lambda x: len(x[1]), reverse=True)

    # List each language/framework with their associated project count
    content_lines = []
    for tech, projects in sorted_techs:
        count = len(projects)
        plural = "project" if count == 1 else "projects"
        content_lines.append(f"- **{tech}** — used in {count} {plural}")

    if not content_lines:
        content_lines.append("No technology data available.")

    return PortfolioSection(
        section_id='tech_summary',
        title='Technology Summary',
        content='\n'.join(content_lines)
    )

# Aggregate projects for portfolio based on a selected git username
def aggregate_projects_for_portfolio(username, all_projects, root_repo_jsons=None):
    """
    Args:
        username: Portfolio owner's username
        all_projects: Dict of project_name -> project_info
        root_repo_jsons: Optional dict of root-level repo JSON files

    Returns:
        List of project dicts suitable for portfolio generation
    """
    portfolio_projects = []

    for name, info in all_projects.items():
        contribs = info.get('contributions', {}) or {}
        user_entry = contribs.get(username)

        # Include project if: Selected sername explicitly contributed to it, OR Project has valuable metadata (to include non-git projects, and solo projects)
        has_metadata = (
            info.get('languages') or
            info.get('frameworks') or
            info.get('skills')
        )

        # Aggregates project data for portfolio
        # Include project if:
        # - user explicitly contributed (git-tracked project), OR
        # - project has no git contributors at all but has metadata (assumed solo / non-git project)
        if user_entry or (not contribs and has_metadata):  # Include only if user contributed OR project has no git data
            project = {
                'project_name': name,
                'path': info.get('project_path'),
                # Unfiltered lists
                'languages': info.get('languages', []),
                'frameworks': info.get('frameworks', []),
                'skills': info.get('skills', []),
                # Confidence-categorized lists
                'high_confidence_languages': info.get('high_confidence_languages', []),
                'medium_confidence_languages': info.get('medium_confidence_languages', []),
                'low_confidence_languages': info.get('low_confidence_languages', []),
                'high_confidence_frameworks': info.get('high_confidence_frameworks', []),
                'medium_confidence_frameworks': info.get('medium_confidence_frameworks', []),
                'low_confidence_frameworks': info.get('low_confidence_frameworks', []),
                # User-specific data
                'user_commits': user_entry.get('commits', 0) if user_entry else 0,
                'user_files': user_entry.get('files', []) if user_entry else [],
                'git_metrics': info.get('git_metrics', {})
            }
            portfolio_projects.append(project)

    # Sort by git project start date, non-git projects last
    return sorted(
        portfolio_projects,
        key=lambda x: (x.get('git_metrics') or {}).get('project_start') or '9999',
        reverse=True
    )

# Build complete Portfolio object from project data
def build_portfolio(username, projects_data, generated_ts=None, confidence_level='high'):
    """
    Args:
        username: Portfolio owner's username
        projects_data: List of project dicts (from aggregate_projects_for_portfolio)
        generated_ts: Optional timestamp string
        confidence_level: Filter level for language/framework confidence ('high', 'medium', 'low')

    Returns:
        Portfolio object with all sections
    """
    if generated_ts is None:
        generated_ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')

    # Organize sections (Overview -> Projects -> Tech Summary)
    sections = OrderedDict()

    # Build 'Overview' section
    sections['overview'] = build_overview_section(projects_data, username, confidence_level)

    # Build project section(s)
    for idx, project in enumerate(projects_data, start=1):
        section = build_project_section(project, idx, username, confidence_level)
        sections[section.section_id] = section

    # Build 'Technology Summary' section
    sections['tech_summary'] = build_tech_summary_section(projects_data, confidence_level)

    return Portfolio(
        username=username,
        sections=sections,
        metadata={'generated_at': generated_ts, 'project_count': len(projects_data)}
    )

# ============================================================================
# Main CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Generate portfolio Markdown from the database for a given username'
    )
    parser.add_argument(
        '--username', '-u',
        required=False,
        help='GitHub username (as found in output contributions). If omitted, will prompt.'
    )
    parser.add_argument(
        '--output-root', '-r',
        default='output',
        help='Deprecated: output folder path is ignored (DB is used)'
    )
    parser.add_argument(
        '--portfolio-dir', '-d',
        default='portfolios',
        help='Directory to write generated portfolios (default: portfolios)'
    )
    parser.add_argument(
        '--confidence', '-c',
        default='high',
        choices=['high', 'medium', 'low'],
        help='Confidence filter for languages/frameworks (default: high). '
             'high=only high confidence, medium=high+medium, low=all levels'
    )
    parser.add_argument(
        '--overwrite',
        default=None,
        help='If provided, overwrite the portfolio file at this path instead of creating a new timestamped file'
    )
    parser.add_argument(
        '--save-to-db',
        action='store_true',
        help='Save portfolio metadata to the local database'
    )
    args = parser.parse_args()

    # output_root retained for CLI compatibility but ignored

    # Blacklist of usernames to exclude
    BLACKLIST = {'githubclassroombot', 'Unknown'}

    # If username not provided, attempt to list detected usernames and prompt the user
    username = args.username
    projects, root_repo_jsons = collect_projects(args.output_root)

    if not username:
        # Discover possible usernames from project contributions
        candidates = set()
        for info in projects.values():
            contribs = info.get('contributions') or {}
            # Handle nested contributions structure
            if isinstance(contribs.get('contributions'), dict):
                contribs = contribs['contributions']
            candidates.update(contribs.keys())
        candidates = sorted([c for c in candidates if c not in BLACKLIST])

        if not candidates:
            print('No candidate usernames detected in the database.')
            try:
                username = input('Enter username to generate portfolio for: ').strip()
            except EOFError:
                print('No username provided and input not available.')
                return 1
            if not username:
                print('No username entered; aborting.')
                return 1
        else:
            print('\nDetected candidate usernames:')
            for i, c in enumerate(candidates, start=1):
                print(f"  {i}. {c}")
            print('\nYou may enter the number (e.g. 1) or the exact username.')
            try:
                user_in = input('Select username (number or name, blank to abort): ').strip()
            except EOFError:
                print('No username provided.')
                return 1
            if not user_in:
                print('No username entered; aborting.')
                return 1

            # Handle numeric selection
            if user_in.isdigit():
                idx = int(user_in) - 1
                if 0 <= idx < len(candidates):
                    username = candidates[idx]
                else:
                    print('Selection out of range; aborting.')
                    return 1
            else:
                username = user_in

    username = username.strip()

    # Create output directory
    os.makedirs(args.portfolio_dir, exist_ok=True)

    # Aggregate project data for portfolio (includes non-git projects)
    portfolio_projects = aggregate_projects_for_portfolio(username, projects, root_repo_jsons)

    if not portfolio_projects:
        print(f"No projects found for user '{username}' in the database")
        return 1

    # Build portfolio with timestamps and confidence filter
    ts_iso = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')
    ts_fname = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

    portfolio = build_portfolio(username, portfolio_projects, ts_iso, args.confidence)

    # Render and save to file
    md = portfolio.render_markdown()
    if args.overwrite:
        out_path = args.overwrite  # <-- overwrite the given file
    else:
        out_path = os.path.join(args.portfolio_dir, f"portfolio_{username}_{ts_fname}.md")

    with open(out_path, 'w', encoding='utf-8') as fh:
        fh.write(md)

    print(f"Portfolio written: {out_path}")
    print(f"  {len(portfolio_projects)} project(s) included")
    print(f"  {len(portfolio.sections)} section(s) generated")
    print(f"  Confidence filter: {args.confidence}")

    # Save to database if requested
    if args.save_to_db:
        try:
            portfolio_metadata = {
                'username': username,
                'project_count': len(portfolio_projects),
                'sections': list(portfolio.sections.keys()),
                'confidence_level': args.confidence,
                'projects': [
                    {
                        'name': p.get('project_name'),
                        'path': p.get('path'),
                        'user_commits': p.get('user_commits', 0)
                    }
                    for p in portfolio_projects
                ]
            }
            portfolio_id = save_portfolio(username, out_path, portfolio_metadata, ts_iso)
            print(f"  Saved to database with ID: {portfolio_id}")
        except Exception as e:
            print(f"  Warning: Failed to save to database: {e}")

    return 0

if __name__ == '__main__':
    raise SystemExit(main())
