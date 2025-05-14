"""Narzędzie Process dla MCP integrujące się z systemem Process."""

import os
import sys
import json
import base64
from typing import Dict, Any, List, Optional, Union, Type
from pathlib import Path

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić import z process i lib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from process.process import Process
from lib.config import load_config
from lib.logging import get_logger


class ProcessTool:
    """Narzędzie Process dla MCP."""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicjalizuje narzędzie Process.
        
        Args:
            config: Konfiguracja narzędzia
        """
        self.config = config
        self.logger = get_logger("mcp.tools.process")
        self.process = Process()
        self.logger.info("Inicjalizacja narzędzia Process dla MCP")
    
    def get_schema(self) -> Dict[str, Any]:
        """Zwraca schemat narzędzia Process dla MCP.
        
        Returns:
            Schemat narzędzia w formacie JSON Schema
        """
        return {
            "name": "process_text",
            "description": "Przetwarza tekst używając silnika Process",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Tekst do przetworzenia"
                    },
                    "language": {
                        "type": "string",
                        "description": "Kod języka (np. 'en-US', 'pl-PL')"
                    },
                    "voice": {
                        "type": "string",
                        "description": "Nazwa głosu do użycia"
                    },
                    "format": {
                        "type": "string",
                        "description": "Format wyjściowy (wav, mp3)",
                        "enum": ["wav", "mp3"]
                    }
                },
                "required": ["text"]
            },
            "returns": {
                "type": "string",
                "description": "Identyfikator URI zasobu"
            }
        }
    
    async def execute(self, parameters: Dict[str, Any]) -> str:
        """Wykonuje przetwarzanie tekstu.
        
        Args:
            parameters: Parametry narzędzia
        
        Returns:
            Identyfikator URI zasobu
        """
        self.logger.info(f"Wykonywanie przetwarzania z parametrami: {parameters}")
        
        try:
            # Wywołaj proces
            result = self.process.run(parameters)
            
            # Utwórz URI zasobu
            resource_uri = f"resource://{result['audio_id']}"
            
            self.logger.info(f"Wygenerowano zasób: {resource_uri}")
            return resource_uri
        
        except Exception as e:
            self.logger.error(f"Błąd podczas przetwarzania: {str(e)}")
            raise


class ResourceProvider:
    """Dostawca zasobów dla MCP."""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicjalizuje dostawcę zasobów.
        
        Args:
            config: Konfiguracja dostawcy
        """
        self.config = config
        self.logger = get_logger("mcp.resources.provider")
        self.process = Process()
        self.logger.info("Inicjalizacja dostawcy zasobów dla MCP")
    
    def get_schema(self) -> Dict[str, Any]:
        """Zwraca schemat zasobów dla MCP.
        
        Returns:
            Schemat zasobów w formacie JSON Schema
        """
        return {
            "uri_template": "resources://",
            "description": "Dostępne zasoby dla przetwarzania",
            "returns": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Nazwa zasobu"
                        },
                        "type": {
                            "type": "string",
                            "description": "Typ zasobu"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Metadane zasobu"
                        }
                    }
                }
            }
        }
    
    async def get_resource(self, uri: str) -> List[Dict[str, Any]]:
        """Pobiera zasób.
        
        Args:
            uri: URI zasobu
        
        Returns:
            Lista dostępnych zasobów z metadanymi
        """
        self.logger.info(f"Pobieranie zasobów dla URI: {uri}")
        
        try:
            # W zależności od URI, pobierz odpowiednie zasoby
            if uri == "resources://voices":
                return self.process.get_available_voices()
            elif uri == "resources://languages":
                return [{"name": lang, "type": "language"} for lang in self.process.get_available_languages()]
            else:
                # Domyślnie zwróć wszystkie dostępne zasoby
                voices = self.process.get_available_voices()
                languages = [{"name": lang, "type": "language"} for lang in self.process.get_available_languages()]
                return voices + languages
        
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania zasobów: {str(e)}")
            raise


