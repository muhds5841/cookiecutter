#!/usr/bin/env python
"""Skrypt uruchamiany po wygenerowaniu projektu."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Usunięcie komponentów, które nie zostały wybrane
components = {
    "process": "{{ cookiecutter.use_process }}" == "yes",
    "grpc": "{{ cookiecutter.use_grpc }}" == "yes",
    "rest": "{{ cookiecutter.use_rest }}" == "yes",
    "mqtt": "{{ cookiecutter.use_mqtt }}" == "yes",
    "ftp": "{{ cookiecutter.use_ftp }}" == "yes",
    "webrtc": "{{ cookiecutter.use_webrtc }}" == "yes",
    "websocket": "{{ cookiecutter.use_websocket }}" == "yes",
    "imap": "{{ cookiecutter.use_imap }}" == "yes",
    "smtp": "{{ cookiecutter.use_smtp }}" == "yes",
    "pop3": "{{ cookiecutter.use_pop3 }}" == "yes",
    "ssh": "{{ cookiecutter.use_ssh }}" == "yes",
    "mcp": "{{ cookiecutter.use_mcp }}" == "yes",
    "shell": "{{ cookiecutter.use_shell }}" == "yes",
}

for component, is_selected in components.items():
    if not is_selected:
        if os.path.exists(component):
            shutil.rmtree(component)
            print(f"Usunięto komponent {component}")

# Dla komponentu MCP, dostosuj transporty
if components["mcp"]:
    mcp_transports = {
        "sse": {{cookiecutter.mcp_configuration.transports.sse}},
        "stdio": {{cookiecutter.mcp_configuration.transports.stdio}},
        "grpc": {{cookiecutter.mcp_configuration.transports.grpc}},
    }

    # Usuń transporty, które nie zostały wybrane
    for transport, is_selected in mcp_transports.items():
        if not is_selected:
            transport_file = Path(f"mcp/transports/{transport}.py")
            if transport_file.exists():
                transport_file.unlink()
                print(f"Usunięto transport MCP: {transport}")

    # Usuń moduły MCP, które nie zostały wybrane
    if not {{cookiecutter.mcp_configuration.include_discovery}}:
        discovery_file = Path("mcp/protocol/discovery.py")
        if discovery_file.exists():
            discovery_file.unlink()
            print("Usunięto moduł wykrywania narzędzi MCP")

    if not {{cookiecutter.mcp_configuration.include_tool_registry}}:
        tool_registry_files = [Path("mcp/resources/uri_templates.py")]
        for file in tool_registry_files:
            if file.exists():
                file.unlink()
                print(f"Usunięto {file}")

    if not {{cookiecutter.mcp_configuration.include_adaptive_sampling}}:
        sampling_dir = Path("mcp/sampling")
        if sampling_dir.exists():
            shutil.rmtree(sampling_dir)
            print("Usunięto moduł adaptacyjnego próbkowania MCP")

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

# Dodatkowe informacje dla MCP
if components["mcp"]:
    print("\nAby uruchomić serwer MCP:")
    print("  cd mcp")
    print("  poetry run python mcp_server.py")
