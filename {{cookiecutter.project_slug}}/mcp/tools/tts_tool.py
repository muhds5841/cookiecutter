"""Narzędzie TTS dla MCP integrujące się z systemem Process."""

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


class TTSTool:
    """Narzędzie TTS dla MCP."""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicjalizuje narzędzie TTS.
        
        Args:
            config: Konfiguracja narzędzia
        """
        self.config = config
        self.logger = get_logger("mcp.tools.tts")
        self.process = Process()
        self.logger.info("Inicjalizacja narzędzia TTS dla MCP")
    
    def get_schema(self) -> Dict[str, Any]:
        """Zwraca schemat narzędzia TTS dla MCP.
        
        Returns:
            Schemat narzędzia w formacie JSON Schema
        """
        return {
            "name": "synthesize_speech",
            "description": "Konwertuje tekst na mowę używając silnika TTS",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Tekst do konwersji na mowę"
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
                        "description": "Format wyjściowy audio (wav, mp3)",
                        "enum": ["wav", "mp3"]
                    }
                },
                "required": ["text"]
            },
            "returns": {
                "type": "string",
                "description": "Identyfikator URI zasobu audio"
            }
        }
    
    async def execute(self, parameters: Dict[str, Any]) -> str:
        """Wykonuje konwersję tekstu na mowę.
        
        Args:
            parameters: Parametry narzędzia
        
        Returns:
            Identyfikator URI zasobu audio
        """
        self.logger.info(f"Wykonywanie syntezy mowy z parametrami: {parameters}")
        
        try:
            # Wywołaj proces TTS
            result = self.process.run(parameters)
            
            # Utwórz URI zasobu audio
            audio_uri = f"audio://{result['audio_id']}"
            
            self.logger.info(f"Wygenerowano audio: {audio_uri}")
            return audio_uri
        
        except Exception as e:
            self.logger.error(f"Błąd podczas syntezy mowy: {str(e)}")
            raise


class VoiceResourceProvider:
    """Dostawca zasobów głosowych dla MCP."""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicjalizuje dostawcę zasobów głosowych.
        
        Args:
            config: Konfiguracja dostawcy
        """
        self.config = config
        self.logger = get_logger("mcp.resources.voices")
        self.process = Process()
        self.logger.info("Inicjalizacja dostawcy zasobów głosowych dla MCP")
    
    def get_schema(self) -> Dict[str, Any]:
        """Zwraca schemat zasobów głosowych dla MCP.
        
        Returns:
            Schemat zasobów w formacie JSON Schema
        """
        return {
            "uri_template": "voices://",
            "description": "Dostępne głosy dla syntezy mowy",
            "returns": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Nazwa głosu"
                        },
                        "language": {
                            "type": "string",
                            "description": "Kod języka (np. 'en-US', 'pl-PL')"
                        },
                        "gender": {
                            "type": "string",
                            "description": "Płeć głosu (male, female)"
                        }
                    }
                }
            }
        }
    
    async def get_resource(self, uri: str) -> List[Dict[str, Any]]:
        """Pobiera zasob głosów.
        
        Args:
            uri: URI zasobu
        
        Returns:
            Lista dostępnych głosów z metadanymi
        """
        self.logger.info(f"Pobieranie zasobów głosowych dla URI: {uri}")
        
        try:
            # Pobierz dostępne głosy z procesu TTS
            voices = self.process.get_available_voices()
            
            self.logger.info(f"Pobrano {len(voices)} głosów")
            return voices
        
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania głosów: {str(e)}")
            raise


