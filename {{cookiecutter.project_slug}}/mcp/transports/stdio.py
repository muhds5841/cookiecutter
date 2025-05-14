"""Implementacja transportu stdio dla MCP."""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional


class StdioTransport:
    """
    Transport MCP oparty o standard input/output.
    Umożliwia komunikację przez stdin/stdout, co jest przydatne w integracji
    z narzędziami CLI i komunikacji międzyprocesowej.
    """

    def __init__(self):
        """Inicjalizuje transport stdio."""
        self.protocol_negotiator = None
        self.discovery_provider = None
        self.running = False

    def set_protocol_negotiator(self, negotiator):
        """Ustawia negocjator protokołu."""
        self.protocol_negotiator = negotiator

    def set_discovery_provider(self, discovery_provider):
        """Ustawia dostawcę discovery."""
        self.discovery_provider = discovery_provider

    async def _read_stdin(self):
        """
        Czyta dane z stdin.

        Returns:
            Odczytana linia lub None w przypadku EOF
        """
        loop = asyncio.get_event_loop()
        try:
            line = await loop.run_in_executor(None, sys.stdin.readline)
            return line if line else None
        except Exception as e:
            print(f"Error reading from stdin: {e}", file=sys.stderr)
            return None

    async def _write_stdout(self, data: Dict[str, Any]):
        """
        Zapisuje dane do stdout.

        Args:
            data: Dane do zapisania
        """
        try:
            json_data = json.dumps(data)
            print(json_data, flush=True)
        except Exception as e:
            print(f"Error writing to stdout: {e}", file=sys.stderr)

    async def _handle_message(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Obsługuje wiadomość od klienta.

        Args:
            message: Wiadomość od klienta

        Returns:
            Odpowiedź dla klienta lub None, jeśli nie ma odpowiedzi
        """
        try:
            request = json.loads(message)
            command = request.get("command")

            if command == "discovery":
                # Obsługa odkrywania narzędzi
                if not self.discovery_provider:
                    return {"error": "Discovery not implemented"}

                tools = self.discovery_provider.get_tools()
                return {"tools": [tool.to_dict() for tool in tools]}

            elif command == "execute":
                # Obsługa wykonywania narzędzi
                if not self.discovery_provider:
                    return {"error": "Tools not available"}

                tool_name = request.get("tool")
                parameters = request.get("parameters", {})

                if not tool_name:
                    return {"error": "Tool name not specified"}

                tool = self.discovery_provider.get_tool(tool_name)
                if not tool:
                    return {"error": f"Tool {tool_name} not found"}

                try:
                    result = tool.execute(parameters)
                    return {"result": result}
                except Exception as e:
                    return {"error": str(e)}

            return {"error": f"Unknown command: {command}"}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON"}
        except Exception as e:
            return {"error": str(e)}

    async def start(self):
        """Uruchamia transport stdio."""
        self.running = True

        try:
            # Informacja o uruchomieniu
            await self._write_stdout({"status": "ready", "transport": "stdio"})

            # Główna pętla odczytu i obsługi wiadomości
            while self.running:
                line = await self._read_stdin()
                if line is None:  # EOF
                    break

                if not line.strip():
                    continue

                response = await self._handle_message(line)
                if response:
                    await self._write_stdout(response)

        except asyncio.CancelledError:
            self.running = False
        except Exception as e:
            print(f"Stdio transport error: {e}", file=sys.stderr)
        finally:
            self.running = False

    async def stop(self):
        """Zatrzymuje transport stdio."""
        self.running = False
