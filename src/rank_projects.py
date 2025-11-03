"""Rank projects recorded in the scans database and display them chronologically.

This script aggregates entries in the `scans` table by `project` and prints
the project's first scan time, last scan time, and number of scans. By
default it sorts by the most recent scan (descending). Use --order asc to
show oldest-first.

Usage:
  python src/rank_projects.py [--order asc|desc] [--limit N]
"""
from __future__ import annotations

import argparse
import sqlite3
from typing import List, Dict, Optional

from db import get_connection


def rank_projects(order: str = "desc", limit: Optional[int] = None) -> List[Dict]:
    """Return a list of projects aggregated from the scans table.

    Each item is a dict: {project, first_scan, last_scan, scans_count}.
    `order` must be 'asc' or 'desc' and controls ordering by last_scan.
    """
    order = order.lower()
    if order not in ("asc", "desc"):
        raise ValueError("order must be 'asc' or 'desc'")

    conn = get_connection()
    cur = conn.cursor()

    sql = (
        "SELECT COALESCE(project, '<unknown>') as project,"
        " MIN(scanned_at) as first_scan,"
        " MAX(scanned_at) as last_scan,"
        " COUNT(*) as scans_count"
        " FROM scans"
        " GROUP BY project"
        f" ORDER BY last_scan {order.upper()}"
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

    headers = ["Project", "First Scan", "Last Scan", "Scans"]
    # Compute column widths
    col_widths = [len(h) for h in headers]
    for p in projects:
        col_widths[0] = max(col_widths[0], len(str(p["project"])))
        col_widths[1] = max(col_widths[1], len(str(p["first_scan"] or "")))
        col_widths[2] = max(col_widths[2], len(str(p["last_scan"] or "")))
        col_widths[3] = max(col_widths[3], len(str(p["scans_count"])))

    # Print header
    fmt = f"{{:<{col_widths[0]}}}  {{:<{col_widths[1]}}}  {{:<{col_widths[2]}}}  {{:>{col_widths[3]}}}"
    print(fmt.format(*headers))
    print("-" * (sum(col_widths) + 6))

    for p in projects:
        print(fmt.format(p["project"], p["first_scan"] or "", p["last_scan"] or "", p["scans_count"]))


def main():
    parser = argparse.ArgumentParser(description="Rank projects stored in the scans DB.")
    parser.add_argument("--order", choices=["asc", "desc"], default="desc", help="Order by last scan (asc or desc). Default: desc")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of projects shown")
    args = parser.parse_args()

    projects = rank_projects(order=args.order, limit=args.limit)
    print_projects(projects)


if __name__ == "__main__":
    main()
