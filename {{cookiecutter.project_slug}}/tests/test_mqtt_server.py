"""
Testy serwera MQTT dla usługi Process.
"""

import os
import sys
import json
import pytest
import unittest
from unittest.mock import patch, MagicMock, call

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić import z mqtt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mqtt.server import MqttServer


class TestMQTTServer(unittest.TestCase):
    """Testy serwera MQTT."""
    
    def setUp(self):
        """Przygotowanie środowiska testowego."""
        # Patch dla klienta MQTT
        self.mqtt_client_patcher = patch('mqtt.server.mqtt.Client')
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
        
        # Patch dla Process
        self.process_patcher = patch('mqtt.server.Process')
        self.mock_process = self.process_patcher.start()
        
        # Mockowanie instancji Process
        self.mock_process_instance = MagicMock()
        self.mock_process.return_value = self.mock_process_instance
        
        # Inicjalizacja serwera MQTT
        self.server = MqttServer()
    
    def tearDown(self):
        """Czyszczenie po testach."""
        self.mqtt_client_patcher.stop()
        self.process_patcher.stop()
    
    def test_init(self):
        """Test inicjalizacji serwera."""
        # Sprawdź, czy klient MQTT został utworzony
        self.mock_mqtt_client.assert_called_once()
        
        # Sprawdź, czy Process został zainicjalizowany
        self.mock_process.assert_called_once()
        
        # Sprawdź, czy callbacki zostały ustawione
        self.assertEqual(self.mock_client_instance.on_connect, self.server.on_connect)
        self.assertEqual(self.mock_client_instance.on_message, self.server.on_message)
        self.assertEqual(self.mock_client_instance.on_disconnect, self.server.on_disconnect)
    
    def test_on_connect(self):
        """Test callbacku on_connect."""
        # Wywołaj callback on_connect
        self.server.on_connect(self.mock_client_instance, None, None, 0)
        
        # Sprawdź, czy subskrypcje zostały utworzone
        self.mock_client_instance.subscribe.assert_has_calls([
            call(f"{self.server.topic_prefix}/process", qos=self.server.qos),
            call(f"{self.server.topic_prefix}/resources", qos=self.server.qos)
        ])
    
    def test_on_disconnect(self):
        """Test callbacku on_disconnect."""
        # Wywołaj callback on_disconnect
        self.server.on_disconnect(self.mock_client_instance, None, 0)
        
        # Nie ma potrzeby sprawdzania czegokolwiek, ponieważ callback tylko loguje
        pass
    
    def test_on_message_process(self):
        """Test obsługi wiadomości process."""
        # Mockowanie wiadomości
        mock_msg = MagicMock()
        mock_msg.topic = f"{self.server.topic_prefix}/process"
        mock_msg.payload = json.dumps({
            "text": "Przykładowy tekst",
            "options": {"language": "pl-PL"},
            "request_id": "test_request_id",
            "response_topic": "test_response_topic"
        }).encode()
        
        # Mockowanie wyniku przetwarzania
        mock_result = MagicMock()
        mock_result.result_id = "test_result_id"
        mock_result.format = "text"
        mock_result.data = "Przetworzony tekst"
        mock_result.metadata = {"test": "metadata"}
        
        self.mock_process_instance.process_text.return_value = mock_result
        
        # Wywołaj callback on_message
        self.server.on_message(self.mock_client_instance, None, mock_msg)
        
        # Sprawdź, czy Process.process_text został wywołany
        self.mock_process_instance.process_text.assert_called_once_with(
            "Przykładowy tekst", language="pl-PL"
        )
        
        # Sprawdź, czy odpowiedź została opublikowana
        self.mock_client_instance.publish.assert_called_once()
        args, kwargs = self.mock_client_instance.publish.call_args
        self.assertEqual(args[0], "test_response_topic")
        
        # Sprawdź zawartość odpowiedzi
        response = json.loads(args[1])
        self.assertEqual(response["request_id"], "test_request_id")
        self.assertEqual(response["result_id"], "test_result_id")
        self.assertEqual(response["format"], "text")
        self.assertEqual(response["data"], "Przetworzony tekst")
        self.assertEqual(response["metadata"], {"test": "metadata"})
    
    def test_on_message_resources(self):
        """Test obsługi wiadomości resources."""
        # Mockowanie wiadomości
        mock_msg = MagicMock()
        mock_msg.topic = f"{self.server.topic_prefix}/resources"
        mock_msg.payload = json.dumps({
            "request_id": "test_request_id",
            "response_topic": "test_response_topic"
        }).encode()
        
        # Mockowanie wyniku pobierania zasobów
        self.mock_process_instance.get_resources.return_value = [
            {"id": "resource1", "name": "Resource 1"},
            {"id": "resource2", "name": "Resource 2"}
        ]
        
        # Wywołaj callback on_message
        self.server.on_message(self.mock_client_instance, None, mock_msg)
        
        # Sprawdź, czy Process.get_resources został wywołany
        self.mock_process_instance.get_resources.assert_called_once()
        
        # Sprawdź, czy odpowiedź została opublikowana
        self.mock_client_instance.publish.assert_called_once()
        args, kwargs = self.mock_client_instance.publish.call_args
        self.assertEqual(args[0], "test_response_topic")
        
        # Sprawdź zawartość odpowiedzi
        response = json.loads(args[1])
        self.assertEqual(response["request_id"], "test_request_id")
        self.assertEqual(len(response["resources"]), 2)
        self.assertEqual(response["resources"][0]["id"], "resource1")
        self.assertEqual(response["resources"][1]["name"], "Resource 2")
    
    def test_on_message_invalid_json(self):
        """Test obsługi nieprawidłowego formatu JSON."""
        # Mockowanie wiadomości
        mock_msg = MagicMock()
        mock_msg.topic = f"{self.server.topic_prefix}/process"
        mock_msg.payload = b"invalid json"
        
        # Wywołaj callback on_message
        self.server.on_message(self.mock_client_instance, None, mock_msg)
        
        # Sprawdź, czy Process.process_text nie został wywołany
        self.mock_process_instance.process_text.assert_not_called()
        
        # Sprawdź, czy odpowiedź nie została opublikowana
        self.mock_client_instance.publish.assert_not_called()
    
    def test_on_message_process_missing_text(self):
        """Test obsługi wiadomości process bez pola text."""
        # Mockowanie wiadomości
        mock_msg = MagicMock()
        mock_msg.topic = f"{self.server.topic_prefix}/process"
        mock_msg.payload = json.dumps({
            "options": {"language": "pl-PL"},
            "request_id": "test_request_id",
            "response_topic": f"{self.server.topic_prefix}/response"
        }).encode()
        
        # Wywołaj callback on_message
        self.server.on_message(self.mock_client_instance, None, mock_msg)
        
        # Sprawdź, czy Process.process_text nie został wywołany
        self.mock_process_instance.process_text.assert_not_called()
        
        # Sprawdź, czy odpowiedź z błędem została opublikowana
        self.mock_client_instance.publish.assert_called_once()
        args, kwargs = self.mock_client_instance.publish.call_args
        self.assertEqual(args[0], f"{self.server.topic_prefix}/error")
        
        # Sprawdź zawartość odpowiedzi
        response = json.loads(args[1])
        self.assertEqual(response["request_id"], "test_request_id")
        self.assertIn("error", response)
    
    def test_publish_error(self):
        """Test publikowania błędu."""
        # Wywołaj metodę publish_error
        self.server.publish_error("Test error", "test_request_id")
        
        # Sprawdź, czy odpowiedź z błędem została opublikowana
        self.mock_client_instance.publish.assert_called_once()
        args, kwargs = self.mock_client_instance.publish.call_args
        self.assertEqual(args[0], f"{self.server.topic_prefix}/error")
        
        # Sprawdź zawartość odpowiedzi
        response = json.loads(args[1])
        self.assertEqual(response["request_id"], "test_request_id")
        self.assertEqual(response["error"], "Test error")
    
    @patch('mqtt.server.time.sleep', side_effect=KeyboardInterrupt)
    def test_start(self, mock_sleep):
        """Test uruchamiania serwera."""
        # Wywołaj metodę start
        self.server.start()
        
        # Sprawdź, czy klient został połączony
        self.mock_client_instance.connect.assert_called_once_with(self.server.host, self.server.port)
        
        # Sprawdź, czy pętla została uruchomiona
        self.mock_client_instance.loop_start.assert_called_once()
        
        # Sprawdź, czy pętla została zatrzymana po KeyboardInterrupt
        self.mock_client_instance.loop_stop.assert_called_once()
        self.mock_client_instance.disconnect.assert_called_once()


if __name__ == '__main__':
    unittest.main()
