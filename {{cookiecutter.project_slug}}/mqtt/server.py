"""
Serwer MQTT dla usługi Process.
"""

import os
import sys
import json
import time
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić import z process i core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import paho.mqtt.client as mqtt

from process.process import Process
from core.config import load_config
from core.logging import get_logger, configure_logging


class MqttServer:
    """Serwer MQTT dla usługi Process."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Inicjalizuje serwer MQTT.
        
        Args:
            config: Konfiguracja serwera
        """
        self.config = config or load_config("mqtt")
        self.logger = get_logger("mqtt.server")
        self.process = Process()
        
        # Konfiguracja MQTT
        self.host = os.environ.get("MQTT_HOST", "0.0.0.0")
        self.port = int(os.environ.get("MQTT_PORT", "1883"))
        self.topic_prefix = os.environ.get("MQTT_TOPIC_PREFIX", "process")
        self.username = os.environ.get("MQTT_USERNAME", "")
        self.password = os.environ.get("MQTT_PASSWORD", "")
        self.use_tls = os.environ.get("MQTT_USE_TLS", "false").lower() == "true"
        self.tls_cert_path = os.environ.get("MQTT_TLS_CERT_PATH", "")
        self.tls_key_path = os.environ.get("MQTT_TLS_KEY_PATH", "")
        self.qos = int(os.environ.get("MQTT_QOS", "1"))
        self.retain = os.environ.get("MQTT_RETAIN", "false").lower() == "true"
        
        # Inicjalizacja klienta MQTT
        self.client = mqtt.Client()
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        
        if self.use_tls and self.tls_cert_path and self.tls_key_path:
            self.client.tls_set(
                ca_certs=None,
                certfile=self.tls_cert_path,
                keyfile=self.tls_key_path
            )
        
        # Konfiguracja callbacków
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        self.logger.info(f"Inicjalizacja serwera MQTT na {self.host}:{self.port}")
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback wywoływany po połączeniu z brokerem MQTT."""
        if rc == 0:
            self.logger.info("Połączono z brokerem MQTT")
            # Subskrybuj tematy
            self.client.subscribe(f"{self.topic_prefix}/process", qos=self.qos)
            self.client.subscribe(f"{self.topic_prefix}/resources", qos=self.qos)
        else:
            self.logger.error(f"Błąd połączenia z brokerem MQTT, kod: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback wywoływany po rozłączeniu z brokerem MQTT."""
        if rc != 0:
            self.logger.warning(f"Nieoczekiwane rozłączenie z brokerem MQTT, kod: {rc}")
        else:
            self.logger.info("Rozłączono z brokerem MQTT")
    
    def on_message(self, client, userdata, msg):
        """Callback wywoływany po otrzymaniu wiadomości MQTT."""
        try:
            self.logger.debug(f"Otrzymano wiadomość na temat: {msg.topic}")
            
            # Dekodowanie wiadomości JSON
            payload = json.loads(msg.payload.decode("utf-8"))
            
            # Obsługa różnych tematów
            if msg.topic == f"{self.topic_prefix}/process":
                self.handle_process_request(payload)
            elif msg.topic == f"{self.topic_prefix}/resources":
                self.handle_resources_request(payload)
            else:
                self.logger.warning(f"Nieznany temat: {msg.topic}")
        
        except json.JSONDecodeError:
            self.logger.error("Nieprawidłowy format JSON w wiadomości")
        except Exception as e:
            self.logger.error(f"Błąd podczas przetwarzania wiadomości: {str(e)}")
    
    def handle_process_request(self, payload: Dict[str, Any]):
        """Obsługuje żądanie przetwarzania tekstu."""
        try:
            # Sprawdź, czy payload zawiera wymagane pola
            if "text" not in payload:
                self.publish_error("Brak wymaganego pola 'text'", payload.get("request_id"))
                return
            
            # Pobierz parametry
            text = payload["text"]
            options = payload.get("options", {})
            request_id = payload.get("request_id", "")
            response_topic = payload.get("response_topic", f"{self.topic_prefix}/response")
            
            # Przetwórz tekst
            self.logger.info(f"Przetwarzanie tekstu: {text[:50]}...")
            result = self.process.process_text(text, **options)
            
            # Przygotuj odpowiedź
            response = {
                "request_id": request_id,
                "result_id": result.result_id,
                "format": result.format,
                "data": result.data,
                "metadata": result.metadata
            }
            
            # Opublikuj odpowiedź
            self.client.publish(
                response_topic,
                json.dumps(response),
                qos=self.qos,
                retain=self.retain
            )
            
            self.logger.info(f"Opublikowano odpowiedź dla request_id: {request_id}")
        
        except Exception as e:
            self.logger.error(f"Błąd podczas przetwarzania żądania: {str(e)}")
            self.publish_error(str(e), payload.get("request_id"))
    
    def handle_resources_request(self, payload: Dict[str, Any]):
        """Obsługuje żądanie pobrania zasobów."""
        try:
            # Pobierz parametry
            request_id = payload.get("request_id", "")
            response_topic = payload.get("response_topic", f"{self.topic_prefix}/response")
            
            # Pobierz zasoby
            resources = self.process.get_resources()
            
            # Przygotuj odpowiedź
            response = {
                "request_id": request_id,
                "resources": resources
            }
            
            # Opublikuj odpowiedź
            self.client.publish(
                response_topic,
                json.dumps(response),
                qos=self.qos,
                retain=self.retain
            )
            
            self.logger.info(f"Opublikowano zasoby dla request_id: {request_id}")
        
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania zasobów: {str(e)}")
            self.publish_error(str(e), payload.get("request_id"))
    
    def publish_error(self, error_message: str, request_id: str = ""):
        """Publikuje komunikat o błędzie."""
        error_response = {
            "request_id": request_id,
            "error": error_message
        }
        
        self.client.publish(
            f"{self.topic_prefix}/error",
            json.dumps(error_response),
            qos=self.qos,
            retain=False
        )
    
    def start(self):
        """Uruchamia serwer MQTT."""
        try:
            # Połącz z brokerem MQTT
            self.client.connect(self.host, self.port)
            
            # Uruchom pętlę obsługi wiadomości
            self.client.loop_start()
            
            self.logger.info(f"Serwer MQTT uruchomiony na {self.host}:{self.port}")
            
            # Utrzymuj serwer uruchomiony
            while True:
                time.sleep(1)
        
        except KeyboardInterrupt:
            self.logger.info("Zatrzymywanie serwera MQTT...")
            self.client.loop_stop()
            self.client.disconnect()
        except Exception as e:
            self.logger.error(f"Błąd podczas uruchamiania serwera MQTT: {str(e)}")
            self.client.loop_stop()
            self.client.disconnect()


def main():
    """Funkcja główna serwera MQTT."""
    # Konfiguracja logowania
    log_level = os.environ.get("MQTT_LOG_LEVEL", "INFO")
    configure_logging(level=log_level)
    
    # Uruchom serwer MQTT
    server = MqttServer()
    server.start()


if __name__ == "__main__":
    main()
