"""
Klient FTP dla usługi Process.
"""

import ftplib
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić import z core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.config import load_config
from core.logging import configure_logging, get_logger
from core.monitoring import HealthCheck


class FTPClient:
    """Klient FTP dla usługi Process."""

    def __init__(
        self,
        host: str = None,
        port: int = None,
        username: str = None,
        password: str = None,
        use_tls: bool = None,
        config: Dict[str, Any] = None,
    ):
        """Inicjalizuje klienta FTP.

        Args:
            host: Host serwera FTP
            port: Port serwera FTP
            username: Nazwa użytkownika
            password: Hasło
            use_tls: Czy używać TLS
            config: Konfiguracja klienta
        """
        self.config = config or load_config("ftp")
        self.logger = get_logger("ftp.client")

        # Konfiguracja FTP
        self.host = host or os.environ.get("FTP_HOST", "localhost")
        self.port = port or int(os.environ.get("FTP_PORT", "21"))
        self.username = username or os.environ.get("FTP_USERNAME", "")
        self.password = password or os.environ.get("FTP_PASSWORD", "")
        self.use_tls = (
            use_tls
            if use_tls is not None
            else os.environ.get("FTP_TLS_ENABLED", "false").lower() == "true"
        )
        self.timeout = int(os.environ.get("FTP_TIMEOUT", "30"))

        # Konfiguracja health check
        self.health_check = HealthCheck(
            service_name="ftp",
            check_interval=int(os.environ.get("FTP_HEALTH_CHECK_INTERVAL", "30")),
            timeout=int(os.environ.get("FTP_HEALTH_CHECK_TIMEOUT", "5")),
        )
        self.health_check.register_check("ftp_connection", self._health_check_connection)

        self.logger.info(f"Klient FTP zainicjalizowany dla {self.host}:{self.port}")

    def _health_check_connection(self) -> Dict[str, Any]:
        """Sprawdza połączenie z serwerem FTP.

        Returns:
            Słownik ze statusem health check
        """
        try:
            conn = self.connect()
            conn.quit()

            return {"status": "healthy", "details": {"server": f"{self.host}:{self.port}"}}
        except Exception as e:
            return {
                "status": "unhealthy",
                "details": {"error": str(e), "server": f"{self.host}:{self.port}"},
            }

    def connect(self) -> Union[ftplib.FTP, ftplib.FTP_TLS]:
        """Łączy z serwerem FTP.

        Returns:
            Obiekt połączenia FTP
        """
        try:
            # Utwórz odpowiedni obiekt FTP
            if self.use_tls:
                conn = ftplib.FTP_TLS(timeout=self.timeout)
            else:
                conn = ftplib.FTP(timeout=self.timeout)

            # Połącz z serwerem
            conn.connect(self.host, self.port)

            # Zaloguj się
            if self.username:
                conn.login(self.username, self.password)
            else:
                conn.login()

            # Włącz TLS, jeśli wymagane
            if self.use_tls and isinstance(conn, ftplib.FTP_TLS):
                conn.prot_p()

            self.logger.info(f"Połączono z serwerem FTP {self.host}:{self.port}")
            return conn

        except Exception as e:
            self.logger.error(f"Błąd podczas łączenia z serwerem FTP: {str(e)}")
            raise

    def list_files(self, remote_path: str = "/") -> List[Dict[str, Any]]:
        """Listuje pliki w katalogu zdalnym.

        Args:
            remote_path: Ścieżka zdalna katalogu

        Returns:
            Lista plików i katalogów
        """
        try:
            conn = self.connect()

            # Pobierz listę plików
            files = []

            def process_line(line):
                parts = line.split()
                if len(parts) >= 9:
                    # Typowy format: "drwxr-xr-x 2 user group 4096 Jan 1 12:34 filename"
                    permissions = parts[0]
                    is_dir = permissions.startswith("d")
                    size = int(parts[4])
                    filename = " ".join(parts[8:])

                    files.append(
                        {
                            "name": filename,
                            "path": os.path.join(remote_path, filename),
                            "size": size,
                            "is_dir": is_dir,
                            "permissions": permissions,
                        }
                    )

            conn.cwd(remote_path)
            conn.retrlines("LIST", process_line)
            conn.quit()

            self.logger.info(f"Pobrano listę {len(files)} plików z {remote_path}")
            return files

        except Exception as e:
            self.logger.error(f"Błąd podczas listowania plików: {str(e)}")
            raise

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Przesyła plik na serwer.

        Args:
            local_path: Ścieżka lokalna pliku
            remote_path: Ścieżka zdalna pliku

        Returns:
            True, jeśli operacja się powiodła
        """
        try:
            conn = self.connect()

            # Przygotuj katalogi, jeśli nie istnieją
            remote_dir = os.path.dirname(remote_path)
            if remote_dir:
                self._make_dirs(conn, remote_dir)

            # Prześlij plik
            with open(local_path, "rb") as file:
                self.logger.info(f"Przesyłanie pliku: {local_path} -> {remote_path}")
                conn.storbinary(f"STOR {remote_path}", file)

            conn.quit()
            self.logger.info(f"Plik przesłany pomyślnie")
            return True

        except Exception as e:
            self.logger.error(f"Błąd podczas przesyłania pliku: {str(e)}")
            raise

    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Pobiera plik z serwera.

        Args:
            remote_path: Ścieżka zdalna pliku
            local_path: Ścieżka lokalna pliku

        Returns:
            True, jeśli operacja się powiodła
        """
        try:
            conn = self.connect()

            # Przygotuj katalogi lokalne, jeśli nie istnieją
            local_dir = os.path.dirname(local_path)
            os.makedirs(local_dir, exist_ok=True)

            # Pobierz plik
            with open(local_path, "wb") as file:
                self.logger.info(f"Pobieranie pliku: {remote_path} -> {local_path}")
                conn.retrbinary(f"RETR {remote_path}", file.write)

            conn.quit()
            self.logger.info(f"Plik pobrany pomyślnie")
            return True

        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania pliku: {str(e)}")
            raise

    def delete_file(self, remote_path: str) -> bool:
        """Usuwa plik z serwera.

        Args:
            remote_path: Ścieżka zdalna pliku

        Returns:
            True, jeśli operacja się powiodła
        """
        try:
            conn = self.connect()

            # Usuń plik
            self.logger.info(f"Usuwanie pliku: {remote_path}")
            conn.delete(remote_path)

            conn.quit()
            self.logger.info(f"Plik usunięty pomyślnie")
            return True

        except Exception as e:
            self.logger.error(f"Błąd podczas usuwania pliku: {str(e)}")
            raise

    def create_directory(self, remote_path: str) -> bool:
        """Tworzy katalog na serwerze.

        Args:
            remote_path: Ścieżka zdalna katalogu

        Returns:
            True, jeśli operacja się powiodła
        """
        try:
            conn = self.connect()

            # Utwórz katalog
            self.logger.info(f"Tworzenie katalogu: {remote_path}")
            self._make_dirs(conn, remote_path)

            conn.quit()
            self.logger.info(f"Katalog utworzony pomyślnie")
            return True

        except Exception as e:
            self.logger.error(f"Błąd podczas tworzenia katalogu: {str(e)}")
            raise

    def _make_dirs(self, conn: Union[ftplib.FTP, ftplib.FTP_TLS], remote_path: str):
        """Tworzy katalogi rekurencyjnie.

        Args:
            conn: Połączenie FTP
            remote_path: Ścieżka zdalna katalogu
        """
        if remote_path == "/" or remote_path == "":
            return

        # Podziel ścieżkę na części
        parts = remote_path.split("/")
        current_path = ""

        for part in parts:
            if not part:
                continue

            current_path += "/" + part

            try:
                # Sprawdź, czy katalog istnieje
                conn.cwd(current_path)
            except ftplib.error_perm:
                # Katalog nie istnieje, utwórz go
                conn.mkd(current_path)

    def health(self) -> Dict[str, Any]:
        """Zwraca status zdrowia usługi.

        Returns:
            Słownik ze statusem zdrowia
        """
        return self.health_check.get_status()


