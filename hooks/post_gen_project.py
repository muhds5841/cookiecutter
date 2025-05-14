#!/usr/bin/env python
"""
Ten skrypt jest uruchamiany po wygenerowaniu projektu.
Usuwa moduły, które nie zostały wybrane przez użytkownika.
"""

import os
import shutil
import sys
from pathlib import Path

# Moduły, które zawsze będą dostępne
CORE_MODULES = ["core", "quality", "scripts", "docs"]

# Mapowanie zmiennych cookiecutter na katalogi
MODULE_DIRS = {
    "use_process": "process",
    "use_grpc": "grpc",
    "use_rest": "rest",
    "use_mqtt": "mqtt",
    "use_ftp": "ftp",
    "use_webrtc": "webrtc",
    "use_websocket": "websocket",
    "use_imap": "imap",
    "use_smtp": "smtp",
    "use_pop3": "pop3",
    "use_ssh": "ssh",
    "use_mcp": "mcp",
    "use_shell": "shell",
}

# Mapowanie modułów na katalogi testów
TEST_DIRS = {
    "use_process": ["tests/process_tests", "process/tests"],
    "use_grpc": ["tests/grpc_tests", "grpc/tests"],
    "use_rest": ["tests/rest_tests", "rest/tests"],
    "use_mqtt": ["tests/mqtt_tests", "mqtt/tests"],
    "use_ftp": ["tests/ftp_tests", "ftp/tests"],
    "use_webrtc": ["tests/webrtc_tests", "webrtc/tests"],
    "use_websocket": ["tests/websocket_tests", "websocket/tests"],
    "use_imap": ["tests/imap_tests", "imap/tests"],
    "use_smtp": ["tests/smtp_tests", "smtp/tests"],
    "use_pop3": ["tests/pop3_tests", "pop3/tests"],
    "use_ssh": ["tests/ssh_tests", "ssh/tests"],
    "use_mcp": ["tests/mcp_tests", "mcp/tests"],
    "use_shell": ["tests/shell_tests", "shell/tests"],
}

def remove_directory(directory):
    """Usuwa katalog, jeśli istnieje."""
    if os.path.exists(directory):
        print(f"Usuwanie katalogu: {directory}")
        shutil.rmtree(directory)
    else:
        print(f"Katalog {directory} nie istnieje, pomijanie.")

def main():
    """Główna funkcja skryptu."""
    print("Uruchamianie skryptu post-gen-project.py...")
    project_dir = os.getcwd()
    
    # Sprawdzenie, które moduły należy usunąć
    for var_name, dir_name in MODULE_DIRS.items():
        # Pobieranie wartości zmiennej cookiecutter z kontekstu
        use_module = "{{{{ cookiecutter.{} }}}}".format(var_name)
        
        if use_module.lower() == "no":
            # Usuń katalog modułu
            module_path = os.path.join(project_dir, dir_name)
            if dir_name not in CORE_MODULES:  # Nie usuwaj podstawowych modułów
                remove_directory(module_path)
            
            # Usuń katalogi testów dla tego modułu
            if var_name in TEST_DIRS:
                for test_dir in TEST_DIRS[var_name]:
                    test_path = os.path.join(project_dir, test_dir)
                    remove_directory(test_path)
    
    # Usuń pliki testów dla niewybranych modułów
    for var_name, dir_name in MODULE_DIRS.items():
        use_module = "{{ cookiecutter." + var_name + " }}"
        
        if use_module.lower() == "no":
            # Usuń pojedyncze pliki testów w katalogu modułu
            test_files = [f for f in os.listdir(project_dir) if f.startswith(f"test_{dir_name}") or f.startswith(f"test_{dir_name.replace('_', '')}")]
            for test_file in test_files:
                test_file_path = os.path.join(project_dir, test_file)
                if os.path.isfile(test_file_path):
                    print(f"Usuwanie pliku testu: {test_file_path}")
                    os.remove(test_file_path)
    
    # Usuń katalog tests, jeśli jest pusty
    tests_dir = os.path.join(project_dir, "tests")
    if os.path.exists(tests_dir) and not os.listdir(tests_dir):
        print(f"Usuwanie pustego katalogu testów: {tests_dir}")
        os.rmdir(tests_dir)
    
    print("Skrypt post-gen-project.py zakończony.")

if __name__ == "__main__":
    main()