class OutputResourceProvider:
    """Dostawca zasobów wyjściowych dla MCP."""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicjalizuje dostawcę zasobów wyjściowych.
        
        Args:
            config: Konfiguracja dostawcy
        """
        self.config = config
        self.logger = get_logger("mcp.resources.output")
        self.resource_cache: Dict[str, Dict[str, Any]] = {}
        self.logger.info("Inicjalizacja dostawcy zasobów wyjściowych dla MCP")
    
    def get_schema(self) -> Dict[str, Any]:
        """Zwraca schemat zasobów wyjściowych dla MCP.
        
        Returns:
            Schemat zasobów w formacie JSON Schema
        """
        return {
            "uri_template": "resource://{resource_id}",
            "description": "Dane wygenerowane przez system Process",
            "returns": {
                "type": "object",
                "properties": {
                    "resource_id": {
                        "type": "string",
                        "description": "Identyfikator zasobu"
                    },
                    "format": {
                        "type": "string",
                        "description": "Format zasobu"
                    },
                    "base64": {
                        "type": "string",
                        "description": "Dane zakodowane w base64"
                    }
                }
            }
        }
    
    def cache_resource(self, resource_id: str, resource_data: Dict[str, Any]) -> None:
        """Zapisuje dane zasobu w pamięci podręcznej.
        
        Args:
            resource_id: Identyfikator zasobu
            resource_data: Dane zasobu
        """
        self.resource_cache[resource_id] = resource_data
        self.logger.info(f"Zapisano zasób w pamięci podręcznej: {resource_id}")
    
    async def get_resource(self, uri: str) -> Dict[str, Any]:
        """Pobiera zasób wyjściowy.
        
        Args:
            uri: URI zasobu
        
        Returns:
            Dane zasobu
        """
        self.logger.info(f"Pobieranie zasobu wyjściowego dla URI: {uri}")
        
        # Wyodrębnij identyfikator zasobu z URI
        if not uri.startswith("resource://"):
            raise ValueError(f"Nieprawidłowy URI zasobu: {uri}")
        
        resource_id = uri[11:]  # Usuń prefiks "resource://"
        
        # Sprawdź, czy zasób jest w pamięci podręcznej
        if resource_id in self.resource_cache:
            self.logger.info(f"Znaleziono zasób w pamięci podręcznej: {resource_id}")
            return self.resource_cache[resource_id]
        
        # W rzeczywistej implementacji tutaj byłoby pobieranie zasobu z bazy danych lub systemu plików
        # Na potrzeby przykładu zwróć błąd
        self.logger.error(f"Nie znaleziono zasobu o ID: {resource_id}")
        raise ValueError(f"Nie znaleziono zasobu o ID: {resource_id}")


class ProcessToolProvider:
    """Dostawca narzędzi Process dla MCP."""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicjalizuje dostawcę narzędzi Process.
        
        Args:
            config: Konfiguracja dostawcy
        """
        self.config = config
        self.logger = get_logger("mcp.tools.provider")
        self.logger.info("Inicjalizacja dostawcy narzędzi Process dla MCP")
        
        # Utwórz narzędzia i dostawców zasobów
        self.process_tool = ProcessTool(config)
        self.resource_provider = ResourceProvider(config)
        self.output_provider = OutputResourceProvider(config)
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Zwraca listę narzędzi dostarczanych przez dostawcę.
        
        Returns:
            Lista narzędzi
        """
        return [self.process_tool.get_schema()]
    
    def get_resource_providers(self) -> List[Dict[str, Any]]:
        """Zwraca listę dostawców zasobów dostarczanych przez dostawcę.
        
        Returns:
            Lista dostawców zasobów
        """
        return [
            self.resource_provider.get_schema(),
            self.output_provider.get_schema()
        ]
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Wykonuje narzędzie o podanej nazwie.
        
        Args:
            tool_name: Nazwa narzędzia
            parameters: Parametry narzędzia
        
        Returns:
            Wynik wykonania narzędzia
        """
        if tool_name == "process_text":
            return await self.process_tool.execute(parameters)
        
        raise ValueError(f"Nieznane narzędzie: {tool_name}")
    
    async def get_resource(self, uri: str) -> Any:
        """Pobiera zasób o podanym URI.
        
        Args:
            uri: URI zasobu
        
        Returns:
            Zasób
        """
        if uri.startswith("resources://"):
            return await self.resource_provider.get_resource(uri)
        
        if uri.startswith("resource://"):
            return await self.output_provider.get_resource(uri)
        
        raise ValueError(f"Nieznany URI zasobu: {uri}")
