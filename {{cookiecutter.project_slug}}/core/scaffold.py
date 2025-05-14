"""Narzędzie do generowania komponentów projektu."""

import argparse
import os
import sys
import textwrap
from pathlib import Path


def generate_adapter(name, process):
    """Generuje adapter dla silnika Process."""
    class_name = f"{name.title()}Process"
    file_path = Path("process/adapters") / f"{name.lower()}.py"

    if file_path.exists():
        print(f"Plik {file_path} już istnieje!", file=sys.stderr)
        return 1

    content = textwrap.dedent(
        f'''
    """Adapter dla silnika Process {process}."""

    from typing import Dict, Any, Optional
    from ..process import ProcessEngine


    class {class_name}(ProcessEngine):
        """Implementacja silnika Process dla {process}."""

        def __init__(self, config: Dict[str, Any]):
            """
            Inicjalizuje silnik Process.

            Args:
                config: Konfiguracja silnika
            """
            super().__init__(config)
            # Tutaj dodać kod inicjalizacji specyficzny dla {process}

        def synthesize(self, text: str, voice_config: Optional[Dict[str, Any]] = None) -> bytes:
            """
            Konwertuje tekst na mowę.

            Args:
                text: Tekst do konwersji
                voice_config: Konfiguracja głosu

            Returns:
                Dane audio w formacie bytes
            """
            if voice_config is None:
                # Tworzymy pusty słownik - unikamy podwójnych nawiasów klamrowych
                voice_config = dict()

            # Tutaj dodać kod syntezy specyficzny dla {process}
            # To jest tylko przykład - należy zaimplementować rzeczywistą integrację
            # Unikamy używania nawiasów klamrowych w f-stringach, które powodują konflikt z Jinja2
            text_var = "text"  # Zmienna pomocnicza
            print(f"Syntezing {text_var}: " + str(text) + f" using {process}")

            # Symulacja zwracania danych audio
            return b"SAMPLE_AUDIO_DATA"

        def get_available_voices(self) -> list:
            """
            Pobiera listę dostępnych głosów.

            Returns:
                Lista dostępnych głosów z metadanymi
            """
            # Tutaj dodać kod pobierania listy głosów specyficzny dla {process}
            # Unikamy podwójnych nawiasów klamrowych, które powodują konflikt z Jinja2
            voices = []
            # Dodajemy głos domyślny
            default_voice = dict()
            default_voice["name"] = "default"
            default_voice["language"] = "en-US"
            default_voice["gender"] = "female"
            voices.append(default_voice)
            # Tutaj można dodać więcej głosów dostępnych w {process}
            return voices
    '''
    ).strip()

    # Tworzenie katalogu, jeśli nie istnieje
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Zapisanie pliku
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Wygenerowano adapter {name} dla silnika {process} w pliku {file_path}")

    # Aktualizacja pliku __init__.py, aby zarejestrować nowy adapter
    init_path = Path("process/adapters/__init__.py")

    with open(init_path, "r", encoding="utf-8") as f:
        init_content = f.read()

    # Dodanie importu
    import_line = f"from .{name.lower()} import {class_name}"
    if import_line not in init_content:
        lines = init_content.split("\n")

        # Znajdowanie miejsca do wstawienia importu
        for i, line in enumerate(lines):
            if line.startswith("from ."):
                continue
            elif line.strip() == "":
                lines.insert(i, import_line)
                break
        else:
            lines.append(import_line)

        # Aktualizacja pliku __init__.py
        with open(init_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    print(f"Zaktualizowano {init_path} o import nowego adaptera")

    return 0


def main():
    """Główna funkcja narzędzia."""
    parser = argparse.ArgumentParser(description="Generuje komponenty projektu")
    subparsers = parser.add_subparsers(dest="command", help="Polecenie do wykonania")

    # Parser dla komendy generate-adapter
    adapter_parser = subparsers.add_parser(
        "generate-adapter", help="Generuje adapter dla silnika Process"
    )
    adapter_parser.add_argument("--name", required=True, help="Nazwa adaptera")
    adapter_parser.add_argument("--engine", required=True, help="Nazwa silnika Process")

    args = parser.parse_args()

    if args.command == "generate-adapter":
        return generate_adapter(args.name, args.engine)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
