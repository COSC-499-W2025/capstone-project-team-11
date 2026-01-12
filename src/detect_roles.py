"""Low-level role detection for project contributors.

This module analyzes contributor activity patterns across a project to categorize
roles without using an LLM. It uses file extensions, content patterns, and activity
metrics to infer roles such as:
- Backend Developer
- Frontend Developer
- Full Stack Developer
- Mobile Developer
- Data Scientist / ML Engineer
- Game Developer
- DevOps / Infrastructure
- QA / Tester
- UI/UX Designer
- Project Lead / Architect
"""

from typing import Dict, List, Optional
from collections import defaultdict, Counter
import os
from contrib_metrics import classify_file, canonical_username


# File extension patterns for role detection
ROLE_PATTERNS = {
    'Backend Developer': {
        'extensions': {'.py', '.java', '.go', '.rs', '.c', '.cpp', '.php', '.rb', '.cs'},
        'keywords': ['backend', 'server', 'api', 'database', 'model'],
    },
    'Frontend Developer': {
        'extensions': {'.js', '.ts', '.jsx', '.tsx', '.vue', '.html', '.css', '.scss'},
        'keywords': ['frontend', 'react', 'vue', 'angular', 'ui', 'component'],
    },
    'Mobile Developer': {
        'extensions': {'.swift', '.kt', '.dart', '.m', '.mm'},
        'keywords': ['mobile', 'android', 'ios', 'flutter', 'xcode'],
    },
    'Data Scientist / ML Engineer': {
        'extensions': {'.py', '.r', '.sql', '.ipynb'},
        'keywords': ['data', 'ml', 'machine learning', 'numpy', 'pandas', 'tensorflow', 'keras'],
    },
    'Game Developer': {
        'extensions': {'.cs', '.cpp', '.shader'},
        'keywords': ['game', 'unity', 'unreal', 'godot', 'engine'],
    },
    'DevOps / Infrastructure': {
        'extensions': {'.yml', '.yaml', '.tf', '.json', '.dockerfile', '.sh', '.bash'},
        'keywords': ['docker', 'kubernetes', 'terraform', 'ansible', 'devops', 'infrastructure'],
    },
    'QA / Tester': {
        'extensions': {'.py', '.js', '.java', '.ts'},
        'keywords': ['test', 'spec', 'pytest', 'jest', 'junit'],
    },
    'UI/UX Designer': {
        'extensions': {'.png', '.jpg', '.svg', '.psd', '.sketch', '.xd', '.figma'},
        'keywords': ['design', 'ui', 'ux', 'mockup'],
    },
}

# Minimum contribution levels to assign a role
MIN_TOTAL_FILES = 3        # Must have at least 3 file contributions


def categorize_contributor_role(
    contributor_name: str,
    files_changed: List[str],
    commits: int,
    lines_added: int,
    lines_removed: int,
    activity_by_category: Dict[str, int]
) -> Dict:
    """
    Categorize a single contributor's role based on their activity patterns.
    
    Args:
        contributor_name: Name of the contributor
        files_changed: List of file paths the contributor modified
        commits: Number of commits by this contributor
        lines_added: Total lines added by this contributor
        lines_removed: Total lines removed by this contributor
        activity_by_category: Dict with keys (code, test, docs, design, other)
                            containing activity counts per category
    
    Returns:
        Dict with keys:
            - name: contributor name
            - primary_role: Main categorized role
            - secondary_roles: List of additional roles detected
            - confidence: Score 0.0-1.0 indicating role certainty
            - contribution_breakdown: Dict with percentages per category
            - metrics: Raw contribution metrics
    """
    if not files_changed or len(files_changed) < MIN_TOTAL_FILES:
        return {
            "name": canonical_username(contributor_name),
            "primary_role": "Contributor",
            "secondary_roles": [],
            "confidence": 0.0,
            "contribution_breakdown": {},
            "metrics": {
                "total_files": len(files_changed) if files_changed else 0,
                "commits": commits,
                "lines_added": lines_added,
                "lines_removed": lines_removed,
            }
        }
    
    # Classify each file and count contributions per category
    category_counts = Counter(activity_by_category)
    total_activity = sum(category_counts.values()) or 1
    
    # Calculate percentages
    contribution_breakdown = {
        cat: (count / total_activity) * 100
        for cat, count in category_counts.items()
    }
    
    # Determine primary and secondary roles based on file patterns
    role_scores = _calculate_role_scores(files_changed, contribution_breakdown)
    
    # Get ranked roles
    sorted_roles = sorted(role_scores.items(), key=lambda x: -x[1])
    roles = [role for role, score in sorted_roles if score > 0]
    
    # Detect Full Stack if multiple major roles detected with significant scores
    if len(roles) >= 3 and len(files_changed) > 10:
        # Check if roles have balanced scores (not just one dominating)
        top_score = sorted_roles[0][1] if sorted_roles else 1
        second_score = sorted_roles[1][1] if len(sorted_roles) > 1 else 0
        third_score = sorted_roles[2][1] if len(sorted_roles) > 2 else 0
        # Full Stack only if roles are reasonably balanced (not >5x difference)
        if top_score > 0 and second_score > top_score * 0.3:
            roles.insert(0, 'Full Stack Developer')
    
    # Detect Project Lead if very high activity
    if commits > 20 and len(files_changed) > 15:
        roles.insert(0, 'Project Lead / Architect')
    
    # Fallback if no roles detected
    if not roles:
        roles.append("Developer")
    
    primary_role = roles[0]
    secondary_roles = roles[1:4] if len(roles) > 1 else []  # Limit to 3 secondary roles
    
    # Calculate confidence
    confidence = _calculate_role_confidence(primary_role, sorted_roles)
    
    return {
        "name": canonical_username(contributor_name),
        "primary_role": primary_role,
        "secondary_roles": secondary_roles,
        "confidence": confidence,
        "contribution_breakdown": {
            cat: round(pct, 2)
            for cat, pct in contribution_breakdown.items()
        },
        "metrics": {
            "total_files": len(files_changed),
            "commits": commits,
            "lines_added": lines_added,
            "lines_removed": lines_removed,
            "avg_lines_per_commit": round(lines_added / commits, 1) if commits > 0 else 0,
        }
    }


