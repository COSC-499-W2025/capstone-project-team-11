"""Low-level role detection for project contributors.

This module analyzes contributor activity patterns across a project to categorize
roles without using an LLM. It uses file extensions, content patterns, and activity
metrics to infer roles such as:
- Backend Developer: Server-side code, APIs, databases, core business logic
- Frontend Developer: UI code, web clients, styling, component development
- Full Stack Developer: Significant contributions across both frontend and backend
- Mobile Developer: Mobile app development (iOS, Android, cross-platform)
- Machine Learning Developer: Data processing, ML models, data pipelines
- Game Developer: Game engines, game mechanics, graphics, physics
- Infrastructure Developer: DevOps, containerization, deployment, cloud config
- Quality Assurance Developer: Testing frameworks, test suites, quality metrics
- UI/UX Designer: Design files, prototypes, visual assets, mockups
- Documentation Specialist: Technical docs, guides, wiki content, API documentation
- Project Steward: High activity levels indicating leadership/coordination role
"""

from typing import Dict, List, Optional
from collections import defaultdict, Counter
import os
from contrib_metrics import classify_file, canonical_username


def get_role_details(role_name: str) -> Dict:
    """
    Get detailed information about a specific role.
    
    Args:
        role_name: Name of the role (e.g., 'Backend Engineer')
    
    Returns:
        Dict containing role information including title, description, and responsibilities
    """
    return ROLE_DESCRIPTIONS.get(role_name, {
        'title': role_name,
        'description': 'Role information not available',
        'responsibilities': []
    })


def list_all_roles() -> List[str]:
    """Return a list of all recognized roles."""
    return list(ROLE_DESCRIPTIONS.keys())


def display_all_roles() -> str:
    """
    Generate a formatted display of all available roles with their details.
    
    Returns:
        A formatted string showing all roles and their information
    """
    report = []
    report.append("\n" + "=" * 100)
    report.append("AVAILABLE CONTRIBUTOR ROLES & DESCRIPTIONS")
    report.append("=" * 100)
    
    for role_name in sorted(ROLE_DESCRIPTIONS.keys()):
        role_info = ROLE_DESCRIPTIONS[role_name]
        report.append(f"\n{'─' * 100}")
        report.append(f"ROLE: {role_info.get('title', role_name).upper()}")
        report.append(f"{'─' * 100}")
        
        report.append(f"\nDescription:")
        report.append(f"  {role_info.get('description', 'N/A')}")
        
        responsibilities = role_info.get('responsibilities', [])
        if responsibilities:
            report.append(f"\nKey Responsibilities:")
            for responsibility in responsibilities:
                report.append(f"  • {responsibility}")
    
    report.append("\n" + "=" * 100 + "\n")
    return "\n".join(report)


