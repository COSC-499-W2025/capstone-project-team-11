"""
skill_timeline.py

Provides utilities for generating and printing a chronological
timeline of skills exercised across projects.
"""

from typing import List, Dict
from datetime import datetime


def print_grouped_skill_timeline(cur, safe_query, human_ts, print_header) -> None:
    """
    Print skills grouped by skill name, with chronological occurrences per project.
    """

    print_header('Skills Exercised (Chronologically — Grouped by Skill)')

    rows = safe_query(cur, """
        SELECT sk.name AS skill,
               s.scanned_at AS used_at,
               p.name AS project
        FROM skills sk
        JOIN project_skills ps ON sk.id = ps.skill_id
        JOIN projects p ON ps.project_id = p.id
        JOIN scans s ON s.project = p.name
        ORDER BY sk.name ASC, used_at ASC
    """)

    if not rows:
        print(" No recorded skills")
        return

    grouped: Dict[str, List] = {}

    for row in rows:
        skill = row["skill"]
        ts = human_ts(row["used_at"])
        proj = row["project"]
        grouped.setdefault(skill, []).append((ts, proj))

    for skill, entries in grouped.items():
        print(f"\n{skill}:")
        for ts, proj in entries:
            print(f"   • {ts}  (project: {proj})")