def _calculate_role_scores(files_changed: List[str], breakdown: Dict[str, float]) -> Dict[str, float]:
    """
    Calculate role scores based on file extensions and patterns.
    
    Returns a dict mapping role names to scores.
    """
    role_scores = defaultdict(float)
    extension_counts = Counter()
    
    # Count file extensions
    for file_path in files_changed:
        _, ext = os.path.splitext(file_path.lower())
        extension_counts[ext] += 1
    
    # Score each role based on matching extensions
    for role, patterns in ROLE_PATTERNS.items():
        score = 0
        for ext, count in extension_counts.items():
            if ext in patterns['extensions']:
                score += count
        
        # Boost score for QA/Tester if test activity is high
        if role == 'QA / Tester' and breakdown.get('test', 0) > 30:
            score += 5
        
        if score > 0:
            role_scores[role] = score
    
    # Boost UI/UX Designer if design activity is dominant
    if breakdown.get('design', 0) > 50:
        role_scores['UI/UX Designer'] = 100
    
    return role_scores


def _detect_roles(breakdown: Dict[str, float], commits: int, total_files: int, total_activity: int) -> List[str]:
    """
    Detect roles based on contribution breakdown percentages.
    
    Returns a list of roles ordered by primary to secondary.
    """
    roles = []
    
    # Check specialized roles
    if breakdown.get('code', 0) >= ROLE_THRESHOLDS['code'] * 100:
        roles.append("Developer")
    
    if breakdown.get('test', 0) >= ROLE_THRESHOLDS['test'] * 100:
        roles.append("Tester")
    
    if breakdown.get('docs', 0) >= ROLE_THRESHOLDS['docs'] * 100:
        roles.append("Documentarian")
    
    if breakdown.get('design', 0) >= ROLE_THRESHOLDS['design'] * 100:
        roles.append("Designer")
    
    # Check for full-stack contributor (balanced across multiple areas)
    if len(roles) >= 3:
        roles = ["Full-Stack Contributor"] + roles[1:]
    elif len(roles) == 0:
        # Default fallback for small/balanced contributors
        roles.append("General Contributor")
    
    # Add leadership indicators based on high activity levels
    if commits > 20 and total_activity > 15:
        roles.insert(0, "Lead Developer")
    elif commits > 10 and total_activity > 10:
        roles.insert(0, "Senior Contributor")
    
    return roles


