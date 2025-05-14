"""Implementacja narzędzia procesu dla MCP."""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Dodajemy katalog główny projektu do ścieżki importu
sys.path.append(str(Path(__file__).parent.parent.parent))

from process.process import Process


class ProcessTool:
    """Narzędzie procesu zgodne z protokołem MCP."""

    def __init__(self, name: str, description: str, process: Process):
        """
        Inicjalizuje narzędzie procesu.

        Args:
            name: Nazwa narzędzia
            description: Opis narzędzia
            process: Klasa procesu
        """
        self.name = name
        self.description = description
        self.process = process

    def get_schema(self) -> Dict[str, Any]:
        """
        Zwraca schemat narzędzia.
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.process.get_parameters_schema(),
            "returns": self.process.get_returns_schema()
        }

    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Wykonuje proces z przekazanymi parametrami.
        """
        return self.process.run(parameters)


class ProcessToolProvider:
    """Dostawca narzędzi procesu dla MCP."""

    def __init__(self, config: Dict[str, Any]):
        """
        Inicjalizuje dostawcę narzędzi procesu.
        """
        self.config = config
        from process.process import DefaultProcess
        self.process = DefaultProcess(config)

    def get_tools(self) -> List[ProcessTool]:
        """
        Zwraca listę dostępnych narzędzi procesu.
        """
        return [
            ProcessTool(
                name="run_process",
                description="Uruchamia proces na podstawie parametrów",
                process=self.process
            )
        ]