"""
Klient SSH dla usługi Process.
"""

import os
import sys
import logging
import paramiko
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić import z core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config import load_config
from core.logging import get_logger, configure_logging


class SSHClient:
    """Klient SSH dla usługi Process."""
    
    def __init__(self, host: str = None, port: int = None, 
                 username: str = None, password: str = None, 
                 key_filename: str = None, config: Dict[str, Any] = None):
        """Inicjalizuje klienta SSH.
        
        Args:
            host: Host serwera SSH
            port: Port serwera SSH
            username: Nazwa użytkownika
            password: Hasło (opcjonalne)
            key_filename: Ścieżka do pliku klucza prywatnego (opcjonalne)
            config: Konfiguracja klienta
        """
        self.config = config or load_config("ssh")
        self.logger = get_logger("ssh.client")
        
        # Konfiguracja SSH
        self.host = host or os.environ.get("SSH_HOST", "localhost")
        self.port = port or int(os.environ.get("SSH_PORT", "22"))
        self.username = username or os.environ.get("SSH_USERNAME", "")
        self.password = password or os.environ.get("SSH_PASSWORD", "")
        self.key_filename = key_filename or os.environ.get("SSH_KEY_FILENAME", "")
        self.timeout = int(os.environ.get("SSH_CONNECTION_TIMEOUT", "60"))
        
        self.logger.info(f"Klient SSH zainicjalizowany dla {self.host}:{self.port}")
    
    def connect(self) -> paramiko.SSHClient:
        """Łączy z serwerem SSH.
        
        Returns:
            Obiekt połączenia SSH
        """
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Przygotuj parametry połączenia
            connect_kwargs = {
                "hostname": self.host,
                "port": self.port,
                "username": self.username,
                "timeout": self.timeout
            }
            
            # Dodaj hasło lub klucz, jeśli podano
            if self.password:
                connect_kwargs["password"] = self.password
            
            if self.key_filename:
                connect_kwargs["key_filename"] = self.key_filename
            
            # Połącz z serwerem
            client.connect(**connect_kwargs)
            self.logger.info(f"Połączono z serwerem SSH {self.host}:{self.port}")
            
            return client
        
        except Exception as e:
            self.logger.error(f"Błąd podczas łączenia z serwerem SSH: {str(e)}")
            raise
    
    def execute_command(self, command: str) -> Tuple[int, str, str]:
        """Wykonuje polecenie na serwerze.
        
        Args:
            command: Polecenie do wykonania
        
        Returns:
            Krotka (kod wyjścia, stdout, stderr)
        """
        try:
            client = self.connect()
            
            # Wykonaj polecenie
            self.logger.info(f"Wykonywanie polecenia: {command}")
            stdin, stdout, stderr = client.exec_command(command)
            
            # Pobierz wyniki
            exit_code = stdout.channel.recv_exit_status()
            stdout_str = stdout.read().decode("utf-8")
            stderr_str = stderr.read().decode("utf-8")
            
            # Zamknij połączenie
            client.close()
            
            self.logger.info(f"Polecenie wykonane, kod wyjścia: {exit_code}")
            return exit_code, stdout_str, stderr_str
        
        except Exception as e:
            self.logger.error(f"Błąd podczas wykonywania polecenia: {str(e)}")
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
            client = self.connect()
            
            # Utwórz klienta SFTP
            sftp = client.open_sftp()
            
            # Przygotuj katalogi, jeśli nie istnieją
            remote_dir = os.path.dirname(remote_path)
            try:
                self._mkdir_p(sftp, remote_dir)
            except IOError:
                pass
            
            # Prześlij plik
            self.logger.info(f"Przesyłanie pliku: {local_path} -> {remote_path}")
            sftp.put(local_path, remote_path)
            
            # Zamknij połączenia
            sftp.close()
            client.close()
            
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
            client = self.connect()
            
            # Utwórz klienta SFTP
            sftp = client.open_sftp()
            
            # Przygotuj katalogi lokalne, jeśli nie istnieją
            local_dir = os.path.dirname(local_path)
            os.makedirs(local_dir, exist_ok=True)
            
            # Pobierz plik
            self.logger.info(f"Pobieranie pliku: {remote_path} -> {local_path}")
            sftp.get(remote_path, local_path)
            
            # Zamknij połączenia
            sftp.close()
            client.close()
            
            self.logger.info(f"Plik pobrany pomyślnie")
            return True
        
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania pliku: {str(e)}")
            raise
    
    def list_files(self, remote_path: str) -> List[Dict[str, Any]]:
        """Listuje pliki w katalogu zdalnym.
        
        Args:
            remote_path: Ścieżka zdalna katalogu
        
        Returns:
            Lista plików i katalogów
        """
        try:
            client = self.connect()
            
            # Utwórz klienta SFTP
            sftp = client.open_sftp()
            
            # Listuj pliki
            self.logger.info(f"Listowanie plików w katalogu: {remote_path}")
            file_list = sftp.listdir_attr(remote_path)
            
            # Przygotuj wyniki
            results = []
            for file_attr in file_list:
                is_dir = True if file_attr.st_mode & 0o40000 else False
                results.append({
                    "name": file_attr.filename,
                    "path": os.path.join(remote_path, file_attr.filename),
                    "size": file_attr.st_size,
                    "mtime": file_attr.st_mtime,
                    "is_dir": is_dir
                })
            
            # Zamknij połączenia
            sftp.close()
            client.close()
            
            return results
        
        except Exception as e:
            self.logger.error(f"Błąd podczas listowania plików: {str(e)}")
            raise
    
    def _mkdir_p(self, sftp, remote_dir):
        """Rekurencyjnie tworzy katalogi na serwerze zdalnym (jak mkdir -p).
        
        Args:
            sftp: Obiekt SFTP
            remote_dir: Ścieżka zdalna katalogu
        """
        if remote_dir == '/':
            return
        
        if remote_dir == '':
            return
        
        try:
            sftp.stat(remote_dir)
        except IOError:
            parent = os.path.dirname(remote_dir)
            if parent:
                self._mkdir_p(sftp, parent)
            sftp.mkdir(remote_dir)


def main():
    """Funkcja główna klienta SSH."""
    # Konfiguracja logowania
    log_level = os.environ.get("SSH_LOG_LEVEL", "INFO")
    configure_logging(level=log_level)
    
    # Przykład użycia klienta
    client = SSHClient(
        host=os.environ.get("SSH_HOST", "localhost"),
        port=int(os.environ.get("SSH_PORT", "22")),
        username=os.environ.get("SSH_USERNAME", "user"),
        password=os.environ.get("SSH_PASSWORD", "password")
    )
    
    try:
        # Wykonaj polecenie
        exit_code, stdout, stderr = client.execute_command("ls -la")
        print(f"Kod wyjścia: {exit_code}")
        print(f"Standardowe wyjście:\n{stdout}")
        if stderr:
            print(f"Standardowe wyjście błędów:\n{stderr}")
        
        # Listuj pliki
        files = client.list_files("/home")
        print(f"Pliki w katalogu /home:")
        for file in files:
            print(f"  {file['name']} ({'katalog' if file['is_dir'] else 'plik'}, {file['size']} bajtów)")
    
    except Exception as e:
        print(f"Błąd: {str(e)}")


if __name__ == "__main__":
    main()
