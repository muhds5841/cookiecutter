"""Integracja z narzędziami analizy bezpieczeństwa kodu (Bandit)."""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Dict


def run_bandit(
        paths: List[str],
        config: Optional[Path] = None,
        level: str = "medium"
) -> int:
    """Uruchamia Bandit dla podanych ścieżek."""
    cmd = ["bandit", "-r"]

    # Ustawienie poziomu ważności
    cmd.extend(["-l", level])

    if config:
        cmd.extend(["-c", str(config)])

    cmd.extend(paths)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    return result.returncode


def run_security_checks(
        paths: List[str],
        config_dir: Optional[Path] = None,
        level: str = "medium"
) -> Dict[str, int]:
    """
    Uruchamia narzędzia analizy bezpieczeństwa dla podanych ścieżek.

    Args:
        paths: Lista ścieżek do sprawdzenia
        config_dir: Katalog z konfiguracjami
        level: Poziom ważności (low, medium, high)

    Returns:
        Słownik z kodami wyjścia dla poszczególnych narzędzi
    """
    results = {}

    if config_dir is None:
        # Domyślnie używamy konfiguracji z katalogu quality w głównym katalogu
        config_dir = Path(__file__).parent.parent.parent / "quality"

    bandit_config = config_dir / "bandit.yaml"
    results["bandit"] = run_bandit(
        paths,
        bandit_config if bandit_config.exists() else None,
        level
    )

    return results


if __name__ == "__main__":
    # Umożliwia uruchamianie modułu bezpośrednio jako skrypt
    import argparse

    parser = argparse.ArgumentParser(
        description="Uruchamia narzędzia analizy bezpieczeństwa dla kodu Python"
    )
    parser.add_argument("paths", nargs="+", help="Ścieżki do sprawdzenia")
    parser.add_argument("--config-dir", help="Katalog z konfiguracjami")
    parser.add_argument("--level", choices=["low", "medium", "high"], default="medium",
                        help="Poziom ważności")

    args = parser.parse_args()

    config_dir = Path(args.config_dir) if args.config_dir else None
    results = run_security_checks(args.paths, config_dir, args.level)

    # Jeśli którekolwiek narzędzie zgłosiło błędy, zwróć błąd
    if any(results.values()):
        sys.exit(1)