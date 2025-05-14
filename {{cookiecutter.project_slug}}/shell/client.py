#!/usr/bin/env python
"""
Klient shell do zarządzania procesami.

Ten moduł implementuje klienta shell, który umożliwia zarządzanie
procesami poprzez interfejs wiersza poleceń. Klient może działać zarówno
samodzielnie, jak i integrować się z modułem process, jeśli jest dostępny.
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple

from core.logging import get_logger

# Sprawdzenie, czy moduł process jest dostępny
try:
    from process.client import ProcessClient
    PROCESS_MODULE_AVAILABLE = True
except ImportError:
    PROCESS_MODULE_AVAILABLE = False

logger = get_logger(__name__)


class ShellClient:
    """Klient shell do zarządzania procesami.

    Umożliwia wykonywanie poleceń shell i zarządzanie procesami
    poprzez interfejs wiersza poleceń. Może działać zarówno samodzielnie,
    jak i integrować się z modułem process, jeśli jest dostępny.
    """

    def __init__(self, use_process: bool = True, process_url: Optional[str] = None):
        """Inicjalizacja klienta shell.

        Args:
            use_process: Czy używać modułu process, jeśli jest dostępny.
            process_url: URL serwera process, jeśli use_process=True.
        """
        self.use_process = use_process and PROCESS_MODULE_AVAILABLE
        self.process_client = None

        if self.use_process:
            try:
                self.process_client = ProcessClient(process_url)
                logger.info("Zainicjalizowano klienta process")
            except Exception as e:
                logger.error(f"Błąd podczas inicjalizacji klienta process: {e}")
                self.use_process = False

    def execute_command(self, command: str, cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None) -> Tuple[int, str, str]:
        """Wykonanie polecenia shell.

        Args:
            command: Polecenie do wykonania.
            cwd: Katalog roboczy dla polecenia.
            env: Zmienne środowiskowe dla polecenia.

        Returns:
            Krotka (kod_wyjścia, standardowe_wyjście, standardowe_wyjście_błędów).
        """
        if self.use_process and self.process_client:
            try:
                result = self.process_client.run_command(command, cwd=cwd, env=env)
                return result.get("exit_code", -1), result.get("stdout", ""), result.get("stderr", "")
            except Exception as e:
                logger.error(f"Błąd podczas wykonywania polecenia przez process: {e}")
                logger.info("Przełączanie na lokalną implementację")

        # Lokalna implementacja, jeśli moduł process nie jest dostępny lub wystąpił błąd
        try:
            # Przygotowanie środowiska
            merged_env = os.environ.copy()
            if env:
                merged_env.update(env)

            # Wykonanie polecenia
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                env=merged_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = process.communicate()
            return process.returncode, stdout, stderr
        except Exception as e:
            logger.error(f"Błąd podczas wykonywania polecenia lokalnie: {e}")
            return -1, "", str(e)

    def list_processes(self) -> List[Dict[str, Any]]:
        """Pobranie listy procesów.

        Returns:
            Lista procesów jako słowniki z informacjami o procesach.
        """
        if self.use_process and self.process_client:
            try:
                return self.process_client.list_processes()
            except Exception as e:
                logger.error(f"Błąd podczas pobierania listy procesów: {e}")
                logger.info("Przełączanie na lokalną implementację")

        # Lokalna implementacja, jeśli moduł process nie jest dostępny lub wystąpił błąd
        try:
            # Użycie polecenia ps do pobrania listy procesów
            exit_code, stdout, stderr = self.execute_command(
                "ps -eo pid,ppid,user,%cpu,%mem,stat,start,time,command --sort=-%cpu | head -n 20"
            )
            if exit_code != 0:
                logger.error(f"Błąd podczas wykonywania polecenia ps: {stderr}")
                return []

            # Parsowanie wyjścia polecenia ps
            lines = stdout.strip().split("\n")
            if len(lines) <= 1:
                return []

            # Nagłówki kolumn
            headers = lines[0].split()
            processes = []

            for line in lines[1:]:
                parts = line.split(None, len(headers) - 1)
                if len(parts) >= len(headers):
                    process = {}
                    for i, header in enumerate(headers):
                        process[header.lower()] = parts[i]
                    processes.append(process)

            return processes
        except Exception as e:
            logger.error(f"Błąd podczas pobierania listy procesów lokalnie: {e}")
            return []

    def kill_process(self, pid: int, signal: int = 15) -> bool:
        """Zabicie procesu o podanym PID.

        Args:
            pid: Identyfikator procesu do zabicia.
            signal: Sygnał do wysłania (domyślnie 15 - SIGTERM).

        Returns:
            True, jeśli proces został pomyślnie zabity, False w przeciwnym razie.
        """
        if self.use_process and self.process_client:
            try:
                return self.process_client.kill_process(pid, signal)
            except Exception as e:
                logger.error(f"Błąd podczas zabijania procesu przez process: {e}")
                logger.info("Przełączanie na lokalną implementację")

        # Lokalna implementacja, jeśli moduł process nie jest dostępny lub wystąpił błąd
        try:
            exit_code, stdout, stderr = self.execute_command(f"kill -{signal} {pid}")
            return exit_code == 0
        except Exception as e:
            logger.error(f"Błąd podczas zabijania procesu lokalnie: {e}")
            return False

    def get_process_info(self, pid: int) -> Optional[Dict[str, Any]]:
        """Pobranie informacji o procesie o podanym PID.

        Args:
            pid: Identyfikator procesu.

        Returns:
            Słownik z informacjami o procesie lub None, jeśli proces nie istnieje.
        """
        if self.use_process and self.process_client:
            try:
                return self.process_client.get_process_info(pid)
            except Exception as e:
                logger.error(f"Błąd podczas pobierania informacji o procesie przez process: {e}")
                logger.info("Przełączanie na lokalną implementację")

        # Lokalna implementacja, jeśli moduł process nie jest dostępny lub wystąpił błąd
        try:
            exit_code, stdout, stderr = self.execute_command(f"ps -p {pid} -o pid,ppid,user,%cpu,%mem,stat,start,time,command --no-headers")
            if exit_code != 0 or not stdout.strip():
                return None

            # Parsowanie wyjścia polecenia ps
            headers = ["pid", "ppid", "user", "cpu", "mem", "stat", "start", "time", "command"]
            parts = stdout.strip().split(None, len(headers) - 1)
            if len(parts) >= len(headers):
                process = {}
                for i, header in enumerate(headers):
                    process[header.lower()] = parts[i]
                return process
            return None
        except Exception as e:
            logger.error(f"Błąd podczas pobierania informacji o procesie lokalnie: {e}")
            return None

    def start_process(self, command: str, cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None, detach: bool = False) -> Optional[int]:
        """Uruchomienie nowego procesu.

        Args:
            command: Polecenie do wykonania.
            cwd: Katalog roboczy dla procesu.
            env: Zmienne środowiskowe dla procesu.
            detach: Czy odłączyć proces od rodzica.

        Returns:
            PID uruchomionego procesu lub None, jeśli wystąpił błąd.
        """
        if self.use_process and self.process_client:
            try:
                result = self.process_client.start_process(command, cwd=cwd, env=env, detach=detach)
                return result.get("pid")
            except Exception as e:
                logger.error(f"Błąd podczas uruchamiania procesu przez process: {e}")
                logger.info("Przełączanie na lokalną implementację")

        # Lokalna implementacja, jeśli moduł process nie jest dostępny lub wystąpił błąd
        try:
            # Przygotowanie środowiska
            merged_env = os.environ.copy()
            if env:
                merged_env.update(env)

            # Uruchomienie procesu
            if detach:
                # Uruchomienie procesu w tle
                if sys.platform == "win32":
                    # Windows
                    process = subprocess.Popen(
                        f"start /b {command}",
                        shell=True,
                        cwd=cwd,
                        env=merged_env,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    return process.pid
                else:
                    # Unix/Linux
                    process = subprocess.Popen(
                        f"nohup {command} > /dev/null 2>&1 &",
                        shell=True,
                        cwd=cwd,
                        env=merged_env,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    return process.pid
            else:
                # Uruchomienie procesu w tle, ale z możliwością śledzenia
                process = subprocess.Popen(
                    command,
                    shell=True,
                    cwd=cwd,
                    env=merged_env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return process.pid
        except Exception as e:
            logger.error(f"Błąd podczas uruchamiania procesu lokalnie: {e}")
            return None


def main() -> None:
    """Punkt wejścia dla klienta shell jako samodzielnej aplikacji."""
    parser = argparse.ArgumentParser(description="Klient shell do zarządzania procesami")
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

    subparsers = parser.add_subparsers(dest="command", help="Polecenie do wykonania")

    # Polecenie execute
    execute_parser = subparsers.add_parser("execute", help="Wykonaj polecenie shell")
    execute_parser.add_argument("cmd", help="Polecenie do wykonania")
    execute_parser.add_argument("--cwd", help="Katalog roboczy dla polecenia")
    execute_parser.add_argument("--env", help="Zmienne środowiskowe dla polecenia (format JSON)")

    # Polecenie list
    list_parser = subparsers.add_parser("list", help="Pobierz listę procesów")

    # Polecenie kill
    kill_parser = subparsers.add_parser("kill", help="Zabij proces o podanym PID")
    kill_parser.add_argument("pid", type=int, help="PID procesu do zabicia")
    kill_parser.add_argument("--signal", type=int, default=15, help="Sygnał do wysłania (domyślnie: 15 - SIGTERM)")

    # Polecenie info
    info_parser = subparsers.add_parser("info", help="Pobierz informacje o procesie o podanym PID")
    info_parser.add_argument("pid", type=int, help="PID procesu")

    # Polecenie start
    start_parser = subparsers.add_parser("start", help="Uruchom nowy proces")
    start_parser.add_argument("cmd", help="Polecenie do wykonania")
    start_parser.add_argument("--cwd", help="Katalog roboczy dla procesu")
    start_parser.add_argument("--env", help="Zmienne środowiskowe dla procesu (format JSON)")
    start_parser.add_argument("--detach", action="store_true", help="Odłącz proces od rodzica")

    args = parser.parse_args()

    # Konfiguracja logowania
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Inicjalizacja klienta shell
    client = ShellClient(use_process=args.use_process, process_url=args.process_url)

    if args.command == "execute":
        # Parsowanie zmiennych środowiskowych
        env = None
        if args.env:
            try:
                env = json.loads(args.env)
            except json.JSONDecodeError as e:
                logger.error(f"Błąd podczas parsowania zmiennych środowiskowych: {e}")
                sys.exit(1)

        # Wykonanie polecenia
        exit_code, stdout, stderr = client.execute_command(args.cmd, cwd=args.cwd, env=env)
        print(f"Kod wyjścia: {exit_code}")
        if stdout:
            print(f"Standardowe wyjście:\n{stdout}")
        if stderr:
            print(f"Standardowe wyjście błędów:\n{stderr}")
        sys.exit(exit_code)

    elif args.command == "list":
        # Pobranie listy procesów
        processes = client.list_processes()
        if processes:
            print(json.dumps(processes, indent=2))
        else:
            print("Brak procesów lub wystąpił błąd podczas pobierania listy procesów.")

    elif args.command == "kill":
        # Zabicie procesu
        success = client.kill_process(args.pid, args.signal)
        if success:
            print(f"Proces {args.pid} został pomyślnie zabity.")
        else:
            print(f"Nie udało się zabić procesu {args.pid}.")
            sys.exit(1)

    elif args.command == "info":
        # Pobranie informacji o procesie
        process_info = client.get_process_info(args.pid)
        if process_info:
            print(json.dumps(process_info, indent=2))
        else:
            print(f"Brak informacji o procesie {args.pid} lub proces nie istnieje.")
            sys.exit(1)

    elif args.command == "start":
        # Parsowanie zmiennych środowiskowych
        env = None
        if args.env:
            try:
                env = json.loads(args.env)
            except json.JSONDecodeError as e:
                logger.error(f"Błąd podczas parsowania zmiennych środowiskowych: {e}")
                sys.exit(1)

        # Uruchomienie procesu
        pid = client.start_process(args.cmd, cwd=args.cwd, env=env, detach=args.detach)
        if pid:
            print(f"Proces uruchomiony z PID: {pid}")
        else:
            print("Nie udało się uruchomić procesu.")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
