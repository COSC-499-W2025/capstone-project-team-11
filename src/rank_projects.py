# Rank projects recorded in the scans database and display them chronologically.
from __future__ import annotations

import argparse
import sys
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime
import re

from db import get_connection
from sqlite3 import OperationalError
from contrib_metrics import canonical_username


def _get_project_collaboration_status(project_name: str) -> str:
    """Determine if a project is collaborative or individual based on contributor count.
    
    Returns 'Collaborative' if the project has 2+ unique contributors, 'Individual' otherwise.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Count distinct contributors for this project
        cur.execute(
            "SELECT COUNT(DISTINCT c.id) AS contrib_count "
            "FROM contributors c "
            "JOIN file_contributors fc ON c.id = fc.contributor_id "
            "JOIN files f ON fc.file_id = f.id "
            "JOIN scans s ON f.scan_id = s.id "
            "WHERE s.project = ?",
            (project_name,)
        )
        row = cur.fetchone()
        contrib_count = row['contrib_count'] if row else 0
        
        if contrib_count >= 2:
            return "Collaborative"
        else:
            return "Individual"
    except Exception:
        return "Individual"


def _get_all_contributors() -> List[str]:
    """Get a sorted list of all unique contributor names from the database, normalized.
    
    Filters out non-human contributors like the GitHub Classroom bot.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT DISTINCT name FROM contributors ORDER BY name")
        rows = cur.fetchall()
        normalized = [canonical_username(row['name']) for row in rows]
        # Remove duplicates while preserving order
        seen = set()
        contributors = [x for x in normalized if not (x in seen or seen.add(x))]
        # Filter out GitHub Classroom bot and other non-human contributors
        filtered = [c for c in contributors if c and 'classroom' not in c.lower() and 'bot' not in c.lower()]
        return filtered
    except Exception:
        return []


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
        # Do not close the connection here because tests may patch get_connection
        # and rely on the caller-managed connection lifecycle.
        pass

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
    headers = ["Project", "Type", "Created", "First Scan", "Last Scan", "Scans"]
    # Compute column widths
    col_widths = [len(h) for h in headers]
    for p in projects:
        col_widths[0] = max(col_widths[0], len(str(p["project"])))
        collab_status = _get_project_collaboration_status(p["project"])
        col_widths[1] = max(col_widths[1], len(collab_status))
        col_widths[2] = max(col_widths[2], len(str(human_ts(p.get("created_at") or ""))))
        col_widths[3] = max(col_widths[3], len(str(human_ts(p["first_scan"] or ""))))
        col_widths[4] = max(col_widths[4], len(str(human_ts(p["last_scan"] or ""))))
        col_widths[5] = max(col_widths[5], len(str(p["scans_count"])))

    # Print header
    fmt = f"{{:<{col_widths[0]}}}  {{:<{col_widths[1]}}}  {{:<{col_widths[2]}}}  {{:<{col_widths[3]}}}  {{:<{col_widths[4]}}}  {{:>{col_widths[5]}}}"
    print(fmt.format(*headers))
    print("-" * (sum(col_widths) + 12))

    for p in projects:
        collab_status = _get_project_collaboration_status(p["project"])
        print(fmt.format(
            p["project"],
            collab_status,
            human_ts(p.get("created_at") or ""),
            human_ts(p["first_scan"] or ""),
            human_ts(p["last_scan"] or ""),
            p["scans_count"],
        ))


def rank_projects_contribution_summary(limit: Optional[int] = None) -> List[Dict]:
    """Return a summary list of projects with contribution stats.

    Each item: {project, total_files, contributors_count, top_contributor, top_contrib_files, top_fraction, top_score}
    """
    # Deprecated wrapper: use unified rank_projects_by_importance
    return rank_projects_by_importance(mode="project", limit=limit)


