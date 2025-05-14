"""
Testy dla modułu konfiguracyjnego.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić import z core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.config import Config, load_config


class TestConfig(unittest.TestCase):
    """Testy dla klasy Config."""

    def setUp(self):
        """Przygotowanie środowiska testowego."""
        # Tworzymy tymczasowy katalog konfiguracyjny
        self.temp_dir = Path("temp_config")
        self.temp_dir.mkdir(exist_ok=True)

        # Tworzymy tymczasowy plik konfiguracyjny
        self.config_file = self.temp_dir / "config.json"
        with open(self.config_file, "w") as f:
            f.write('{"TEST_KEY": "test_value", "NESTED": {"KEY": "value"}}')

        # Tworzymy obiekt konfiguracji
        self.config = Config(config_dir=self.temp_dir)

    def tearDown(self):
        """Czyszczenie po testach."""
        # Usuwamy tymczasowy plik konfiguracyjny
        if self.config_file.exists():
            self.config_file.unlink()

        # Usuwamy tymczasowy katalog
        if self.temp_dir.exists():
            self.temp_dir.rmdir()

    def test_init(self):
        """Test inicjalizacji obiektu Config."""
        self.assertEqual(self.config.config_dir, self.temp_dir)
        self.assertEqual(self.config.config, {})

    def test_load_from_file(self):
        """Test ładowania konfiguracji z pliku."""
        self.config.load_from_file(self.config_file)
        self.assertEqual(self.config.get("TEST_KEY"), "test_value")
        self.assertEqual(self.config.get("NESTED.KEY"), "value")

    @patch.dict(os.environ, {"PREFIX_TEST": "env_value", "OTHER_VAR": "other_value"})
    def test_load_from_env(self):
        """Test ładowania konfiguracji ze zmiennych środowiskowych."""
        self.config.load_from_env(prefix="PREFIX_")
        self.assertEqual(self.config.get("TEST"), "env_value")
        self.assertIsNone(self.config.get("OTHER_VAR"))

    def test_get(self):
        """Test pobierania wartości z konfiguracji."""
        self.config.config = {"KEY": "value", "NESTED": {"DEEP": {"DEEPER": "nested_value"}}}

        self.assertEqual(self.config.get("KEY"), "value")
        self.assertEqual(self.config.get("NESTED.DEEP.DEEPER"), "nested_value")
        self.assertEqual(self.config.get("NON_EXISTENT", "default"), "default")
        self.assertIsNone(self.config.get("NON_EXISTENT"))

    def test_set(self):
        """Test ustawiania wartości w konfiguracji."""
        self.config.set("NEW_KEY", "new_value")
        self.assertEqual(self.config.get("NEW_KEY"), "new_value")

        self.config.set("NESTED.NEW", "nested_value")
        self.assertEqual(self.config.get("NESTED.NEW"), "nested_value")


class TestLoadConfig(unittest.TestCase):
    """Testy dla funkcji load_config."""

    @patch("core.config.Config")
    def test_load_config(self, mock_config):
        """Test funkcji load_config."""
        # Przygotowanie mocka
        mock_instance = MagicMock()
        mock_config.return_value = mock_instance

        # Wywołanie funkcji
        result = load_config(config_dir="test_dir", env_prefix="TEST_")

        # Sprawdzenie, czy Config został utworzony z odpowiednimi parametrami
        mock_config.assert_called_once_with(config_dir="test_dir")

        # Sprawdzenie, czy metody zostały wywołane
        mock_instance.load_from_env.assert_called_once_with(prefix="TEST_")
        self.assertTrue(mock_instance.load_from_file.called)

        # Sprawdzenie wyniku
        self.assertEqual(result, mock_instance)


if __name__ == "__main__":
    unittest.main()
