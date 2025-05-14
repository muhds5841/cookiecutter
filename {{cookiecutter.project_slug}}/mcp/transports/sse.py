"""Implementacja transportu SSE (Server-Sent Events) dla MCP."""

import asyncio
import json
from typing import Any, Callable, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse


class SSETransport:
    """
    Transport MCP oparty o Server-Sent Events (SSE).
    Pozwala na strumieniowe przesyłanie wiadomości od serwera do klienta.
    """

    def __init__(self, port: int = 4000):
        """
        Inicjalizuje transport SSE.

        Args:
            port: Port, na którym ma nasłuchiwać serwer
        """
        self.port = port
        self.app = FastAPI(title="MCP SSE Server")
        self.protocol_negotiator = None
        self.discovery_provider = None
        self.running = False
        self._configure_app()

    def _configure_app(self):
        """Konfiguruje aplikację FastAPI."""
        # Dodanie middleware CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Endpointy
        @self.app.get("/")
        async def root():
            return {"message": "MCP SSE Server"}

        @self.app.get("/mcp/discovery")
        async def discovery():
            """Endpoint do odkrywania dostępnych narzędzi."""
            if not self.discovery_provider:
                raise HTTPException(status_code=501, detail="Discovery not implemented")

            tools = self.discovery_provider.get_tools()
            return {"tools": [tool.to_dict() for tool in tools]}

        @self.app.post("/mcp/execute/{tool_name}")
        async def execute_tool(tool_name: str, request: Request):
            """Endpoint do wykonywania narzędzi."""
            if not self.discovery_provider:
                raise HTTPException(status_code=501, detail="Tools not available")

            tool = self.discovery_provider.get_tool(tool_name)
            if not tool:
                raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")

            try:
                data = await request.json()
                result = tool.execute(data)
                return {"result": result}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.app.get("/mcp/stream")
        async def stream(request: Request):
            """Endpoint do strumieniowego przesyłania wiadomości."""

            async def event_generator():
                try:
                    while True:
                        if await request.is_disconnected():
                            break

                        # Wysłanie informacji o dostępnych narzędziach
                        if self.discovery_provider:
                            tools = self.discovery_provider.get_tools()
                            yield {
                                "event": "tools",
                                "data": json.dumps({"tools": [tool.to_dict() for tool in tools]}),
                            }

                        # Czekanie przed wysłaniem kolejnej wiadomości
                        await asyncio.sleep(5)
                except Exception as e:
                    print(f"Stream error: {e}")

            return EventSourceResponse(event_generator())

    def set_protocol_negotiator(self, negotiator):
        """Ustawia negocjator protokołu."""
        self.protocol_negotiator = negotiator

    def set_discovery_provider(self, discovery_provider):
        """Ustawia dostawcę discovery."""
        self.discovery_provider = discovery_provider

    async def start(self):
        """Uruchamia serwer SSE."""
        config = uvicorn.Config(self.app, host="0.0.0.0", port=self.port, log_level="info")
        server = uvicorn.Server(config)
        self.running = True

        # Uruchomienie serwera w tle
        await server.serve()

    async def stop(self):
        """Zatrzymuje serwer SSE."""
        self.running = False