def print_projects_contribution_summary(projects: List[Dict]):
    if not projects:
        print("No contribution summary available.")
        return
    headers = ["Project", "Type", "TotalFiles", "Contributors", "TopContributor", "TopFiles", "TopFraction", "TopScore"]
    col_widths = [len(h) for h in headers]
    for p in projects:
        col_widths[0] = max(col_widths[0], len(str(p["project"])))
        collab_status = _get_project_collaboration_status(p["project"])
        col_widths[1] = max(col_widths[1], len(collab_status))
        col_widths[2] = max(col_widths[2], len(str(p.get("total_files", 0))))
        col_widths[3] = max(col_widths[3], len(str(p.get("contributors_count", 0))))
        col_widths[4] = max(col_widths[4], len(str(p.get("top_contributor") or "")))
        col_widths[5] = max(col_widths[5], len(str(p.get("top_contrib_files", 0))))
        col_widths[6] = max(col_widths[6], len("0.00"))
        col_widths[7] = max(col_widths[7], len("0.00"))

    fmt = (
        f"{{:<{col_widths[0]}}}  {{:<{col_widths[1]}}}  {{:>{col_widths[2]}}}  {{:>{col_widths[3]}}}  {{:<{col_widths[4]}}}  "
        f"{{:>{col_widths[5]}}}  {{:>{col_widths[6]}}}  {{:>{col_widths[7]}}}"
    )
    print(fmt.format(*headers))
    print("-" * (sum(col_widths) + 16))
    for p in projects:
        collab_status = _get_project_collaboration_status(p["project"])
        print(fmt.format(
            p["project"],
            collab_status,
            p.get("total_files", 0),
            p.get("contributors_count", 0),
            p.get("top_contributor") or "",
            p.get("top_contrib_files", 0),
            f"{p.get('top_fraction', 0.0):.2f}",
            f"{p.get('top_score', 0.0):.2f}",
        ))

    # Briefly explain the metric so CLI output is self-documenting.
    print("\n=== Scoring Explanation ===")
    print("TopFraction = fraction of files contributed by the top contributor.")
    print()
    print("TopScore (project-level) = 60% coverage + 30% dominance gap + 10% team-size factor")
    print("  * Coverage (60%): Percentage of project files touched by the top contributor.")
    print("    Higher coverage indicates a more central role in the project.")
    print()
    print("  * Dominance Gap (30%): Lead of the top contributor over the next highest.")
    print("    Measured as (top_files - second_files) / total_files.")
    print("    Higher gap indicates the top contributor had a more distinct/leading role.")
    print()
    print("  * Team-Size Factor (10%): Inverse of contributor count (1 / num_contributors).")
    print("    Smaller teams get slightly higher scores since individual influence per person is larger.")
    print()
    print("Contributor score (per-user view) uses the same formula for consistent ranking.")


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


def rank_projects_by_contributor(contributor_name: str, limit: Optional[int] = None) -> List[Dict]:
    """Return projects ranked by how important they are to `contributor_name`.

    Importance uses a composite score (coverage, dominance gap, team size)
    rather than a simple "percent of files touched" so that small sample sizes
    and uneven team splits are handled more robustly.
    """
    # Deprecated wrapper: use unified rank_projects_by_importance
    return rank_projects_by_importance(mode="contributor", contributor_name=contributor_name, limit=limit)


