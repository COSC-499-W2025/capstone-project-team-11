"""
regenerate_resume.py

Handles headless regeneration of an existing resume.
Main_menu.py calls this to overwrite a resume without prompting.
"""

import os
import json
import re
from datetime import datetime
from db import save_resume

# Common acronyms to preserve capitalization
ACRONYMS = {
    'tcp': 'TCP', 'udp': 'UDP', 'api': 'API', 'sql': 'SQL',
    'html': 'HTML', 'css': 'CSS', 'json': 'JSON', 'js': 'JS',
    'r': 'R', 'c#': 'C#', 'c++': 'C++', 'go': 'Go',
    'java': 'Java', 'kotlin': 'Kotlin', 'typescript': 'TypeScript',
    'django': 'Django', 'fastapi': 'FastAPI', 'flask': 'Flask'
}

def normalize_project_name(name, path=None):
    """Normalize project names like in generate_resume.py"""
    if not name and path:
        name = os.path.basename(path)
    if not name:
        return ''
    s = str(name)
    s = re.sub(r'(_info[_-].*|_summary[_-].*|_info.*|_summary.*)$', '', s, flags=re.IGNORECASE)
    s = re.sub(r'[\._/]+', ' ', s)
    s = s.replace('-', ' ').replace('__', ' ').strip()
    tokens = s.split()
    out_tokens = []
    for tok in tokens:
        tl = tok.lower()
        if tl in ACRONYMS:
            out_tokens.append(ACRONYMS[tl])
        else:
            if re.search(r'[A-Z]', tok[1:]):
                out_tokens.append(tok)
            else:
                out_tokens.append(tok.capitalize())
    return ' '.join(out_tokens).strip()


def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except Exception:
        return None


def collect_projects(output_root):
    """Collect project JSONs from output folder"""
    projects = {}
    for dirpath, dirs, files in os.walk(output_root):
        for f in files:
            if f.endswith('.json'):
                p = os.path.join(dirpath, f)
                j = load_json(p)
                if not j:
                    continue
                if isinstance(j, dict) and 'project_name' in j:
                    projects[j['project_name']] = j
    return projects


def aggregate_for_user(username, projects):
    """Aggregate projects, skills, techs, commits, lines added"""
    user_projects = []
    tech_set = set()
    skills_set = set()
    total_commits = 0
    total_lines = 0

    for name, info in projects.items():
        contribs = info.get('contributions', {}) or {}
        user_entry = contribs.get(username)
        if user_entry:
            pj = {
                'project_name': name,
                'path': info.get('project_path'),
                'languages': info.get('languages', []),
                'frameworks': info.get('frameworks', []),
                'skills': info.get('skills', []),
                'user_commits': user_entry.get('commits', 0),
                'user_files': user_entry.get('files', []),
                'git_metrics': info.get('git_metrics', {})
            }
            user_projects.append(pj)
            tech_set.update(pj['languages'] or [])
            tech_set.update(pj['frameworks'] or [])
            skills_set.update(pj['skills'] or [])
            total_commits += pj['user_commits'] or 0
            gm = pj.get('git_metrics') or {}
            laps = gm.get('lines_added_per_author', {})
            if isinstance(laps, dict):
                total_lines += laps.get(username) or 0

    return {
        'username': username,
        'projects': sorted(user_projects, key=lambda x: x.get('git_metrics', {}).get('project_start') or '', reverse=True),
        'technologies': sorted([t for t in tech_set if t]),
        'skills': sorted([s for s in skills_set if s]),
        'total_commits': total_commits,
        'total_lines_added': total_lines
    }


def render_markdown(agg):
    """Render aggregated data into Markdown resume format"""
    username = agg['username']
    date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')
    md = [f"# Resume — {username}", '']

    # Summary
    summary_lines = []
    if agg['skills']:
        summary_lines.append(', '.join(agg['skills']))
    if agg['technologies']:
        summary_lines.append('Experience with: ' + ', '.join(agg['technologies']))
    summary = ' · '.join(summary_lines) if summary_lines else 'Contributed to multiple coding and data-analysis projects.'
    md += ['## Summary', '', summary, '']

    # Technical skills
    md += ['## Technical Skills', '']
    if agg['technologies']:
        md.append('- Languages & Tools: **' + '**, **'.join(agg['technologies']) + '**')
    else:
        md.append('- Languages & Tools: (no detected languages)')
    if agg['skills']:
        md.append('- Skills: ' + ', '.join(agg['skills']))
    md.append('')

    # Projects
    md += ['## Projects', '']
    if not agg['projects']:
        md.append('- No project-specific contributions found.')
    for p in agg['projects']:
        name = p.get('project_name')
        normalized_name = normalize_project_name(name, p.get('path')) or name
        md.append(f"**{normalized_name}**")
        if p.get('path'):
            md.append(f"- Path: `{p.get('path')}`")
        techs = ', '.join([t for t in (p.get('languages') or []) + (p.get('frameworks') or []) if t])
        bullets = []
        if p.get('user_commits'):
            bullets.append(f"Implemented features and fixes across the codebase ({p.get('user_commits')} commits); files changed: {len(p.get('user_files', []))}.")
        if techs:
            bullets.append(f"Technologies: {techs}.")
        if p.get('skills'):
            bullets.append(f"Skills demonstrated: {', '.join(p.get('skills'))}.")
        for b in bullets:
            md.append(f"- {b}")
        md.append('')

    # Metrics
    md += ['## Evidence & Metrics', '']
    md.append(f"- Total commits (detected): {agg.get('total_commits', 0)}")
    md.append(f"- Total lines added (detected): {agg.get('total_lines_added', 0)}")
    md.append('')
    md.append(f"_Generated (UTC): {date}_")
    return '\n'.join(md)


def regenerate_resume(username: str, resume_path: str, output_root: str = "output"):
    """Headless regeneration for an existing resume file"""
    if not username:
        raise ValueError("username is required")
    if not resume_path:
        raise ValueError("resume_path is required")
    if not os.path.isdir(output_root):
        raise ValueError(f"output_root not found: {output_root}")

    os.makedirs(os.path.dirname(resume_path), exist_ok=True)

    projects = collect_projects(output_root)
    agg = aggregate_for_user(username, projects)
    md = render_markdown(agg)

    with open(resume_path, 'w', encoding='utf-8') as fh:
        fh.write(md)

    # Save metadata to DB if table exists
    try:
        save_resume(username=username, resume_path=resume_path, metadata=agg)
    except Exception:
        pass  # fail silently if db unavailable

    print(f"Resume successfully regenerated: {resume_path}")
