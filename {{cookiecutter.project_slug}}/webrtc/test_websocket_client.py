"""
Testy klienta WebSocket dla usługi Process.
"""

import json
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić import z websocket
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from websocket.client import WebSocketClient


class TestWebSocketClient(unittest.TestCase):
    """Testy klienta WebSocket."""

    def setUp(self):
        """Przygotowanie środowiska testowego."""
        # Patch dla websockets.connect
        self.connect_patcher = patch("websocket.client.websockets.connect")
        self.mock_connect = self.connect_patcher.start()

        # Mockowanie połączenia WebSocket
        self.mock_websocket = AsyncMock()
        self.mock_connect.return_value.__aenter__.return_value = self.mock_websocket

        # Mockowanie metod WebSocket
        self.mock_websocket.send = AsyncMock()
        self.mock_websocket.recv = AsyncMock()

        # Patch dla asyncio.run
        self.asyncio_run_patcher = patch("websocket.client.asyncio.run")
        self.mock_asyncio_run = self.asyncio_run_patcher.start()

        # Patch dla HealthCheck
        self.health_check_patcher = patch("websocket.client.HealthCheck")
        self.mock_health_check = self.health_check_patcher.start()

        # Mockowanie instancji HealthCheck
        self.mock_health_check_instance = MagicMock()
        self.mock_health_check.return_value = self.mock_health_check_instance

        # Inicjalizacja klienta WebSocket
        self.client = WebSocketClient(url="ws://localhost:8000/ws")

    def tearDown(self):
        """Czyszczenie po testach."""
        self.connect_patcher.stop()
        self.asyncio_run_patcher.stop()
        self.health_check_patcher.stop()

    def test_init(self):
        """Test inicjalizacji klienta."""
        # Sprawdź, czy klient został skonfigurowany
        self.assertEqual(self.client.url, "ws://localhost:8000/ws")
        self.assertEqual(self.client.timeout, 30)

        # Sprawdź, czy HealthCheck został zainicjalizowany
        self.mock_health_check.assert_called_once()
        self.mock_health_check_instance.register_check.assert_called_once_with(
            "websocket_connection", self.client._health_check_connection
        )

    def test_process_text(self):
        """Test przetwarzania tekstu."""
        # Mockowanie odpowiedzi
        self.mock_websocket.recv.return_value = json.dumps(
            {
                "request_id": "test_request_id",
                "result_id": "test_result_id",
                "format": "text",
                "data": "Przetworzony tekst",
                "metadata": {"test": "metadata"},
            }
        )

        # Mockowanie asyncio.run
        def run_side_effect(coroutine):
            # Symuluj wykonanie coroutine
            return {
                "request_id": "test_request_id",
                "result_id": "test_result_id",
                "format": "text",
                "data": "Przetworzony tekst",
                "metadata": {"test": "metadata"},
            }

        self.mock_asyncio_run.side_effect = run_side_effect

        # Wywołaj metodę process_text
        result = self.client.process_text("Przykładowy tekst", language="pl-PL")

        # Sprawdź, czy asyncio.run został wywołany
        self.mock_asyncio_run.assert_called_once()

        # Sprawdź, czy odpowiedź jest poprawna
        self.assertEqual(result["result_id"], "test_result_id")
        self.assertEqual(result["format"], "text")
        self.assertEqual(result["data"], "Przetworzony tekst")
        self.assertEqual(result["metadata"], {"test": "metadata"})

    def test_get_resources(self):
        """Test pobierania zasobów."""
        # Mockowanie odpowiedzi
        self.mock_websocket.recv.return_value = json.dumps(
            {
                "request_id": "test_request_id",
                "resources": [
                    {"id": "resource1", "name": "Resource 1"},
                    {"id": "resource2", "name": "Resource 2"},
                ],
            }
        )

        # Mockowanie asyncio.run
        def run_side_effect(coroutine):
            # Symuluj wykonanie coroutine
            return [
                {"id": "resource1", "name": "Resource 1"},
                {"id": "resource2", "name": "Resource 2"},
            ]

        self.mock_asyncio_run.side_effect = run_side_effect

        # Wywołaj metodę get_resources
        resources = self.client.get_resources()

        # Sprawdź, czy asyncio.run został wywołany
        self.mock_asyncio_run.assert_called_once()

        # Sprawdź, czy odpowiedź jest poprawna
        self.assertEqual(len(resources), 2)
        self.assertEqual(resources[0]["id"], "resource1")
        self.assertEqual(resources[1]["name"], "Resource 2")

    def test_health(self):
        """Test sprawdzania stanu zdrowia."""
        # Mockowanie get_status
        self.mock_health_check_instance.get_status.return_value = {
            "status": "healthy",
            "checks": {
                "websocket_connection": {
                    "status": "healthy",
                    "details": {"url": "ws://localhost:8000/ws"},
                }
            },
        }

        # Wywołaj metodę health
        health = self.client.health()

        # Sprawdź, czy get_status został wywołany
        self.mock_health_check_instance.get_status.assert_called_once()

        # Sprawdź, czy zwrócono poprawny status
        self.assertEqual(health["status"], "healthy")
        self.assertEqual(health["checks"]["websocket_connection"]["status"], "healthy")
        self.assertEqual(
            health["checks"]["websocket_connection"]["details"]["url"], "ws://localhost:8000/ws"
        )

    def test_health_check_connection(self):
        """Test health check połączenia."""
        # Mockowanie _async_health_check_connection
        self.client._async_health_check_connection = AsyncMock()
        self.client._async_health_check_connection.return_value = {
            "status": "healthy",
            "details": {"url": "ws://localhost:8000/ws"},
        }

        # Mockowanie asyncio.run
        def run_side_effect(coroutine):
            # Symuluj wykonanie coroutine
            return {"status": "healthy", "details": {"url": "ws://localhost:8000/ws"}}

        self.mock_asyncio_run.side_effect = run_side_effect

        # Wywołaj metodę _health_check_connection
        result = self.client._health_check_connection()

        # Sprawdź, czy asyncio.run został wywołany
        self.mock_asyncio_run.assert_called_once()

        # Sprawdź, czy zwrócono poprawny status
        self.assertEqual(result["status"], "healthy")
        self.assertEqual(result["details"]["url"], "ws://localhost:8000/ws")

    @patch("websocket.client.uuid.uuid4")
    async def test_async_process_text(self, mock_uuid4):
        """Test asynchronicznego przetwarzania tekstu."""
        # Mockowanie uuid4
        mock_uuid4.return_value = "test_request_id"

        # Mockowanie odpowiedzi
        self.mock_websocket.recv.return_value = json.dumps(
            {
                "request_id": "test_request_id",
                "result_id": "test_result_id",
                "format": "text",
                "data": "Przetworzony tekst",
                "metadata": {"test": "metadata"},
            }
        )

        # Wywołaj metodę _async_process_text
        result = await self.client._async_process_text("Przykładowy tekst", language="pl-PL")

        # Sprawdź, czy websockets.connect został wywołany
        self.mock_connect.assert_called_once_with(self.client.url)

        # Sprawdź, czy send został wywołany
        self.mock_websocket.send.assert_called_once()
        args, kwargs = self.mock_websocket.send.call_args
        request = json.loads(args[0])
        self.assertEqual(request["type"], "process")
        self.assertEqual(request["text"], "Przykładowy tekst")
        self.assertEqual(request["options"]["language"], "pl-PL")
        self.assertEqual(request["request_id"], "test_request_id")

        # Sprawdź, czy recv został wywołany
        self.mock_websocket.recv.assert_called_once()

        # Sprawdź, czy odpowiedź jest poprawna
        self.assertEqual(result["result_id"], "test_result_id")
        self.assertEqual(result["format"], "text")
        self.assertEqual(result["data"], "Przetworzony tekst")
        self.assertEqual(result["metadata"], {"test": "metadata"})

    @patch("websocket.client.uuid.uuid4")
    async def test_async_get_resources(self, mock_uuid4):
        """Test asynchronicznego pobierania zasobów."""
        # Mockowanie uuid4
        mock_uuid4.return_value = "test_request_id"

        # Mockowanie odpowiedzi
        self.mock_websocket.recv.return_value = json.dumps(
            {
                "request_id": "test_request_id",
                "resources": [
                    {"id": "resource1", "name": "Resource 1"},
                    {"id": "resource2", "name": "Resource 2"},
                ],
            }
        )

        # Wywołaj metodę _async_get_resources
        resources = await self.client._async_get_resources()

        # Sprawdź, czy websockets.connect został wywołany
        self.mock_connect.assert_called_once_with(self.client.url)

        # Sprawdź, czy send został wywołany
        self.mock_websocket.send.assert_called_once()
        args, kwargs = self.mock_websocket.send.call_args
        request = json.loads(args[0])
        self.assertEqual(request["type"], "resources")
        self.assertEqual(request["request_id"], "test_request_id")

        # Sprawdź, czy recv został wywołany
        self.mock_websocket.recv.assert_called_once()

        # Sprawdź, czy odpowiedź jest poprawna
        self.assertEqual(len(resources), 2)
        self.assertEqual(resources[0]["id"], "resource1")
        self.assertEqual(resources[1]["name"], "Resource 2")

    async def test_async_health_check_connection(self):
        """Test asynchronicznego health check połączenia."""
        # Wywołaj metodę _async_health_check_connection
        result = await self.client._async_health_check_connection()

        # Sprawdź, czy websockets.connect został wywołany
        self.mock_connect.assert_called_once_with(self.client.url)

        # Sprawdź, czy zwrócono poprawny status
        self.assertEqual(result["status"], "healthy")
        self.assertEqual(result["details"]["url"], "ws://localhost:8000/ws")

    async def test_async_health_check_connection_error(self):
        """Test asynchronicznego health check połączenia z błędem."""
        # Mockowanie connect z błędem
        self.mock_connect.side_effect = Exception("Connection error")

        # Wywołaj metodę _async_health_check_connection
        result = await self.client._async_health_check_connection()

        # Sprawdź, czy websockets.connect został wywołany
        self.mock_connect.assert_called_once_with(self.client.url)

        # Sprawdź, czy zwrócono poprawny status
        self.assertEqual(result["status"], "unhealthy")
        self.assertEqual(result["details"]["error"], "Connection error")
        self.assertEqual(result["details"]["url"], "ws://localhost:8000/ws")


if __name__ == "__main__":
    unittest.main()
