import importlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import generate_resume as gr
import db as db_mod
import project_evidence as pe_mod


class TestGenerateResume(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, 'file_data.db')
        self._old_env = os.environ.get("FILE_DATA_DB_PATH")
        os.environ["FILE_DATA_DB_PATH"] = self.db_path

        global db_mod, gr
        db_mod = importlib.reload(db_mod)
        db_mod.init_db()
        gr = importlib.reload(gr)

        self.output_dir = self.tmpdir.name

        project_name = 'assignment-5-tcp-and-udp-programming-with-java-jaxsonkahl'
        project_path = os.path.join(self.tmpdir.name, project_name)
        git_metrics = {
            'commits_per_author': {'jaxsonkahl': 4},
            'lines_added_per_author': {'jaxsonkahl': 120},
            'files_changed_per_author': {'jaxsonkahl': ['src/Main.java', 'README.md']},
            'project_start': '2025-01-01 00:00:00',
            'total_commits': 4,
        }
        tech_summary = {
            'languages': ['Java', 'Python', 'Go', 'TCP'],
            'frameworks': ['Flask'],
            'high_confidence_languages': ['Java', 'Python'],
            'medium_confidence_languages': ['Go'],
            'low_confidence_languages': ['TCP'],
            'high_confidence_frameworks': ['Flask'],
            'medium_confidence_frameworks': [],
            'low_confidence_frameworks': [],
        }

        conn = db_mod.get_connection()
        try:
            conn.execute(
                "INSERT INTO projects (name, project_path, git_metrics_json, tech_json) VALUES (?, ?, ?, ?)",
                (project_name, project_path, json.dumps(git_metrics), json.dumps(tech_summary)),
            )
            for skill in ["Asynchronous Programming", "Database / SQL"]:
                conn.execute("INSERT OR IGNORE INTO skills (name) VALUES (?)", (skill,))
                skill_id = conn.execute(
                    "SELECT id FROM skills WHERE name = ?",
                    (skill,),
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

    def tearDown(self):
        import gc
        gc.collect()
        if self._old_env is None:
            os.environ.pop("FILE_DATA_DB_PATH", None)
        else:
            os.environ["FILE_DATA_DB_PATH"] = self._old_env
        self.tmpdir.cleanup()

    def test_normalize_project_name_acronyms(self):
        name = 'assignment-5-tcp-and-udp-programming-with-java-jaxsonkahl'
        norm = gr.normalize_project_name(name)
        # Acronyms preserved
        self.assertIn('TCP', norm)
        self.assertIn('UDP', norm)
        # Words capitalized
        self.assertTrue(norm.split()[0].startswith('Assignment'))

    def test_collect_projects_returns_dicts(self):
        projects, root = gr.collect_projects(self.output_dir)
        self.assertIsInstance(projects, dict)
        self.assertIsInstance(root, dict)
        # Expect at least one project info file to be present in output/
        self.assertGreaterEqual(len(projects), 1)

    def test_aggregate_and_render_for_user(self):
        projects, root = gr.collect_projects(self.output_dir)
        agg = gr.aggregate_for_user('jaxsonkahl', projects, root)
        self.assertIsInstance(agg, dict)
        self.assertEqual(agg.get('username'), 'jaxsonkahl')
        md = gr.render_markdown(agg, generated_ts='2025-11-27 00:00:00Z')
        self.assertIn('# Resume — jaxsonkahl', md)
        self.assertIn('_Generated (UTC): 2025-11-27 00:00:00Z_', md)


class RobustGenerateResumeTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.output_root = os.path.join(self.tmpdir.name, 'output')
        os.makedirs(self.output_root, exist_ok=True)

        self.resume_dir = os.path.join(self.tmpdir.name, 'resumes')
        os.makedirs(self.resume_dir, exist_ok=True)

        self.db_path = os.path.join(self.tmpdir.name, 'file_data.db')
        self._old_env = os.environ.get("FILE_DATA_DB_PATH")
        os.environ["FILE_DATA_DB_PATH"] = self.db_path

        global db_mod, gr
        db_mod = importlib.reload(db_mod)
        db_mod.init_db()
        gr = importlib.reload(gr)

        project_name = 'assignment-5-tcp-and-udp-programming-with-java-alice'
        project_path = os.path.join(self.tmpdir.name, project_name)
        git_metrics = {
            'commits_per_author': {'alice': 3, 'githubclassroombot': 1},
            'lines_added_per_author': {'alice': 120, 'githubclassroombot': 50},
            'files_changed_per_author': {'alice': ['src/Main.java', 'README.md']},
            'project_start': '2025-01-01 00:00:00',
            'total_commits': 4,
        }
        tech_summary = {
            'languages': ['Java', 'Python', 'Go', 'TCP'],
            'frameworks': ['Flask'],
            'high_confidence_languages': ['Java', 'Python'],
            'medium_confidence_languages': ['Go'],
            'low_confidence_languages': ['TCP'],
            'high_confidence_frameworks': ['Flask'],
            'medium_confidence_frameworks': [],
            'low_confidence_frameworks': [],
        }
        conn = db_mod.get_connection()
        try:
            conn.execute(
                "INSERT INTO projects (name, project_path, git_metrics_json, tech_json) VALUES (?, ?, ?, ?)",
                (project_name, project_path, json.dumps(git_metrics), json.dumps(tech_summary)),
            )
            for skill in ["Asynchronous Programming", "Database / SQL"]:
                conn.execute("INSERT OR IGNORE INTO skills (name) VALUES (?)", (skill,))
                skill_id = conn.execute(
                    "SELECT id FROM skills WHERE name = ?",
                    (skill,),
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

    def tearDown(self):
        # Close any lingering SQLite connections before cleanup (Windows)
        import gc
        gc.collect()
        if self._old_env is None:
            os.environ.pop("FILE_DATA_DB_PATH", None)
        else:
            os.environ["FILE_DATA_DB_PATH"] = self._old_env
        self.tmpdir.cleanup()

    def test_normalize_project_name(self):
        name = 'assignment-5-tcp-and-udp-programming-with-java-alice'
        norm = gr.normalize_project_name(name)
        # Should preserve TCP and UDP acronyms
        self.assertIn('TCP', norm)
        self.assertIn('UDP', norm)
        self.assertTrue(norm.lower().startswith('assignment'))

    def test_aggregate_for_user_and_render(self):
        projects, root = gr.collect_projects(self.output_root)
        agg = gr.aggregate_for_user('alice', projects, root)
        self.assertEqual(agg['username'], 'alice')
        self.assertGreaterEqual(agg['total_commits'], 1)
        md = gr.render_markdown(agg, generated_ts='2025-11-27 01:02:03Z')
        self.assertIn('# Resume — alice', md)
        self.assertIn('_Generated (UTC): 2025-11-27 01:02:03Z_', md)
        # Check normalized project heading is present
        self.assertRegex(md, r'\*\*Assignment.*TCP.*UDP.*\*\*', msg=md)

    def test_render_includes_evidence_impact_when_present(self):
        db_path = os.path.join(self.tmpdir.name, 'file_data.db')
        prev_db = os.environ.get("FILE_DATA_DB_PATH")
        os.environ["FILE_DATA_DB_PATH"] = db_path
        try:
            # Reload modules to pick up the temp DB path
            db_local = importlib.reload(db_mod)
            db_local.init_db()
            pe_local = importlib.reload(pe_mod)
            gr_local = importlib.reload(gr)

            project_name = 'assignment-5-tcp-and-udp-programming-with-java-alice'
            conn = db_local.get_connection()
            try:
                git_metrics = {
                    'commits_per_author': {'alice': 1},
                    'lines_added_per_author': {'alice': 10},
                    'files_changed_per_author': {'alice': ['src/Main.java']},
                }
                tech_summary = {
                    'languages': ['Java'],
                    'frameworks': ['Flask'],
                    'high_confidence_languages': ['Java'],
                    'medium_confidence_languages': [],
                    'low_confidence_languages': [],
                    'high_confidence_frameworks': ['Flask'],
                    'medium_confidence_frameworks': [],
                    'low_confidence_frameworks': [],
                }
                conn.execute(
                    "INSERT INTO projects (name, project_path, git_metrics_json, tech_json) VALUES (?, ?, ?, ?)",
                    (project_name, '/tmp/project', json.dumps(git_metrics), json.dumps(tech_summary)),
                )
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

            projects, root = gr_local.collect_projects(self.output_root)
            agg = gr_local.aggregate_for_user('alice', projects, root)
            md = gr_local.render_markdown(agg, generated_ts='2025-11-27 01:02:03Z')
            self.assertIn("Impact: 500 users (Analytics)", md)
        finally:
            # Force close any remaining connections and collect garbage (Windows)
            import gc
            gc.collect()
            if prev_db is None:
                os.environ.pop("FILE_DATA_DB_PATH", None)
            else:
                os.environ["FILE_DATA_DB_PATH"] = prev_db

    def test_cli_generates_file_and_respects_blacklist(self):
        # Run CLI to generate for alice
        cmd = [sys.executable, os.path.join('src', 'generate_resume.py'), '--output-root', self.output_root, '--resume-dir', self.resume_dir, '--username', 'alice']
        proc = subprocess.run(cmd, capture_output=True, text=True, env=os.environ.copy())
        self.assertEqual(proc.returncode, 0, msg=f"stdout:{proc.stdout}\nstderr:{proc.stderr}")
        # Find generated file
        files = os.listdir(self.resume_dir)
        self.assertTrue(any(f.startswith('resume_alice_') and f.endswith('.md') for f in files))

        # Attempt to generate for bot (should be blocked)
        cmd_bot = [sys.executable, os.path.join('src', 'generate_resume.py'), '--output-root', self.output_root, '--resume-dir', self.resume_dir, '--username', 'githubclassroombot']
        proc2 = subprocess.run(cmd_bot, capture_output=True, text=True, env=os.environ.copy())
        self.assertNotEqual(proc2.returncode, 0)
        self.assertIn("Generation disabled for user 'githubclassroombot'", proc2.stdout + proc2.stderr)

        # Now override with --allow-bots
        cmd_bot_allow = [sys.executable, os.path.join('src', 'generate_resume.py'), '--output-root', self.output_root, '--resume-dir', self.resume_dir, '--username', 'githubclassroombot', '--allow-bots']
        proc3 = subprocess.run(cmd_bot_allow, capture_output=True, text=True, env=os.environ.copy())
        self.assertEqual(proc3.returncode, 0, msg=f"stdout:{proc3.stdout}\nstderr:{proc3.stderr}")
        files2 = os.listdir(self.resume_dir)
        self.assertTrue(any(f.startswith('resume_githubclassroombot_') and f.endswith('.md') for f in files2))

    def test_cli_saves_resume_to_db(self):
        db_path = os.path.join(self.tmpdir.name, 'file_data.db')
        # Ensure both this process and the subprocess use the temp DB
        os.environ['FILE_DATA_DB_PATH'] = db_path
        env = os.environ.copy()

        # Initialize database with resumes table
        import db as db_mod
        db_mod = importlib.reload(db_mod)
        db_mod.init_db()

        project_name = 'assignment-5-tcp-and-udp-programming-with-java-alice'
        project_path = os.path.join(self.tmpdir.name, project_name)
        git_metrics = {
            'commits_per_author': {'alice': 3},
            'lines_added_per_author': {'alice': 120},
            'files_changed_per_author': {'alice': ['src/Main.java', 'README.md']},
            'project_start': '2025-01-01 00:00:00',
            'total_commits': 3,
        }
        tech_summary = {
            'languages': ['Java', 'Python'],
            'frameworks': ['Flask'],
            'high_confidence_languages': ['Java', 'Python'],
            'medium_confidence_languages': [],
            'low_confidence_languages': [],
            'high_confidence_frameworks': ['Flask'],
            'medium_confidence_frameworks': [],
            'low_confidence_frameworks': [],
        }
        conn = db_mod.get_connection()
        try:
            conn.execute(
                "INSERT INTO projects (name, project_path, git_metrics_json, tech_json) VALUES (?, ?, ?, ?)",
                (project_name, project_path, json.dumps(git_metrics), json.dumps(tech_summary)),
            )
            conn.commit()
        finally:
            conn.close()

        cmd = [
            sys.executable, os.path.join('src', 'generate_resume.py'),
            '--output-root', self.output_root,
            '--resume-dir', self.resume_dir,
            '--username', 'alice',
            '--save-to-db'
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
        self.assertEqual(proc.returncode, 0, msg=f"stdout:{proc.stdout}\nstderr:{proc.stderr}")

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT username, resume_path, metadata_json FROM resumes").fetchall()
        conn.close()
        
        # Close any cached connections to allow cleanup
        import gc
        gc.collect()
        
        self.assertTrue(any(r['username'] == 'alice' for r in rows))


if __name__ == '__main__':
    unittest.main()
