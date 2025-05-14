"""Implementacja wieloprotokołowego serwera MCP."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Any, List

from mcp.transports.sse import SSETransport
from mcp.transports.stdio import StdioTransport

try:
    from mcp.transports.grpc_transport import GRPCTransport

    GRPC_AVAILABLE = True
except ImportError:
    GRPC_AVAILABLE = False


class HybridServer:
    """
    Serwer MCP obsługujący wiele protokołów transportowych jednocześnie.
    Pozwala na komunikację zarówno przez SSE, stdio, jak i opcjonalnie gRPC.
    """

    def __init__(
            self,
            port: int = 4000,
            use_sse: bool = True,
            use_stdio: bool = True,
            use_grpc: bool = False
    ):
        """
        Inicjalizuje wieloprotokołowy serwer MCP.

        Args:
            port: Port dla transportu SSE
            use_sse: Czy używać transportu SSE
            use_stdio: Czy używać transportu stdio
            use_grpc: Czy używać transportu gRPC
        """
        self.transports = {}

        if use_sse:
            self.transports["sse"] = SSETransport(port=port)

        if use_stdio:
            self.transports["stdio"] = StdioTransport()

        if use_grpc and GRPC_AVAILABLE:
            self.transports["grpc"] = GRPCTransport(port=port + 1)

        if not self.transports:
            raise ValueError("Musisz włączyć przynajmniej jeden transport")

        self.protocol_negotiator = None
        self.discovery_provider = None
        self.running_tasks = []

    def set_protocol_negotiator(self, negotiator):
        """Ustawia negocjator protokołu dla wszystkich transportów."""
        self.protocol_negotiator = negotiator
        for transport in self.transports.values():
            transport.set_protocol_negotiator(negotiator)

    def set_discovery_provider(self, discovery_provider):
        """Ustawia dostawcę discovery dla wszystkich transportów."""
        self.discovery_provider = discovery_provider
        for transport in self.transports.values():
            transport.set_discovery_provider(discovery_provider)

    async def start(self):
        """Uruchamia wszystkie transporty w osobnych wątkach."""
        tasks = []

        for name, transport in self.transports.items():
            task = asyncio.create_task(transport.start())
            self.running_tasks.append(task)
            tasks.append(task)
            print(f"Uruchomiono transport: {name}")

        # Oczekiwanie na inicjalizację wszystkich transportów
        await asyncio.gather(*tasks, return_exceptions=True)

    async def stop(self):
        """Zatrzymuje wszystkie transporty."""
        stop_tasks = []

        for name, transport in self.transports.items():
            task = asyncio.create_task(transport.stop())
            stop_tasks.append(task)
            print(f"Zatrzymywanie transportu: {name}")

        # Oczekiwanie na zatrzymanie wszystkich transportów
        await asyncio.gather(*stop_tasks, return_exceptions=True)

        # Anulowanie uruchomionych zadań
        for task in self.running_tasks:
            if not task.done():
                task.cancel()