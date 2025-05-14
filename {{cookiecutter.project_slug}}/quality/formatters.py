"""Integracja z narzędziami formatowania kodu (Black, isort)."""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union


def run_black(paths: List[str], check: bool = False, config: Optional[Path] = None) -> int:
    """Uruchamia Black dla podanych ścieżek."""
    cmd = ["black"]
    if check:
        cmd.append("--check")
    if config:
        cmd.extend(["--config", str(config)])
    cmd.extend(paths)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    return result.returncode


def run_isort(paths: List[str], check: bool = False, config: Optional[Path] = None) -> int:
    """Uruchamia isort dla podanych ścieżek."""
    cmd = ["isort"]
    if check:
        cmd.append("--check")
    if config:
        cmd.extend(["--settings-path", str(config)])
    cmd.extend(paths)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    return result.returncode


def run_formatters(
    paths: List[str],
    check: bool = False,
    config_file: Optional[Path] = None,
    formatters: List[str] = ["black", "isort"],
) -> Dict[str, int]:
    """
    Uruchamia wybrane formatery dla podanych ścieżek.

    Args:
        paths: Lista ścieżek do sformatowania
        check: Jeśli True, tylko sprawdza formatowanie, nie modyfikuje plików
        config_file: Ścieżka do pliku konfiguracyjnego (pyproject.toml)
        formatters: Lista formaterów do uruchomienia

    Returns:
        Słownik z kodami wyjścia dla poszczególnych formaterów
    """
    results = {}

    if "black" in formatters:
        results["black"] = run_black(paths, check, config_file)

    if "isort" in formatters:
        results["isort"] = run_isort(paths, check, config_file)

    return results


if __name__ == "__main__":
    # Umożliwia uruchamianie modułu bezpośrednio jako skrypt
    import argparse

    parser = argparse.ArgumentParser(description="Uruchamia formatery dla kodu Python")
    parser.add_argument("paths", nargs="+", help="Ścieżki do sformatowania")
    parser.add_argument("--check", action="store_true", help="Tylko sprawdza formatowanie")
    parser.add_argument("--config", help="Plik konfiguracyjny")
    parser.add_argument(
        "--formatters", nargs="+", default=["black", "isort"], help="Formatery do uruchomienia"
    )

    args = parser.parse_args()

    config_file = Path(args.config) if args.config else None
    results = run_formatters(args.paths, args.check, config_file, args.formatters)

    # Jeśli którykolwiek formater zgłosił błędy, zwróć błąd
    if any(results.values()):
        sys.exit(1)
