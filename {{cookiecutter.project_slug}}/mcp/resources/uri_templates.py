"""Implementacja URI templates dla zasobów MCP."""

import re
from typing import Dict, Any, List, Optional, Callable, Pattern, Tuple


class URITemplate:
    """Klasa reprezentująca URI template dla zasobu MCP."""

    def __init__(self, pattern: str, params: Dict[str, str] = None):
        """
        Inicjalizuje URI template.

        Args:
            pattern: Wzorzec URI z parametrami w formacie {param}
            params: Słownik z wzorcami wyrażeń regularnych dla parametrów
        """
        self.pattern = pattern
        self.params = params or {}
        self.regex_pattern = self._build_regex_pattern()
        self.compiled_regex = re.compile(self.regex_pattern)

    def _build_regex_pattern(self) -> str:
        """
        Buduje wzorzec wyrażenia regularnego na podstawie URI template.

        Returns:
            Wzorzec wyrażenia regularnego
        """
        pattern = self.pattern
        # Zamiana parametrów na grupy przechwytujące w wyrażeniu regularnym
        for param_name, param_regex in self.params.items():
            {% raw %}
            placeholder = f"{{{param_name}}}"
            {% endraw %}
            if placeholder in pattern:
                pattern = pattern.replace(
                    placeholder,
                    f"(?P<{param_name}>{param_regex})"
                )
        return f"^{pattern}$"

    def match(self, uri: str) -> Optional[Dict[str, str]]:
        """
        Sprawdza, czy URI pasuje do szablonu i wyodrębnia parametry.

        Args:
            uri: URI do dopasowania

        Returns:
            Słownik z wyodrębnionymi parametrami lub None, jeśli URI nie pasuje
        """
        match = self.compiled_regex.match(uri)
        if not match:
            return None
        return match.groupdict()


class MCPResource:
    """Abstrakcyjna klasa reprezentująca zasób MCP."""

    def __init__(
            self,
            uri_template: URITemplate,
            methods: List[str] = None,
            handler: Callable = None
    ):
        """
        Inicjalizuje zasób MCP.

        Args:
            uri_template: Szablon URI dla zasobu
            methods: Lista obsługiwanych metod HTTP
            handler: Funkcja obsługująca żądania do zasobu
        """
        self.uri_template = uri_template
        self.methods = methods or ["GET"]
        self.handler = handler

    def handle_request(self, method: str, uri: str, data: Any = None) -> Any:
        """
        Obsługuje żądanie do zasobu.

        Args:
            method: Metoda HTTP (GET, POST, itp.)
            uri: URI żądania
            data: Dane żądania

        Returns:
            Wynik obsługi żądania
        """
        if method not in self.methods:
            raise ValueError(f"Metoda {method} nie jest obsługiwana")

        params = self.uri_template.match(uri)
        if params is None:
            raise ValueError(f"URI {uri} nie pasuje do szablonu")

        if self.handler:
            return self.handler(method, params, data)

        # Domyślna implementacja do nadpisania w klasach pochodnych
        return {"status": "success", "params": params}


class ResourceRegistry:
    """Rejestr zasobów MCP."""

    def __init__(self):
        """Inicjalizuje rejestr zasobów."""
        self.resources = []

    def register_resource(self, resource: MCPResource):
        """
        Rejestruje zasób MCP.

        Args:
            resource: Zasób do zarejestrowania
        """
        self.resources.append(resource)

    def find_resource(self, method: str, uri: str) -> Tuple[Optional[MCPResource], Optional[Dict[str, str]]]:
        """
        Znajduje zasób obsługujący dane żądanie.

        Args:
            method: Metoda HTTP
            uri: URI żądania

        Returns:
            Krotka (zasób, parametry) lub (None, None), jeśli nie znaleziono
        """
        for resource in self.resources:
            if method in resource.methods:
                params = resource.uri_template.match(uri)
                if params is not None:
                    return resource, params

        return None, None


def mcp_resource(uri_template: str, methods: List[str] = None, params: Dict[str, str] = None):
    """
    Dekorator do rejestracji zasobów MCP.

    Args:
        uri_template: Szablon URI
        methods: Lista obsługiwanych metod
        params: Słownik z wyrażeniami regularnymi dla parametrów

    Returns:
        Dekorator
    """

    def decorator(cls):
        # Tworzenie URI template
        template = URITemplate(uri_template, params)

        # Zapamiętanie oryginalnej metody __init__
        original_init = cls.__init__

        def __init__(self, *args, **kwargs):
            # Wywołanie oryginalnego inicjalizatora
            original_init(self, *args, **kwargs)
            # Dodanie atrybutów związanych z MCP
            self.uri_template = template
            self.methods = methods or ["GET"]

        # Zastąpienie inicjalizatora
        cls.__init__ = __init__

        return cls

    return decorator