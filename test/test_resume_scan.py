import os
import pytest
from unittest.mock import patch, MagicMock

from regenerate_resume_scan import resume_scan


def test_resume_scan_invalid_path():
    with pytest.raises(ValueError):
        resume_scan("")


def test_resume_scan_valid_directory(tmp_path):
    fake_repo = tmp_path / "repo"
    fake_repo.mkdir()

    with patch("regenerate_resume_scan.detect_languages_and_frameworks") as mock_langs, \
         patch("regenerate_resume_scan.detect_skills") as mock_skills, \
         patch("regenerate_resume_scan.analyze_repo") as mock_metrics, \
         patch("regenerate_resume_scan.gather_project_info") as mock_project_info, \
         patch("regenerate_resume_scan.output_project_info"), \
         patch("regenerate_resume_scan.save_scan"):

        mock_langs.return_value = {"languages": ["Python"]}
        mock_skills.return_value = {"skills": ["pytest"]}
        mock_metrics.return_value = {
            "commits_per_author": {"alice": 5}
        }
        mock_project_info.return_value = {
            "languages": ["Python"],
            "frameworks": [],
            "skills": ["pytest"],
            "generated_at": "2026-01-10",
        }

        result = resume_scan(str(fake_repo))

        assert result["path"] == str(fake_repo)
        assert "Python" in result["languages"]
        assert "pytest" in result["skills"]
        assert "alice" in result["contributors"]