def _calculate_role_confidence(primary_role: str, role_scores: List[tuple]) -> float:
    """
    Calculate confidence score (0.0-1.0) for the primary role assignment.
    
    role_scores is a list of (role, score) tuples sorted by score descending.
    """
    if not role_scores:
        return 0.0
    
    if primary_role == 'Project Lead / Architect':
        return 0.95  # Very high confidence for leads
    
    if primary_role == 'Full Stack Developer':
        # For full stack, confidence based on balance
        if len(role_scores) >= 2:
            top_score = role_scores[0][1]
            second_score = role_scores[1][1]
            if top_score > 0:
                return min(1.0, second_score / top_score)
        return 0.7
    
    # For specialized roles, confidence based on dominance
    if role_scores:
        primary_score = next((s for r, s in role_scores if r == primary_role), 1)
        top_score = role_scores[0][1]
        if top_score > 0:
            return min(1.0, primary_score / top_score)
    
    return 0.5


def analyze_project_roles(contributors_data: Dict) -> Dict:
    """
    Analyze all contributors in a project and return role assignments.
    
    Args:
        contributors_data: Dict where keys are contributor names and values are dicts
                          containing: files_changed, commits, lines_added, lines_removed,
                          activity_by_category
    
    Returns:
        Dict with structure:
            - contributors: List of role analysis dicts for each contributor
            - summary: Project-level role distribution summary
    """
    contributor_roles = []
    
    for name, data in contributors_data.items():
        # Normalize the contributor name using canonical_username
        canonical_name = canonical_username(name)
        role_analysis = categorize_contributor_role(
            canonical_name,
            data.get("files_changed", []),
            data.get("commits", 0),
            data.get("lines_added", 0),
            data.get("lines_removed", 0),
            data.get("activity_by_category", {})
        )
        contributor_roles.append(role_analysis)
    
    # Generate project summary with deduplicated contributors by canonical name
    unique_contributors = {}
    for role in contributor_roles:
        canonical_name = role["name"]
        if canonical_name not in unique_contributors:
            unique_contributors[canonical_name] = role
    
    deduped_roles = list(unique_contributors.values())
    
    role_counts = Counter(r["primary_role"] for r in deduped_roles)
    role_distribution = {
        role: count
        for role, count in sorted(role_counts.items(), key=lambda x: -x[1])
    }
    
    leads = [r for r in deduped_roles if "Lead" in r["primary_role"]]
    developers = [r for r in deduped_roles if "Developer" in r["primary_role"]]
    
    summary = {
        "total_contributors": len(deduped_roles),
        "role_distribution": role_distribution,
        "leadership_count": len(leads),
        "development_team_size": len(developers),
        "team_composition": _describe_team_composition(deduped_roles),
    }
    
    return {
        "contributors": deduped_roles,
        "summary": summary
    }


def _describe_team_composition(contributor_roles: List[Dict]) -> str:
    """Generate a text description of the team composition."""
    if not contributor_roles:
        return "No contributors detected."
    
    role_counts = Counter(r["primary_role"] for r in contributor_roles)
    
    descriptions = []
    for role, count in sorted(role_counts.items(), key=lambda x: -x[1]):
        if count == 1:
            descriptions.append(f"1 {role}")
        else:
            descriptions.append(f"{count} {role}s")
    
    return ", ".join(descriptions)


def format_roles_report(analysis_result: Dict) -> str:
    """
    Format the role analysis results as a human-readable report.
    """
    report = []
    report.append("\n" + "=" * 70)
    report.append("PROJECT ROLE ANALYSIS REPORT")
    report.append("=" * 70)
    
    summary = analysis_result.get("summary", {})
    report.append(f"\nTotal Contributors: {summary.get('total_contributors', 0)}")
    report.append(f"Team Composition: {summary.get('team_composition', 'Unknown')}")
    report.append(f"Leadership Roles: {summary.get('leadership_count', 0)}")
    report.append(f"Development Team: {summary.get('development_team_size', 0)}")
    
    if summary.get('role_distribution'):
        report.append(f"\nRole Distribution:")
        for role, count in summary['role_distribution'].items():
            report.append(f"  - {role}: {count}")
    
    report.append("\n" + "-" * 70)
    report.append("CONTRIBUTOR ROLES")
    report.append("-" * 70)
    
    for contributor in analysis_result.get("contributors", []):
        report.append(f"\n{contributor['name']}:")
        report.append(f"  Primary Role: {contributor['primary_role']}")
        
        if contributor['secondary_roles']:
            report.append(f"  Secondary Roles: {', '.join(contributor['secondary_roles'])}")
        
        report.append(f"  Confidence: {contributor['confidence']:.1%}")
        
        metrics = contributor.get('metrics', {})
        report.append(f"  Metrics:")
        report.append(f"    - Files: {metrics.get('total_files', 0)}")
        report.append(f"    - Commits: {metrics.get('commits', 0)}")
        report.append(f"    - Lines Added: {metrics.get('lines_added', 0)}")
        report.append(f"    - Lines Removed: {metrics.get('lines_removed', 0)}")
        report.append(f"    - Avg Lines/Commit: {metrics.get('avg_lines_per_commit', 0)}")
        
        breakdown = contributor.get('contribution_breakdown', {})
        if breakdown:
            report.append(f"  Contribution Breakdown:")
            for cat, pct in sorted(breakdown.items(), key=lambda x: -x[1]):
                if pct > 0:
                    report.append(f"    - {cat.capitalize()}: {pct:.1f}%")
    
    report.append("\n" + "=" * 70)
    
    return "\n".join(report)


