"""
Testy klienta MQTT dla usługi Process.
"""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, call, patch

import pytest

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić import z mqtt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mqtt.client import ProcessClient


class TestMQTTClient(unittest.TestCase):
    """Testy klienta MQTT."""

    def setUp(self):
        """Przygotowanie środowiska testowego."""
        # Patch dla klienta MQTT
        self.mqtt_client_patcher = patch("mqtt.client.mqtt.Client")
        self.mock_mqtt_client = self.mqtt_client_patcher.start()

        # Mockowanie instancji klienta MQTT
        self.mock_client_instance = MagicMock()
        self.mock_mqtt_client.return_value = self.mock_client_instance

        # Mockowanie metod klienta
        self.mock_client_instance.connect = MagicMock()
        self.mock_client_instance.loop_start = MagicMock()
        self.mock_client_instance.loop_stop = MagicMock()
        self.mock_client_instance.disconnect = MagicMock()
        self.mock_client_instance.publish = MagicMock()
        self.mock_client_instance.subscribe = MagicMock()

        # Inicjalizacja klienta Process
        self.client = ProcessClient(broker_host="localhost", broker_port=1883)

    def tearDown(self):
        """Czyszczenie po testach."""
        self.mqtt_client_patcher.stop()

    def test_init(self):
        """Test inicjalizacji klienta."""
        # Sprawdź, czy klient MQTT został utworzony
        self.mock_mqtt_client.assert_called_once()

        # Sprawdź, czy klient został skonfigurowany
        self.assertEqual(self.client.host, "localhost")
        self.assertEqual(self.client.port, 1883)

        # Sprawdź, czy klient został połączony
        self.mock_client_instance.connect.assert_called_once_with("localhost", 1883)
        self.mock_client_instance.loop_start.assert_called_once()

    def test_disconnect(self):
        """Test rozłączania klienta."""
        # Rozłącz klienta
        self.client.disconnect()

        # Sprawdź, czy klient został rozłączony
        self.mock_client_instance.loop_stop.assert_called_once()
        self.mock_client_instance.disconnect.assert_called_once()

    @patch("mqtt.client.threading.Event")
    def test_process_text(self, mock_event):
        """Test przetwarzania tekstu."""
        # Mockowanie Event
        mock_event_instance = MagicMock()
        mock_event.return_value = mock_event_instance
        mock_event_instance.wait.return_value = True

        # Mockowanie odpowiedzi
        self.client.pending_requests = {}

        def side_effect(request_id, value):
            # Symuluj otrzymanie odpowiedzi
            event, callback = value
            callback(
                {
                    "request_id": request_id,
                    "result_id": "test_result_id",
                    "format": "text",
                    "data": "Przetworzony tekst",
                    "metadata": {"test": "metadata"},
                }
            )
            return None

        # Mockowanie słownika pending_requests
        self.client.pending_requests.__setitem__ = MagicMock(side_effect=side_effect)

        # Wywołaj metodę process_text
        result = self.client.process_text("Przykładowy tekst", language="pl-PL")

        # Sprawdź, czy żądanie zostało opublikowane
        self.mock_client_instance.publish.assert_called_once()
        args, kwargs = self.mock_client_instance.publish.call_args
        self.assertEqual(args[0], "process/process")

        # Sprawdź, czy odpowiedź jest poprawna
        self.assertEqual(result["result_id"], "test_result_id")
        self.assertEqual(result["format"], "text")
        self.assertEqual(result["data"], "Przetworzony tekst")
        self.assertEqual(result["metadata"], {"test": "metadata"})

    @patch("mqtt.client.threading.Event")
    def test_get_resources(self, mock_event):
        """Test pobierania zasobów."""
        # Mockowanie Event
        mock_event_instance = MagicMock()
        mock_event.return_value = mock_event_instance
        mock_event_instance.wait.return_value = True

        # Mockowanie odpowiedzi
        self.client.pending_requests = {}

        def side_effect(request_id, value):
            # Symuluj otrzymanie odpowiedzi
            event, callback = value
            callback(
                {
                    "request_id": request_id,
                    "resources": [
                        {"id": "resource1", "name": "Resource 1"},
                        {"id": "resource2", "name": "Resource 2"},
                    ],
                }
            )
            return None

        # Mockowanie słownika pending_requests
        self.client.pending_requests.__setitem__ = MagicMock(side_effect=side_effect)

        # Wywołaj metodę get_resources
        resources = self.client.get_resources()

        # Sprawdź, czy żądanie zostało opublikowane
        self.mock_client_instance.publish.assert_called_once()
        args, kwargs = self.mock_client_instance.publish.call_args
        self.assertEqual(args[0], "process/resources")

        # Sprawdź, czy odpowiedź jest poprawna
        self.assertEqual(len(resources), 2)
        self.assertEqual(resources[0]["id"], "resource1")
        self.assertEqual(resources[1]["name"], "Resource 2")

    def test_on_message(self):
        """Test obsługi wiadomości."""
        # Mockowanie wiadomości
        mock_msg = MagicMock()
        mock_msg.topic = "process/response"
        mock_msg.payload = json.dumps(
            {"request_id": "test_request_id", "result": "test_result"}
        ).encode()

        # Mockowanie pending_requests
        mock_event = MagicMock()
        mock_callback = MagicMock()
        self.client.pending_requests = {"test_request_id": (mock_event, mock_callback)}

        # Wywołaj metodę on_message
        self.client.on_message(None, None, mock_msg)

        # Sprawdź, czy callback został wywołany
        mock_callback.assert_called_once_with(
            {"request_id": "test_request_id", "result": "test_result"}
        )

        # Sprawdź, czy event został ustawiony
        mock_event.set.assert_called_once()


if __name__ == "__main__":
    unittest.main()
