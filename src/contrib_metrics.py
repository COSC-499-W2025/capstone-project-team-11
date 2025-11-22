"""Contribution metrics extractor for git repositories.

This module analyzes a git repository and produces high-level contribution
metrics such as project duration, commits per author, lines added/removed,
and activity frequency by file-type categories (code, tests, docs, design).

Usage (from project root):
  python -m src.contrib_metrics /path/to/repo

The analyzer relies on `git` being available in PATH.
"""
from __future__ import annotations

import os
import subprocess
import datetime
from collections import defaultdict, Counter
from typing import Dict, List
import re


CATEGORY_MAP = {
    'code': {'.py', '.js', '.ts', '.java', '.c', '.cpp', '.go', '.rb', '.rs'},
    'test': {'.py', '.js', '.java'},
    'docs': {'.md', '.rst', '.txt', '.docx'},
    'design': {'.png', '.jpg', '.jpeg', '.svg', '.psd', '.sketch'},
}


def classify_file(path: str) -> str:
    """Return a category for a file path: 'test', 'code', 'docs', 'design', or 'other'."""
    p = path.replace('\\', '/')
    fname = os.path.basename(p)
    lower = fname.lower()
    if '/test/' in p or '/tests/' in p or lower.startswith('test') or lower.endswith('_test.py'):
        return 'test'

    ext = os.path.splitext(fname)[1].lower()
    for cat, exts in CATEGORY_MAP.items():
        if ext in exts:
            return cat
    return 'other'


def _run_git_log(repo_root: str) -> List[str]:
    """Run git log and return lines of output with numstat and commit markers."""
    cmd = [
        'git',
        'log',
        '--no-merges',
        "--pretty=format:--GIT-COMMIT--%n%H|%an|%ad",
        '--date=iso',
        '--numstat',
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=repo_root)
    if proc.returncode != 0:
        raise RuntimeError(f"git log failed: {proc.stderr.strip()}")
    return proc.stdout.splitlines()


def canonical_username(name: str, email: str = "") -> str:
    """
    Automatically normalize author identity for any git repo.
    - GitHub noreply emails: use the username part after '+'
    - Regular emails: use local part before '@'
    - Otherwise: use cleaned name
    """
    base = None

    if email:
        base = email.split("@")[0].lower()
        # GitHub noreply emails like 12345+username@users.noreply.github.com
        match = re.match(r"\d+\+([a-z0-9-]+)", base)
        if match:
            base = match.group(1)
    if not base and name:
        base = name.lower()

    if not base:
        return "unknown"

    # remove non-alphanumeric characters
    base = re.sub(r"[^0-9a-z]+", "", base.strip())
    return base