def main():
    """Funkcja główna klienta FTP."""
    # Konfiguracja logowania
    log_level = os.environ.get("FTP_LOG_LEVEL", "INFO")
    configure_logging(level=log_level)

    # Przykład użycia klienta
    client = FTPClient(
        host=os.environ.get("FTP_HOST", "localhost"),
        port=int(os.environ.get("FTP_PORT", "21")),
        username=os.environ.get("FTP_USERNAME", "user"),
        password=os.environ.get("FTP_PASSWORD", "password"),
        use_tls=os.environ.get("FTP_TLS_ENABLED", "false").lower() == "true",
    )

    try:
        # Sprawdź status zdrowia
        health_status = client.health()
        print(f"Status zdrowia: {health_status}")

        # Listuj pliki
        files = client.list_files("/")
        print(f"Pliki w katalogu root:")
        for file in files:
            print(
                f"  {file['name']} ({'katalog' if file['is_dir'] else 'plik'}, {file['size']} bajtów)"
            )

        # Przykład przesyłania pliku
        # client.upload_file("local.txt", "/remote/path/remote.txt")

        # Przykład pobierania pliku
        # client.download_file("/remote/path/remote.txt", "downloaded.txt")

    except Exception as e:
        print(f"Błąd: {str(e)}")


if __name__ == "__main__":
    main()
