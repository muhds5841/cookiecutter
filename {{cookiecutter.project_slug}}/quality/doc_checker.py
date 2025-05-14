"""Narzędzie do sprawdzania dokumentacji."""

import re
import sys
from pathlib import Path
from typing import List, Dict, Set


def check_docstrings(file_path: Path) -> Dict[str, List[int]]:
    """Sprawdza poprawność dokumentacji w pliku."""
    issues = {
        "missing_function_docstring": [],
        "missing_class_docstring": [],
        "missing_parameter_description": []
    }

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        # Sprawdzanie deklaracji funkcji
        if re.match(r'^\s*def\s+\w+\s*\(', line):
            if i + 1 >= len(lines) or not re.search(r'"""', lines[i + 1]):
                issues["missing_function_docstring"].append(i + 1)

        # Sprawdzanie deklaracji klas
        elif re.match(r'^\s*class\s+\w+', line):
            if i + 1 >= len(lines) or not re.search(r'"""', lines[i + 1]):
                issues["missing_class_docstring"].append(i + 1)

    return issues


def check_project_docstrings(paths: List[str]) -> Dict[str, Dict[str, List[int]]]:
    """Sprawdza dokumentację w całym projekcie."""
    results = {}

    for path_str in paths:
        path = Path(path_str)

        if path.is_file() and path.suffix == ".py":
            results[str(path)] = check_docstrings(path)
        elif path.is_dir():
            for py_file in path.glob("**/*.py"):
                results[str(py_file)] = check_docstrings(py_file)

    return results


def print_report(results: Dict[str, Dict[str, List[int]]]) -> bool:
    """Wyświetla raport z analizy dokumentacji."""
    has_issues = False

    for file_path, issues in results.items():
        file_has_issues = any(len(lines) > 0 for lines in issues.values())

        if file_has_issues:
            has_issues = True
            print(f"\nProblemy z dokumentacją w pliku {file_path}:")

            if issues["missing_function_docstring"]:
                print(f"  * Brak dokumentacji funkcji w liniach: {issues['missing_function_docstring']}")

            if issues["missing_class_docstring"]:
                print(f"  * Brak dokumentacji klas w liniach: {issues['missing_class_docstring']}")

            if issues["missing_parameter_description"]:
                print(f"  * Brak opisu parametrów w liniach: {issues['missing_parameter_description']}")

    if not has_issues:
        print("Brak problemów z dokumentacją.")

    return has_issues


if __name__ == "__main__":
    # Umożliwia uruchamianie modułu bezpośrednio jako skrypt
    import argparse

    parser = argparse.ArgumentParser(description="Sprawdza dokumentację w kodzie Python")
    parser.add_argument("paths", nargs="+", help="Ścieżki do sprawdzenia")

    args = parser.parse_args()

    results = check_project_docstrings(args.paths)
    has_issues = print_report(results)

    if has_issues:
        sys.exit(1)