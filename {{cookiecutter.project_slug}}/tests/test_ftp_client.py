"""
Testy klienta FTP dla usługi Process.
"""

import os
import sys
import ftplib
import pytest
import unittest
from unittest.mock import patch, MagicMock, call

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić import z ftp
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ftp.client import FTPClient


class TestFTPClient(unittest.TestCase):
    """Testy klienta FTP."""
    
    def setUp(self):
        """Przygotowanie środowiska testowego."""
        # Patch dla FTP
        self.ftp_patcher = patch('ftp.client.ftplib.FTP')
        self.mock_ftp = self.ftp_patcher.start()
        
        # Mockowanie instancji FTP
        self.mock_ftp_instance = MagicMock()
        self.mock_ftp.return_value = self.mock_ftp_instance
        
        # Patch dla FTP_TLS
        self.ftp_tls_patcher = patch('ftp.client.ftplib.FTP_TLS')
        self.mock_ftp_tls = self.ftp_tls_patcher.start()
        
        # Mockowanie instancji FTP_TLS
        self.mock_ftp_tls_instance = MagicMock()
        self.mock_ftp_tls.return_value = self.mock_ftp_tls_instance
        
        # Patch dla HealthCheck
        self.health_check_patcher = patch('ftp.client.HealthCheck')
        self.mock_health_check = self.health_check_patcher.start()
        
        # Mockowanie instancji HealthCheck
        self.mock_health_check_instance = MagicMock()
        self.mock_health_check.return_value = self.mock_health_check_instance
        
        # Inicjalizacja klienta FTP
        self.client = FTPClient(
            host="ftp.example.com",
            port=21,
            username="user",
            password="password",
            use_tls=False
        )
    
    def tearDown(self):
        """Czyszczenie po testach."""
        self.ftp_patcher.stop()
        self.ftp_tls_patcher.stop()
        self.health_check_patcher.stop()
    
    def test_init(self):
        """Test inicjalizacji klienta."""
        # Sprawdź, czy klient został skonfigurowany
        self.assertEqual(self.client.host, "ftp.example.com")
        self.assertEqual(self.client.port, 21)
        self.assertEqual(self.client.username, "user")
        self.assertEqual(self.client.password, "password")
        self.assertEqual(self.client.use_tls, False)
        
        # Sprawdź, czy HealthCheck został zainicjalizowany
        self.mock_health_check.assert_called_once()
        self.mock_health_check_instance.register_check.assert_called_once_with(
            "ftp_connection", self.client._health_check_connection
        )
    
    def test_connect(self):
        """Test łączenia z serwerem FTP."""
        # Wywołaj metodę connect
        conn = self.client.connect()
        
        # Sprawdź, czy FTP został utworzony
        self.mock_ftp.assert_called_once()
        
        # Sprawdź, czy połączenie zostało nawiązane
        self.mock_ftp_instance.connect.assert_called_once_with("ftp.example.com", 21)
        
        # Sprawdź, czy logowanie zostało wykonane
        self.mock_ftp_instance.login.assert_called_once_with("user", "password")
        
        # Sprawdź, czy zwrócono poprawne połączenie
        self.assertEqual(conn, self.mock_ftp_instance)
    
    def test_connect_tls(self):
        """Test łączenia z serwerem FTP z TLS."""
        # Zmień konfigurację klienta
        self.client.use_tls = True
        
        # Wywołaj metodę connect
        conn = self.client.connect()
        
        # Sprawdź, czy FTP_TLS został utworzony
        self.mock_ftp_tls.assert_called_once()
        
        # Sprawdź, czy połączenie zostało nawiązane
        self.mock_ftp_tls_instance.connect.assert_called_once_with("ftp.example.com", 21)
        
        # Sprawdź, czy logowanie zostało wykonane
        self.mock_ftp_tls_instance.login.assert_called_once_with("user", "password")
        
        # Sprawdź, czy TLS został włączony
        self.mock_ftp_tls_instance.prot_p.assert_called_once()
        
        # Sprawdź, czy zwrócono poprawne połączenie
        self.assertEqual(conn, self.mock_ftp_tls_instance)
    
    def test_list_files(self):
        """Test listowania plików."""
        # Mockowanie metody retrlines
        def retrlines_side_effect(cmd, callback):
            # Symuluj odpowiedź LIST
            callback("drwxr-xr-x 2 user group 4096 Jan 1 12:34 dir1")
            callback("-rw-r--r-- 1 user group 1024 Jan 1 12:34 file1.txt")
        
        self.mock_ftp_instance.retrlines = MagicMock(side_effect=retrlines_side_effect)
        
        # Wywołaj metodę list_files
        files = self.client.list_files("/test")
        
        # Sprawdź, czy połączenie zostało nawiązane
        self.mock_ftp.assert_called_once()
        
        # Sprawdź, czy zmieniono katalog
        self.mock_ftp_instance.cwd.assert_called_once_with("/test")
        
        # Sprawdź, czy wywołano retrlines
        self.mock_ftp_instance.retrlines.assert_called_once_with('LIST', self.mock_ftp_instance.retrlines.call_args[0][1])
        
        # Sprawdź, czy zwrócono poprawną listę plików
        self.assertEqual(len(files), 2)
        self.assertEqual(files[0]["name"], "dir1")
        self.assertEqual(files[0]["path"], "/test/dir1")
        self.assertEqual(files[0]["size"], 4096)
        self.assertEqual(files[0]["is_dir"], True)
        self.assertEqual(files[0]["permissions"], "drwxr-xr-x")
        
        self.assertEqual(files[1]["name"], "file1.txt")
        self.assertEqual(files[1]["path"], "/test/file1.txt")
        self.assertEqual(files[1]["size"], 1024)
        self.assertEqual(files[1]["is_dir"], False)
        self.assertEqual(files[1]["permissions"], "-rw-r--r--")
    
    def test_upload_file(self):
        """Test przesyłania pliku."""
        # Mockowanie open
        mock_file = MagicMock()
        mock_open = MagicMock(return_value=mock_file)
        
        with patch('builtins.open', mock_open):
            # Wywołaj metodę upload_file
            result = self.client.upload_file("local.txt", "/remote/path/remote.txt")
        
        # Sprawdź, czy połączenie zostało nawiązane
        self.mock_ftp.assert_called_once()
        
        # Sprawdź, czy utworzono katalogi
        self.mock_ftp_instance.cwd.assert_called_with("/remote/path")
        
        # Sprawdź, czy otwarto plik
        mock_open.assert_called_once_with("local.txt", "rb")
        
        # Sprawdź, czy przesłano plik
        self.mock_ftp_instance.storbinary.assert_called_once_with("STOR /remote/path/remote.txt", mock_file)
        
        # Sprawdź, czy zwrócono True
        self.assertTrue(result)
    
    def test_download_file(self):
        """Test pobierania pliku."""
        # Mockowanie open
        mock_file = MagicMock()
        mock_open = MagicMock(return_value=mock_file)
        
        # Mockowanie os.makedirs
        with patch('builtins.open', mock_open), patch('os.makedirs') as mock_makedirs:
            # Wywołaj metodę download_file
            result = self.client.download_file("/remote/path/remote.txt", "local.txt")
        
        # Sprawdź, czy połączenie zostało nawiązane
        self.mock_ftp.assert_called_once()
        
        # Sprawdź, czy utworzono katalogi lokalne
        mock_makedirs.assert_called_once_with("", exist_ok=True)
        
        # Sprawdź, czy otwarto plik
        mock_open.assert_called_once_with("local.txt", "wb")
        
        # Sprawdź, czy pobrano plik
        self.mock_ftp_instance.retrbinary.assert_called_once_with("RETR /remote/path/remote.txt", mock_file.write)
        
        # Sprawdź, czy zwrócono True
        self.assertTrue(result)
    
    def test_delete_file(self):
        """Test usuwania pliku."""
        # Wywołaj metodę delete_file
        result = self.client.delete_file("/remote/path/remote.txt")
        
        # Sprawdź, czy połączenie zostało nawiązane
        self.mock_ftp.assert_called_once()
        
        # Sprawdź, czy usunięto plik
        self.mock_ftp_instance.delete.assert_called_once_with("/remote/path/remote.txt")
        
        # Sprawdź, czy zwrócono True
        self.assertTrue(result)
    
    def test_create_directory(self):
        """Test tworzenia katalogu."""
        # Wywołaj metodę create_directory
        result = self.client.create_directory("/remote/path/dir")
        
        # Sprawdź, czy połączenie zostało nawiązane
        self.mock_ftp.assert_called_once()
        
        # Sprawdź, czy utworzono katalogi
        self.mock_ftp_instance.cwd.assert_called()
        
        # Sprawdź, czy zwrócono True
        self.assertTrue(result)
    
    def test_health(self):
        """Test sprawdzania stanu zdrowia."""
        # Mockowanie get_status
        self.mock_health_check_instance.get_status.return_value = {
            "status": "healthy",
            "checks": {
                "ftp_connection": {
                    "status": "healthy",
                    "details": {
                        "server": "ftp.example.com:21"
                    }
                }
            }
        }
        
        # Wywołaj metodę health
        health = self.client.health()
        
        # Sprawdź, czy get_status został wywołany
        self.mock_health_check_instance.get_status.assert_called_once()
        
        # Sprawdź, czy zwrócono poprawny status
        self.assertEqual(health["status"], "healthy")
        self.assertEqual(health["checks"]["ftp_connection"]["status"], "healthy")
        self.assertEqual(health["checks"]["ftp_connection"]["details"]["server"], "ftp.example.com:21")
    
    def test_health_check_connection(self):
        """Test health check połączenia."""
        # Mockowanie connect i quit
        self.client.connect = MagicMock()
        self.client.connect.return_value = self.mock_ftp_instance
        
        # Wywołaj metodę _health_check_connection
        result = self.client._health_check_connection()
        
        # Sprawdź, czy connect został wywołany
        self.client.connect.assert_called_once()
        
        # Sprawdź, czy quit został wywołany
        self.mock_ftp_instance.quit.assert_called_once()
        
        # Sprawdź, czy zwrócono poprawny status
        self.assertEqual(result["status"], "healthy")
        self.assertEqual(result["details"]["server"], "ftp.example.com:21")
    
    def test_health_check_connection_error(self):
        """Test health check połączenia z błędem."""
        # Mockowanie connect z błędem
        self.client.connect = MagicMock(side_effect=Exception("Connection error"))
        
        # Wywołaj metodę _health_check_connection
        result = self.client._health_check_connection()
        
        # Sprawdź, czy connect został wywołany
        self.client.connect.assert_called_once()
        
        # Sprawdź, czy zwrócono poprawny status
        self.assertEqual(result["status"], "unhealthy")
        self.assertEqual(result["details"]["error"], "Connection error")
        self.assertEqual(result["details"]["server"], "ftp.example.com:21")


if __name__ == '__main__':
    unittest.main()
