"""
Serwer FTP dla usługi Process.
"""

import logging
import os
import socket
import sys
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić import z process i core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

from core.config import load_config
from core.logging import configure_logging, get_logger
from core.monitoring import HealthCheck, MetricsCollector, create_health_endpoint
from process.process import Process


class ProcessFTPHandler(FTPHandler):
    """Handler FTP z integracją z Process."""

    def on_file_received(self, file):
        """Obsługuje zdarzenie otrzymania pliku.

        Args:
            file: Ścieżka do otrzymanego pliku
        """
        # Pobierz instancję serwera
        server = self.server.ftp_server

        # Pobierz względną ścieżkę pliku
        rel_path = os.path.relpath(file, server.root_dir)

        # Loguj zdarzenie
        server.logger.info(f"Otrzymano plik: {rel_path}")

        # Inkrementuj licznik
        if server.enable_metrics:
            server.metrics.increment("ftp_files_received_total")

        # Sprawdź, czy plik powinien być przetworzony
        if server.auto_process and file.endswith(server.process_extensions):
            server.logger.info(f"Automatyczne przetwarzanie pliku: {rel_path}")

            try:
                # Odczytaj zawartość pliku
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Przetwórz zawartość
                result = server.process.process_text(content)

                # Zapisz wynik
                output_file = f"{file}.processed"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(result.data)

                server.logger.info(f"Plik przetworzony pomyślnie: {rel_path}")

                # Inkrementuj licznik
                if server.enable_metrics:
                    server.metrics.increment("ftp_files_processed_total")

            except Exception as e:
                server.logger.error(f"Błąd podczas przetwarzania pliku {rel_path}: {str(e)}")

                # Inkrementuj licznik błędów
                if server.enable_metrics:
                    server.metrics.increment("ftp_processing_errors_total")

    def on_file_sent(self, file):
        """Obsługuje zdarzenie wysłania pliku.

        Args:
            file: Ścieżka do wysłanego pliku
        """
        # Pobierz instancję serwera
        server = self.server.ftp_server

        # Pobierz względną ścieżkę pliku
        rel_path = os.path.relpath(file, server.root_dir)

        # Loguj zdarzenie
        server.logger.info(f"Wysłano plik: {rel_path}")

        # Inkrementuj licznik
        if server.enable_metrics:
            server.metrics.increment("ftp_files_sent_total")


