"""Implementacja wykrywania narzędzi MCP."""

import json
from typing import Any, Callable, Dict, List, Optional


class MCPTool:
    """Reprezentacja narzędzia MCP."""

    def __init__(
        self, name: str, description: str, schema: Dict[str, Any], handler: Callable = None
    ):
        """
        Inicjalizuje narzędzie MCP.

        Args:
            name: Nazwa narzędzia
            description: Opis narzędzia
            schema: Schemat narzędzia w formacie MCP
            handler: Funkcja obsługująca wywołania narzędzia
        """
        self.name = name
        self.description = description
        self.schema = schema
        self.handler = handler
        self.uri = f"tool://{name}"

    def to_dict(self) -> Dict[str, Any]:
        """
        Konwertuje narzędzie na słownik.

        Returns:
            Reprezentacja narzędzia jako słownik
        """
        return {"name": self.name, "description": self.description, "schema": self.schema}

    def execute(self, parameters: Dict[str, Any]) -> Any:
        """
        Wykonuje narzędzie z podanymi parametrami.

        Args:
            parameters: Parametry dla narzędzia

        Returns:
            Wynik działania narzędzia
        """
        if self.handler:
            return self.handler(parameters)
        raise NotImplementedError(f"Narzędzie {self.name} nie ma zaimplementowanego handlera")


class ToolObserver:
    """Interfejs dla obserwatorów rejestru narzędzi."""

    def on_tool_update(self, tools: Dict[str, MCPTool]):
        """
        Metoda wywoływana przy aktualizacji listy narzędzi.

        Args:
            tools: Aktualna lista narzędzi
        """
        pass


class ToolDiscovery:
    """Komponent odpowiedzialny za wykrywanie i zarządzanie narzędziami MCP."""

    def __init__(self):
        """Inicjalizuje rejestr narzędzi."""
        self.tools = {}
        self.observers = []

    def register_tool(self, tool: MCPTool):
        """
        Rejestruje narzędzie MCP.

        Args:
            tool: Narzędzie do zarejestrowania
        """
        self.tools[tool.name] = tool
        self._notify_observers()

    def unregister_tool(self, tool_name: str):
        """
        Wyrejestrowuje narzędzie MCP.

        Args:
            tool_name: Nazwa narzędzia do wyrejestrowania
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            self._notify_observers()

    def get_tools(self) -> List[MCPTool]:
        """
        Zwraca listę zarejestrowanych narzędzi.

        Returns:
            Lista narzędzi
        """
        return list(self.tools.values())

    def get_tool(self, name: str) -> Optional[MCPTool]:
        """
        Zwraca narzędzie o podanej nazwie.

        Args:
            name: Nazwa narzędzia

        Returns:
            Narzędzie o podanej nazwie lub None, jeśli nie znaleziono
        """
        return self.tools.get(name)

    def register_observer(self, observer: ToolObserver):
        """
        Rejestruje obserwatora aktualizacji listy narzędzi.

        Args:
            observer: Obserwator do zarejestrowania
        """
        self.observers.append(observer)

    def _notify_observers(self):
        """Powiadamia obserwatorów o aktualizacji listy narzędzi."""
        for observer in self.observers:
            observer.on_tool_update(self.tools)
