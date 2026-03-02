import importlib
import json
import os
import subprocess
import sys
import tempfile
import unittest

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import generate_portfolio as gp
import db as db_mod
import project_evidence as pe_mod
from collections import OrderedDict
from generate_resume import collect_projects

class TestGeneratePortfolio(unittest.TestCase):

    # Set up output directory path
    def setUp(self):
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.output_dir = os.path.join(repo_root, 'output')

    # Verify PortfolioSection renders markdown when enabled and returns empty string when disabled
    def test_portfolio_section_render(self):
        section = gp.PortfolioSection('test', 'Test', 'Content', enabled=True)
        self.assertIn('## Test', section.render())
        self.assertIn('Content', section.render())

        section.enabled = False
        self.assertEqual(section.render(), '')

    # Verify Portfolio class can toggle sections and render complete markdown output
    def test_portfolio_toggle_and_render(self):
        sections = OrderedDict()
        sections['overview'] = gp.PortfolioSection('overview', 'Overview', 'Test overview')

        portfolio = gp.Portfolio('john', sections)
        self.assertEqual(portfolio.username, 'john')

        portfolio.toggle_section('overview')
        self.assertFalse(portfolio.sections['overview'].enabled)

        md = portfolio.render_markdown()
        self.assertIn('# Portfolio — john', md)

    # Verify overview section aggregates technologies and skills across multiple projects
    def test_build_overview_section(self):
        projects_data = [
            {'languages': ['Python', 'JavaScript'], 'frameworks': ['React'], 'skills': ['API Design'],
             'high_confidence_languages': ['Python', 'JavaScript'], 'high_confidence_frameworks': ['React']},
            {'languages': ['Python', 'SQL'], 'frameworks': ['Django'], 'skills': ['Database Design'],
             'high_confidence_languages': ['Python', 'SQL'], 'high_confidence_frameworks': ['Django']}
        ]
        section = gp.build_overview_section(projects_data, 'john', 'high')

        self.assertEqual(section.section_id, 'overview')
        self.assertIn('2 project(s)', section.content)
        self.assertIn('Python', section.content)
        self.assertIn('React', section.content)

    # Verify project sections correctly label projects as Individual or Collaborative based on contributor count
    def test_build_project_section_types(self):
        collab_project = {
            'project_name': 'CollabProject',
            'path': '/path',
            'languages': ['Python'],
            'frameworks': [],
            'skills': [],
            'high_confidence_languages': ['Python'],
            'high_confidence_frameworks': [],
            'user_commits': 10,
            'user_files': ['file1.py'],
            'git_metrics': {'commits_per_author': {'john': 5, 'jane': 5}}
        }
        section = gp.build_project_section(collab_project, 1, 'john', 'high')
        self.assertIn('(Collaborative Project)', section.content)

        solo_project = {
            'project_name': 'SoloProject',
            'path': '/path',
            'languages': ['JavaScript'],
            'frameworks': [],
            'skills': [],
            'high_confidence_languages': ['JavaScript'],
            'high_confidence_frameworks': [],
            'user_commits': 0,
            'user_files': [],
            'git_metrics': {}
        }
        section2 = gp.build_project_section(solo_project, 2, 'john', 'high')
        self.assertIn('(Individual Project)', section2.content)

    # Verify technology summary aggregates and ranks tech usage across all projects
    def test_build_tech_summary(self):
        projects_data = [
            {'project_name': 'A', 'languages': ['Python'], 'frameworks': ['React'],
             'high_confidence_languages': ['Python'], 'high_confidence_frameworks': ['React']},
            {'project_name': 'B', 'languages': ['Python', 'Java'], 'frameworks': [],
             'high_confidence_languages': ['Python', 'Java'], 'high_confidence_frameworks': []},
        ]
        section = gp.build_tech_summary_section(projects_data, 'high')

        self.assertEqual(section.section_id, 'tech_summary')
        self.assertIn('Python', section.content)
        self.assertIn('2 projects', section.content)

    # Verify aggregation includes non-git projects with metadata even without user contributions
    def test_aggregate_projects_includes_metadata(self):
        all_projects = {
            'UserProject': {
                'project_path': '/user',
                'languages': ['Python'],
                'frameworks': [],
                'skills': [],
                'contributions': {'john': {'commits': 5, 'files': ['a.py']}},
                'git_metrics': {}
            },
            'NonGitProject': {
                'project_path': '/nongit',
                'languages': ['HTML'],
                'frameworks': ['Bootstrap'],
                'skills': ['Frontend'],
                'contributions': {},
                'git_metrics': None
            }
        }

        portfolio_projects = gp.aggregate_projects_for_portfolio('john', all_projects, {})

        # Should include both: one with user contribution, one with metadata
        self.assertEqual(len(portfolio_projects), 2)
        project_names = [p['project_name'] for p in portfolio_projects]
        self.assertIn('UserProject', project_names)
        self.assertIn('NonGitProject', project_names)

    # Verify aggregation excludes git projects without user contributions
    def test_aggregate_projects_excludes_non_contributor_git_project(self):
        all_projects = {
            'OtherUserProject': {
                'project_path': '/other',
                'languages': ['Python'],
                'frameworks': [],
                'skills': ['Testing'],
                'contributions': {
                    'alice': {'commits': 5, 'files': ['a.py']}
                },
                'git_metrics': {
                    'total_commits': 5
                }
            }
        }

        portfolio_projects = gp.aggregate_projects_for_portfolio('john', all_projects, {})

        # project should be excluded
        self.assertEqual(portfolio_projects, [])

    # Verify complete portfolio has all required sections and metadata
    def test_build_portfolio_structure(self):
        projects_data = [
            {'project_name': 'A', 'path': '/a', 'languages': ['Python'], 'frameworks': [],
             'high_confidence_languages': ['Python'], 'high_confidence_frameworks': [],
             'skills': [], 'user_commits': 0, 'user_files': [], 'git_metrics': {}}
        ]

        portfolio = gp.build_portfolio('john', projects_data, '2026-01-11 12:00:00Z', 'high')

        self.assertEqual(portfolio.username, 'john')
        self.assertIn('overview', portfolio.sections)
        self.assertIn('project_1', portfolio.sections)
        self.assertIn('tech_summary', portfolio.sections)
        self.assertEqual(portfolio.metadata['project_count'], 1)

    # Verify confidence filtering correctly filters languages/frameworks by level
    def test_confidence_filtering(self):
        project_data = {
            'project_name': 'TestProject',
            'path': '/test',
            'languages': ['Python', 'JavaScript', 'Swift', 'Ruby'],
            'frameworks': ['React', 'Django', 'Bootstrap'],
            'high_confidence_languages': ['Python', 'JavaScript'],
            'medium_confidence_languages': ['Swift'],
            'low_confidence_languages': ['Ruby'],
            'high_confidence_frameworks': ['React'],
            'medium_confidence_frameworks': ['Django'],
            'low_confidence_frameworks': ['Bootstrap'],
            'skills': []
        }

        # Test high confidence only
        langs_high, fws_high = gp.get_filtered_technologies(project_data, 'high')
        self.assertEqual(set(langs_high), {'Python', 'JavaScript'})
        self.assertEqual(set(fws_high), {'React'})

        # Test high + medium confidence
        langs_med, fws_med = gp.get_filtered_technologies(project_data, 'medium')
        self.assertEqual(set(langs_med), {'Python', 'JavaScript', 'Swift'})
        self.assertEqual(set(fws_med), {'React', 'Django'})

        # Test all confidence levels (high + medium + low)
        langs_low, fws_low = gp.get_filtered_technologies(project_data, 'low')
        self.assertEqual(set(langs_low), {'Python', 'JavaScript', 'Swift', 'Ruby'})
        self.assertEqual(set(fws_low), {'React', 'Django', 'Bootstrap'})

    # Verify backward compatibility when confidence data is missing
    def test_confidence_filtering_fallback(self):
        project_data = {
            'project_name': 'OldProject',
            'path': '/old',
            'languages': ['Python', 'Java'],
            'frameworks': ['Flask'],
            'skills': []
        }

        # Should fallback to flat lists when confidence data is missing
        langs, fws = gp.get_filtered_technologies(project_data, 'high')
        self.assertEqual(set(langs), {'Python', 'Java'})
        self.assertEqual(set(fws), {'Flask'})

    # Verify performance metrics are included in project sections
    def test_performance_metrics_in_project_section(self):
        project_data = {
            'project_name': 'MetricsProject',
            'path': '/metrics',
            'languages': ['Python'],
            'frameworks': [],
            'high_confidence_languages': ['Python'],
            'high_confidence_frameworks': [],
            'skills': [],
            'user_commits': 45,
            'user_files': ['app.py', 'test.py', 'utils.py'],
            'git_metrics': {
                'total_commits': 100,
                'duration_days': 90,
                'commits_per_author': {'john': 45, 'jane': 35, 'bob': 20},
                'lines_added_per_author': {'john': 2500, 'jane': 1800, 'bob': 500},
                'lines_removed_per_author': {'john': 800, 'jane': 400, 'bob': 100},
                'files_changed_per_author': {
                    'john': ['app.py', 'test.py', 'utils.py'],
                    'jane': ['app.py', 'docs.md'],
                    'bob': ['config.py']
                },
                'project_start': '2025-01-01',
                'project_end': '2025-03-31'
            }
        }

        section = gp.build_project_section(project_data, 1, 'john', 'high')
        content = section.content

        # Check for commit metrics
        self.assertIn('45 commit(s)', content)
        self.assertIn('45.0% of total commits', content)  # 45/100
        self.assertIn('commit(s)/week', content)

        # Check for file metrics
        self.assertIn('3 file(s) modified', content)
        self.assertIn('file ownership', content)

        # Check for code contribution metrics
        self.assertIn('Lines: +2500 / -800', content)
        self.assertIn('Ranked #1 of 3 contributor(s)', content)  # john has most commits
        self.assertIn('My first/last commit', content)

    # Verify contributor ranking is accurate
    def test_contributor_ranking(self):
        project_data = {
            'project_name': 'RankingProject',
            'path': '/rank',
            'languages': ['JavaScript'],
            'frameworks': [],
            'high_confidence_languages': ['JavaScript'],
            'high_confidence_frameworks': [],
            'skills': [],
            'user_commits': 20,
            'user_files': ['c.js'],
            'git_metrics': {
                'total_commits': 100,
                'commits_per_author': {'john': 50, 'jane': 30, 'bob': 20},
                'lines_added_per_author': {'john': 3000, 'jane': 1500, 'bob': 800},
                'lines_removed_per_author': {'john': 500, 'jane': 300, 'bob': 200},
                'files_changed_per_author': {'john': ['a.js'], 'jane': ['b.js'], 'bob': ['c.js']}
            }
        }

        section = gp.build_project_section(project_data, 1, 'bob', 'high')
        content = section.content

        # bob should be ranked #3 (john=50, jane=30, bob=20)
        self.assertIn('Ranked #3 of 3 contributor(s)', content)

