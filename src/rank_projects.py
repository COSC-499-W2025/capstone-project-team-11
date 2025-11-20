# Rank projects recorded in the scans database and display them chronologically.
from __future__ import annotations

import argparse
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime
import re

from db import get_connection


def rank_projects(order: str = "desc", limit: Optional[int] = None) -> List[Dict]:
    """Return a list of projects aggregated from the scans table.

    Each item is a dict: {project, created_at, first_scan, last_scan, scans_count}.
    Projects are ordered by project creation date when available (projects.created_at).
    If a project row is not present for a scans.project value, the earliest scan date
    for that project is used as a fallback for `created_at`.
    `order` must be 'asc' or 'desc' and controls ordering by created_at.
    """
    order = order.lower()
    if order not in ("asc", "desc"):
        raise ValueError("order must be 'asc' or 'desc'")

    conn = get_connection()
    cur = conn.cursor()

    # Prefer ordering by project creation date if the `projects` table exists.
    # We left-join `projects` to `scans` and use COALESCE(projects.created_at, MIN(scanned_at))
    # so that projects without a row still get a sensible created_at value.
    sql = (
        "SELECT "
        " COALESCE(p.name, COALESCE(s.project, '<unknown>')) AS project,"
        " COALESCE(p.created_at, MIN(s.scanned_at)) AS created_at,"
        " MIN(s.scanned_at) AS first_scan,"
        " MAX(s.scanned_at) AS last_scan,"
        " COUNT(s.id) AS scans_count"
        " FROM scans s"
        " LEFT JOIN projects p ON p.name = s.project"
        " GROUP BY COALESCE(p.name, s.project)"
        f" ORDER BY created_at {order.upper()}"
    )
    if limit is not None and isinstance(limit, int) and limit > 0:
        sql = sql + f" LIMIT {int(limit)}"

    try:
        cur.execute(sql)
        rows = cur.fetchall()
    except sqlite3.OperationalError:
        # Likely DB not initialized or table missing; return empty list
        rows = []
    finally:
        conn.close()

    result = []
    for r in rows:
        result.append({
            "project": r["project"],
            "created_at": r["created_at"],
            "first_scan": r["first_scan"],
            "last_scan": r["last_scan"],
            "scans_count": r["scans_count"],
        })
    return result


def print_projects(projects: List[Dict]):
    """Print projects in a simple aligned table."""
    if not projects:
        print("No projects found in the database.")
        return
    headers = ["Project", "Created", "First Scan", "Last Scan", "Scans"]
    # Compute column widths
    col_widths = [len(h) for h in headers]
    for p in projects:
        col_widths[0] = max(col_widths[0], len(str(p["project"])))
        col_widths[1] = max(col_widths[1], len(str(human_ts(p.get("created_at") or ""))))
        col_widths[2] = max(col_widths[2], len(str(human_ts(p["first_scan"] or ""))))
        col_widths[3] = max(col_widths[3], len(str(human_ts(p["last_scan"] or ""))))
        col_widths[4] = max(col_widths[4], len(str(p["scans_count"])))

    # Print header
    fmt = f"{{:<{col_widths[0]}}}  {{:<{col_widths[1]}}}  {{:<{col_widths[2]}}}  {{:<{col_widths[3]}}}  {{:>{col_widths[4]}}}"
    print(fmt.format(*headers))
    print("-" * (sum(col_widths) + 8))

    for p in projects:
        print(fmt.format(
            p["project"],
            human_ts(p.get("created_at") or ""),
            human_ts(p["first_scan"] or ""),
            human_ts(p["last_scan"] or ""),
            p["scans_count"],
        ))


def human_ts(ts):
    """Return a human-friendly timestamp for various ISO/SQL formats.

    Repairs a common truncated timezone form like '-08:0' -> '-08:00'
    and falls back to a couple of common formats before returning raw string.
    """
    if not ts:
        return 'N/A'
    # Try strict ISO parse first
    try:
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo:
            return dt.strftime('%Y-%m-%d %H:%M:%S %z')
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        pass

    # Attempt to repair truncated timezone like '-08:0' -> '-08:00'
    try:
        m = re.search(r'([+-]\d{2}:\d)$', ts)
        if m:
            ts2 = ts + '0'
            try:
                dt = datetime.fromisoformat(ts2)
                if dt.tzinfo:
                    return dt.strftime('%Y-%m-%d %H:%M:%S %z')
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                pass
    except Exception:
        pass

    # Fallbacks for common SQL-like formats
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S'):
        try:
            dt = datetime.strptime(ts, fmt)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            continue
    return str(ts)
    return str(ts)


def main():
    parser = argparse.ArgumentParser(description="Rank projects stored in the scans DB.")
    parser.add_argument("--order", choices=["asc", "desc"], default="desc", help="Order by project creation date (asc or desc). Default: desc")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of projects shown")
    args = parser.parse_args()

    projects = rank_projects(order=args.order, limit=args.limit)
    print_projects(projects)


if __name__ == "__main__":
    main()