def analyze_repo(path: str) -> Dict:
    """Analyze the git repo at `path` and return a metrics dict."""
    repo_root = os.path.abspath(path)
    lines = _run_git_log(repo_root)

    project_start = None
    project_end = None
    total_commits = 0
    commits_per_author = Counter()
    lines_added_per_author = Counter()
    lines_removed_per_author = Counter()
    files_changed_per_author = defaultdict(set)
    activity_counts_per_category = Counter()
    commits_per_week = Counter()

    current_author = None
    current_date = None
    in_commit = False
    touched_categories = set()

    for line in lines:
        if line.startswith('--GIT-COMMIT--'):
            # flush previous commit
            if touched_categories and current_author:
                for c in touched_categories:
                    activity_counts_per_category[c] += 1
            in_commit = True
            touched_categories = set()
            continue

        if in_commit and '|' in line:
            parts = line.split('|')
            if len(parts) >= 3:
                _, author, date_str = parts[0], parts[1].strip(), parts[2].strip()
                try:
                    dt = datetime.datetime.fromisoformat(date_str)
                except Exception:
                    dt = datetime.datetime.strptime(date_str[:19], '%Y-%m-%d %H:%M:%S')

                if project_start is None or dt < project_start:
                    project_start = dt
                if project_end is None or dt > project_end:
                    project_end = dt

                #  Use canonical username for all metrics
                current_author = canonical_username(author)

                total_commits += 1
                commits_per_author[current_author] += 1
                current_date = dt

                week_key = f"{dt.isocalendar()[0]}-W{dt.isocalendar()[1]:02d}"
                commits_per_week[week_key] += 1
                in_commit = False
            continue

        parts = line.split('\t')
        if len(parts) == 3 and current_author:
            added, removed, fpath = parts
            try:
                a = int(added) if added != '-' else 0
            except ValueError:
                a = 0
            try:
                r = int(removed) if removed != '-' else 0
            except ValueError:
                r = 0

            lines_added_per_author[current_author] += a
            lines_removed_per_author[current_author] += r
            files_changed_per_author[current_author].add(fpath)

            category = classify_file(fpath)
            touched_categories.add(category)
            continue

    if project_start and project_end:
        duration_days = (project_end - project_start).days
    else:
        duration_days = None

    if touched_categories and current_author:
        for c in touched_categories:
            activity_counts_per_category[c] += 1

    return {
        'repo_root': repo_root,
        'project_start': project_start,
        'project_end': project_end,
        'duration_days': duration_days,
        'total_commits': total_commits,
        'commits_per_author': dict(commits_per_author),
        'lines_added_per_author': dict(lines_added_per_author),
        'lines_removed_per_author': dict(lines_removed_per_author),
        'activity_counts_per_category': dict(activity_counts_per_category),
        'commits_per_week': dict(commits_per_week),
        'files_changed_per_author': {a: sorted(list(f)) for a, f in files_changed_per_author.items()},
    }


def pretty_print_metrics(metrics: Dict) -> None:
    """Print a human-friendly summary of the metrics, ignoring zero-commit authors."""
    print('Repository:', metrics.get('repo_root'))
    ps = metrics.get('project_start')
    pe = metrics.get('project_end')
    print('Project period:', f"{ps} -> {pe}")
    print('Duration (days):', metrics.get('duration_days'))
    print('Total commits:', metrics.get('total_commits'))

    # Filter authors with commits > 0
    commits = {a: c for a, c in metrics.get('commits_per_author', {}).items() if c > 0}
    added = {a: c for a, c in metrics.get('lines_added_per_author', {}).items() if commits.get(a, 0) > 0}
    removed = {a: c for a, c in metrics.get('lines_removed_per_author', {}).items() if commits.get(a, 0) > 0}
    files = {a: f for a, f in metrics.get('files_changed_per_author', {}).items() if commits.get(a, 0) > 0}

    print('\nCommits per author:')
    for a, c in sorted(commits.items(), key=lambda x: -x[1]):
        print(f'  {a}: {c}')

    print('\nLines added per author:')
    for a, c in sorted(added.items(), key=lambda x: -x[1]):
        print(f'  {a}: +{c}')

    print('\nLines removed per author:')
    for a, c in sorted(removed.items(), key=lambda x: -x[1]):
        print(f'  {a}: {c}')  # already positive

    print('\nActivity counts by category (commits touching category):')
    activity = {cat: n for cat, n in metrics.get('activity_counts_per_category', {}).items() if n > 0}
    for cat, n in activity.items():
        print(f'  {cat}: {n}')

    print('\nCommits per week (recent 12):')
    weeks = sorted(metrics.get('commits_per_week', {}).items(), key=lambda x: x[0])
    for wk, cnt in weeks[-12:]:
        if cnt > 0:
            print(f'  {wk}: {cnt}')


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser(description='Extract contribution metrics from a git repo')
    p.add_argument('path', nargs='?', default='.', help='Path to repository root')
    args = p.parse_args()
    try:
        m = analyze_repo(args.path)
    except Exception as e:
        print('Error analyzing repository:', e)
    else:
        pretty_print_metrics(m)