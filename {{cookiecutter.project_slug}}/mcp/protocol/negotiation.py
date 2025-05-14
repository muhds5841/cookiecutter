"""Obsługa negocjacji wersji protokołu MCP."""

from typing import Any, Dict, List, Optional


class ProtocolNegotiator:
    """Komponent do negocjacji wersji protokołu MCP."""

    def __init__(self, supported_versions: List[str], default_version: Optional[str] = None):
        """
        Inicjalizuje negocjator protokołu.

        Args:
            supported_versions: Lista obsługiwanych wersji protokołu
            default_version: Domyślna wersja protokołu (jeśli None, używana jest najwyższa wersja)
        """
        self.supported_versions = set(supported_versions)
        self.default_version = default_version or max(supported_versions, default="0.8.1")

    def detect_version(self, headers: Dict[str, str]) -> str:
        """
        Wykrywa najlepszą wersję protokołu na podstawie nagłówków.

        Args:
            headers: Nagłówki żądania

        Returns:
            Najlepsza wersja protokołu do użycia
        """
        if not headers or "mcp-versions" not in headers:
            return self.default_version

        client_versions = set(headers["mcp-versions"].split(","))
        common_versions = self.supported_versions.intersection(client_versions)

        if not common_versions:
            return self.default_version

        return max(common_versions)

    def get_headers(self) -> Dict[str, str]:
        """
        Zwraca nagłówki protokołu MCP do wysłania.

        Returns:
            Nagłówki protokołu
        """
        return {"mcp-versions": ",".join(sorted(self.supported_versions, reverse=True))}
