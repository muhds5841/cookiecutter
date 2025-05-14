#!/bin/bash
# Skrypt do sprawdzania jakości kodu
# Uruchomienie: ./scripts/quality.sh [katalog]

# Wyłączamy automatyczne zatrzymywanie skryptu przy błędach, aby wszystkie testy mogły zostać wykonane
set +e

# Domyślny katalog do sprawdzenia
TARGET_DIR=${1:-.}

# Zmienne do śledzenia błędów
ERROR_COUNT=0
FIX_COUNT=0

echo "=== Sprawdzanie jakości kodu w katalogu: $TARGET_DIR ==="

# Sprawdź, czy wymagane narzędzia są zainstalowane
check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo "Narzędzie $1 nie jest zainstalowane. Instalowanie..."
        pip install $1
        if [ $? -ne 0 ]; then
            echo "Błąd podczas instalacji $1. Pomijanie testów z tym narzędziem."
            return 1
        fi
    fi
    return 0
}

# Funkcja do uruchamiania testów i raportowania wyników
run_test() {
    local name=$1
    local command=$2
    local auto_fix=$3
    local fix_command=$4

    echo ""
    echo "=== Sprawdzanie $name ==="
    
    eval $command
    local result=$?
    
    if [ $result -ne 0 ]; then
        if [ "$auto_fix" = "true" ] && [ -n "$fix_command" ]; then
            echo "Znaleziono problemy. Naprawianie..."
            eval $fix_command
            if [ $? -eq 0 ]; then
                echo "Problemy zostały automatycznie naprawione."
                ((FIX_COUNT++))
            else
                echo "Nie udało się automatycznie naprawić problemów."
                ((ERROR_COUNT++))
            fi
        else
            echo "Znaleziono problemy. Proszę naprawić je ręcznie."
            ((ERROR_COUNT++))
        fi
    else
        echo "Test $name przeszedł pomyślnie."
    fi
}

# Instalacja narzędzi
for tool in black isort flake8 pylint mypy pytest; do
    check_tool $tool
done

# Uruchomienie testów
run_test "formatowania kodu (black)" "black --check $TARGET_DIR" "true" "black $TARGET_DIR"
run_test "kolejności importów (isort)" "isort --check $TARGET_DIR" "true" "isort $TARGET_DIR"
run_test "zgodności z PEP 8 (flake8)" "flake8 $TARGET_DIR" "false" ""
run_test "statycznej analizy kodu (pylint)" "pylint --recursive=y $TARGET_DIR" "false" ""
run_test "typów (mypy)" "mypy $TARGET_DIR" "false" ""

# Uruchamianie testów
if [ "$TARGET_DIR" = "." ]; then
    # Dla całego projektu uruchamiamy wszystkie testy
    run_test "testów jednostkowych (pytest)" "pytest" "false" ""
elif [[ "$TARGET_DIR" == *"/" ]]; then
    # Jeśli ścieżka kończy się na "/", usuwamy ostatni znak
    TARGET_DIR=${TARGET_DIR%/}
    # Sprawdzamy, czy w katalogu są pliki testów
    if ls "$TARGET_DIR"/test_*.py &> /dev/null || [ -d "$TARGET_DIR/tests" ]; then
        echo ""
        echo "=== Uruchamianie testów dla modułu: $TARGET_DIR ==="
        run_test "testów jednostkowych (pytest)" "pytest $TARGET_DIR" "false" ""
    else
        echo ""
        echo "=== Pomijanie testów jednostkowych (pytest) ==="
        echo "Nie znaleziono plików testów w katalogu $TARGET_DIR."
    fi
else
    # Sprawdzamy, czy w katalogu są pliki testów
    if ls "$TARGET_DIR"/test_*.py &> /dev/null || [ -d "$TARGET_DIR/tests" ]; then
        echo ""
        echo "=== Uruchamianie testów dla modułu: $TARGET_DIR ==="
        run_test "testów jednostkowych (pytest)" "pytest $TARGET_DIR" "false" ""
    else
        echo ""
        echo "=== Pomijanie testów jednostkowych (pytest) ==="
        echo "Nie znaleziono plików testów w katalogu $TARGET_DIR."
    fi
fi

# Podsumowanie
echo ""
echo "=== Podsumowanie ==="
if [ $ERROR_COUNT -eq 0 ]; then
    echo "Wszystkie testy przeszły pomyślnie!"
else
    echo "Znaleziono $ERROR_COUNT problemów, które wymagają ręcznej naprawy."
fi

if [ $FIX_COUNT -gt 0 ]; then
    echo "Automatycznie naprawiono $FIX_COUNT problemów."
fi

echo "Sprawdzanie jakości kodu zakończone."

# Zwróć kod błędu, jeśli były problemy
if [ $ERROR_COUNT -gt 0 ]; then
    exit 1
fi

exit 0