def load_contributors_from_db() -> Dict:
    """
    Load actual contributors and their metrics from the database.
    
    Returns a dictionary suitable for analyze_project_roles().
    """
    try:
        from db import get_connection
    except ImportError:
        print("Error: Could not import db module")
        return {}
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Get all contributors and their file activity
        cur.execute("""
            SELECT DISTINCT c.name, c.id
            FROM contributors c
            JOIN file_contributors fc ON c.id = fc.contributor_id
            ORDER BY c.name
        """)
        
        contributors = cur.fetchall()
        print(f"Found {len(contributors)} contributors in database")
        
        if not contributors:
            print("No contributors found in database.")
            return {}
        
        contributors_data = {}
        
        for contrib_row in contributors:
            contrib_name = contrib_row['name']
            contrib_id = contrib_row['id']
            
            # Get all files for this contributor
            cur.execute("""
                SELECT DISTINCT f.file_path, f.file_name
                FROM files f
                JOIN file_contributors fc ON f.id = fc.file_id
                WHERE fc.contributor_id = ?
            """, (contrib_id,))
            
            files = cur.fetchall()
            files_changed = [f['file_path'] for f in files]
            
            print(f"  {contrib_name}: {len(files_changed)} files")
            
            # Classify files by category
            activity_by_category = {"code": 0, "test": 0, "docs": 0, "design": 0, "other": 0}
            for file_path in files_changed:
                category = classify_file(file_path)
                activity_by_category[category] = activity_by_category.get(category, 0) + 1
            
            # Count total file contributions (number of files they've touched)
            # and estimate commits/lines (using file count as proxy if git data unavailable)
            file_count = len(files_changed)
            estimated_commits = max(1, file_count)  # At least 1 commit per file touched
            estimated_lines_added = file_count * 50  # Rough estimate: 50 lines per file
            estimated_lines_removed = file_count * 10
            
            # Normalize the contributor name using canonical_username
            canonical_name = canonical_username(contrib_name)
            contributors_data[canonical_name] = {
                "files_changed": files_changed,
                "commits": estimated_commits,
                "lines_added": estimated_lines_added,
                "lines_removed": estimated_lines_removed,
                "activity_by_category": activity_by_category
            }
        
        print(f"Loaded {len(contributors_data)} unique contributors (deduplicated)")
        return contributors_data
    
    except Exception as e:
        print(f"Error querying database: {e}")
        import traceback
        traceback.print_exc()
        return {}
    
    finally:
        conn.close()


if __name__ == "__main__":
    # Load actual contributors from database
    print("Loading contributors from database...")
    contributors_data = load_contributors_from_db()
    
    print(f"\nDatabase query returned {len(contributors_data)} contributors:")
    for name in contributors_data:
        print(f"  - {name}")
    
    if not contributors_data:
        print("No contributor data available. Using example data.")
        contributors_data = {
            "alice": {
                "files_changed": ["main.py", "utils.py", "config.py"],
                "commits": 15,
                "lines_added": 500,
                "lines_removed": 100,
                "activity_by_category": {"code": 3, "test": 0, "docs": 0, "design": 0, "other": 0}
            },
            "bob": {
                "files_changed": ["test_main.py", "test_utils.py", "test_config.py", "README.md"],
                "commits": 8,
                "lines_added": 300,
                "lines_removed": 50,
                "activity_by_category": {"code": 0, "test": 3, "docs": 1, "design": 0, "other": 0}
            },
            "charlie": {
                "files_changed": ["design.png", "mockup.svg"],
                "commits": 2,
                "lines_added": 0,
                "lines_removed": 0,
                "activity_by_category": {"code": 0, "test": 0, "docs": 0, "design": 2, "other": 0}
            }
        }
    
    result = analyze_project_roles(contributors_data)
    print(format_roles_report(result))
