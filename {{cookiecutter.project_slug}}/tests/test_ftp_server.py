"""
Testy serwera FTP dla usługi Process.
"""

import os
import sys
import socket
import pytest
import unittest
from unittest.mock import patch, MagicMock, call

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić import z ftp
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ftp.server import FTPServer, ProcessFTPHandler


class TestFTPServer(unittest.TestCase):
    """Testy serwera FTP."""
    
    def setUp(self):
        """Przygotowanie środowiska testowego."""
        # Patch dla FTPServer
        self.ftp_server_patcher = patch('ftp.server.FTPServer')
        self.mock_ftp_server = self.ftp_server_patcher.start()
        
        # Mockowanie instancji FTPServer
        self.mock_ftp_server_instance = MagicMock()
        self.mock_ftp_server.return_value = self.mock_ftp_server_instance
        
        # Patch dla Process
        self.process_patcher = patch('ftp.server.Process')
        self.mock_process = self.process_patcher.start()
        
        # Mockowanie instancji Process
        self.mock_process_instance = MagicMock()
        self.mock_process.return_value = self.mock_process_instance
        
        # Patch dla HealthCheck
        self.health_check_patcher = patch('ftp.server.HealthCheck')
        self.mock_health_check = self.health_check_patcher.start()
        
        # Mockowanie instancji HealthCheck
        self.mock_health_check_instance = MagicMock()
        self.mock_health_check.return_value = self.mock_health_check_instance
        
        # Patch dla MetricsCollector
        self.metrics_collector_patcher = patch('ftp.server.MetricsCollector')
        self.mock_metrics_collector = self.metrics_collector_patcher.start()
        
        # Mockowanie instancji MetricsCollector
        self.mock_metrics_collector_instance = MagicMock()
        self.mock_metrics_collector.return_value = self.mock_metrics_collector_instance
        
        # Patch dla create_health_endpoint
        self.create_health_endpoint_patcher = patch('ftp.server.create_health_endpoint')
        self.mock_create_health_endpoint = self.create_health_endpoint_patcher.start()
        
        # Patch dla Path.mkdir
        self.path_mkdir_patcher = patch('ftp.server.Path.mkdir')
        self.mock_path_mkdir = self.path_mkdir_patcher.start()
        
        # Patch dla DummyAuthorizer
        self.dummy_authorizer_patcher = patch('ftp.server.DummyAuthorizer')
        self.mock_dummy_authorizer = self.dummy_authorizer_patcher.start()
        
        # Mockowanie instancji DummyAuthorizer
        self.mock_dummy_authorizer_instance = MagicMock()
        self.mock_dummy_authorizer.return_value = self.mock_dummy_authorizer_instance
        
        # Inicjalizacja serwera FTP
        self.server = FTPServer()
    
    def tearDown(self):
        """Czyszczenie po testach."""
        self.ftp_server_patcher.stop()
        self.process_patcher.stop()
        self.health_check_patcher.stop()
        self.metrics_collector_patcher.stop()
        self.create_health_endpoint_patcher.stop()
        self.path_mkdir_patcher.stop()
        self.dummy_authorizer_patcher.stop()
    
    def test_init(self):
        """Test inicjalizacji serwera."""
        # Sprawdź, czy Process został zainicjalizowany
        self.mock_process.assert_called_once()
        
        # Sprawdź, czy HealthCheck został zainicjalizowany
        self.mock_health_check.assert_called_once()
        
        # Sprawdź, czy zarejestrowano health check
        self.mock_health_check_instance.register_check.assert_has_calls([
            call("ftp_server", self.server._health_check_server),
            call("process_connection", self.server._health_check_process)
        ])
        
        # Sprawdź, czy utworzono endpoint health check
        self.mock_create_health_endpoint.assert_called_once()
        
        # Sprawdź, czy utworzono katalog główny
        self.mock_path_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    
    def test_init_with_metrics(self):
        """Test inicjalizacji serwera z metrykami."""
        # Sprawdź, czy MetricsCollector został zainicjalizowany
        self.mock_metrics_collector.assert_called_once()
        
        # Sprawdź, czy zarejestrowano metryki
        self.mock_metrics_collector_instance.register_counter.assert_has_calls([
            call("ftp_connections_total", "Total number of FTP connections"),
            call("ftp_files_received_total", "Total number of files received"),
            call("ftp_files_sent_total", "Total number of files sent"),
            call("ftp_files_processed_total", "Total number of files processed"),
            call("ftp_processing_errors_total", "Total number of processing errors")
        ])
        
        self.mock_metrics_collector_instance.register_gauge.assert_called_once_with(
            "ftp_active_connections", "Number of active FTP connections"
        )
    
    @patch('ftp.server.socket.socket')
    def test_health_check_server(self, mock_socket):
        """Test health check serwera."""
        # Mockowanie socket
        mock_socket_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_socket_instance
        mock_socket_instance.connect_ex.return_value = 0
        
        # Mockowanie os.path.isdir
        with patch('os.path.isdir', return_value=True), \
             patch('builtins.open', MagicMock()), \
             patch('os.remove', MagicMock()):
            # Wywołaj metodę _health_check_server
            result = self.server._health_check_server()
        
        # Sprawdź, czy socket został utworzony
        mock_socket.assert_called_once()
        
        # Sprawdź, czy connect_ex został wywołany
        mock_socket_instance.connect_ex.assert_called_once_with((self.server.host, self.server.port))
        
        # Sprawdź, czy zwrócono poprawny status
        self.assertEqual(result["status"], "healthy")
        self.assertEqual(result["details"]["server"], f"{self.server.host}:{self.server.port}")
        self.assertEqual(result["details"]["root_dir"], self.server.root_dir)
    
    @patch('ftp.server.socket.socket')
    def test_health_check_server_port_closed(self, mock_socket):
        """Test health check serwera z zamkniętym portem."""
        # Mockowanie socket
        mock_socket_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_socket_instance
        mock_socket_instance.connect_ex.return_value = 1
        
        # Wywołaj metodę _health_check_server
        result = self.server._health_check_server()
        
        # Sprawdź, czy socket został utworzony
        mock_socket.assert_called_once()
        
        # Sprawdź, czy connect_ex został wywołany
        mock_socket_instance.connect_ex.assert_called_once_with((self.server.host, self.server.port))
        
        # Sprawdź, czy zwrócono poprawny status
        self.assertEqual(result["status"], "unhealthy")
        self.assertEqual(result["details"]["error"], f"Port {self.server.port} nie jest otwarty")
        self.assertEqual(result["details"]["server"], f"{self.server.host}:{self.server.port}")
    
    def test_health_check_process(self):
        """Test health check połączenia z Process."""
        # Mockowanie get_resources
        self.mock_process_instance.get_resources.return_value = [
            {"id": "resource1", "name": "Resource 1"},
            {"id": "resource2", "name": "Resource 2"}
        ]
        
        # Wywołaj metodę _health_check_process
        result = self.server._health_check_process()
        
        # Sprawdź, czy get_resources został wywołany
        self.mock_process_instance.get_resources.assert_called_once()
        
        # Sprawdź, czy zwrócono poprawny status
        self.assertEqual(result["status"], "healthy")
        self.assertEqual(result["details"]["resources_count"], 2)
        self.assertEqual(result["details"]["process_service"], "available")
    
    def test_health_check_process_error(self):
        """Test health check połączenia z Process z błędem."""
        # Mockowanie get_resources z błędem
        self.mock_process_instance.get_resources.side_effect = Exception("Process error")
        
        # Wywołaj metodę _health_check_process
        result = self.server._health_check_process()
        
        # Sprawdź, czy get_resources został wywołany
        self.mock_process_instance.get_resources.assert_called_once()
        
        # Sprawdź, czy zwrócono poprawny status
        self.assertEqual(result["status"], "unhealthy")
        self.assertEqual(result["details"]["error"], "Process error")
        self.assertEqual(result["details"]["process_service"], "unavailable")
    
    @patch('ftp.server.DummyAuthorizer')
    def test_start(self, mock_authorizer):
        """Test uruchamiania serwera."""
        # Mockowanie authorizer
        mock_authorizer_instance = MagicMock()
        mock_authorizer.return_value = mock_authorizer_instance
        
        # Mockowanie FTPServer
        mock_server = MagicMock()
        with patch('ftp.server.FTPServer', return_value=mock_server), \
             patch('ftp.server.ProcessFTPHandler') as mock_handler:
            # Wywołaj metodę start z KeyboardInterrupt
            mock_server.serve_forever.side_effect = KeyboardInterrupt()
            self.server.start()
        
        # Sprawdź, czy authorizer został utworzony
        mock_authorizer.assert_called_once()
        
        # Sprawdź, czy dodano użytkownika
        mock_authorizer_instance.add_user.assert_called_once()
        
        # Sprawdź, czy utworzono serwer
        mock_server.serve_forever.assert_called_once()


