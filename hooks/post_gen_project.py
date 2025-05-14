#!/usr/bin/env python
"""
Ten skrypt jest uruchamiany po wygenerowaniu projektu.
Usuwa moduły, które nie zostały wybrane przez użytkownika.
"""

import os
import shutil
import sys

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
    
    # Usuwanie katalogów dla niewybranych modułów
    if "{{ cookiecutter.use_docker }}" == "no":
        remove_directory(os.path.join(project_dir, "docker"))
        remove_directory(os.path.join(project_dir, "docker-compose.yml"))
        remove_directory(os.path.join(project_dir, "docker-compose.prod.yml"))
    
    if "{{ cookiecutter.use_process }}" == "no":
        remove_directory(os.path.join(project_dir, "process"))
    
    if "{{ cookiecutter.use_grpc }}" == "no":
        remove_directory(os.path.join(project_dir, "grpc"))
    
    if "{{ cookiecutter.use_rest }}" == "no":
        remove_directory(os.path.join(project_dir, "rest"))
    
    if "{{ cookiecutter.use_mqtt }}" == "no":
        remove_directory(os.path.join(project_dir, "mqtt"))
    
    if "{{ cookiecutter.use_ftp }}" == "no":
        remove_directory(os.path.join(project_dir, "ftp"))
    
    if "{{ cookiecutter.use_webrtc }}" == "no":
        remove_directory(os.path.join(project_dir, "webrtc"))
    
    if "{{ cookiecutter.use_websocket }}" == "no":
        remove_directory(os.path.join(project_dir, "websocket"))
    
    if "{{ cookiecutter.use_imap }}" == "no":
        remove_directory(os.path.join(project_dir, "imap"))
    
    if "{{ cookiecutter.use_smtp }}" == "no":
        remove_directory(os.path.join(project_dir, "smtp"))
    
    if "{{ cookiecutter.use_pop3 }}" == "no":
        remove_directory(os.path.join(project_dir, "pop3"))
    
    if "{{ cookiecutter.use_ssh }}" == "no":
        remove_directory(os.path.join(project_dir, "ssh"))
    
    if "{{ cookiecutter.use_mcp }}" == "no":
        remove_directory(os.path.join(project_dir, "mcp"))
    
    if "{{ cookiecutter.use_shell }}" == "no":
        remove_directory(os.path.join(project_dir, "shell"))
    
    # Usuń katalog tests, jeśli jest pusty
    tests_dir = os.path.join(project_dir, "tests")
    if os.path.exists(tests_dir) and os.path.isdir(tests_dir):
        if not os.listdir(tests_dir):
            print(f"Usuwanie pustego katalogu testów: {tests_dir}")
            shutil.rmtree(tests_dir)
    
    print("Skrypt post-gen-project.py zakończony.")

if __name__ == "__main__":
    main()
