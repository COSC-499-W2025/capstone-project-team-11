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
from typing import Dict, List, Tuple
import re


CATEGORY_MAP = {
    'code': {'.py', '.js', '.ts', '.java', '.c', '.cpp', '.go', '.rb', '.rs'},
    'test': {'.py', '.js', '.java'},
    'docs': {'.md', '.rst', '.txt', '.docx'},
    'design': {'.png', '.jpg', '.jpeg', '.svg', '.psd', '.sketch'},
}


def classify_file(path: str) -> str:
    """Return a category for a file path: 'test', 'code', 'docs', 'design', or 'other'.

    Heuristics used:
    - If the path contains a test directory ("/test/" or startswith "test_") or
      filename matches common test patterns, mark as 'test'.
    - Otherwise map by file extension to code/docs/design.
    """
    p = path.replace('\\', '/')
    fname = os.path.basename(p)
    lower = fname.lower()
    if '/test/' in p or p.startswith('test_') or lower.startswith('test') or lower.endswith('_test.py') or '/tests/' in p:
        return 'test'

    ext = os.path.splitext(fname)[1].lower()
    for cat, exts in CATEGORY_MAP.items():
        if ext in exts:
            # test-files are a subset of code extensions; we handled tests above
            if cat == 'code':
                return 'code'
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


def analyze_repo(path: str) -> Dict:
    """Analyze the git repo at `path` and return a metrics dict.

    Metrics include:
      - project_start (datetime), project_end (datetime), duration_days
      - total_commits
      - commits_per_author
      - lines_added_per_author, lines_removed_per_author
      - activity_counts_per_category (commits touching that category)
      - commits_per_week (Counter mapping yyyy-WW -> count)
    """
    repo_root = os.path.abspath(path)
    # ensure it's a git repo
    if not os.path.isdir(os.path.join(repo_root, '.git')):
        # allow .git being a file (worktrees); rely on git itself to fail if not a repo
        pass

    lines = _run_git_log(repo_root)

    project_start = None
    project_end = None
    total_commits = 0
    commits_per_author = Counter()
    lines_added_per_author = Counter()
    lines_removed_per_author = Counter()
    activity_counts_per_category = Counter()
    commits_per_week = Counter()

    current_author = None
    current_date = None
    in_commit = False
    touched_categories = set()

    for line in lines:
        if line.startswith('--GIT-COMMIT--'):
            # New commit marker. Flush previous commit's touched categories (if any)
            if touched_categories and current_author:
                for c in touched_categories:
                    activity_counts_per_category[c] += 1
            # commit header follows on next line(s) but our format puts the payload after marker
            in_commit = True
            # reset per-commit
            touched_categories = set()
            continue
        if in_commit and '|' in line:
            # header line like <hash>|<author>|<date>
            parts = line.split('|')
            if len(parts) >= 3:
                _, author, date_str = parts[0], parts[1].strip(), parts[2].strip()
                try:
                    dt = datetime.datetime.fromisoformat(date_str)
                except Exception:
                    # fallback parse
                    dt = datetime.datetime.strptime(date_str[:19], '%Y-%m-%d %H:%M:%S')

                if project_start is None or dt < project_start:
                    project_start = dt
                if project_end is None or dt > project_end:
                    project_end = dt

                # normalize author names to merge obvious variants (hyphens, camelcase,
                # punctuation, extra whitespace). This prevents duplicate entries like
                # 'TannerDyck' and 'Tanner Dyck' or 'travis-frank' and 'Travis Frank'.
                def normalize_author(name: str) -> str:
                    if not name:
                        return name
                    # insert space before camelcase boundary: 'TannerDyck' -> 'Tanner Dyck'
                    s = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
                    # replace non-alphanumeric characters with space
                    s = re.sub(r'[^0-9A-Za-z]+', ' ', s)
                    # collapse whitespace and strip
                    s = ' '.join(s.split()).strip()
                    # title-case but preserve all-caps acronyms
                    return s.title()

                normalized_author = normalize_author(author)
                total_commits += 1
                commits_per_author[normalized_author] += 1
                current_author = normalized_author
                current_date = dt
                # week key
                week_key = f"{dt.isocalendar()[0]}-W{dt.isocalendar()[1]:02d}"
                commits_per_week[week_key] += 1
                # after header, following lines are numstat until next commit marker
                in_commit = False
            continue

        # numstat lines: added<TAB>removed<TAB>path
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

            category = classify_file(fpath)
            touched_categories.add(category)
            # continue to next numstat
            continue

        # other lines are ignored; we purposely don't flush here because we
        # flush when we encounter the next commit marker (above) or at loop end.

    duration_days = None
    if project_start and project_end:
        duration_days = (project_end - project_start).days

    # flush last commit's categories (if any)
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
    }


def pretty_print_metrics(metrics: Dict) -> None:
    """Print a human-friendly summary of the metrics."""
    print('Repository:', metrics.get('repo_root'))
    ps = metrics.get('project_start')
    pe = metrics.get('project_end')
    print('Project period:', f"{ps} -> {pe}")
    print('Duration (days):', metrics.get('duration_days'))
    print('Total commits:', metrics.get('total_commits'))
    print('\nCommits per author:')
    for a, c in sorted(metrics.get('commits_per_author', {}).items(), key=lambda x: -x[1]):
        print(f'  {a}: {c}')

    print('\nLines added per author:')
    for a, c in sorted(metrics.get('lines_added_per_author', {}).items(), key=lambda x: -x[1]):
        print(f'  {a}: +{c}')

    print('\nLines removed per author:')
    for a, c in sorted(metrics.get('lines_removed_per_author', {}).items(), key=lambda x: -x[1]):
        print(f'  {a}: -{c}')

    print('\nActivity counts by category (commits touching category):')
    for cat, n in metrics.get('activity_counts_per_category', {}).items():
        print(f'  {cat}: {n}')

    print('\nCommits per week (recent 12):')
    weeks = sorted(metrics.get('commits_per_week', {}).items(), key=lambda x: x[0])
    for wk, cnt in weeks[-12:]:
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
