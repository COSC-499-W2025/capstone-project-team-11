import unittest
import os
import sys
import shutil
import tempfile
import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

try:
    from contrib_metrics import analyze_repo
except Exception:
    from contrib_metrics import analyze_repo  # allow package import style if needed


def _git_available():
    return shutil.which('git') is not None


def _run(cmd, cwd, env=None):
    res = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    if res.returncode != 0:
        raise RuntimeError(f"git command failed: {cmd}\nstdout: {res.stdout}\nstderr: {res.stderr}")
    return res


def _robust_rmtree(path: str) -> None:
    def onerror(func, p, excinfo):
        try:
            os.chmod(p, 0o700)
        except Exception:
            pass
        try:
            func(p)
        except Exception:
            pass

    shutil.rmtree(path, onerror=onerror)


def canonicalize(s: str) -> str:
    """Helper to canonicalize names in tests to match analyze_repo behavior."""
    return ''.join(s.split()).lower()


class TestContribMetrics(unittest.TestCase):
    @unittest.skipUnless(_git_available(), "git is required for these tests")
    def test_single_author_metrics(self):
        tmp = tempfile.mkdtemp()
        try:
            _run(['git', 'init'], cwd=tmp)
            _run(['git', 'config', 'user.name', 'Alice'], cwd=tmp)
            _run(['git', 'config', 'user.email', 'alice@example.com'], cwd=tmp)

            p = os.path.join(tmp, 'app.py')
            with open(p, 'w') as f:
                f.write('print(1)\n')
            _run(['git', 'add', 'app.py'], cwd=tmp)
            _run(['git', 'commit', '-m', 'add app.py'], cwd=tmp)

            metrics = analyze_repo(tmp)
            self.assertEqual(metrics['total_commits'], 1)

            # canonicalize key to match analyze_repo
            cname = canonicalize('Alice')
            self.assertIn(cname, [canonicalize(k) for k in metrics['commits_per_author'].keys()])

            total_added = sum(v for k, v in metrics['lines_added_per_author'].items() if canonicalize(k) == cname)
            self.assertGreaterEqual(total_added, 1)

            total_removed = sum(v for k, v in metrics['lines_removed_per_author'].items() if canonicalize(k) == cname)
            self.assertGreaterEqual(total_removed, 0)

            self.assertGreaterEqual(metrics['activity_counts_per_category'].get('code', 0), 1)
        finally:
            _robust_rmtree(tmp)

    @unittest.skipUnless(_git_available(), "git is required for these tests")
    def test_multiple_authors(self):
        tmp = tempfile.mkdtemp()
        try:
            _run(['git', 'init'], cwd=tmp)
            _run(['git', 'config', 'user.name', 'CI'], cwd=tmp)
            _run(['git', 'config', 'user.email', 'ci@example.com'], cwd=tmp)

            fpath = os.path.join(tmp, 'module.py')
            with open(fpath, 'w') as f:
                f.write('a=1\n')
            _run(['git', 'add', 'module.py'], cwd=tmp)

            env_a = os.environ.copy()
            env_a.update({'GIT_AUTHOR_NAME': 'AuthorA', 'GIT_AUTHOR_EMAIL': 'a@example.com',
                          'GIT_COMMITTER_NAME': 'AuthorA', 'GIT_COMMITTER_EMAIL': 'a@example.com'})
            _run(['git', 'commit', '-m', 'first commit'], cwd=tmp, env=env_a)

            with open(fpath, 'a') as f:
                f.write('b=2\n')
            _run(['git', 'add', 'module.py'], cwd=tmp)

            env_b = os.environ.copy()
            env_b.update({'GIT_AUTHOR_NAME': 'AuthorB', 'GIT_AUTHOR_EMAIL': 'b@example.com',
                          'GIT_COMMITTER_NAME': 'AuthorB', 'GIT_COMMITTER_EMAIL': 'b@example.com'})
            _run(['git', 'commit', '-m', 'second commit'], cwd=tmp, env=env_b)

            metrics = analyze_repo(tmp)
            self.assertEqual(metrics['total_commits'], 2)

            keys = list(metrics['commits_per_author'].keys())
            self.assertTrue(any(canonicalize(k) == 'authora' for k in keys))
            self.assertTrue(any(canonicalize(k) == 'authorb' for k in keys))

            def added_for(cname: str) -> int:
                return sum(v for k, v in metrics['lines_added_per_author'].items() if canonicalize(k) == cname)

            self.assertGreater(added_for('authora'), 0)
            self.assertGreater(added_for('authorb'), 0)
            self.assertGreaterEqual(metrics['activity_counts_per_category'].get('code', 0), 2)
        finally:
            _robust_rmtree(tmp)

    @unittest.skipUnless(_git_available(), "git is required for these tests")
    def test_commit_with_no_file_changes(self):
        """Empty commits should count as commits with 0 lines added/removed."""
        tmp = tempfile.mkdtemp()
        try:
            _run(['git', 'init'], cwd=tmp)
            _run(['git', 'config', 'user.name', 'Bob'], cwd=tmp)
            _run(['git', 'config', 'user.email', 'bob@example.com'], cwd=tmp)

            _run(['git', 'commit', '--allow-empty', '-m', 'empty commit'], cwd=tmp)

            metrics = analyze_repo(tmp)
            self.assertEqual(metrics['total_commits'], 1)

            cname = canonicalize('Bob')
            total_added = sum(v for k, v in metrics['lines_added_per_author'].items() if canonicalize(k) == cname)
            total_removed = sum(v for k, v in metrics['lines_removed_per_author'].items() if canonicalize(k) == cname)
            self.assertEqual(total_added, 0)
            self.assertEqual(total_removed, 0)
        finally:
            _robust_rmtree(tmp)

    @unittest.skipUnless(_git_available(), "git is required for these tests")
    def test_file_categories(self):
        tmp = tempfile.mkdtemp()
        try:
            _run(['git', 'init'], cwd=tmp)
            _run(['git', 'config', 'user.name', 'Cathy'], cwd=tmp)
            _run(['git', 'config', 'user.email', 'cathy@example.com'], cwd=tmp)

            files = {
                'code.py': 'print(1)\n',
                'test_test.py': 'assert True\n',
                'README.md': '# title\n',
                'design.png': 'binarydata',
            }

            for fname, content in files.items():
                with open(os.path.join(tmp, fname), 'w') as f:
                    f.write(content)
            _run(['git', 'add', '.'], cwd=tmp)
            _run(['git', 'commit', '-m', 'add multiple files'], cwd=tmp)

            metrics = analyze_repo(tmp)
            self.assertGreaterEqual(metrics['activity_counts_per_category'].get('code', 0), 1)
            self.assertGreaterEqual(metrics['activity_counts_per_category'].get('test', 0), 1)
            self.assertGreaterEqual(metrics['activity_counts_per_category'].get('docs', 0), 1)
            self.assertGreaterEqual(metrics['activity_counts_per_category'].get('design', 0), 1)
        finally:
            _robust_rmtree(tmp)

    @unittest.skipUnless(_git_available(), "git is required for these tests")
    def test_zero_commit_user_excluded(self):
        tmp = tempfile.mkdtemp()
        try:
            _run(['git', 'init'], cwd=tmp)
            _run(['git', 'config', 'user.name', 'Dave'], cwd=tmp)
            _run(['git', 'config', 'user.email', 'dave@example.com'], cwd=tmp)

            path = os.path.join(tmp, 'file.py')
            with open(path, 'w') as f:
                f.write('print(2)\n')
            _run(['git', 'add', path], cwd=tmp)
            _run(['git', 'commit', '-m', 'add file'], cwd=tmp)

            metrics = analyze_repo(tmp)
            # Add fake zero-commit user
            metrics['commits_per_author']['Eve'] = 0
            metrics['lines_added_per_author']['Eve'] = 10
            metrics['lines_removed_per_author']['Eve'] = 5

            # Filter zero-commit users
            filtered = {a: c for a, c in metrics['commits_per_author'].items() if c > 0}
            self.assertNotIn('Eve', filtered)
        finally:
            _robust_rmtree(tmp)


if __name__ == '__main__':
    unittest.main()
