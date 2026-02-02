"""
thumbnail_manager.py
---------------------------------
Helpers for viewing and editing project thumbnails.
"""

import os

from db import get_connection, _ensure_projects_thumbnail_column
from file_utils import is_image_file


def _list_projects():
    with get_connection() as conn:
        _ensure_projects_thumbnail_column(conn)
        rows = conn.execute(
            "SELECT id, name, thumbnail_path FROM projects ORDER BY name COLLATE NOCASE"
        ).fetchall()
    return rows


def _print_projects(projects):
    print("\nAvailable projects:")
    for row in projects:
        thumb = row["thumbnail_path"] if row["thumbnail_path"] else "<none>"
        print(f"  {row['id']}. {row['name']}  | thumbnail: {thumb}")


def _select_project(projects):
    project_ids = {str(row["id"]) for row in projects}
    choice = input("\nEnter project ID (blank to cancel): ").strip()
    if not choice:
        return None
    if choice not in project_ids:
        print("Invalid project ID.")
        return None
    return int(choice)


def _prompt_action():
    action = input("Choose action: (a)dd/update, (r)emove, (c)ancel [a]: ").strip().lower() or "a"
    if action not in {"a", "r", "c"}:
        print("Invalid action.")
        return None
    return action


def _update_thumbnail(project_id, path):
    if not os.path.isfile(path):
        print("Thumbnail path does not point to a file.")
        return False
    if not is_image_file(path):
        print("Unsupported image type. Please use a common image format (e.g., .png, .jpg).")
        return False
    with get_connection() as conn:
        _ensure_projects_thumbnail_column(conn)
        conn.execute(
            "UPDATE projects SET thumbnail_path = ? WHERE id = ?",
            (path, project_id),
        )
        conn.commit()
    return True


def _remove_thumbnail(project_id):
    with get_connection() as conn:
        _ensure_projects_thumbnail_column(conn)
        conn.execute(
            "UPDATE projects SET thumbnail_path = NULL WHERE id = ?",
            (project_id,),
        )
        conn.commit()


def handle_edit_project_thumbnail():
    """Menu flow to edit a project's thumbnail path."""
    print("\n=== Edit Thumbnail for a Project ===")
    projects = _list_projects()
    if not projects:
        print("No projects found in database.")
        return

    _print_projects(projects)
    project_id = _select_project(projects)
    if project_id is None:
        return

    action = _prompt_action()
    if action in (None, "c"):
        return

    if action == "r":
        _remove_thumbnail(project_id)
        print("Thumbnail removed from database.")
        return

    path = input("Enter path to thumbnail image (blank to cancel): ").strip()
    if not path:
        print("No path provided. Cancelled.")
        return
    if _update_thumbnail(project_id, path):
        print("Thumbnail updated.")
