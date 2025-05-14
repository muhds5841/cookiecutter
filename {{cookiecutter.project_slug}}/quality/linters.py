"""Integracja z linterami (Pylint, Flake8)."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union


def run_pylint(paths: List[str], rcfile: Optional[Path] = None) -> int:
    """Uruchamia Pylint dla podanych ścieżek."""
    cmd = ["pylint"]
    if rcfile:
        cmd.extend(["--rcfile", str(rcfile)])
    cmd.extend(paths)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    return result.returncode


def run_flake8(paths: List[str], config: Optional[Path] = None) -> int:
    """Uruchamia Flake8 dla podanych ścieżek."""
    cmd = ["flake8"]
    if config:
        cmd.extend(["--config", str(config)])
    cmd.extend(paths)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    return result.returncode


def run_linters(
    paths: List[str], config_dir: Optional[Path] = None, linters: List[str] = ["pylint", "flake8"]
) -> Dict[str, int]:
    """
    Uruchamia wybrane lintery dla podanych ścieżek.

    Args:
        paths: Lista ścieżek do sprawdzenia
        config_dir: Katalog z konfiguracjami linterów
        linters: Lista linterów do uruchomienia

    Returns:
        Słownik z kodami wyjścia dla poszczególnych linterów
    """
    results = {}

    if config_dir is None:
        # Domyślnie używamy konfiguracji z katalogu quality w głównym katalogu
        config_dir = Path(__file__).parent.parent.parent / "quality"

    if "pylint" in linters:
        pylint_rcfile = config_dir / ".pylintrc"
        results["pylint"] = run_pylint(paths, pylint_rcfile if pylint_rcfile.exists() else None)

    if "flake8" in linters:
        flake8_config = config_dir / ".flake8"
        results["flake8"] = run_flake8(paths, flake8_config if flake8_config.exists() else None)

    return results


if __name__ == "__main__":
    # Umożliwia uruchamianie modułu bezpośrednio jako skrypt
    import argparse

    parser = argparse.ArgumentParser(description="Uruchamia lintery dla kodu Python")
    parser.add_argument("paths", nargs="+", help="Ścieżki do sprawdzenia")
    parser.add_argument("--config-dir", help="Katalog z konfiguracjami linterów")
    parser.add_argument(
        "--linters", nargs="+", default=["pylint", "flake8"], help="Lintery do uruchomienia"
    )

    args = parser.parse_args()

    config_dir = Path(args.config_dir) if args.config_dir else None
    results = run_linters(args.paths, config_dir, args.linters)

    # Jeśli którykolwiek linter zgłosił błędy, zwróć błąd
    if any(results.values()):
        sys.exit(1)
