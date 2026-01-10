import builtins
from unittest.mock import patch, MagicMock

from main_menu import handle_add_to_resume


def test_handle_add_to_resume_calls_scan_and_regenerate(capsys):
    resume_row = {
        "id": 1,
        "username": "testuser",
        "resume_path": "resumes/test_resume.md",
    }
    path = "/fake/project/path"

    with patch("main_menu.resume_scan") as mock_scan, \
         patch("main_menu.regenerate_resume") as mock_regen:

        handle_add_to_resume(resume_row, path)

        mock_scan.assert_called_once_with(path, save_to_db=True)
        mock_regen.assert_called_once_with(
            username="testuser",
            resume_path="resumes/test_resume.md",
        )

    captured = capsys.readouterr()
    assert "Scanning new directory" in captured.out
    assert "Regenerating resume" in captured.out
    assert "Resume successfully updated" in captured.out
