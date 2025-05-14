#!/bin/bash
# Skrypt do sprawdzania jakości kodu
# Uruchomienie: ./scripts/quality.sh [katalog]

set -e

# Domyślny katalog do sprawdzenia
TARGET_DIR=${1:-.}

echo "=== Sprawdzanie jakości kodu w katalogu: $TARGET_DIR ==="

# Sprawdź, czy wymagane narzędzia są zainstalowane
check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo "Narzędzie $1 nie jest zainstalowane. Instalowanie..."
        pip install $1
    fi
}

check_tool black
check_tool isort
check_tool flake8
check_tool pylint
check_tool mypy

echo ""
echo "=== Sprawdzanie formatowania kodu (black) ==="
black --check $TARGET_DIR || {
    echo "Formatowanie kodu nie jest zgodne z black. Naprawianie..."
    black $TARGET_DIR
    echo "Kod został sformatowany przez black."
}

echo ""
echo "=== Sprawdzanie kolejności importów (isort) ==="
isort --check $TARGET_DIR || {
    echo "Kolejność importów nie jest poprawna. Naprawianie..."
    isort $TARGET_DIR
    echo "Importy zostały uporządkowane przez isort."
}

echo ""
echo "=== Sprawdzanie zgodności z PEP 8 (flake8) ==="
flake8 $TARGET_DIR || {
    echo "Znaleziono problemy z PEP 8. Proszę naprawić je ręcznie."
}

echo ""
echo "=== Sprawdzanie statycznej analizy kodu (pylint) ==="
pylint $TARGET_DIR || {
    echo "Pylint znalazł problemy. Proszę naprawić je ręcznie."
}

echo ""
echo "=== Sprawdzanie typów (mypy) ==="
mypy $TARGET_DIR || {
    echo "Mypy znalazł problemy z typami. Proszę naprawić je ręcznie."
}

echo ""
echo "=== Sprawdzanie testów jednostkowych (pytest) ==="
pytest $TARGET_DIR || {
    echo "Testy jednostkowe nie przeszły. Proszę naprawić je ręcznie."
}

echo ""
echo "=== Podsumowanie ==="
echo "Sprawdzanie jakości kodu zakończone."
