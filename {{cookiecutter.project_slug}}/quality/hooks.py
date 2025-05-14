"""
Hooks for pre-commit and other quality checks.
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from .formatters import run_formatters
from .linters import run_linters


def setup_hooks(hooks_dir: Optional[Path] = None) -> Dict[str, bool]:
    """
    Konfiguruje git hooks dla projektu.

    Args:
        hooks_dir: Ścieżka do katalogu z git hooks. Jeśli None, używa domyślnej ścieżki.

    Returns:
        Słownik z informacją o zainstalowanych hooks.
    """
    if hooks_dir is None:
        git_dir = Path(
            subprocess.check_output(["git", "rev-parse", "--git-dir"], text=True).strip()
        )
        hooks_dir = git_dir / "hooks"

    hooks_dir.mkdir(exist_ok=True)

    # Lista hooków do zainstalowania
    hooks = {
        "pre-commit": _create_pre_commit_hook,
        "pre-push": _create_pre_push_hook,
    }

    results = {}

    for hook_name, hook_creator in hooks.items():
        hook_path = hooks_dir / hook_name
        hook_creator(hook_path)
        os.chmod(hook_path, 0o755)  # Nadanie uprawnień wykonywania
        results[hook_name] = True

    return results


def _create_pre_commit_hook(hook_path: Path) -> None:
    """
    Tworzy hook pre-commit, który sprawdza formatowanie kodu.

    Args:
        hook_path: Ścieżka do pliku hooka.
    """
    content = """
#!/bin/bash
set -e

# Uruchom formatery kodu
python -m quality.formatters $(git diff --cached --name-only --diff-filter=ACM | grep -E '\\.py$')

# Dodaj sformatowane pliki do staging
git add $(git diff --cached --name-only --diff-filter=ACM | grep -E '\\.py$')
"""

    with open(hook_path, "w") as f:
        f.write(content)


def _create_pre_push_hook(hook_path: Path) -> None:
    """
    Tworzy hook pre-push, który uruchamia lintery i testy.

    Args:
        hook_path: Ścieżka do pliku hooka.
    """
    content = """
#!/bin/bash
set -e

# Uruchom lintery
python -m quality.linters

# Uruchom testy
python -m pytest
"""

    with open(hook_path, "w") as f:
        f.write(content)