class TestProcessFTPHandler(unittest.TestCase):
    """Testy handlera FTP z integracją z Process."""
    
    def setUp(self):
        """Przygotowanie środowiska testowego."""
        # Utwórz mock serwera
        self.mock_server = MagicMock()
        self.mock_server.root_dir = "/ftp_root"
        self.mock_server.logger = MagicMock()
        self.mock_server.enable_metrics = True
        self.mock_server.metrics = MagicMock()
        self.mock_server.auto_process = True
        self.mock_server.process_extensions = (".txt", ".md")
        self.mock_server.process = MagicMock()
        
        # Utwórz mock instancji serwera
        self.mock_server_instance = MagicMock()
        self.mock_server_instance.ftp_server = self.mock_server
        
        # Utwórz handler
        self.handler = ProcessFTPHandler()
        self.handler.server = self.mock_server_instance
    
    def test_on_file_received(self):
        """Test obsługi zdarzenia otrzymania pliku."""
        # Wywołaj metodę on_file_received
        self.handler.on_file_received("/ftp_root/test.txt")
        
        # Sprawdź, czy zalogowano zdarzenie
        self.mock_server.logger.info.assert_called_with("Otrzymano plik: test.txt")
        
        # Sprawdź, czy inkrementowano licznik
        self.mock_server.metrics.increment.assert_called_with("ftp_files_received_total")
    
    def test_on_file_received_with_processing(self):
        """Test obsługi zdarzenia otrzymania pliku z przetwarzaniem."""
        # Mockowanie open
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = "Przykładowy tekst"
        
        # Mockowanie wyniku przetwarzania
        mock_result = MagicMock()
        mock_result.data = "Przetworzony tekst"
        self.mock_server.process.process_text.return_value = mock_result
        
        with patch('builtins.open', return_value=mock_file):
            # Wywołaj metodę on_file_received
            self.handler.on_file_received("/ftp_root/test.txt")
        
        # Sprawdź, czy zalogowano zdarzenie
        self.mock_server.logger.info.assert_has_calls([
            call("Otrzymano plik: test.txt"),
            call("Automatyczne przetwarzanie pliku: test.txt"),
            call("Plik przetworzony pomyślnie: test.txt")
        ])
        
        # Sprawdź, czy process_text został wywołany
        self.mock_server.process.process_text.assert_called_once_with("Przykładowy tekst")
        
        # Sprawdź, czy inkrementowano liczniki
        self.mock_server.metrics.increment.assert_has_calls([
            call("ftp_files_received_total"),
            call("ftp_files_processed_total")
        ])
    
    def test_on_file_received_with_processing_error(self):
        """Test obsługi zdarzenia otrzymania pliku z błędem przetwarzania."""
        # Mockowanie open
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = "Przykładowy tekst"
        
        # Mockowanie wyniku przetwarzania z błędem
        self.mock_server.process.process_text.side_effect = Exception("Processing error")
        
        with patch('builtins.open', return_value=mock_file):
            # Wywołaj metodę on_file_received
            self.handler.on_file_received("/ftp_root/test.txt")
        
        # Sprawdź, czy zalogowano zdarzenie
        self.mock_server.logger.info.assert_has_calls([
            call("Otrzymano plik: test.txt"),
            call("Automatyczne przetwarzanie pliku: test.txt")
        ])
        
        # Sprawdź, czy zalogowano błąd
        self.mock_server.logger.error.assert_called_once()
        
        # Sprawdź, czy process_text został wywołany
        self.mock_server.process.process_text.assert_called_once_with("Przykładowy tekst")
        
        # Sprawdź, czy inkrementowano liczniki
        self.mock_server.metrics.increment.assert_has_calls([
            call("ftp_files_received_total"),
            call("ftp_processing_errors_total")
        ])
    
    def test_on_file_sent(self):
        """Test obsługi zdarzenia wysłania pliku."""
        # Wywołaj metodę on_file_sent
        self.handler.on_file_sent("/ftp_root/test.txt")
        
        # Sprawdź, czy zalogowano zdarzenie
        self.mock_server.logger.info.assert_called_with("Wysłano plik: test.txt")
        
        # Sprawdź, czy inkrementowano licznik
        self.mock_server.metrics.increment.assert_called_with("ftp_files_sent_total")


if __name__ == '__main__':
    unittest.main()
