# tests/test_regenerate_portfolio.py
import os
import tempfile
import shutil
import pytest
from unittest import mock

# --- Import modules to test ---
import regenerate_portfolio_scan as rps
import regenerate_portfolio as rp
import generate_portfolio as gp

# ---------------------------
# Tests for regenerate_portfolio_scan.py
# ---------------------------
def test_portfolio_scan_invalid_path():
    with pytest.raises(ValueError):
        rps.portfolio_scan("nonexistent_path")

@mock.patch("regenerate_portfolio_scan.run_headless_scan")
def test_portfolio_scan_directory(mock_scan):
    with tempfile.TemporaryDirectory() as tmpdir:
        rps.portfolio_scan(tmpdir)
        mock_scan.assert_called_once()
        args, kwargs = mock_scan.call_args
        assert kwargs["path"] == tmpdir
        assert kwargs["recursive"] is True
        assert kwargs["save_to_db"] is True

@mock.patch("regenerate_portfolio_scan.run_headless_scan")
def test_portfolio_scan_zip_file(mock_scan):
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "test.zip")
        with open(zip_path, "wb") as f:
            f.write(b"Fake zip content")
        rps.portfolio_scan(zip_path)
        mock_scan.assert_called_once()
        assert "zip_extract_dir" in mock_scan.call_args[1]

# ---------------------------
# Tests for regenerate_portfolio.py
# ---------------------------
@mock.patch("regenerate_portfolio.collect_projects")
@mock.patch("regenerate_portfolio.aggregate_projects_for_portfolio")
@mock.patch("regenerate_portfolio.build_portfolio")
@mock.patch("regenerate_portfolio.save_portfolio")
def test_regenerate_portfolio_happy_path(mock_save, mock_build, mock_agg, mock_collect):
    username = "testuser"
    with tempfile.TemporaryDirectory() as output_root:
        # Setup mocks
        mock_collect.return_value = ({}, {})
        mock_agg.return_value = [{"project_name": "proj1"}]
        mock_portfolio = mock.Mock()
        mock_portfolio.render_markdown.return_value = "# Portfolio"
        mock_portfolio.sections = {"overview": mock.Mock()}
        mock_build.return_value = mock_portfolio

        portfolio_path = os.path.join(output_root, "portfolio.md")
        rp.regenerate_portfolio(username=username, portfolio_path=portfolio_path, output_root=output_root, save_to_db=True)

        # File written
        assert os.path.exists(portfolio_path)
        with open(portfolio_path) as f:
            content = f.read()
        assert "# Portfolio" in content

        mock_save.assert_called_once()

def test_regenerate_portfolio_missing_username(tmp_path):
    with pytest.raises(ValueError):
        rp.regenerate_portfolio("", tmp_path / "file.md", output_root=tmp_path)

def test_regenerate_portfolio_missing_portfolio_path(tmp_path):
    with pytest.raises(ValueError):
        rp.regenerate_portfolio("user", "", output_root=tmp_path)

def test_regenerate_portfolio_missing_output_root(tmp_path):
    # Non-existent output_root
    missing_root = tmp_path / "nope"
    with mock.patch("regenerate_portfolio.collect_projects") as mock_collect, \
         mock.patch("regenerate_portfolio.aggregate_projects_for_portfolio") as mock_agg, \
         mock.patch("regenerate_portfolio.build_portfolio") as mock_build:
        mock_collect.return_value = ({}, {})
        mock_agg.return_value = [{"project_name": "proj1"}]
        mock_portfolio = mock.Mock()
        mock_portfolio.render_markdown.return_value = "# Portfolio"
        mock_portfolio.sections = {"overview": mock.Mock()}
        mock_build.return_value = mock_portfolio

        rp.regenerate_portfolio("user", tmp_path / "file.md", output_root=missing_root)
        assert (tmp_path / "file.md").exists()

# ---------------------------
# Tests for generate_portfolio.py modifications
# ---------------------------
def test_overwrite_flag(tmp_path):
    # Create dummy portfolio file
    overwrite_file = tmp_path / "existing.md"
    overwrite_file.write_text("OLD CONTENT")

    # Mock projects
    projects = {
        "proj1": {
            "project_path": "/path/to/proj1",
            "contributions": {"user": {"commits": 1, "files": []}},
            "languages": ["Python"], "frameworks": [], "skills": ["OOP"]
        }
    }

    # Mock collect_projects
    with mock.patch("generate_portfolio.collect_projects", return_value=(projects, {})):
        # Build portfolio normally
        portfolio_projects = gp.aggregate_projects_for_portfolio("user", projects)
        portfolio = gp.build_portfolio("user", portfolio_projects)

        md = portfolio.render_markdown()

        # Overwrite file
        out_path = str(overwrite_file)
        with open(out_path, "w") as f:
            f.write(md)

        content = overwrite_file.read_text()
        assert "# Portfolio — user" in content
        assert "proj1" in content

def test_section_rendering():
    sections = {
        "overview": gp.build_overview_section([], "user"),
        "tech_summary": gp.build_tech_summary_section([])
    }
    portfolio = gp.Portfolio("user", sections)
    md = portfolio.render_markdown()
    assert "# Portfolio — user" in md
    assert "Overview" in md
    assert "Technology Summary" in md