# File extension patterns for role detection
ROLE_PATTERNS = {
    'Backend Developer': {
        'extensions': {'.py', '.java', '.go', '.rs', '.c', '.cpp', '.php', '.rb', '.cs'},
        'keywords': ['backend', 'server', 'api', 'database', 'model', 'service', 'controller'],
        'description': 'Focuses on server-side code, APIs, databases, and business logic implementation'
    },
    'Frontend Developer': {
        'extensions': {'.js', '.ts', '.jsx', '.tsx', '.vue', '.html', '.css', '.scss', '.less'},
        'keywords': ['frontend', 'react', 'vue', 'angular', 'ui', 'component', 'view'],
        'description': 'Specializes in user interfaces, web components, styling, and client-side logic'
    },
    'Mobile Developer': {
        'extensions': {'.swift', '.kt', '.dart', '.m', '.mm', '.java'},
        'keywords': ['mobile', 'android', 'ios', 'flutter', 'xcode', 'gradle'],
        'description': 'Develops native or cross-platform mobile applications and related SDKs'
    },
    'Machine Learning Developer': {
        'extensions': {'.py', '.r', '.sql', '.ipynb', '.jl'},
        'keywords': ['data', 'ml', 'machine learning', 'numpy', 'pandas', 'tensorflow', 'keras', 'sklearn', 'pytorch'],
        'description': 'Works on data pipelines, model training, ML research, and data analysis'
    },
    'Game Developer': {
        'extensions': {'.cs', '.cpp', '.shader', '.unity', '.unreal'},
        'keywords': ['game', 'unity', 'unreal', 'godot', 'engine', 'physics', 'graphics'],
        'description': 'Develops game mechanics, engines, graphics, and interactive entertainment systems'
    },
    'Infrastructure Developer': {
        'extensions': {'.yml', '.yaml', '.tf', '.json', '.dockerfile', '.sh', '.bash', '.hcl'},
        'keywords': ['docker', 'kubernetes', 'terraform', 'ansible', 'devops', 'infrastructure', 'cloud', 'deploy'],
        'description': 'Manages deployment pipelines, containerization, cloud infrastructure, and system configuration'
    },
    'Quality Assurance Developer': {
        'extensions': {'.py', '.js', '.java', '.ts', '.go'},
        'keywords': ['test', 'spec', 'pytest', 'jest', 'junit', 'mocha', 'testing', 'qa', 'quality'],
        'description': 'Creates and maintains test frameworks, ensures code quality, and validates functionality'
    },
    'UI/UX Designer': {
        'extensions': {'.png', '.jpg', '.svg', '.psd', '.sketch', '.xd', '.figma', '.pdf'},
        'keywords': ['design', 'ui', 'ux', 'mockup', 'prototype', 'visual'],
        'description': 'Creates visual designs, prototypes, mockups, and user experience assets'
    },
    'Documentation Specialist': {
        'extensions': {'.md', '.rst', '.txt', '.adoc'},
        'keywords': ['documentation', 'guide', 'tutorial', 'readme', 'docs', 'api doc'],
        'description': 'Writes technical documentation, guides, API references, and knowledge resources'
    },
}

# Minimum contribution levels to assign a role
MIN_TOTAL_FILES = 3        # Must have at least 3 file contributions

# Thresholds for specialized role detection
ROLE_THRESHOLDS = {
    'code': 0.30,      # 30% code contributions
    'test': 0.30,      # 30% test contributions
    'docs': 0.20,      # 20% documentation
    'design': 0.50,    # 50% design assets
}

