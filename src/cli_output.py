# src/cli_output.py
from __future__ import annotations
from typing import Optional

def print_error(message: str, hint: Optional[str] = None) -> None:
    print(f"\nError: {message}")
    if hint:
        print(f"  Hint: {hint}")
