import json
import os
import httpx
import hashlib
from collections import Counter
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from db import get_connection, _ensure_projects_column


DEFAULT_MODEL = "llama3.2:3b"
DEFAULT_OLLAMA_HOST = os.environ.get("OLLAMA_HOST")
README_CANDIDATES = (
    "README.md",
    "README.txt",
    "README.rst",
    "README",
)


def _read_text_file(path: str, max_chars: int = 4000) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read(max_chars)
    except Exception:
        return None


def _find_readme(project_root: str) -> Tuple[Optional[str], Optional[str]]:
    if not project_root or not os.path.isdir(project_root):
        return None, None

    # Prefer common README names first.
    for name in README_CANDIDATES:
        candidate = os.path.join(project_root, name)
        if os.path.isfile(candidate):
            return candidate, _read_text_file(candidate)

    # Fallback: first file matching README* at root.
    try:
        for entry in os.listdir(project_root):
            if entry.upper().startswith("README") and os.path.isfile(os.path.join(project_root, entry)):
                candidate = os.path.join(project_root, entry)
                return candidate, _read_text_file(candidate)
    except Exception:
        pass

    return None, None


def _extract_extension(path: str) -> str:
    if not path:
        return ""
    # zip display paths can include "zipfile:inner/path"
    name = path.split(":")[-1]
    _, ext = os.path.splitext(name)
    return ext.lower()


def build_summary_input(
    project_name: str,
    project_root: str,
    files_found: List,
    languages: List[str],
    frameworks: List[str],
    skills: List[str],
) -> Dict:
    ext_counts = Counter()
    for item in files_found or []:
        display = item[0] if isinstance(item, tuple) else item
        ext = _extract_extension(display)
        if ext:
            ext_counts[ext] += 1

    readme_path, readme_text = _find_readme(project_root)
    readme_excerpt = readme_text[:2000] if readme_text else None
    readme_filename = os.path.basename(readme_path) if readme_path else None

    return {
        "project_name": project_name,
        "project_root_name": os.path.basename(project_root) if project_root else None,
        "total_files": len(files_found or []),
        "file_extensions": [
            {"ext": ext, "count": count}
            for ext, count in ext_counts.most_common(10)
        ],
        "languages": languages or [],
        "frameworks": frameworks or [],
        "skills": skills or [],
        "readme_filename": readme_filename,
        "readme_excerpt": readme_excerpt,
    }


def compute_input_hash(payload: Dict) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _get_cached_summary(project_name: str, input_hash: str, model: str) -> Optional[str]:
    if not project_name or not input_hash:
        return None
    try:
        with get_connection() as conn:
            _ensure_projects_column(conn, "summary_text", "TEXT")
            _ensure_projects_column(conn, "summary_model", "TEXT")
            _ensure_projects_column(conn, "summary_input_hash", "TEXT")
            row = conn.execute(
                """
                SELECT summary_text
                FROM projects
                WHERE name = ? AND summary_input_hash = ? AND summary_model = ?
                """,
                (project_name, input_hash, model),
            ).fetchone()
            return row["summary_text"] if row and row["summary_text"] else None
    except Exception:
        return None


def _run_ollama(prompt: str, model: str, timeout: int = 120) -> Optional[str]:
    hosts = []
    if DEFAULT_OLLAMA_HOST:
        hosts.append(DEFAULT_OLLAMA_HOST)
    else:
        # Prefer Docker service name first, then local Ollama.
        hosts.extend(["http://ollama:11434", "http://localhost:11434"])

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    for host in hosts:
        url = f"{host.rstrip('/')}/api/generate"
        try:
            with httpx.Client(timeout=timeout) as client:
                res = client.post(url, json=payload)
                if res.status_code != 200:
                    continue
                data = res.json()
        except Exception:
            continue

        output = (data.get("response") or "").strip()
        if output:
            return output

    return None


def generate_summary_text(payload: Dict, model: str = DEFAULT_MODEL) -> Optional[str]:
    prompt = (
        "You are given structured project metadata and an optional README excerpt.\n"
        "Write a concise 3-5 sentence summary that covers:\n"
        "1) What the project is\n"
        "2) What problem it solves\n"
        "3) What it accomplishes\n\n"
        "Rules:\n"
        "- Use plain language.\n"
        "- Output only the summary text. Do not add any preface or label.\n"
        "- Do not mention git, commits, or contributors.\n"
        "- If information is missing, state that it is not specified.\n\n"
        "Project metadata (JSON):\n"
        f"{json.dumps(payload, indent=2, ensure_ascii=True)}\n"
    )
    result = _run_ollama(prompt, model=model)
    if not result:
        return None
    # Strip common prefatory phrases if the model still adds them.
    lowered = result.strip().lower()
    prefixes = (
        "here is a concise",
        "here is a brief",
        "summary:",
        "project summary:",
    )
    for prefix in prefixes:
        if lowered.startswith(prefix):
            # Remove the first line if it looks like a preface.
            lines = result.splitlines()
            if len(lines) > 1:
                return "\n".join(lines[1:]).strip()
    return result.strip()


def generate_resume_summary_text(payload: Dict, model: str = DEFAULT_MODEL) -> Optional[str]:
    prompt = (
        "You are given structured contributor and project metadata.\n"
        "Write a concise resume summary (3-6 sentences) that:\n"
        "1) Summarizes the contributor's overall work across projects\n"
        "2) Highlights key skills and technologies\n"
        "3) Explicitly mentions every project name provided\n\n"
        "Rules:\n"
        "- Use plain language.\n"
        "- Output only the summary text. Do not add any preface or label.\n"
        "- Do not mention consent, scanning, or LLMs.\n"
        "- If information is missing, state that it is not specified.\n\n"
        "Contributor metadata (JSON):\n"
        f"{json.dumps(payload, indent=2, ensure_ascii=True)}\n"
    )
    result = _run_ollama(prompt, model=model)
    if not result:
        return None
    lowered = result.strip().lower()
    prefixes = (
        "here is a concise",
        "here is a brief",
        "summary:",
        "resume summary:",
    )
    for prefix in prefixes:
        if lowered.startswith(prefix):
            lines = result.splitlines()
            if len(lines) > 1:
                return "\n".join(lines[1:]).strip()
    return result.strip()


def get_or_generate_summary(
    project_name: str,
    project_root: str,
    files_found: List,
    languages: List[str],
    frameworks: List[str],
    skills: List[str],
    model: str = DEFAULT_MODEL,
) -> Tuple[Optional[str], Optional[str], str, bool]:
    payload = build_summary_input(
        project_name=project_name,
        project_root=project_root,
        files_found=files_found,
        languages=languages,
        frameworks=frameworks,
        skills=skills,
    )
    input_hash = compute_input_hash(payload)
    cached = _get_cached_summary(project_name, input_hash, model)
    if cached:
        return cached, input_hash, model, True

    summary = generate_summary_text(payload, model=model)
    return summary, input_hash, model, False


def summary_timestamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
