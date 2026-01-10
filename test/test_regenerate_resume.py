import os
import pytest
from unittest.mock import patch

from regenerate_resume import regenerate_resume


def test_regenerate_resume_missing_username():
    with pytest.raises(ValueError):
        regenerate_resume(username="", resume_path="resumes/test.md")


def test_regenerate_resume_missing_resume_path():
    with pytest.raises(ValueError):
        regenerate_resume(username="user", resume_path="")


def test_regenerate_resume_creates_file(tmp_path):
    output_root = tmp_path / "output"
    output_root.mkdir()

    resume_path = tmp_path / "resumes" / "resume.md"

    with patch("regenerate_resume.collect_projects") as mock_collect, \
         patch("regenerate_resume.aggregate_for_user") as mock_agg, \
         patch("regenerate_resume.render_markdown") as mock_render:

        mock_collect.return_value = ([], [])
        mock_agg.return_value = {"username": "testuser"}
        mock_render.return_value = "# Resume"

        result = regenerate_resume(
            username="testuser",
            resume_path=str(resume_path),
            output_root=str(output_root),
        )

        assert os.path.exists(resume_path)
        with open(resume_path, "r") as f:
            assert "# Resume" in f.read()

        assert result == str(resume_path)
