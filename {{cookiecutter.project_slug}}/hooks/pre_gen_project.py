#!/usr/bin/env python
"""Skrypt uruchamiany przed wygenerowaniem projektu."""

import re
import sys

# Sprawdzanie poprawności nazwy projektu
PROJECT_SLUG = "{{ cookiecutter.project_slug }}"

if not re.match(r"^[a-z][a-z0-9_]+$", PROJECT_SLUG):
    print(f"ERROR: {PROJECT_SLUG} nie jest poprawną nazwą pakietu Python.")
    print("Nazwa powinna składać się z małych liter, cyfr i podkreśleń.")
    print("Musi rozpoczynać się od litery.")
    sys.exit(1)

# Sprawdzanie, czy wybrano przynajmniej jeden komponent
components = [
    "{{ cookiecutter.use_process }}",
    "{{ cookiecutter.use_grpc }}",
    "{{ cookiecutter.use_rest }}",
    "{{ cookiecutter.use_mqtt }}",
    "{{ cookiecutter.use_ftp }}",
    "{{ cookiecutter.use_webrtc }}",
    "{{ cookiecutter.use_websocket }}",
    "{{ cookiecutter.use_imap }}",
    "{{ cookiecutter.use_smtp }}",
    "{{ cookiecutter.use_pop3 }}",
    "{{ cookiecutter.use_ssh }}",
    "{{ cookiecutter.use_mcp }}",
    "{{ cookiecutter.use_shell }}",
]

if all(comp.lower() == "no" for comp in components):
    print("ERROR: Musisz wybrać przynajmniej jeden komponent.")
    sys.exit(1)

# Wszystkie sprawdzenia przeszły pomyślnie
print("Walidacja wstępna zakończona sukcesem!")
