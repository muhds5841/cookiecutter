"""
Serwer IMAP dla usługi Process.
"""

import asyncio
import json
import logging
import os
import socket
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić import z process i core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.config import load_config
from core.logging import configure_logging, get_logger
from core.monitoring import HealthCheck, MetricsCollector
from process.process import Process


class IMAPServer:
    """Serwer IMAP dla usługi Process."""

    def __init__(self, config: Dict[str, Any] = None):
        """Inicjalizuje serwer IMAP.

        Args:
            config: Konfiguracja serwera
        """
        self.config = config or load_config("imap")
        self.logger = get_logger("imap.server")
        self.process = Process()

        # Konfiguracja IMAP
        self.host = os.environ.get("IMAP_HOST", "0.0.0.0")
        self.port = int(os.environ.get("IMAP_PORT", "143"))
        self.ssl_port = int(os.environ.get("IMAP_SSL_PORT", "993"))
        self.use_ssl = os.environ.get("IMAP_USE_SSL", "false").lower() == "true"
        self.max_connections = int(os.environ.get("IMAP_MAX_CONNECTIONS", "10"))
        self.attachment_dir = os.environ.get("IMAP_ATTACHMENT_DIR", "./attachments")

        # Utwórz katalog na załączniki, jeśli nie istnieje
        Path(self.attachment_dir).mkdir(parents=True, exist_ok=True)

        # Konfiguracja monitorowania
        self.enable_metrics = os.environ.get("IMAP_ENABLE_METRICS", "true").lower() == "true"
        if self.enable_metrics:
            self.metrics = MetricsCollector(
                service_name="imap", metrics_port=int(os.environ.get("IMAP_METRICS_PORT", "9101"))
            )
            self.metrics.register_counter(
                "imap_connections_total", "Total number of IMAP connections"
            )
            self.metrics.register_counter(
                "imap_commands_total", "Total number of IMAP commands processed"
            )
            self.metrics.register_counter("imap_errors_total", "Total number of IMAP errors")
            self.metrics.register_gauge(
                "imap_active_connections", "Number of active IMAP connections"
            )
            self.metrics.register_histogram(
                "imap_command_processing_time", "Time to process IMAP commands"
            )

        # Konfiguracja health check
        self.health_check = HealthCheck(
            service_name="imap",
            check_interval=int(os.environ.get("IMAP_HEALTH_CHECK_INTERVAL", "30")),
            timeout=int(os.environ.get("IMAP_HEALTH_CHECK_TIMEOUT", "5")),
        )
        self.health_check.register_check("imap_server", self._health_check_server)
        self.health_check.register_check("process_connection", self._health_check_process)

        # Uruchom serwer HTTP dla health check
        self.health_server = self._start_health_server()

        # Aktywne połączenia
        self.active_connections = 0
        self.connections_lock = threading.Lock()

        self.logger.info(f"Serwer IMAP zainicjalizowany na {self.host}:{self.port}")

    def _health_check_server(self) -> Dict[str, Any]:
        """Sprawdza stan serwera IMAP.

        Returns:
            Słownik ze statusem health check
        """
        try:
            # Sprawdź, czy serwer nasłuchuje
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((self.host, self.port))
                if result != 0:
                    return {
                        "status": "unhealthy",
                        "details": {
                            "error": f"Port {self.port} nie jest otwarty",
                            "server": f"{self.host}:{self.port}",
                        },
                    }

            return {
                "status": "healthy",
                "details": {
                    "active_connections": self.active_connections,
                    "server": f"{self.host}:{self.port}",
                },
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "details": {"error": str(e), "server": f"{self.host}:{self.port}"},
            }

    def _health_check_process(self) -> Dict[str, Any]:
        """Sprawdza połączenie z usługą Process.

        Returns:
            Słownik ze statusem health check
        """
        try:
            # Sprawdź, czy usługa Process jest dostępna
            resources = self.process.get_resources()
            return {
                "status": "healthy",
                "details": {"resources_count": len(resources), "process_service": "available"},
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "details": {"error": str(e), "process_service": "unavailable"},
            }

    def _start_health_server(self):
        """Uruchamia serwer HTTP dla health check.

        Returns:
            Wątek serwera HTTP
        """
        health_port = int(os.environ.get("IMAP_HEALTH_PORT", "8080"))

        class HealthHandler(BaseHTTPRequestHandler):
            def __init__(self_handler, *args, **kwargs):
                self_handler.server_instance = self
                super().__init__(*args, **kwargs)

            def do_GET(self_handler):
                if self_handler.path == "/health" or self_handler.path == "/healthz":
                    health_status = self.health_check.get_status()
                    overall_status = "healthy"

                    # Sprawdź, czy wszystkie komponenty są zdrowe
                    for check in health_status["checks"]:
                        if health_status["checks"][check]["status"] != "healthy":
                            overall_status = "unhealthy"
                            break

                    health_status["status"] = overall_status

                    self_handler.send_response(200 if overall_status == "healthy" else 503)
                    self_handler.send_header("Content-type", "application/json")
                    self_handler.end_headers()
                    self_handler.wfile.write(json.dumps(health_status).encode())
                elif self_handler.path == "/metrics" and self.enable_metrics:
                    metrics_data = self.metrics.get_metrics()
                    self_handler.send_response(200)
                    self_handler.send_header("Content-type", "text/plain")
                    self_handler.end_headers()
                    self_handler.wfile.write(metrics_data.encode())
                else:
                    self_handler.send_response(404)
                    self_handler.send_header("Content-type", "text/plain")
                    self_handler.end_headers()
                    self_handler.wfile.write(b"Not Found")

            def log_message(self_handler, format, *args):
                # Przekieruj logi do naszego loggera
                self.logger.debug(format % args)

        def run_server():
            server = HTTPServer((self.host, health_port), HealthHandler)
            self.logger.info(
                f"Serwer HTTP dla health check uruchomiony na {self.host}:{health_port}"
            )
            server.serve_forever()

        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        return thread

    def handle_client(self, client_socket, client_address):
        """Obsługuje połączenie klienta IMAP.

        Args:
            client_socket: Gniazdo klienta
            client_address: Adres klienta
        """
        with self.connections_lock:
            self.active_connections += 1
            if self.enable_metrics:
                self.metrics.increment("imap_connections_total")
                self.metrics.set("imap_active_connections", self.active_connections)

        self.logger.info(f"Nowe połączenie od {client_address[0]}:{client_address[1]}")

        try:
            # Wyślij powitanie
            client_socket.sendall(b"* OK IMAP4 Process IMAP Server ready\r\n")

            # Główna pętla obsługi komend
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break

                command = data.decode("utf-8").strip()
                self.logger.debug(f"Otrzymano komendę: {command}")

                if self.enable_metrics:
                    self.metrics.increment("imap_commands_total")

                # Tutaj byłaby pełna implementacja obsługi komend IMAP
                # Na potrzeby przykładu obsługujemy tylko kilka podstawowych komend

                if command.upper().startswith("CAPABILITY"):
                    response = "* CAPABILITY IMAP4rev1 AUTH=PLAIN\r\n"
                    response += f"{command.split()[0]} OK CAPABILITY completed\r\n"
                    client_socket.sendall(response.encode())
                elif command.upper().startswith("LOGOUT"):
                    response = "* BYE IMAP4rev1 Server logging out\r\n"
                    response += f"{command.split()[0]} OK LOGOUT completed\r\n"
                    client_socket.sendall(response.encode())
                    break
                else:
                    # Domyślna odpowiedź dla nieobsługiwanych komend
                    response = f"{command.split()[0]} BAD Command not implemented\r\n"
                    client_socket.sendall(response.encode())

                    if self.enable_metrics:
                        self.metrics.increment("imap_errors_total")

        except Exception as e:
            self.logger.error(f"Błąd podczas obsługi klienta: {str(e)}")
            if self.enable_metrics:
                self.metrics.increment("imap_errors_total")
        finally:
            client_socket.close()
            with self.connections_lock:
                self.active_connections -= 1
                if self.enable_metrics:
                    self.metrics.set("imap_active_connections", self.active_connections)
            self.logger.info(f"Połączenie z {client_address[0]}:{client_address[1]} zamknięte")

    def start(self):
        """Uruchamia serwer IMAP."""
        try:
            # Utwórz gniazdo serwera
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(self.max_connections)

            self.logger.info(f"Serwer IMAP uruchomiony na {self.host}:{self.port}")

            # Główna pętla serwera
            while True:
                client_socket, client_address = server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client, args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()

        except KeyboardInterrupt:
            self.logger.info("Zatrzymywanie serwera IMAP...")
        except Exception as e:
            self.logger.error(f"Błąd podczas uruchamiania serwera IMAP: {str(e)}")
        finally:
            if "server_socket" in locals():
                server_socket.close()


def main():
    """Funkcja główna serwera IMAP."""
    # Konfiguracja logowania
    log_level = os.environ.get("IMAP_LOG_LEVEL", "INFO")
    configure_logging(level=log_level)

    # Uruchom serwer IMAP
    server = IMAPServer()
    server.start()


if __name__ == "__main__":
    main()