class RobustGeneratePortfolioTests(unittest.TestCase):

    # Set up temporary output and portfolio directories with sample project data
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.output_root = os.path.join(self.tmpdir.name, 'output')
        os.makedirs(self.output_root, exist_ok=True)

        self.portfolio_dir = os.path.join(self.tmpdir.name, 'portfolios')
        os.makedirs(self.portfolio_dir, exist_ok=True)

        self.db_path = os.path.join(self.tmpdir.name, 'file_data.db')
        self._old_env = os.environ.get("FILE_DATA_DB_PATH")
        os.environ["FILE_DATA_DB_PATH"] = self.db_path

        global db_mod, gp, collect_projects
        db_mod = importlib.reload(db_mod)
        db_mod.init_db()
        gp = importlib.reload(gp)
        gr_local = importlib.import_module("generate_resume")
        gr_local = importlib.reload(gr_local)
        collect_projects = gr_local.collect_projects

        project_name = 'test-project-john'
        project_path = os.path.join(self.tmpdir.name, project_name)
        git_metrics = {
            'total_commits': 15,
            'duration_days': 30,
            'commits_per_author': {'john': 10, 'jane': 5},
            'lines_added_per_author': {'john': 120, 'jane': 40},
            'files_changed_per_author': {'john': ['app.py', 'index.js'], 'jane': ['test.py']},
            'project_start': '2025-01-01 00:00:00',
        }
        tech_summary = {
            'languages': ['Python', 'JavaScript'],
            'frameworks': ['React'],
            'high_confidence_languages': ['Python', 'JavaScript'],
            'medium_confidence_languages': [],
            'low_confidence_languages': [],
            'high_confidence_frameworks': ['React'],
            'medium_confidence_frameworks': [],
            'low_confidence_frameworks': [],
        }
        conn = db_mod.get_connection()
        try:
            conn.execute(
                "INSERT INTO projects (name, project_path, git_metrics_json, tech_json) VALUES (?, ?, ?, ?)",
                (project_name, project_path, json.dumps(git_metrics), json.dumps(tech_summary)),
            )
            conn.execute("INSERT OR IGNORE INTO skills (name) VALUES (?)", ("Web Development",))
            skill_id = conn.execute(
                "SELECT id FROM skills WHERE name = ?",
                ("Web Development",),
            ).fetchone()["id"]
            project_id = conn.execute(
                "SELECT id FROM projects WHERE name = ?",
                (project_name,),
            ).fetchone()["id"]
            conn.execute(
                "INSERT OR IGNORE INTO project_skills (project_id, skill_id) VALUES (?, ?)",
                (project_id, skill_id),
            )
            conn.commit()
        finally:
            conn.close()

    # Clean up temporary directories after tests
    def tearDown(self):
        # Close any lingering SQLite connections before cleanup (Windows)
        import gc
        gc.collect()
        if self._old_env is None:
            os.environ.pop("FILE_DATA_DB_PATH", None)
        else:
            os.environ["FILE_DATA_DB_PATH"] = self._old_env
        self.tmpdir.cleanup()

    # Verify project collection, aggregation, and full portfolio building
    def test_aggregate_and_build_portfolio(self):
        projects, root = collect_projects()

        portfolio_projects = gp.aggregate_projects_for_portfolio('john', projects, root)
        self.assertGreaterEqual(len(portfolio_projects), 1)

        portfolio = gp.build_portfolio('john', portfolio_projects, confidence_level='high')
        md = portfolio.render_markdown()

        self.assertIn('# Portfolio — john', md)
        self.assertIn('test project john', md.lower())

    # Verify CLI subprocess creates valid portfolio markdown file
    def test_cli_generates_portfolio_file(self):
        cmd = [
            sys.executable, os.path.join('src', 'generate_portfolio.py'),
            '--output-root', self.output_root,
            '--portfolio-dir', self.portfolio_dir,
            '--username', 'john'
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, env=os.environ.copy())
        self.assertEqual(proc.returncode, 0, msg=f"stdout:{proc.stdout}\nstderr:{proc.stderr}")

        # Verify file was created
        files = os.listdir(self.portfolio_dir)
        self.assertTrue(any(f.startswith('portfolio_john_') and f.endswith('.md') for f in files))

        # Verify content
        portfolio_file = [f for f in files if f.startswith('portfolio_john_')][0]
        with open(os.path.join(self.portfolio_dir, portfolio_file), 'r', encoding='utf-8') as fh:
            content = fh.read()

        self.assertIn('# Portfolio — john', content)
        self.assertIn('Python', content)
        self.assertIn('React', content)

    def test_project_section_includes_evidence_when_present(self):
        db_path = os.path.join(self.tmpdir.name, 'file_data.db')
        prev_db = os.environ.get("FILE_DATA_DB_PATH")
        os.environ["FILE_DATA_DB_PATH"] = db_path
        try:
            # Reload modules to pick up the temp DB path
            db_local = importlib.reload(db_mod)
            db_local.init_db()
            pe_local = importlib.reload(pe_mod)
            gp_local = importlib.reload(gp)

            project_name = 'test-project-john'
            conn = db_local.get_connection()
            try:
                conn.execute("INSERT INTO projects (name) VALUES (?)", (project_name,))
                project_id = conn.execute(
                    "SELECT id FROM projects WHERE name = ?",
                    (project_name,),
                ).fetchone()["id"]
                conn.commit()
            finally:
                conn.close()

            pe_local.add_evidence(
                project_id,
                {"type": "metric", "value": "500 users", "source": "Analytics"},
            )

            project_data = {
                'project_name': project_name,
                'path': '/path',
                'languages': ['Python'],
                'frameworks': [],
                'skills': [],
                'high_confidence_languages': ['Python'],
                'high_confidence_frameworks': [],
                'user_commits': 0,
                'user_files': [],
                'git_metrics': {}
            }

            section = gp_local.build_project_section(project_data, 1, 'john', 'high')
            self.assertIn("**Evidence of Success:**", section.content)
            self.assertIn("- **Metric** (Analytics): 500 users", section.content)
        finally:
            # Force close any remaining connections and collect garbage (Windows)
            import gc
            gc.collect()
            if prev_db is None:
                os.environ.pop("FILE_DATA_DB_PATH", None)
            else:
                os.environ["FILE_DATA_DB_PATH"] = prev_db

if __name__ == '__main__':
    unittest.main()
