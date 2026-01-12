# Generates a project-centric portfolio Markdown file using scanned project summaries
# The script reads project JSON files in output/, and aggregates relevant project-level details
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
from datetime import datetime, UTC
# Import shared functions from generate_resume.py
from generate_resume import collect_projects, normalize_project_name

# ============================================================================
# Portfolio Structure & Helper Functions
# ============================================================================

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
        timestamp = self.metadata.get('generated_at', datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%SZ'))
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
def build_overview_section(projects_data, username):
    """
    Args:
        projects_data: List of project dicts
        username: Portfolio owner's GitHub username
    """
    total_projects = len(projects_data)
    all_techs = set()
    all_skills = set()

    for proj in projects_data:
        all_techs.update(proj.get('languages', []))
        all_techs.update(proj.get('frameworks', []))
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
def build_project_section(project_data, index):
    """
    Args:
        project_data: Project dict from aggregated data
        index: Project number (for section_id)
    """
    # Gathers and formats project details, includes fallbacks for missing data
    name = project_data.get('project_name', 'Unnamed Project')
    normalized_name = normalize_project_name(name, project_data.get('path'))
    path = project_data.get('path', 'N/A')
    languages = project_data.get('languages', [])
    frameworks = project_data.get('frameworks', [])
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

    # Build 'User-Specific Contributions' summary
    user_commits = project_data.get('user_commits', 0)
    user_files = project_data.get('user_files', [])
    if user_commits:
        content_lines.append("**My Contributions:**")
        content_lines.append(f"- {user_commits} commit(s)")
        content_lines.append(f"- {len(user_files)} file(s) modified")
        content_lines.append("")

    return PortfolioSection(
        section_id=f'project_{index}',
        title=normalized_name,
        content='\n'.join(content_lines),
        metadata={'project_name': name, 'path': path}
    )

# Build 'Technology Summary' section
def build_tech_summary_section(projects_data):

    tech_usage = {}

    # Aggregate language/framework usage across all included projects
    for proj in projects_data:
        proj_name = proj.get('project_name', 'Unknown')
        for tech in proj.get('languages', []) + proj.get('frameworks', []):
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
def aggregate_projects_for_portfolio(username, all_projects, root_repo_jsons):
    """
    Args:
        username: Portfolio owner's username
        all_projects: Dict of project_name -> project_info
        root_repo_jsons: Dict of root-level JSONs

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
        if user_entry or has_metadata:
            project = {
                'project_name': name,
                'path': info.get('project_path'),
                'languages': info.get('languages', []),
                'frameworks': info.get('frameworks', []),
                'skills': info.get('skills', []),
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
def build_portfolio(username, projects_data, generated_ts=None):
    """
    Args:
        username: Portfolio owner's username
        projects_data: List of project dicts (from aggregate_projects_for_portfolio)
        generated_ts: Optional timestamp string

    Returns:
        Portfolio object with all sections
    """
    if generated_ts is None:
        generated_ts = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%SZ')

    # Organize sections (Overview -> Projects -> Tech Summary)
    sections = OrderedDict()

    # Build 'Overview' section
    sections['overview'] = build_overview_section(projects_data, username)

    # Build project section(s)
    for idx, project in enumerate(projects_data, start=1):
        section = build_project_section(project, idx)
        sections[section.section_id] = section

    # Build 'Technology Summary' section
    sections['tech_summary'] = build_tech_summary_section(projects_data)

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
        description='Generate portfolio Markdown from output/ for a given username'
    )
    parser.add_argument(
        '--username', '-u',
        required=False,
        help='GitHub username (as found in output contributions). If omitted, will prompt.'
    )
    parser.add_argument(
        '--output-root', '-r',
        default='output',
        help='Path to the output folder (default: output)'
    )
    parser.add_argument(
        '--portfolio-dir', '-d',
        default='portfolios',
        help='Directory to write generated portfolios (default: portfolios)'
    )
    args = parser.parse_args()

    if not os.path.isdir(args.output_root):
        print(f"Output folder not found: {args.output_root}")
        return 1

    # Blacklist of usernames to exclude
    BLACKLIST = {'githubclassroombot'}

    # Username selection (interactive if not provided)
    username = args.username
    projects, root_repo_jsons = collect_projects(args.output_root)

    if not username:
        # Discover possible usernames from project contributions
        candidates = set()
        for info in projects.values():
            contribs = info.get('contributions') or {}
            candidates.update(contribs.keys())
        candidates = sorted([c for c in candidates if c not in BLACKLIST])

        if not candidates:
            print('No candidate usernames detected in `output/`.')
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
        print(f"No projects found for user '{username}' in {args.output_root}")
        return 1

    # Build portfolio with timestamps
    ts_iso = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%SZ')
    ts_fname = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')

    portfolio = build_portfolio(username, portfolio_projects, ts_iso)

    # Render and save to file
    md = portfolio.render_markdown()
    out_path = os.path.join(args.portfolio_dir, f"portfolio_{username}_{ts_fname}.md")

    with open(out_path, 'w', encoding='utf-8') as fh:
        fh.write(md)

    print(f"Portfolio written: {out_path}")
    print(f"  {len(portfolio_projects)} project(s) included")
    print(f"  {len(portfolio.sections)} section(s) generated")

    return 0

if __name__ == '__main__':
    raise SystemExit(main())