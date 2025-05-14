"""Implementacja serwera MCP dla integracji z systemem Process."""

import asyncio
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Type

# Dodajemy katalog główny projektu do ścieżki importu
sys.path.append(str(Path(__file__).parent.parent))

from lib.config import load_config
from lib.logging import setup_logger
from mcp.protocol.negotiation import ProtocolNegotiator
from mcp.protocol.discovery import ToolDiscovery
from mcp.tools.tts_tool import ProcessToolProvider
from mcp.resources.uri_templates import ResourceRegistry
from mcp.transports.hybrid import HybridServer

logger = setup_logger("mcp_server")


class MCPServer:
    """Serwer MCP integrujący różne narzędzia i zasoby."""

    def __init__(self, config: Dict[str, Any]):
        """
        Inicjalizuje serwer MCP.

        Args:
            config: Konfiguracja serwera
        """
        self.config = config
        self.protocol_negotiator = ProtocolNegotiator(
            supported_versions=config.get("supported_versions", ["0.8.1"])
        )
        self.tool_discovery = ToolDiscovery()
        self.resource_registry = ResourceRegistry()

        # Inicjalizacja dostawców narzędzi
        self.tool_providers = [
            ProcessToolProvider(config.get("tts_config", {}))
        ]

        # Inicjalizacja transportu
        transport_config = config.get("transport", {})
        self.server = HybridServer(
            port=transport_config.get("port", 4000),
            use_sse=transport_config.get("use_sse", True),
            use_stdio=transport_config.get("use_stdio", True),
            use_grpc=transport_config.get("use_grpc", False)
        )

    async def start(self):
        """Uruchamia serwer MCP."""
        # Rejestracja narzędzi
        for provider in self.tool_providers:
            tools = provider.get_tools()
            for tool in tools:
                self.tool_discovery.register_tool(tool)
                logger.info(f"Zarejestrowano narzędzie: {tool.name}")

        # Konfiguracja handlerów
        self.server.set_protocol_negotiator(self.protocol_negotiator)
        self.server.set_discovery_provider(self.tool_discovery)

        # Uruchomienie serwera
        logger.info("Uruchamianie serwera MCP...")
        await self.server.start()

    async def stop(self):
        """Zatrzymuje serwer MCP."""
        logger.info("Zatrzymywanie serwera MCP...")
        await self.server.stop()


async def main():
    """Funkcja główna serwera MCP."""
    config = load_config()
    server = MCPServer(config)

    try:
        await server.start()
        # Utrzymanie serwera uruchomionego
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Otrzymano sygnał przerwania, zamykanie serwera...")
    finally:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())