def rank_projects_by_importance(mode: str = "project", contributor_name: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
    """Unified function to compute importance-based rankings.

    mode: 'project' -> return per-project contribution summaries
          'contributor' -> return per-project importance for the given contributor_name
    This consolidates the previous two separate implementations.
    """
    mode = (mode or "project").lower()
    conn = get_connection()
    cur = conn.cursor()
    try:
        # total files per project (used by both modes)
        cur.execute(
            "SELECT s.project AS project, COUNT(f.id) AS total_files "
            "FROM scans s JOIN files f ON f.scan_id = s.id "
            "GROUP BY s.project"
        )
        totals = {row[0]: row[1] for row in cur.fetchall()}

        if mode == "project":
            cur.execute(
                "SELECT s.project AS project, c.name AS contributor, COUNT(DISTINCT f.id) AS file_count "
                "FROM scans s "
                "JOIN files f ON f.scan_id = s.id "
                "JOIN file_contributors fc ON fc.file_id = f.id "
                "JOIN contributors c ON c.id = fc.contributor_id "
                "GROUP BY s.project, c.id "
                "ORDER BY s.project"
            )
            rows = cur.fetchall()

            proj_map = {}
            for project, total in totals.items():
                proj_map[project] = {
                    "project": project,
                    "total_files": total,
                    "contributors_count": 0,
                    "top_contributor": None,
                    "top_contrib_files": 0,
                    "top_fraction": 0.0,
                    "_contributors": {},
                }

            for r in rows:
                project = r[0]
                raw_contrib = r[1]
                fcount = r[2]
                # normalize contributor name using canonical_username to match contrib_metrics
                contrib = canonical_username(raw_contrib or "")
                if project not in proj_map:
                    proj_map[project] = {
                        "project": project,
                        "total_files": totals.get(project, 0),
                        "contributors_count": 0,
                        "top_contributor": None,
                        "top_contrib_files": 0,
                        "top_fraction": 0.0,
                        "_contributors": {},
                    }
                # accumulate counts for the canonical contributor key
                proj_map[project]["_contributors"][contrib] = proj_map[project]["_contributors"].get(contrib, 0) + fcount

            # finalize stats
            result = []
            for p, info in proj_map.items():
                contribs = info.pop("_contributors", {})
                info["contributors_count"] = len(contribs)
                if contribs:
                    top_name = max(contribs.items(), key=lambda x: x[1])[0]
                    top_files = contribs[top_name]
                    info["top_contributor"] = top_name
                    info["top_contrib_files"] = top_files
                    total = info.get("total_files") or 0
                    second_count = sorted(contribs.values(), reverse=True)[1] if len(contribs) > 1 else 0
                    coverage = float(top_files) / float(total) if total > 0 else 0.0
                    dominance_gap = (top_files - second_count) / float(total) if total > 0 else 0.0
                    team_factor = 1.0 / float(info["contributors_count"]) if info["contributors_count"] > 0 else 0.0
                    info["top_fraction"] = coverage
                    info["top_score"] = (0.6 * coverage) + (0.3 * dominance_gap) + (0.1 * team_factor)
                else:
                    info["top_fraction"] = 0.0
                    info["top_score"] = 0.0
                result.append(info)

            # sort by composite score, then coverage, then size
            result.sort(key=lambda x: (-x.get("top_score", 0.0), -x.get("top_fraction", 0.0), -x.get("total_files", 0), x["project"]))
            if limit is not None and isinstance(limit, int) and limit > 0:
                return result[:limit]
            return result

        elif mode == "contributor":
            if not contributor_name:
                return []
            # Fetch all contributor counts and canonicalize names, then filter by canonical contributor_name.
            # Score is intentionally more robust than a raw "percent of files touched" metric by blending three factors:
            #   - Coverage (60%): Fraction of files touched in the project by this contributor.
            #     A contributor touching more files shows broader project engagement.
            #   - Dominance Gap (30%): Lead over the next highest contributor, measured as
            #     (this_contrib_files - second_highest_files) / total_files.
            #     This measures how distinctly this person led compared to peers.
            #     Only counts if this contributor is in the top position.
            #   - Team Size Factor (10%): Computed as 1 / number_of_contributors.
            #     Smaller teams give individuals more influence per capita, reflecting
            #     the reality that one person's work matters more in a 2-person team
            #     than in a 10-person team.
            cur.execute(
                "SELECT s.project AS project, c.name AS contributor, COUNT(DISTINCT f.id) AS contrib_files "
                "FROM scans s "
                "JOIN files f ON f.scan_id = s.id "
                "JOIN file_contributors fc ON fc.file_id = f.id "
                "JOIN contributors c ON c.id = fc.contributor_id "
                "GROUP BY s.project, c.id",
            )
            rows = cur.fetchall()

            # canonicalize the input contributor name for matching
            target = canonical_username(contributor_name or "")
            per_project: Dict[str, Dict[str, int]] = {}
            for r in rows:
                project = r[0]
                raw_contrib = r[1]
                contrib_files = r[2]
                canon = canonical_username(raw_contrib or "")
                per_project.setdefault(project, {})
                per_project[project][canon] = per_project[project].get(canon, 0) + contrib_files

            result = []
            for project, contribs in per_project.items():
                if target not in contribs:
                    continue

                total = totals.get(project, 0)
                contrib_files = contribs.get(target, 0)
                contributors_count = len(contribs)

                coverage = float(contrib_files) / float(total) if total > 0 else 0.0

                # dominance measures how far ahead the contributor is compared to the next highest contributor
                sorted_counts = sorted(contribs.values(), reverse=True)
                top_count = sorted_counts[0]
                second_count = sorted_counts[1] if len(sorted_counts) > 1 else 0
                dominance_gap = (contrib_files - second_count) / float(total) if total > 0 and contrib_files == top_count else 0.0

                team_factor = 1.0 / float(contributors_count) if contributors_count > 0 else 0.0

                # Weighted composite score for stability across different project sizes/team sizes
                score = (0.6 * coverage) + (0.3 * dominance_gap) + (0.1 * team_factor)

                result.append({
                    "project": project,
                    "contrib_files": contrib_files,
                    "total_files": total,
                    "contributors_count": contributors_count,
                    "score": score,
                })

            result.sort(key=lambda x: (-x["score"], -x["contrib_files"], x["project"]))
            if limit is not None and isinstance(limit, int) and limit > 0:
                return result[:limit]
            return result

        else:
            return []
    finally:
        # Do not close the connection here for the same reason as above.
        pass


def print_projects_by_contributor(projects: List[Dict], contributor_name: str):
    """Print a compact table of projects and the contributor's importance score."""
    if not projects:
        print(f"No projects found for contributor '{contributor_name}'.")
        return
    headers = ["Project", "Type", "ContribFiles", "TotalFiles", "Score"]
    col_widths = [len(h) for h in headers]
    for p in projects:
        col_widths[0] = max(col_widths[0], len(str(p["project"])))
        collab_status = _get_project_collaboration_status(p["project"])
        col_widths[1] = max(col_widths[1], len(collab_status))
        col_widths[2] = max(col_widths[2], len(str(p["contrib_files"])))
        col_widths[3] = max(col_widths[3], len(str(p["total_files"])))
        col_widths[4] = max(col_widths[4], len("0.00"))

    fmt = f"{{:<{col_widths[0]}}}  {{:<{col_widths[1]}}}  {{:>{col_widths[2]}}}  {{:>{col_widths[3]}}}  {{:>{col_widths[4]}}}"
    print(fmt.format(*headers))
    print("-" * (sum(col_widths) + 10))
    for p in projects:
        collab_status = _get_project_collaboration_status(p["project"])
        print(fmt.format(p["project"], collab_status, p["contrib_files"], p["total_files"], f"{p['score']:.2f}"))


def main():
    parser = argparse.ArgumentParser(description="Rank projects stored in the scans DB.")
    parser.add_argument("--order", choices=["asc", "desc"], default="desc", help="Order by project creation date (asc or desc). Default: desc")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of projects shown")
    parser.add_argument("--by-user", dest="by_user", default=None, help="Rank projects by importance for a given contributor name")
    args = parser.parse_args()

    # Always print projects ordered by creation date first
    print(f"Ranking projects by creation date (order={args.order})\n")
    projects = rank_projects(order=args.order, limit=args.limit)
    print_projects(projects)

    # Always print a project-level contributions summary table
    print('\nProject-level contributions summary:')
    contrib_summary = rank_projects_contribution_summary(limit=args.limit)
    print_projects_contribution_summary(contrib_summary)

    # If a specific contributor was requested via CLI flag, print their per-project importance table
    if args.by_user:
        print(f"\nRanking projects by contributor: {args.by_user}\n")
        user_projects = rank_projects_by_contributor(args.by_user, limit=args.limit)
        print_projects_by_contributor(user_projects, args.by_user)
    else:
        # Otherwise, if running interactively, ask the user whether they'd like a per-user ranking
        try:
            if sys.stdin and sys.stdin.isatty():
                # Display available contributors
                contributors = _get_all_contributors()
                if contributors:
                    print("\n=== Available Contributors ===")
                    for i, contrib in enumerate(contributors, 1):
                        print(f"  {i}. {contrib}")
                    print()
                    
                    user_input = input('Enter a contributor name or number to show per-project importance (leave blank to skip): ').strip()
                    if user_input:
                        # Check if user entered a number
                        name = None
                        try:
                            index = int(user_input) - 1
                            if 0 <= index < len(contributors):
                                name = contributors[index]
                            else:
                                print(f"Invalid number. Please enter a number between 1 and {len(contributors)}.")
                        except ValueError:
                            # User entered a name, not a number
                            name = user_input
                        
                        if name:
                            print(f"\nRanking projects by contributor: {name}\n")
                            user_projects = rank_projects_by_contributor(name, limit=args.limit)
                            print_projects_by_contributor(user_projects, name)
        except Exception:
            # If input isn't available (non-interactive), simply skip
            pass

if __name__ == "__main__":
    main()
