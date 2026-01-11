from typing import List, Dict, Optional
import sqlite3
import os
from db import get_connection

def add_evidence(project_id: int, evidence_data: Dict) -> int:
    """Insert new evidence row and return the new id."""
    conn = get_connection()
    conn.execute('PRAGMA foreign_keys = ON')
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO project_evidence (project_id, type, description, value, source, url, added_by_user)
            VALUES (:project_id, :type, :description, :value, :source, :url, :added_by_user)
            """,
            {
                "project_id": project_id,
                "type": evidence_data.get("type"),
                "description": evidence_data.get("description"),
                "value": evidence_data.get("value"),
                "source": evidence_data.get("source"),
                "url": evidence_data.get("url"),
                "added_by_user": evidence_data.get("added_by_user", True),
            },
        )
        conn.commit()
        return cur.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_evidence_for_project(project_id: int) -> List[Dict]:
    """Return list of evidence dicts for a project, ordered by created_at DESC."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT id, project_id, type, description, value, source, url, added_by_user, created_at
            FROM project_evidence
            WHERE project_id = ?
            ORDER BY created_at DESC
            """,
            (project_id,),
        )
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def update_evidence(ev_id: int, updates: Dict) -> bool:
    """Update specific fields in an evidence row."""
    if not updates:
        return False
    conn = get_connection()
    conn.execute('PRAGMA foreign_keys = ON')
    cur = conn.cursor()
    try:
        fields = ", ".join(f"{key} = :{key}" for key in updates.keys())
        updates["id"] = ev_id
        cur.execute(
            f"UPDATE project_evidence SET {fields} WHERE id = :id",
            updates,
        )
        conn.commit()
        return cur.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def delete_evidence(ev_id: int) -> bool:
    """Delete evidence by id."""
    conn = get_connection()
    conn.execute('PRAGMA foreign_keys = ON')
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM project_evidence WHERE id = ?", (ev_id,))
        conn.commit()
        return cur.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def format_evidence_list(evidence_list: List[Dict]) -> str:
    """
    Return a clean markdown-formatted string of all evidence items.
    Designed for both CLI display and future portfolio/resume outputs.
    """
    if not evidence_list:
        return "No evidence of success added yet."

    lines = []
    for ev in evidence_list:
        type_str = ev['type'].capitalize()
        source_str = f"({ev['source']})" if ev['source'] and ev['source'].strip() else ""
        value_str = ev['value'].strip() if ev['value'] and ev['value'].strip() else "(no value provided)"

        main_line = f"- **{type_str}** {source_str}: {value_str}"

        # Indented description
        if ev.get('description') and ev['description'].strip():
            main_line += f"\n  {ev['description'].strip()}"

        # URL – shorten if very long
        if ev.get('url') and ev['url'].strip():
            url = ev['url'].strip()
            display_url = url[:60] + '...' if len(url) > 60 else url
            main_line += f"\n  [View →]({url})"

        # Timestamp – only show date+time, cut microseconds
        if ev.get('created_at'):
            ts = ev['created_at'].split('.')[0]  # remove microseconds if present
            main_line += f"  *(Added: {ts})*"

        lines.append(main_line)

    return "\n\n".join(lines)

def handle_project_evidence():
    """Manage evidence of success for a project."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Check if projects exist
        cur.execute("SELECT id, name, repo_url FROM projects ORDER BY name")
        projects = cur.fetchall()
        if not projects:
            print("No projects found in the database.")
            return

        # Display projects
        print("\nAvailable Projects:")
        for project in projects:
            print(f"  {project['id']}. {project['name']} (Repo: {project['repo_url'] or 'N/A'})")

        # Prompt for project ID
        project_id = input("\nEnter the project ID to manage evidence: ").strip()
        if not project_id.isdigit() or int(project_id) not in [p['id'] for p in projects]:
            print("Invalid project ID.")
            return
        project_id = int(project_id)

        # Show current evidence
        evidence = get_evidence_for_project(project_id)
        print("\nCurrent Evidence:")
        if not evidence:
            print("  No evidence found for this project.")
        else:
            for idx, ev in enumerate(evidence, start=1):
                print(f"  {idx}. {ev['type']} | {ev['description']} | {ev['value']} | {ev['source']} | {ev['url'] or 'N/A'}")

        # Sub-menu loop
        while True:
            print("\nEvidence Management:")
            print("1. Add new evidence")
            print("2. Edit existing evidence")
            print("3. Delete evidence")
            print("4. Back")
            choice = input("Select an option: ").strip()

            if choice == "1":
                # Add new evidence
                ev_type = input("Enter evidence type (e.g., metric, feedback, award, link, other): ").strip()
                description = input("Enter a short description: ").strip()
                value = input("Enter the value/content: ").strip()
                source = input("Enter the source (e.g., GitHub, Email): ").strip()
                url = input("Enter a URL (optional): ").strip()
                added_by_user = True
                ev_data = {
                    "type": ev_type,
                    "description": description,
                    "value": value,
                    "source": source,
                    "url": url,
                    "added_by_user": added_by_user,
                }
                try:
                    ev_id = add_evidence(project_id, ev_data)
                    print(f"Evidence added successfully with ID {ev_id}.")
                except Exception as e:
                    print(f"Failed to add evidence: {e}")

            elif choice == "2":
                # Edit existing evidence
                if not evidence:
                    print("No evidence to edit.")
                    continue
                ev_idx = input("Enter the number of the evidence to edit: ").strip()
                if not ev_idx.isdigit() or int(ev_idx) not in range(1, len(evidence) + 1):
                    print("Invalid selection.")
                    continue
                ev_id = evidence[int(ev_idx) - 1]['id']
                updates = {}
                if input("Update type? (y/n): ").strip().lower() == "y":
                    updates["type"] = input("Enter new type: ").strip()
                if input("Update description? (y/n): ").strip().lower() == "y":
                    updates["description"] = input("Enter new description: ").strip()
                if input("Update value? (y/n): ").strip().lower() == "y":
                    updates["value"] = input("Enter new value: ").strip()
                if input("Update source? (y/n): ").strip().lower() == "y":
                    updates["source"] = input("Enter new source: ").strip()
                if input("Update URL? (y/n): ").strip().lower() == "y":
                    updates["url"] = input("Enter new URL: ").strip()
                try:
                    if update_evidence(ev_id, updates):
                        print("Evidence updated successfully.")
                    else:
                        print("No changes made.")
                except Exception as e:
                    print(f"Failed to update evidence: {e}")

            elif choice == "3":
                # Delete evidence
                if not evidence:
                    print("No evidence to delete.")
                    continue
                ev_idx = input("Enter the number of the evidence to delete: ").strip()
                if not ev_idx.isdigit() or int(ev_idx) not in range(1, len(evidence) + 1):
                    print("Invalid selection.")
                    continue
                ev_id = evidence[int(ev_idx) - 1]['id']
                try:
                    if delete_evidence(ev_id):
                        print("Evidence deleted successfully.")
                        evidence = [ev for ev in evidence if ev['id'] != ev_id]
                    else:
                        print("Failed to delete evidence.")
                except Exception as e:
                    print(f"Failed to delete evidence: {e}")

            elif choice == "4":
                # Back to main menu
                break

            else:
                print("Invalid option. Please select a valid number.")
    finally:
        conn.close()