class LanguageResourceProvider:
    """Dostawca zasobów językowych dla MCP."""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicjalizuje dostawcę zasobów językowych.
        
        Args:
            config: Konfiguracja dostawcy
        """
        self.config = config
        self.logger = get_logger("mcp.resources.languages")
        self.process = Process()
        self.logger.info("Inicjalizacja dostawcy zasobów językowych dla MCP")
    
    def get_schema(self) -> Dict[str, Any]:
        """Zwraca schemat zasobów językowych dla MCP.
        
        Returns:
            Schemat zasobów w formacie JSON Schema
        """
        return {
            "uri_template": "languages://",
            "description": "Dostępne języki dla syntezy mowy",
            "returns": {
                "type": "array",
                "items": {
                    "type": "string",
                    "description": "Kod języka (np. 'en-US', 'pl-PL')"
                }
            }
        }
    
    async def get_resource(self, uri: str) -> List[str]:
        """Pobiera zasób języków.
        
        Args:
            uri: URI zasobu
        
        Returns:
            Lista dostępnych języków
        """
        self.logger.info(f"Pobieranie zasobów językowych dla URI: {uri}")
        
        try:
            # Pobierz dostępne języki z procesu TTS
            languages = self.process.get_available_languages()
            
            self.logger.info(f"Pobrano {len(languages)} języków")
            return languages
        
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania języków: {str(e)}")
            raise


class AudioResourceProvider:
    """Dostawca zasobów audio dla MCP."""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicjalizuje dostawcę zasobów audio.
        
        Args:
            config: Konfiguracja dostawcy
        """
        self.config = config
        self.logger = get_logger("mcp.resources.audio")
        self.audio_cache: Dict[str, Dict[str, Any]] = {}
        self.logger.info("Inicjalizacja dostawcy zasobów audio dla MCP")
    
    def get_schema(self) -> Dict[str, Any]:
        """Zwraca schemat zasobów audio dla MCP.
        
        Returns:
            Schemat zasobów w formacie JSON Schema
        """
        return {
            "uri_template": "audio://{audio_id}",
            "description": "Dane audio wygenerowane przez silnik TTS",
            "returns": {
                "type": "object",
                "properties": {
                    "audio_id": {
                        "type": "string",
                        "description": "Identyfikator audio"
                    },
                    "format": {
                        "type": "string",
                        "description": "Format audio (wav, mp3)"
                    },
                    "base64": {
                        "type": "string",
                        "description": "Dane audio zakodowane w base64"
                    }
                }
            }
        }
    
    def cache_audio(self, audio_id: str, audio_data: Dict[str, Any]) -> None:
        """Zapisuje dane audio w pamięci podręcznej.
        
        Args:
            audio_id: Identyfikator audio
            audio_data: Dane audio
        """
        self.audio_cache[audio_id] = audio_data
        self.logger.info(f"Zapisano audio w pamięci podręcznej: {audio_id}")
    
    async def get_resource(self, uri: str) -> Dict[str, Any]:
        """Pobiera zasób audio.
        
        Args:
            uri: URI zasobu
        
        Returns:
            Dane audio
        """
        self.logger.info(f"Pobieranie zasobu audio dla URI: {uri}")
        
        # Wyodrębnij identyfikator audio z URI
        if not uri.startswith("audio://"):
            raise ValueError(f"Nieprawidłowy URI audio: {uri}")
        
        audio_id = uri[8:]  # Usuń prefiks "audio://"
        
        # Sprawdź, czy audio jest w pamięci podręcznej
        if audio_id in self.audio_cache:
            self.logger.info(f"Znaleziono audio w pamięci podręcznej: {audio_id}")
            return self.audio_cache[audio_id]
        
        # W rzeczywistej implementacji tutaj byłoby pobieranie audio z bazy danych lub systemu plików
        # Na potrzeby przykładu zwróć błąd
        self.logger.error(f"Nie znaleziono audio o ID: {audio_id}")
        raise ValueError(f"Nie znaleziono audio o ID: {audio_id}")


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
        self.tts_tool = TTSTool(config)
        self.voice_provider = VoiceResourceProvider(config)
        self.language_provider = LanguageResourceProvider(config)
        self.audio_provider = AudioResourceProvider(config)
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Zwraca listę narzędzi dostarczanych przez dostawcę.
        
        Returns:
            Lista narzędzi
        """
        return [self.tts_tool.get_schema()]
    
    def get_resource_providers(self) -> List[Dict[str, Any]]:
        """Zwraca listę dostawców zasobów dostarczanych przez dostawcę.
        
        Returns:
            Lista dostawców zasobów
        """
        return [
            self.voice_provider.get_schema(),
            self.language_provider.get_schema(),
            self.audio_provider.get_schema()
        ]
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Wykonuje narzędzie o podanej nazwie.
        
        Args:
            tool_name: Nazwa narzędzia
            parameters: Parametry narzędzia
        
        Returns:
            Wynik wykonania narzędzia
        """
        if tool_name == "synthesize_speech":
            return await self.tts_tool.execute(parameters)
        
        raise ValueError(f"Nieznane narzędzie: {tool_name}")
    
    async def get_resource(self, uri: str) -> Any:
        """Pobiera zasób o podanym URI.
        
        Args:
            uri: URI zasobu
        
        Returns:
            Zasób
        """
        if uri.startswith("voices://"):
            return await self.voice_provider.get_resource(uri)
        
        if uri.startswith("languages://"):
            return await self.language_provider.get_resource(uri)
        
        if uri.startswith("audio://"):
            return await self.audio_provider.get_resource(uri)
        
        raise ValueError(f"Nieznany URI zasobu: {uri}")
