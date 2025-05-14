#!/usr/bin/env python
"""
Główny punkt wejścia dla modułu shell.

Ten moduł implementuje główny punkt wejścia dla modułu shell, który umożliwia
zarządzanie procesami poprzez interfejs wiersza poleceń. Moduł może działać
zarówno samodzielnie, jak i integrować się z modułem process, jeśli jest dostępny.
"""

import argparse
import logging
import sys
from typing import Optional

from core.logging import get_logger
from shell.client import ShellClient, main as client_main
from shell.interactive import InteractiveShell, main as interactive_main

logger = get_logger(__name__)


def main() -> None:
    """Główny punkt wejścia dla modułu shell."""
    parser = argparse.ArgumentParser(description="Shell do zarządzania procesami")
    parser.add_argument(
        "--use-process",
        action="store_true",
        help="Użyj modułu process, jeśli jest dostępny",
    )
    parser.add_argument(
        "--process-url",
        type=str,
        default=None,
        help="URL serwera process (jeśli używany)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Poziom logowania (domyślnie: INFO)",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Uruchom w trybie interaktywnym",
    )

    # Parsowanie argumentów wiersza poleceń
    # Jeśli nie podano żadnych argumentów, wyświetl pomoc
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    # Sprawdzenie, czy podano polecenie dla klienta
    client_commands = ["execute", "list", "kill", "info", "start"]
    if any(cmd in sys.argv for cmd in client_commands):
        # Przekazanie sterowania do klienta
        client_main()
        return

    # Parsowanie argumentów
    args = parser.parse_args()

    # Konfiguracja logowania
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Uruchomienie w trybie interaktywnym lub przekazanie sterowania do klienta
    if args.interactive:
        # Uruchomienie w trybie interaktywnym
        shell = InteractiveShell(use_process=args.use_process, process_url=args.process_url)
        shell.cmdloop()
    else:
        # Przekazanie sterowania do klienta
        client_main()


def run_command(command: str, use_process: bool = True, process_url: Optional[str] = None) -> int:
    """Wykonanie polecenia shell i zwrócenie kodu wyjścia.

    Args:
        command: Polecenie do wykonania.
        use_process: Czy używać modułu process, jeśli jest dostępny.
        process_url: URL serwera process, jeśli use_process=True.

    Returns:
        Kod wyjścia polecenia.
    """
    client = ShellClient(use_process=use_process, process_url=process_url)
    exit_code, stdout, stderr = client.execute_command(command)

    # Wyświetlenie wyjścia
    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)

    return exit_code


if __name__ == "__main__":
    main()
