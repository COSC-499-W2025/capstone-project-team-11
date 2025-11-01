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
    """Remove a directory tree robustly on Windows by fixing permissions on error.

    This helper attempts to change file permissions and retry removal when
    shutil.rmtree raises an error (common on Windows with read-only bits).
    """
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


class TestContribMetrics(unittest.TestCase):
    @unittest.skipUnless(_git_available(), "git is required for these tests")
    def test_single_author_metrics(self):
        tmp = tempfile.mkdtemp()
        try:
            # init git repo
            _run(['git', 'init'], cwd=tmp)
            _run(['git', 'config', 'user.name', 'Alice'], cwd=tmp)
            _run(['git', 'config', 'user.email', 'alice@example.com'], cwd=tmp)

            # create a code file and commit
            p = os.path.join(tmp, 'app.py')
            with open(p, 'w') as f:
                f.write('print(1)\n')
            _run(['git', 'add', 'app.py'], cwd=tmp)
            _run(['git', 'commit', '-m', 'add app.py'], cwd=tmp)

            metrics = analyze_repo(tmp)
            self.assertEqual(metrics['total_commits'], 1)
            self.assertIn('Alice', metrics['commits_per_author'])
            self.assertGreaterEqual(metrics['lines_added_per_author'].get('Alice', 0), 1)
            # activity category 'code' should have at least 1 commit
            self.assertGreaterEqual(metrics['activity_counts_per_category'].get('code', 0), 1)
        finally:
            _robust_rmtree(tmp)

    @unittest.skipUnless(_git_available(), "git is required for these tests")
    def test_multiple_authors(self):
        tmp = tempfile.mkdtemp()
        try:
            _run(['git', 'init'], cwd=tmp)
            # local committer config
            _run(['git', 'config', 'user.name', 'CI'], cwd=tmp)
            _run(['git', 'config', 'user.email', 'ci@example.com'], cwd=tmp)

            fpath = os.path.join(tmp, 'module.py')
            with open(fpath, 'w') as f:
                f.write('a=1\n')
            _run(['git', 'add', 'module.py'], cwd=tmp)
            # commit by Author A
            env = os.environ.copy()
            env.update({'GIT_AUTHOR_NAME': 'AuthorA', 'GIT_AUTHOR_EMAIL': 'a@example.com', 'GIT_COMMITTER_NAME': 'AuthorA', 'GIT_COMMITTER_EMAIL': 'a@example.com'})
            _run(['git', 'commit', '-m', 'first commit'], cwd=tmp, env=env)

            # modify and commit by AuthorB
            with open(fpath, 'a') as f:
                f.write('b=2\n')
            _run(['git', 'add', 'module.py'], cwd=tmp)
            env2 = os.environ.copy()
            env2.update({'GIT_AUTHOR_NAME': 'AuthorB', 'GIT_AUTHOR_EMAIL': 'b@example.com', 'GIT_COMMITTER_NAME': 'AuthorB', 'GIT_COMMITTER_EMAIL': 'b@example.com'})
            _run(['git', 'commit', '-m', 'second commit'], cwd=tmp, env=env2)

            metrics = analyze_repo(tmp)
            self.assertEqual(metrics['total_commits'], 2)
            # Normalization may have inserted a space (e.g. 'AuthorA' -> 'Author A'),
            # so check canonicalized keys (remove whitespace, lowercase) to be robust.
            def canonical(s: str) -> str:
                return ''.join(s.split()).lower()

            keys = list(metrics['commits_per_author'].keys())
            self.assertTrue(any(canonical(k) == 'authora' for k in keys))
            self.assertTrue(any(canonical(k) == 'authorb' for k in keys))
            # both authors should have non-zero added lines (sum values for canonical match)
            def added_for(canon_name: str) -> int:
                total = 0
                for k, v in metrics['lines_added_per_author'].items():
                    if canonical(k) == canon_name:
                        total += v
                return total

            self.assertGreater(added_for('authora'), 0)
            self.assertGreater(added_for('authorb'), 0)
            # code category should be touched
            self.assertGreaterEqual(metrics['activity_counts_per_category'].get('code', 0), 2)
        finally:
            _robust_rmtree(tmp)


if __name__ == '__main__':
    unittest.main()