class FTPServer:
    """Serwer FTP dla usługi Process."""

    def __init__(self, config: Dict[str, Any] = None):
        """Inicjalizuje serwer FTP.

        Args:
            config: Konfiguracja serwera
        """
        self.config = config or load_config("ftp")
        self.logger = get_logger("ftp.server")
        self.process = Process()

        # Konfiguracja FTP
        self.host = os.environ.get("FTP_HOST", "0.0.0.0")
        self.port = int(os.environ.get("FTP_PORT", "21"))
        self.root_dir = os.environ.get("FTP_ROOT_DIR", "./ftp_root")
        self.passive_ports = os.environ.get("FTP_PASSIVE_PORTS", "60000-60100")
        self.max_connections = int(os.environ.get("FTP_MAX_CONNECTIONS", "10"))
        self.timeout = int(os.environ.get("FTP_TIMEOUT", "300"))
        self.max_login_attempts = int(os.environ.get("FTP_MAX_LOGIN_ATTEMPTS", "3"))
        self.banner = os.environ.get("FTP_BANNER", "Welcome to Process FTP Server")
        self.anonymous_enabled = os.environ.get("FTP_ANONYMOUS_ENABLED", "false").lower() == "true"
        self.tls_enabled = os.environ.get("FTP_TLS_ENABLED", "false").lower() == "true"
        self.tls_cert_file = os.environ.get("FTP_TLS_CERT_FILE", "./certs/ftpd.crt")
        self.tls_key_file = os.environ.get("FTP_TLS_KEY_FILE", "./certs/ftpd.key")
        self.user_db_file = os.environ.get("FTP_USER_DB_FILE", "./ftpusers.db")
        self.default_umask = int(os.environ.get("FTP_DEFAULT_UMASK", "022"), 8)

        # Konfiguracja automatycznego przetwarzania
        self.auto_process = os.environ.get("FTP_AUTO_PROCESS", "false").lower() == "true"
        self.process_extensions = tuple(
            os.environ.get("FTP_PROCESS_EXTENSIONS", ".txt,.md").split(",")
        )

        # Konfiguracja monitorowania
        self.enable_metrics = os.environ.get("FTP_ENABLE_METRICS", "true").lower() == "true"
        if self.enable_metrics:
            self.metrics = MetricsCollector(
                service_name="ftp", metrics_port=int(os.environ.get("FTP_METRICS_PORT", "9102"))
            )
            self.metrics.register_counter(
                "ftp_connections_total", "Total number of FTP connections"
            )
            self.metrics.register_counter(
                "ftp_files_received_total", "Total number of files received"
            )
            self.metrics.register_counter("ftp_files_sent_total", "Total number of files sent")
            self.metrics.register_counter(
                "ftp_files_processed_total", "Total number of files processed"
            )
            self.metrics.register_counter(
                "ftp_processing_errors_total", "Total number of processing errors"
            )
            self.metrics.register_gauge(
                "ftp_active_connections", "Number of active FTP connections"
            )

        # Konfiguracja health check
        self.health_check = HealthCheck(
            service_name="ftp",
            check_interval=int(os.environ.get("FTP_HEALTH_CHECK_INTERVAL", "30")),
            timeout=int(os.environ.get("FTP_HEALTH_CHECK_TIMEOUT", "5")),
        )
        self.health_check.register_check("ftp_server", self._health_check_server)
        self.health_check.register_check("process_connection", self._health_check_process)

        # Uruchom serwer HTTP dla health check
        self.health_server = create_health_endpoint(
            service_name="ftp",
            health_check=self.health_check,
            port=int(os.environ.get("FTP_HEALTH_PORT", "8081")),
        )

        # Utwórz katalog główny, jeśli nie istnieje
        Path(self.root_dir).mkdir(parents=True, exist_ok=True)

        # Przygotuj zakres portów pasywnych
        if "-" in self.passive_ports:
            start, end = self.passive_ports.split("-")
            self.passive_ports_range = (int(start), int(end))
        else:
            self.passive_ports_range = None

        self.logger.info(f"Serwer FTP zainicjalizowany na {self.host}:{self.port}")

    def _health_check_server(self) -> Dict[str, Any]:
        """Sprawdza stan serwera FTP.

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

            # Sprawdź, czy katalog główny istnieje i jest dostępny
            if not os.path.isdir(self.root_dir):
                return {
                    "status": "unhealthy",
                    "details": {
                        "error": f"Katalog główny {self.root_dir} nie istnieje",
                        "server": f"{self.host}:{self.port}",
                    },
                }

            # Sprawdź, czy katalog główny jest zapisywalny
            test_file = os.path.join(self.root_dir, ".health_check")
            try:
                with open(test_file, "w") as f:
                    f.write("health check")
                os.remove(test_file)
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "details": {
                        "error": f"Katalog główny {self.root_dir} nie jest zapisywalny: {str(e)}",
                        "server": f"{self.host}:{self.port}",
                    },
                }

            return {
                "status": "healthy",
                "details": {"server": f"{self.host}:{self.port}", "root_dir": self.root_dir},
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

    def start(self):
        """Uruchamia serwer FTP."""
        try:
            # Utwórz autoryzator
            authorizer = DummyAuthorizer()

            # Dodaj użytkowników
            if self.anonymous_enabled:
                authorizer.add_anonymous(self.root_dir)

            # Dodaj użytkownika z pliku konfiguracyjnego
            username = os.environ.get("FTP_USERNAME", "user")
            password = os.environ.get("FTP_PASSWORD", "password")
            if username and password:
                authorizer.add_user(username, password, self.root_dir, perm="elradfmwMT")

            # Utwórz handler
            handler = ProcessFTPHandler
            handler.authorizer = authorizer
            handler.banner = self.banner
            handler.timeout = self.timeout
            handler.passive_ports = self.passive_ports_range

            # Włącz TLS, jeśli wymagane
            if self.tls_enabled:
                try:
                    import ssl

                    handler.tls_control_required = True
                    handler.tls_data_required = True
                    handler.certfile = self.tls_cert_file
                    handler.keyfile = self.tls_key_file
                except ImportError:
                    self.logger.error("Moduł ssl nie jest dostępny, TLS zostanie wyłączone")

            # Utwórz serwer
            server = FTPServer((self.host, self.port), handler)
            server.max_cons = self.max_connections
            server.max_cons_per_ip = 5

            # Dodaj referencję do serwera FTP
            server.ftp_server = self

            self.logger.info(f"Serwer FTP uruchomiony na {self.host}:{self.port}")

            # Uruchom serwer
            server.serve_forever()

        except KeyboardInterrupt:
            self.logger.info("Zatrzymywanie serwera FTP...")
        except Exception as e:
            self.logger.error(f"Błąd podczas uruchamiania serwera FTP: {str(e)}")


def main():
    """Funkcja główna serwera FTP."""
    # Konfiguracja logowania
    log_level = os.environ.get("FTP_LOG_LEVEL", "INFO")
    configure_logging(level=log_level)

    # Uruchom serwer FTP
    server = FTPServer()
    server.start()


if __name__ == "__main__":
    main()
