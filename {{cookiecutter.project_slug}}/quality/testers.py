"""Integracja z narzędziami testowymi (pytest, tox)."""

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def run_pytest(
    paths: List[str] = ["tests"],
    config: Optional[Path] = None,
    coverage: bool = True,
    markers: Optional[List[str]] = None,
    extra_args: Optional[List[str]] = None,
) -> int:
    """Uruchamia pytest dla podanych ścieżek."""
    cmd = ["pytest"]

    if config:
        cmd.extend(["-c", str(config)])

    if coverage:
        cmd.extend(["--cov=.", "--cov-report=term", "--cov-report=xml"])

    if markers:
        for marker in markers:
            cmd.extend(["-m", marker])

    if extra_args:
        cmd.extend(extra_args)

    cmd.extend(paths)

    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


def run_tox(envs: Optional[List[str]] = None, config: Optional[Path] = None) -> int:
    """Uruchamia tox dla podanych środowisk."""
    cmd = ["tox"]

    if envs:
        env_str = ",".join(envs)
        cmd.extend(["-e", env_str])

    if config:
        cmd.extend(["-c", str(config)])

    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


def run_tests(
    test_type: str = "pytest",
    paths: List[str] = ["tests"],
    config_dir: Optional[Path] = None,
    coverage: bool = True,
    markers: Optional[List[str]] = None,
    tox_envs: Optional[List[str]] = None,
    extra_args: Optional[List[str]] = None,
) -> int:
    """
    Uruchamia testy wybranym narzędziem.

    Args:
        test_type: Typ testu do uruchomienia ("pytest" lub "tox")
        paths: Ścieżki do testowania (dla pytest)
        config_dir: Katalog z konfiguracjami
        coverage: Czy mierzyć pokrycie kodu
        markers: Markery testów (dla pytest)
        tox_envs: Środowiska tox do uruchomienia
        extra_args: Dodatkowe argumenty dla narzędzia testowego

    Returns:
        Kod wyjścia (0 oznacza sukces)
    """
    if config_dir is None:
        # Domyślnie używamy konfiguracji z katalogu quality w głównym katalogu
        config_dir = Path(__file__).parent.parent.parent / "quality"

    if test_type == "pytest":
        pytest_config = config_dir / "pytest.ini"
        return run_pytest(
            paths, pytest_config if pytest_config.exists() else None, coverage, markers, extra_args
        )
    elif test_type == "tox":
        tox_config = config_dir / "tox.ini"
        return run_tox(tox_envs, tox_config if tox_config.exists() else None)
    else:
        print(f"Nieznany typ testu: {test_type}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    # Umożliwia uruchamianie modułu bezpośrednio jako skrypt
    import argparse

    parser = argparse.ArgumentParser(description="Uruchamia testy dla kodu Python")
    parser.add_argument(
        "--test-type", choices=["pytest", "tox"], default="pytest", help="Typ testu do uruchomienia"
    )
    parser.add_argument(
        "--paths", nargs="+", default=["tests"], help="Ścieżki do testowania (dla pytest)"
    )
    parser.add_argument("--config-dir", help="Katalog z konfiguracjami")
    parser.add_argument("--no-coverage", action="store_true", help="Nie mierz pokrycia kodu")
    parser.add_argument("--markers", nargs="+", help="Markery testów (dla pytest)")
    parser.add_argument("--tox-envs", nargs="+", help="Środowiska tox do uruchomienia")
    parser.add_argument("--extra-args", nargs="+", help="Dodatkowe argumenty")

    args = parser.parse_args()

    config_dir = Path(args.config_dir) if args.config_dir else None
    exit_code = run_tests(
        args.test_type,
        args.paths,
        config_dir,
        not args.no_coverage,
        args.markers,
        args.tox_envs,
        args.extra_args,
    )

    sys.exit(exit_code)
