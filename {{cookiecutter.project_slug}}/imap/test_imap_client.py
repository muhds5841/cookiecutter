"""
Testy klienta IMAP dla usługi Process.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

import pytest

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić import z imap
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from imap.client import IMAPClient


class TestIMAPClient(unittest.TestCase):
    """Testy klienta IMAP."""

    @patch("imap.client.load_config")
    @patch("imap.client.get_logger")
    @patch("imap.client.MetricsCollector")
    @patch("imap.client.HealthCheck")
    def setUp(self, mock_health_check, mock_metrics, mock_logger, mock_load_config):
        """Przygotowanie środowiska testowego."""
        # Mockowanie zależności
        self.mock_load_config = mock_load_config
        self.mock_logger = mock_logger
        self.mock_metrics = mock_metrics
        self.mock_health_check = mock_health_check

        # Mockowanie instancji
        self.mock_metrics_instance = MagicMock()
        self.mock_health_check_instance = MagicMock()
        mock_metrics.return_value = self.mock_metrics_instance
        mock_health_check.return_value = self.mock_health_check_instance

        # Ustawienie zmiennych środowiskowych dla testów
        self.env_vars = {
            "IMAP_HOST": "test.example.com",
            "IMAP_PORT": "143",
            "IMAP_SSL_PORT": "993",
            "IMAP_USERNAME": "testuser",
            "IMAP_PASSWORD": "testpass",
            "IMAP_USE_SSL": "true",
            "IMAP_DEFAULT_FOLDER": "INBOX",
            "IMAP_ATTACHMENT_DIR": "./test_attachments",
            "IMAP_ENABLE_METRICS": "true",
            "IMAP_METRICS_PORT": "9101",
            "IMAP_HEALTH_CHECK_INTERVAL": "30",
            "IMAP_HEALTH_CHECK_TIMEOUT": "5",
        }

        # Inicjalizacja klienta IMAP
        with patch.dict(os.environ, self.env_vars):
            self.client = IMAPClient()

    def test_init(self):
        """Test inicjalizacji klienta IMAP."""
        # Sprawdzenie, czy konfiguracja została załadowana
        self.mock_load_config.assert_called_once_with("imap")

        # Sprawdzenie, czy logger został skonfigurowany
        self.mock_logger.assert_called_once_with("imap.client")

        # Sprawdzenie, czy metryki zostały zarejestrowane
        self.assertEqual(self.mock_metrics.call_count, 1)
        self.assertEqual(self.mock_metrics_instance.register_counter.call_count, 3)
        self.assertEqual(self.mock_metrics_instance.register_gauge.call_count, 1)
        self.assertEqual(self.mock_metrics_instance.register_histogram.call_count, 1)

        # Sprawdzenie, czy health check został zarejestrowany
        self.assertEqual(self.mock_health_check.call_count, 1)
        self.assertEqual(self.mock_health_check_instance.register_check.call_count, 1)

        # Sprawdzenie, czy parametry zostały poprawnie ustawione
        self.assertEqual(self.client.host, "test.example.com")
        self.assertEqual(self.client.port, 993)  # SSL port, bo use_ssl=True
        self.assertEqual(self.client.username, "testuser")
        self.assertEqual(self.client.password, "testpass")
        self.assertTrue(self.client.use_ssl)
        self.assertEqual(self.client.default_folder, "INBOX")
        self.assertEqual(self.client.attachment_dir, "./test_attachments")

    @patch("imaplib.IMAP4_SSL")
    @patch("imaplib.IMAP4")
    def test_connect_ssl(self, mock_imap4, mock_imap4_ssl):
        """Test połączenia z serwerem IMAP przez SSL."""
        # Mockowanie odpowiedzi z serwera
        mock_connection = MagicMock()
        mock_imap4_ssl.return_value = mock_connection
        mock_connection.login.return_value = ("OK", [b"Login successful"])

        # Wywołanie metody connect
        result = self.client.connect()

        # Sprawdzenie, czy IMAP4_SSL został wywołany z poprawnymi parametrami
        mock_imap4_ssl.assert_called_once_with(self.client.host, self.client.port)

        # Sprawdzenie, czy IMAP4 nie został wywołany
        mock_imap4.assert_not_called()

        # Sprawdzenie, czy login został wywołany z poprawnymi parametrami
        mock_connection.login.assert_called_once_with(self.client.username, self.client.password)

        # Sprawdzenie wyniku
        self.assertEqual(result, mock_connection)

    @patch("imaplib.IMAP4_SSL")
    @patch("imaplib.IMAP4")
    def test_connect_no_ssl(self, mock_imap4, mock_imap4_ssl):
        """Test połączenia z serwerem IMAP bez SSL."""
        # Zmiana konfiguracji na połączenie bez SSL
        self.client.use_ssl = False
        self.client.port = 143

        # Mockowanie odpowiedzi z serwera
        mock_connection = MagicMock()
        mock_imap4.return_value = mock_connection
        mock_connection.login.return_value = ("OK", [b"Login successful"])

        # Wywołanie metody connect
        result = self.client.connect()

        # Sprawdzenie, czy IMAP4 został wywołany z poprawnymi parametrami
        mock_imap4.assert_called_once_with(self.client.host, self.client.port)

        # Sprawdzenie, czy IMAP4_SSL nie został wywołany
        mock_imap4_ssl.assert_not_called()

        # Sprawdzenie, czy login został wywołany z poprawnymi parametrami
        mock_connection.login.assert_called_once_with(self.client.username, self.client.password)

        # Sprawdzenie wyniku
        self.assertEqual(result, mock_connection)

    @patch.object(IMAPClient, "connect")
    def test_get_folders(self, mock_connect):
        """Test pobierania listy folderów."""
        # Mockowanie połączenia i odpowiedzi z serwera
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.list.return_value = (
            "OK",
            [
                b'(\\HasNoChildren) "/" "INBOX"',
                b'(\\HasNoChildren) "/" "Sent"',
                b'(\\HasNoChildren) "/" "Drafts"',
            ],
        )

        # Wywołanie metody get_folders
        result = self.client.get_folders()

        # Sprawdzenie, czy connect został wywołany
        mock_connect.assert_called_once()

        # Sprawdzenie, czy list został wywołany
        mock_connection.list.assert_called_once()

        # Sprawdzenie, czy logout został wywołany
        mock_connection.logout.assert_called_once()

        # Sprawdzenie wyniku
        self.assertEqual(len(result), 3)
        self.assertIn("INBOX", result)
        self.assertIn("Sent", result)
        self.assertIn("Drafts", result)

    def test_health(self):
        """Test metody health."""
        # Mockowanie odpowiedzi z health check
        self.mock_health_check_instance.get_status.return_value = {
            "status": "healthy",
            "checks": {"imap_connection": {"status": "healthy"}},
        }

        # Wywołanie metody health
        result = self.client.health()

        # Sprawdzenie, czy get_status został wywołany
        self.mock_health_check_instance.get_status.assert_called_once()

        # Sprawdzenie wyniku
        self.assertEqual(result["status"], "healthy")
        self.assertEqual(result["checks"]["imap_connection"]["status"], "healthy")


if __name__ == "__main__":
    unittest.main()