# Detailed role descriptions with guidance
ROLE_DESCRIPTIONS = {
    'Backend Developer': {
        'title': 'Backend Developer',
        'description': 'Develops and maintains server-side systems, APIs, and business logic',
        'responsibilities': [
            'Server-side code and API development',
            'Database design and management',
            'Business logic implementation',
            'Service architecture',
            'Performance optimization'
        ]
    },
    'Frontend Developer': {
        'title': 'Frontend Developer',
        'description': 'Creates user interfaces, interactive components, and client-side functionality',
        'responsibilities': [
            'UI component development',
            'User interaction implementation',
            'CSS and styling',
            'Browser compatibility',
            'Client-side state management'
        ]
    },
    'Full Stack Developer': {
        'title': 'Full Stack Developer',
        'description': 'Contributes significantly to both frontend and backend systems',
        'responsibilities': [
            'End-to-end feature implementation',
            'API and UI coordination',
            'Database to interface integration',
            'Full-stack architectural decisions'
        ]
    },
    'Mobile Developer': {
        'title': 'Mobile Developer',
        'description': 'Develops mobile applications for various platforms',
        'responsibilities': [
            'Mobile app development (iOS/Android)',
            'Cross-platform solutions',
            'Mobile UI/UX implementation',
            'Mobile performance optimization',
            'App store integration'
        ]
    },
    'Machine Learning Developer': {
        'title': 'Machine Learning Developer',
        'description': 'Builds, trains, and deploys machine learning models and data pipelines',
        'responsibilities': [
            'ML model development and training',
            'Data pipeline construction',
            'Data preprocessing and analysis',
            'Statistical analysis',
            'Model evaluation and optimization'
        ]
    },
    'Game Developer': {
        'title': 'Game Developer',
        'description': 'Develops game mechanics, engines, and interactive systems',
        'responsibilities': [
            'Game engine development',
            'Physics and graphics implementation',
            'Game mechanics design',
            'Performance optimization for gaming',
            'Interactive system architecture'
        ]
    },
    'Infrastructure Developer': {
        'title': 'Infrastructure Developer',
        'description': 'Manages deployment, containerization, and cloud infrastructure',
        'responsibilities': [
            'CI/CD pipeline development',
            'Docker/Kubernetes orchestration',
            'Cloud infrastructure setup',
            'Deployment automation',
            'System monitoring and scaling'
        ]
    },
    'Quality Assurance Developer': {
        'title': 'Quality Assurance Developer',
        'description': 'Develops testing frameworks and ensures code quality standards',
        'responsibilities': [
            'Test framework development',
            'Unit and integration testing',
            'Quality metrics tracking',
            'Bug identification and reporting',
            'Test automation'
        ]
    },
    'UI/UX Designer': {
        'title': 'UI/UX Designer',
        'description': 'Creates visual designs, prototypes, and user experience assets',
        'responsibilities': [
            'Visual design creation',
            'Prototype development',
            'Mockup creation',
            'User experience design',
            'Design asset management'
        ]
    },
    'Documentation Specialist': {
        'title': 'Documentation Specialist',
        'description': 'Creates and maintains technical documentation and knowledge resources',
        'responsibilities': [
            'Technical documentation writing',
            'API documentation',
            'User guide creation',
            'Knowledge base development',
            'Tutorial creation'
        ]
    },
    'Project Steward': {
        'title': 'Project Steward',
        'description': 'High-activity contributor showing leadership and coordination across the project',
        'responsibilities': [
            'Cross-functional coordination',
            'Architecture decisions',
            'Code review and guidance',
            'Project planning and direction',
            'Team mentoring'
        ]
    },
}


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
            - role_title: Human-readable title for the primary role
            - role_description: Detailed description of the role
            - secondary_roles: List of additional roles detected
            - confidence: Score 0.0-1.0 indicating role certainty
            - contribution_breakdown: Dict with percentages per category
            - metrics: Raw contribution metrics
    """
    if not files_changed or len(files_changed) < MIN_TOTAL_FILES:
        return {
            "name": canonical_username(contributor_name),
            "primary_role": "Contributor",
            "role_title": "Contributor",
            "role_description": "Occasional contributor with limited activity",
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
    if len(roles) >= 2:
        # Check if roles have balanced scores
        top_score = sorted_roles[0][1] if sorted_roles else 1
        second_score = sorted_roles[1][1] if len(sorted_roles) > 1 else 0
        # Full Stack if contributions are reasonably balanced (not >5x difference)
        if top_score > 0 and second_score > top_score * 0.3:
            roles.insert(0, 'Full Stack Developer')
    
    # Detect Project Steward if very high activity
    if commits > 20 and len(files_changed) > 15:
        roles.insert(0, 'Project Steward')
    
    # Fallback if no roles detected
    if not roles:
        roles.append("Developer")
    
    primary_role = roles[0]
    secondary_roles = roles[1:4] if len(roles) > 1 else []  # Limit to 3 secondary roles
    
    # Calculate confidence
    confidence = _calculate_role_confidence(primary_role, sorted_roles)
    
    # Get role metadata
    role_info = ROLE_DESCRIPTIONS.get(primary_role, {})
    
    return {
        "name": canonical_username(contributor_name),
        "primary_role": primary_role,
        "role_title": role_info.get('title', primary_role),
        "role_description": role_info.get('description', ''),
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
        
        # Boost score for Quality Assurance Developer if test activity is high
        if role == 'Quality Assurance Developer' and breakdown.get('test', 0) > 30:
            score += 5
        
        # Boost score for Documentation Specialist if docs activity is high
        if role == 'Documentation Specialist' and breakdown.get('docs', 0) > 30:
            score += 5
        
        if score > 0:
            role_scores[role] = score
    
    # Boost UI/UX Designer if design activity is dominant
    if breakdown.get('design', 0) > 50:
        role_scores['UI/UX Designer'] = 100
    
    return role_scores


def _calculate_role_confidence(primary_role: str, role_scores: List[tuple]) -> float:
    """
    Calculate confidence score (0.0-1.0) for the primary role assignment.
    
    role_scores is a list of (role, score) tuples sorted by score descending.
    """
    if not role_scores:
        return 0.0
    
    if primary_role == 'Project Steward':
        return 0.95  # Very high confidence for stewards
    
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
    
    leads = [r for r in deduped_roles if "Steward" in r["primary_role"]]
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


def format_roles_report(analysis_result: Dict, per_project_data: Dict[str, Dict] = None) -> str:
    """
    Format the role analysis results as a human-readable report.
    
    Args:
        analysis_result: Overall role analysis (across all projects)
        per_project_data: Optional dict of per-project contributor analyses
    """
    report = []
    report.append("\n" + "=" * 80)
    report.append("PROJECT ROLE ANALYSIS REPORT")
    report.append("=" * 80)
    
    summary = analysis_result.get("summary", {})
    report.append(f"\nTotal Contributors: {summary.get('total_contributors', 0)}")
    report.append(f"Team Composition: {summary.get('team_composition', 'Unknown')}")
    report.append(f"Leadership Roles: {summary.get('leadership_count', 0)}")
    report.append(f"Development Team: {summary.get('development_team_size', 0)}")
    
    if summary.get('role_distribution'):
        report.append(f"\nRole Distribution:")
        for role, count in summary['role_distribution'].items():
            report.append(f"  - {role}: {count}")
    
    report.append("\n" + "-" * 80)
    report.append("CONTRIBUTOR ROLES (OVERALL)")
    report.append("-" * 80)
    
    for contributor in analysis_result.get("contributors", []):
        report.append(f"\n{contributor['name'].upper()}")
        report.append(f"  Primary Role: {contributor['primary_role']}")
        report.append(f"  Title: {contributor.get('role_title', contributor['primary_role'])}")
        report.append(f"  Description: {contributor.get('role_description', 'N/A')}")
        
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
    
    # Add per-project breakdown if available
    if per_project_data:
        report.append("\n" + "=" * 80)
        report.append("PER-PROJECT CONTRIBUTIONS")
        report.append("=" * 80)
        
        for project_name, project_analysis in sorted(per_project_data.items()):
            report.append(f"\n{'-' * 80}")
            report.append(f"Project: {project_name}")
            report.append(f"{'-' * 80}")
            
            for contributor in project_analysis.get("contributors", []):
                report.append(f"\n  {contributor['name']}:")
                report.append(f"    Primary Role: {contributor['primary_role']}")
                report.append(f"    Description: {contributor.get('role_description', 'N/A')}")
                
                if contributor['secondary_roles']:
                    report.append(f"    Secondary Roles: {', '.join(contributor['secondary_roles'])}")
                
                metrics = contributor.get('metrics', {})
                report.append(f"    Files: {metrics.get('total_files', 0)} | "
                            f"Commits: {metrics.get('commits', 0)} | "
                            f"Lines: +{metrics.get('lines_added', 0)}/-{metrics.get('lines_removed', 0)}")
                
                breakdown = contributor.get('contribution_breakdown', {})
                if breakdown:
                    breakdown_str = ", ".join(
                        f"{cat.capitalize()}: {pct:.0f}%" 
                        for cat, pct in sorted(breakdown.items(), key=lambda x: -x[1]) 
                        if pct > 0
                    )
                    report.append(f"    Breakdown: {breakdown_str}")
    
    report.append("\n" + "=" * 80)
    
    return "\n".join(report)


def load_contributors_per_project_from_db() -> Dict[str, Dict]:
    """Load contributors and their metrics per project from the database.
    
    Returns a nested dictionary:
        {
            'project_name': {
                'contributor_name': {
                    'files_changed': [...],
                    'commits': int,
                    'lines_added': int,
                    'lines_removed': int,
                    'activity_by_category': {...}
                }
            }
        }
    """
    try:
        from db import get_connection
    except ImportError:
        print("Error: Could not import db module")
        return {}
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Get all projects from scans
        cur.execute("""
            SELECT DISTINCT s.project
            FROM scans s
            WHERE s.project IS NOT NULL
            ORDER BY s.project
        """)
        
        projects = [row['project'] for row in cur.fetchall()]
        print(f"Found {len(projects)} projects in database")
        
        if not projects:
            print("No projects found in database.")
            return {}
        
        projects_data = {}
        
        for project_name in projects:
            # Get all contributors for this project
            cur.execute("""
                SELECT DISTINCT c.name, c.id
                FROM contributors c
                JOIN file_contributors fc ON c.id = fc.contributor_id
                JOIN files f ON fc.file_id = f.id
                JOIN scans s ON f.scan_id = s.id
                WHERE s.project = ?
                ORDER BY c.name
            """, (project_name,))
            
            contributors = cur.fetchall()
            print(f"  {project_name}: {len(contributors)} contributors")
            
            if not contributors:
                continue
            
            contributors_data = {}
            
            for contrib_row in contributors:
                contrib_name = contrib_row['name']
                contrib_id = contrib_row['id']
                
                # Get all files for this contributor in this project
                cur.execute("""
                    SELECT DISTINCT f.file_path, f.file_name
                    FROM files f
                    JOIN file_contributors fc ON f.id = fc.file_id
                    JOIN scans s ON f.scan_id = s.id
                    WHERE fc.contributor_id = ? AND s.project = ?
                """, (contrib_id, project_name))
                
                files = cur.fetchall()
                files_changed = [f['file_path'] for f in files]
                
                # Classify files by category
                activity_by_category = {"code": 0, "test": 0, "docs": 0, "design": 0, "other": 0}
                for file_path in files_changed:
                    category = classify_file(file_path)
                    activity_by_category[category] = activity_by_category.get(category, 0) + 1
                
                # Count total file contributions
                file_count = len(files_changed)
                estimated_commits = max(1, file_count)
                estimated_lines_added = file_count * 50
                estimated_lines_removed = file_count * 10
                
                # Normalize the contributor name
                canonical_name = canonical_username(contrib_name)
                contributors_data[canonical_name] = {
                    "files_changed": files_changed,
                    "commits": estimated_commits,
                    "lines_added": estimated_lines_added,
                    "lines_removed": estimated_lines_removed,
                    "activity_by_category": activity_by_category
                }
            
            projects_data[project_name] = contributors_data
        
        print(f"Loaded data for {len(projects_data)} projects")
        return projects_data
    
    except Exception as e:
        print(f"Error querying database: {e}")
        import traceback
        traceback.print_exc()
        return {}
    
    finally:
        conn.close()


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
    # Ask user if they want to see all available roles
    print("\n" + "=" * 100)
    print("CONTRIBUTOR ROLE ANALYSIS SYSTEM")
    print("=" * 100)
    
    show_roles = input("\nWould you like to see all available contributor roles and their descriptions? (yes/no): ").strip().lower()
    
    if show_roles in ['yes', 'y']:
        print(display_all_roles())
    
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
    
    # Analyze overall roles
    result = analyze_project_roles(contributors_data)
    
    # Load and analyze per-project contributions
    print("\nLoading per-project contributor data...")
    per_project_raw = load_contributors_per_project_from_db()
    
    # Analyze roles for each project
    per_project_analysis = {}
    if per_project_raw:
        for project_name, project_contributors in per_project_raw.items():
            per_project_analysis[project_name] = analyze_project_roles(project_contributors)
    
    # Generate and print the complete report
    print(format_roles_report(result, per_project_analysis))

