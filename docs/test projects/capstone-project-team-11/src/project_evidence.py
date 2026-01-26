from typing import List, Dict, Optional
import sqlite3
import os
from db import get_connection

# Valid evidence types - used for validation
EVIDENCE_TYPES = ['metric', 'feedback', 'award', 'testimonial', 'link', 'other']


def validate_evidence_type(ev_type: str) -> str:
    """Validate and normalize evidence type. Returns normalized type or raises ValueError."""
    if not ev_type:
        raise ValueError("Evidence type is required.")
    normalized = ev_type.lower().strip()
    if normalized not in EVIDENCE_TYPES:
        raise ValueError(f"Invalid type '{ev_type}'. Must be one of: {', '.join(EVIDENCE_TYPES)}")
    return normalized


def add_evidence(project_id: int, evidence_data: Dict) -> int:
    """Insert new evidence row and return the new id.
    
    Required fields: type, value (the statement)
    Optional fields: source, url
    The 'description' field is deprecated - use 'value' for the statement.
    """
    # Validate type
    ev_type = validate_evidence_type(evidence_data.get("type", ""))
    
    # Validate statement (stored in 'value' field)
    statement = evidence_data.get("value", "").strip() if evidence_data.get("value") else ""
    if not statement:
        raise ValueError("Evidence statement is required.")
    
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
                "type": ev_type,
                "description": "",  # Deprecated, leave empty
                "value": statement,
                "source": evidence_data.get("source", "").strip() if evidence_data.get("source") else "",
                "url": evidence_data.get("url", "").strip() if evidence_data.get("url") else "",
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


def get_project_id_by_name(project_name: str) -> Optional[int]:
    """Return the project_id for a given project name, or None if not found.
    
    This helper bridges the gap between output JSON files (which use project_name)
    and the project_evidence table (which uses project_id as a foreign key).
    """
    if not project_name:
        return None
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM projects WHERE name = ?", (project_name,))
        row = cur.fetchone()
        return row['id'] if row else None
    except Exception:
        return None
    finally:
        conn.close()


def format_evidence_for_resume(evidence_list: List[Dict], max_items: int = 2) -> Optional[str]:
    """Format evidence as a concise impact clause for resume bullets.
    
    Returns a single-line string suitable for appending as a bullet, or None if no evidence.
    Limits output to max_items to keep resume concise.
    """
    if not evidence_list:
        return None
    
    # Take only the first max_items (most recent, since ordered by created_at DESC)
    items = evidence_list[:max_items]
    
    parts = []
    for ev in items:
        # Statement is stored in 'value' field (fallback to 'description' for legacy data)
        statement = ev.get('value', '').strip() if ev.get('value') else ''
        if not statement:
            statement = ev.get('description', '').strip() if ev.get('description') else ''
        if not statement:
            continue
        
        source = ev.get('source', '').strip() if ev.get('source') else ''
        if source:
            parts.append(f"{statement} ({source})")
        else:
            parts.append(statement)
    
    if not parts:
        return None
    
    return "Impact: " + "; ".join(parts)


def format_evidence_for_portfolio(evidence_list: List[Dict]) -> Optional[str]:
    """Format evidence as a markdown section for portfolio output.
    
    Returns formatted markdown lines suitable for inclusion in a portfolio section,
    or None if no evidence exists.
    """
    if not evidence_list:
        return None
    
    lines = []
    for ev in evidence_list:
        ev_type = ev.get('type', 'evidence').capitalize()
        # Statement is stored in 'value' field (fallback to 'description' for legacy data)
        statement = ev.get('value', '').strip() if ev.get('value') else ''
        if not statement:
            statement = ev.get('description', '').strip() if ev.get('description') else ''
        if not statement:
            continue
        
        source = ev.get('source', '').strip() if ev.get('source') else ''
        
        # Build the evidence line
        if source:
            line = f"- **{ev_type}** ({source}): {statement}"
        else:
            line = f"- **{ev_type}**: {statement}"
        
        lines.append(line)
    
    return "\n".join(lines) if lines else None


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
        source_str = f"({ev['source']})" if ev.get('source') and ev['source'].strip() else ""
        # Statement is in 'value' field (fallback to 'description' for legacy)
        statement = ev.get('value', '').strip() if ev.get('value') else ''
        if not statement:
            statement = ev.get('description', '').strip() if ev.get('description') else ''
        statement = statement or "(no statement)"

        main_line = f"- **{type_str}** {source_str}: {statement}"

        # URL – shorten if very long
        if ev.get('url') and ev['url'].strip():
            url = ev['url'].strip()
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
                # Statement is in 'value' field (fallback to 'description' for legacy)
                statement = ev.get('value', '').strip() or ev.get('description', '').strip() or "(empty)"
                source_str = f" ({ev['source']})" if ev.get('source') else ""
                print(f"  {idx}. [{ev['type']}] {statement}{source_str}")

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
                print(f"\nValid types: {', '.join(EVIDENCE_TYPES)}")
                ev_type = input("Type: ").strip()
                statement = input("Statement: ").strip()
                source = input("Source (optional): ").strip()
                
                ev_data = {
                    "type": ev_type,
                    "value": statement,
                    "source": source,
                }
                try:
                    ev_id = add_evidence(project_id, ev_data)
                    source_str = f" ({source})" if source else ""
                    print(f"✓ Added: [{ev_type}] {statement}{source_str}")
                    # Refresh evidence list
                    evidence = get_evidence_for_project(project_id)
                except ValueError as e:
                    print(f"Error: {e}")
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
                ev_record = evidence[int(ev_idx) - 1]
                ev_id = ev_record['id']
                current_statement = ev_record.get('value', '').strip() or ev_record.get('description', '')
                
                print(f"\nEditing: [{ev_record['type']}] {current_statement}")
                print("(Press Enter to keep current value)\n")
                
                updates = {}
                new_type = input(f"Type [{ev_record['type']}]: ").strip()
                if new_type:
                    try:
                        updates["type"] = validate_evidence_type(new_type)
                    except ValueError as e:
                        print(f"Error: {e}")
                        continue
                
                new_statement = input(f"Statement [{current_statement}]: ").strip()
                if new_statement:
                    updates["value"] = new_statement
                
                new_source = input(f"Source [{ev_record.get('source', '')}]: ").strip()
                if new_source:
                    updates["source"] = new_source
                
                try:
                    if updates and update_evidence(ev_id, updates):
                        print("✓ Evidence updated.")
                        # Refresh evidence list
                        evidence = get_evidence_for_project(project_id)
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

