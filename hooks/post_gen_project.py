#!/usr/bin/env python
"""Skrypt uruchamiany po wygenerowaniu projektu."""

import os
import subprocess
import sys
import shutil
from pathlib import Path

# Usunięcie komponentów, które nie zostały wybrane
components = {
    "tts_engine": {{cookiecutter.components.tts_engine}},
    "grpc": {{cookiecutter.components.grpc}},
    "rest": {{cookiecutter.components.rest}},
    "webrtc": {{cookiecutter.components.webrtc}},
    "mcp": {{cookiecutter.components.mcp}},
    "shell": {{cookiecutter.components.shell}}
}

for component, is_selected in components.items():
    if not is_selected:
        if os.path.exists(component):
            shutil.rmtree(component)
            print(f"Usunięto komponent {component}")

# Inicjalizacja repozytorium Git
if "{{ cookiecutter.init_git }}" == "yes":
    try:
        subprocess.run(["git", "init"], check=True)
        print("Zainicjalizowano repozytorium Git")

        # Dodanie plików do repozytorium
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
        print("Utworzono początkowy commit")
    except subprocess.CalledProcessError as e:
        print(f"OSTRZEŻENIE: Nie udało się zainicjalizować repozytorium Git: {e}", file=sys.stderr)

# Konfiguracja pre-commit
if "{{ cookiecutter.use_pre_commit }}" == "yes":
    try:
        subprocess.run(["pip", "install", "pre-commit"], check=True)
        subprocess.run(["pre-commit", "install"], check=True)
        print("Zainstalowano pre-commit hooks")
    except subprocess.CalledProcessError as e:
        print(f"OSTRZEŻENIE: Nie udało się skonfigurować pre-commit: {e}", file=sys.stderr)

# Instalacja zależności
if "{{ cookiecutter.install_dependencies }}" == "yes":
    try:
        subprocess.run(["pip", "install", "poetry"], check=True)
        subprocess.run(["poetry", "install"], check=True)
        print("Zainstalowano zależności projektu z Poetry")
    except subprocess.CalledProcessError as e:
        print(f"OSTRZEŻENIE: Nie udało się zainstalować zależności: {e}", file=sys.stderr)

print("\nProjekt wygenerowany pomyślnie!")
print("\nAby rozpocząć:")
if "{{ cookiecutter.install_dependencies }}" != "yes":
    print("  poetry install  # Instalacja zależności")
print("  make test        # Uruchomienie testów")
print("  make quality     # Sprawdzenie jakości kodu")