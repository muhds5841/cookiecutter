#!/usr/bin/env python
"""
Tryb interaktywny dla modułu shell.

Ten moduł implementuje interaktywny shell, który umożliwia zarządzanie
procesami poprzez interfejs wiersza poleceń. Shell może działać zarówno
samodzielnie, jak i integrować się z modułem process, jeśli jest dostępny.
"""

import argparse
import cmd
import json
import logging
import os
import re
import shlex
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple

from core.logging import get_logger
from shell.client import ShellClient

logger = get_logger(__name__)


class InteractiveShell(cmd.Cmd):
    """Interaktywny shell do zarządzania procesami.

    Umożliwia wykonywanie poleceń shell i zarządzanie procesami
    poprzez interaktywny interfejs wiersza poleceń. Może działać zarówno
    samodzielnie, jak i integrować się z modułem process, jeśli jest dostępny.
    """

    intro = "Witaj w interaktywnym shellu. Wpisz 'help' lub '?' aby zobaczyć listę dostępnych poleceń.\n"
    prompt = "shell> "

    def __init__(self, use_process: bool = True, process_url: Optional[str] = None):
        """Inicjalizacja interaktywnego shella.

        Args:
            use_process: Czy używać modułu process, jeśli jest dostępny.
            process_url: URL serwera process, jeśli use_process=True.
        """
        super().__init__()
        self.client = ShellClient(use_process=use_process, process_url=process_url)
        self.current_dir = os.getcwd()
        self.env = os.environ.copy()
        self.last_exit_code = 0

    def do_cd(self, arg: str) -> None:
        """Zmiana katalogu roboczego.

        Składnia: cd <katalog>
        """
        if not arg:
            # Bez argumentu, przejście do katalogu domowego
            self.current_dir = os.path.expanduser("~")
            os.chdir(self.current_dir)
            print(f"Zmieniono katalog na: {self.current_dir}")
            return

        # Rozwijanie ścieżki względem bieżącego katalogu
        if not os.path.isabs(arg):
            path = os.path.join(self.current_dir, arg)
        else:
            path = arg

        # Sprawdzenie, czy katalog istnieje
        if os.path.isdir(path):
            self.current_dir = os.path.abspath(path)
            os.chdir(self.current_dir)
            print(f"Zmieniono katalog na: {self.current_dir}")
        else:
            print(f"Błąd: Katalog '{arg}' nie istnieje.")

    def do_pwd(self, arg: str) -> None:
        """Wyświetlenie bieżącego katalogu roboczego.

        Składnia: pwd
        """
        print(self.current_dir)

    def do_ls(self, arg: str) -> None:
        """Wyświetlenie zawartości katalogu.

        Składnia: ls [katalog]
        """
        # Wykonanie polecenia ls lub dir (w zależności od systemu)
        if sys.platform == "win32":
            command = f"dir {arg}" if arg else "dir"
        else:
            command = f"ls {arg}" if arg else "ls"

        exit_code, stdout, stderr = self.client.execute_command(command, cwd=self.current_dir)
        self.last_exit_code = exit_code

        if stdout:
            print(stdout)
        if stderr:
            print(stderr)

    def do_exec(self, arg: str) -> None:
        """Wykonanie polecenia shell.

        Składnia: exec <polecenie>
        """
        if not arg:
            print("Błąd: Brak polecenia do wykonania.")
            return

        exit_code, stdout, stderr = self.client.execute_command(arg, cwd=self.current_dir, env=self.env)
        self.last_exit_code = exit_code

        if stdout:
            print(stdout)
        if stderr:
            print(stderr)

        print(f"Kod wyjścia: {exit_code}")

    def do_ps(self, arg: str) -> None:
        """Wyświetlenie listy procesów.

        Składnia: ps [opcje]
        """
        if arg:
            # Jeśli podano argumenty, wykonaj polecenie ps z tymi argumentami
            command = f"ps {arg}"
            exit_code, stdout, stderr = self.client.execute_command(command, cwd=self.current_dir)
            self.last_exit_code = exit_code

            if stdout:
                print(stdout)
            if stderr:
                print(stderr)
        else:
            # W przeciwnym razie użyj metody list_processes
            processes = self.client.list_processes()
            if processes:
                # Formatowanie wyjścia
                headers = ["PID", "PPID", "USER", "%CPU", "%MEM", "COMMAND"]
                format_str = "{:<8} {:<8} {:<10} {:<6} {:<6} {:<}"
                print(format_str.format(*headers))

                for process in processes:
                    pid = process.get("pid", "")
                    ppid = process.get("ppid", "")
                    user = process.get("user", "")[:10]  # Przycięcie długich nazw użytkowników
                    cpu = process.get("cpu", "")
                    mem = process.get("mem", "")
                    command = process.get("command", "")[:50]  # Przycięcie długich poleceń

                    print(format_str.format(pid, ppid, user, cpu, mem, command))
            else:
                print("Brak procesów lub wystąpił błąd podczas pobierania listy procesów.")

    def do_kill(self, arg: str) -> None:
        """Zabicie procesu o podanym PID.

        Składnia: kill <pid> [sygnał]
        """
        args = shlex.split(arg)
        if not args:
            print("Błąd: Brak PID procesu do zabicia.")
            return

        try:
            pid = int(args[0])
            signal = int(args[1]) if len(args) > 1 else 15  # Domyślnie SIGTERM

            success = self.client.kill_process(pid, signal)
            if success:
                print(f"Proces {pid} został pomyślnie zabity.")
            else:
                print(f"Nie udało się zabić procesu {pid}.")
        except ValueError:
            print("Błąd: PID i sygnał muszą być liczbami całkowitymi.")

    def do_pinfo(self, arg: str) -> None:
        """Pobranie informacji o procesie o podanym PID.

        Składnia: pinfo <pid>
        """
        if not arg:
            print("Błąd: Brak PID procesu.")
            return

        try:
            pid = int(arg)
            process_info = self.client.get_process_info(pid)

            if process_info:
                print(json.dumps(process_info, indent=2))
            else:
                print(f"Brak informacji o procesie {pid} lub proces nie istnieje.")
        except ValueError:
            print("Błąd: PID musi być liczbą całkowitą.")

    def do_start(self, arg: str) -> None:
        """Uruchomienie nowego procesu.

        Składnia: start [-d] <polecenie>
        Opcje:
          -d, --detach  Odłącz proces od rodzica
        """
        if not arg:
            print("Błąd: Brak polecenia do uruchomienia.")
            return

        # Parsowanie argumentów
        detach = False
        if arg.startswith("-d ") or arg.startswith("--detach "):
            detach = True
            arg = re.sub(r"^(-d|--detach)\s+", "", arg)

        if not arg:
            print("Błąd: Brak polecenia do uruchomienia.")
            return

        pid = self.client.start_process(arg, cwd=self.current_dir, env=self.env, detach=detach)
        if pid:
            print(f"Proces uruchomiony z PID: {pid}")
        else:
            print("Nie udało się uruchomić procesu.")

    def do_env(self, arg: str) -> None:
        """Zarządzanie zmiennymi środowiskowymi.

        Składnia: env [set <nazwa>=<wartość> | unset <nazwa> | list]
        """
        args = shlex.split(arg) if arg else ["list"]
        command = args[0].lower() if args else "list"

        if command == "list":
            # Wyświetlenie wszystkich zmiennych środowiskowych
            for key, value in sorted(self.env.items()):
                print(f"{key}={value}")

        elif command == "set" and len(args) > 1:
            # Ustawienie zmiennej środowiskowej
            for var_def in args[1:]:
                if "=" in var_def:
                    key, value = var_def.split("=", 1)
                    self.env[key] = value
                    print(f"Ustawiono {key}={value}")
                else:
                    print(f"Błąd: Nieprawidłowy format zmiennej środowiskowej: {var_def}")

        elif command == "unset" and len(args) > 1:
            # Usunięcie zmiennej środowiskowej
            for key in args[1:]:
                if key in self.env:
                    del self.env[key]
                    print(f"Usunięto zmienną {key}")
                else:
                    print(f"Błąd: Zmienna {key} nie istnieje")

        else:
            print("Błąd: Nieprawidłowa składnia. Użyj: env [set <nazwa>=<wartość> | unset <nazwa> | list]")

    def do_exit(self, arg: str) -> bool:
        """Wyjście z interaktywnego shella.

        Składnia: exit
        """
        print("Do widzenia!")
        return True

    def do_quit(self, arg: str) -> bool:
        """Wyjście z interaktywnego shella.

        Składnia: quit
        """
        return self.do_exit(arg)

    def do_echo(self, arg: str) -> None:
        """Wyświetlenie tekstu lub wartości zmiennej środowiskowej.

        Składnia: echo [tekst]
        """
        # Rozwijanie zmiennych środowiskowych w tekście
        result = arg
        for match in re.finditer(r"\$(\w+|\{\w+\})", arg):
            var = match.group(1)
            if var.startswith("{") and var.endswith("}"):
                var = var[1:-1]  # Usunięcie nawiaswów klamrowych

            if var in self.env:
                result = result.replace(match.group(0), self.env[var])

        print(result)

    def do_status(self, arg: str) -> None:
        """Wyświetlenie statusu ostatniego polecenia.

        Składnia: status
        """
        print(f"Ostatni kod wyjścia: {self.last_exit_code}")

    def emptyline(self) -> None:
        """Obsługa pustej linii (Enter)."""
        pass

    def default(self, line: str) -> None:
        """Obsługa nierozpoznanych poleceń.

        Args:
            line: Linia polecenia do wykonania.
        """
        # Sprawdzenie, czy to polecenie zmiany katalogu
        if line.startswith("cd "):
            self.do_cd(line[3:])
            return

        # W przeciwnym razie wykonaj jako polecenie shell
        self.do_exec(line)


def main() -> None:
    """Punkt wejścia dla interaktywnego shella jako samodzielnej aplikacji."""
    parser = argparse.ArgumentParser(description="Interaktywny shell do zarządzania procesami")
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

    args = parser.parse_args()

    # Konfiguracja logowania
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Uruchomienie interaktywnego shella
    shell = InteractiveShell(use_process=args.use_process, process_url=args.process_url)
    shell.cmdloop()


if __name__ == "__main__":
    main()
