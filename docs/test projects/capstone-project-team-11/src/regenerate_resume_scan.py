"""
regenerate_resume_scan.py
Headless scan wrapper used during resume regeneration.
"""

import os
import tempfile
from scan import run_headless_scan

def resume_scan(path: str, save_to_db: bool = True):
    """
    Perform a headless scan on a directory or zip, then regenerate resume.
    """
    if not path or not os.path.exists(path):
        raise ValueError(f"Path does not exist: {path}")

    zip_ctx = None
    zip_extract_dir = None

    try:
        if os.path.isfile(path) and path.lower().endswith(".zip"):
            zip_ctx = tempfile.TemporaryDirectory()
            zip_extract_dir = zip_ctx.name

        # Run the headless scan
        run_headless_scan(
            path=path,
            recursive=True,
            file_type=None,
            save_to_db=save_to_db,
            zip_extract_dir=zip_extract_dir,
        )
    finally:
        if zip_ctx:
            zip_ctx.cleanup()
