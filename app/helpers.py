from os import getenv
import os
from typing import Optional
from pathlib import Path

def getenv_or_raise(key: str) -> str:
    value = getenv(key)
    if not value:
        raise ValueError(f"{key} environment variable is not set")
    return value

def find_project_root(current_path) -> Optional[Path]:
    """
    Attempts to find the project root by looking for a marker file/directory.
    This example looks for a '.git' directory.
    """
    current_dir = os.path.abspath(current_path)
    while True:
        if os.path.exists(os.path.join(current_dir, 'uv.lock')):
            return current_dir
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            return None
        current_dir = parent_dir
