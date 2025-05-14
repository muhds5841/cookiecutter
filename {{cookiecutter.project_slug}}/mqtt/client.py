"""
Klient MQTT dla usługi Process.
"""

import json
import os
import sys
import threading
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Union

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić import z core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import paho.mqtt.client as mqtt

from core.config import load_config
from core.logging import configure_logging, get_logger


class ProcessClient:
    """Klient MQTT dla usługi Process."""

    def __init__(
        self, broker_host: str = "localhost", broker_port: int = 1883, config: Dict[str, Any] = None
    ):
        """Inicjalizuje klienta MQTT.

        Args:
            broker_host: Host brokera MQTT
            broker_port: Port brokera MQTT
            config: Konfiguracja klienta
        """
        self.config = config or load_config("mqtt")
        self.logger = get_logger("mqtt.client")

        # Konfiguracja MQTT
        self.host = broker_host
        self.port = broker_port
        self.topic_prefix = os.environ.get("MQTT_TOPIC_PREFIX", "process")
        self.username = os.environ.get("MQTT_USERNAME", "")
        self.password = os.environ.get("MQTT_PASSWORD", "")
        self.use_tls = os.environ.get("MQTT_USE_TLS", "false").lower() == "true"
        self.tls_cert_path = os.environ.get("MQTT_TLS_CERT_PATH", "")
        self.tls_key_path = os.environ.get("MQTT_TLS_KEY_PATH", "")
        self.qos = int(os.environ.get("MQTT_QOS", "1"))

        # Inicjalizacja klienta MQTT
        self.client_id = f"process-client-{uuid.uuid4().hex[:8]}"
        self.client = mqtt.Client(client_id=self.client_id)

        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)

        if self.use_tls and self.tls_cert_path and self.tls_key_path:
            self.client.tls_set(
                ca_certs=None, certfile=self.tls_cert_path, keyfile=self.tls_key_path
            )

        # Konfiguracja callbacków
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        # Słownik oczekujących odpowiedzi
        self.pending_requests = {}
        self.lock = threading.Lock()

        # Połącz z brokerem
        self.connect()

        self.logger.info(f"Klient MQTT zainicjalizowany, połączony z {self.host}:{self.port}")

    def connect(self):
        """Łączy z brokerem MQTT."""
        try:
            self.client.connect(self.host, self.port)
            self.client.loop_start()
        except Exception as e:
            self.logger.error(f"Błąd podczas łączenia z brokerem MQTT: {str(e)}")
            raise

    def disconnect(self):
        """Rozłącza z brokerem MQTT."""
        self.client.loop_stop()
        self.client.disconnect()
        self.logger.info("Rozłączono z brokerem MQTT")

    def on_connect(self, client, userdata, flags, rc):
        """Callback wywoływany po połączeniu z brokerem MQTT."""
        if rc == 0:
            self.logger.info("Połączono z brokerem MQTT")
            # Subskrybuj tematy odpowiedzi
            self.client.subscribe(f"{self.topic_prefix}/response", qos=self.qos)
            self.client.subscribe(f"{self.topic_prefix}/error", qos=self.qos)
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

            # Pobierz request_id
            request_id = payload.get("request_id", "")

            if not request_id:
                self.logger.warning("Otrzymano wiadomość bez request_id")
                return

            # Sprawdź, czy mamy oczekujące żądanie
            with self.lock:
                if request_id in self.pending_requests:
                    event, callback = self.pending_requests[request_id]

                    # Wywołaj callback, jeśli istnieje
                    if callback:
                        callback(payload)

                    # Ustaw event, aby odblokować oczekujące wywołanie
                    event.set()
                else:
                    self.logger.warning(
                        f"Otrzymano odpowiedź dla nieznanego request_id: {request_id}"
                    )

        except json.JSONDecodeError:
            self.logger.error("Nieprawidłowy format JSON w wiadomości")
        except Exception as e:
            self.logger.error(f"Błąd podczas przetwarzania wiadomości: {str(e)}")

    def process_text(self, text: str, **options) -> Dict[str, Any]:
        """Przetwarza tekst za pomocą usługi Process.

        Args:
            text: Tekst do przetworzenia
            **options: Dodatkowe opcje przetwarzania

        Returns:
            Wynik przetwarzania
        """
        # Generuj unikalny request_id
        request_id = str(uuid.uuid4())

        # Przygotuj żądanie
        request = {
            "request_id": request_id,
            "text": text,
            "options": options,
            "response_topic": f"{self.topic_prefix}/response",
        }

        # Utwórz event do synchronizacji
        event = threading.Event()

        # Zmienna na odpowiedź
        response_data = {"result": None, "error": None}

        # Callback do obsługi odpowiedzi
        def handle_response(response):
            if "error" in response:
                response_data["error"] = response["error"]
            else:
                response_data["result"] = response

        # Zarejestruj oczekujące żądanie
        with self.lock:
            self.pending_requests[request_id] = (event, handle_response)

        try:
            # Opublikuj żądanie
            self.client.publish(f"{self.topic_prefix}/process", json.dumps(request), qos=self.qos)

            self.logger.info(f"Wysłano żądanie przetwarzania, request_id: {request_id}")

            # Czekaj na odpowiedź (z timeoutem)
            if not event.wait(timeout=60.0):
                self.logger.error(f"Timeout oczekiwania na odpowiedź, request_id: {request_id}")
                raise TimeoutError("Timeout oczekiwania na odpowiedź")

            # Sprawdź, czy wystąpił błąd
            if response_data["error"]:
                self.logger.error(f"Błąd przetwarzania: {response_data['error']}")
                raise Exception(response_data["error"])

            return response_data["result"]

        finally:
            # Usuń oczekujące żądanie
            with self.lock:
                self.pending_requests.pop(request_id, None)

    def get_resources(self) -> Dict[str, Any]:
        """Pobiera dostępne zasoby.

        Returns:
            Dostępne zasoby
        """
        # Generuj unikalny request_id
        request_id = str(uuid.uuid4())

        # Przygotuj żądanie
        request = {"request_id": request_id, "response_topic": f"{self.topic_prefix}/response"}

        # Utwórz event do synchronizacji
        event = threading.Event()

        # Zmienna na odpowiedź
        response_data = {"result": None, "error": None}

        # Callback do obsługi odpowiedzi
        def handle_response(response):
            if "error" in response:
                response_data["error"] = response["error"]
            else:
                response_data["result"] = response

        # Zarejestruj oczekujące żądanie
        with self.lock:
            self.pending_requests[request_id] = (event, handle_response)

        try:
            # Opublikuj żądanie
            self.client.publish(f"{self.topic_prefix}/resources", json.dumps(request), qos=self.qos)

            self.logger.info(f"Wysłano żądanie pobrania zasobów, request_id: {request_id}")

            # Czekaj na odpowiedź (z timeoutem)
            if not event.wait(timeout=30.0):
                self.logger.error(f"Timeout oczekiwania na odpowiedź, request_id: {request_id}")
                raise TimeoutError("Timeout oczekiwania na odpowiedź")

            # Sprawdź, czy wystąpił błąd
            if response_data["error"]:
                self.logger.error(f"Błąd pobierania zasobów: {response_data['error']}")
                raise Exception(response_data["error"])

            return response_data["result"]["resources"]

        finally:
            # Usuń oczekujące żądanie
            with self.lock:
                self.pending_requests.pop(request_id, None)


def main():
    """Funkcja główna klienta MQTT."""
    # Konfiguracja logowania
    log_level = os.environ.get("MQTT_LOG_LEVEL", "INFO")
    configure_logging(level=log_level)

    # Przykład użycia klienta
    client = ProcessClient()

    try:
        # Pobierz zasoby
        resources = client.get_resources()
        print(f"Dostępne zasoby: {json.dumps(resources, indent=2)}")

        # Przetwórz tekst
        text = "Przykładowy tekst do przetworzenia"
        result = client.process_text(text, language="pl-PL")
        print(f"Wynik przetwarzania: {json.dumps(result, indent=2)}")

    except Exception as e:
        print(f"Błąd: {str(e)}")

    finally:
        # Rozłącz klienta
        client.disconnect()


if __name__ == "__main__":
    main()
