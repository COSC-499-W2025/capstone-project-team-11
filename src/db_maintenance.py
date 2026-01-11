# src/db_maintenance.py
import sqlite3
from typing import Optional


def prune_old_project_scans(conn: sqlite3.Connection, project_name: str, keep_scan_id: int) -> int:
    """
    Deletes all older scans (and their file + join-table rows) for a given project,
    keeping only keep_scan_id.

    Returns:
        int: number of scans deleted
    """
    if not project_name:
        return 0

    cur = conn.cursor()

    # Find scans for this project that are NOT the one we just created
    cur.execute(
        """
        SELECT id
        FROM scans
        WHERE project = ?
          AND id != ?
        """,
        (project_name, keep_scan_id),
    )
    old_scan_ids = [row["id"] if isinstance(row, sqlite3.Row) else row[0] for row in cur.fetchall()]

    if not old_scan_ids:
        return 0

    placeholders = ",".join(["?"] * len(old_scan_ids))

    # Delete join-table rows first (file_languages, file_contributors)
    cur.execute(
        f"""
        DELETE FROM file_languages
        WHERE file_id IN (
            SELECT id FROM files WHERE scan_id IN ({placeholders})
        )
        """,
        old_scan_ids,
    )

    cur.execute(
        f"""
        DELETE FROM file_contributors
        WHERE file_id IN (
            SELECT id FROM files WHERE scan_id IN ({placeholders})
        )
        """,
        old_scan_ids,
    )

    # Delete files for those scans
    cur.execute(
        f"DELETE FROM files WHERE scan_id IN ({placeholders})",
        old_scan_ids,
    )

    # Delete old scans
    cur.execute(
        f"DELETE FROM scans WHERE id IN ({placeholders})",
        old_scan_ids,
    )

    return len(old_scan_ids)
