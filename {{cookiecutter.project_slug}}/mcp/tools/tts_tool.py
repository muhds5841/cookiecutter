"""Implementacja narzędzia TTS dla MCP."""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Dodajemy katalog główny projektu do ścieżki importu
sys.path.append(str(Path(__file__).parent.parent.parent))

from tts_engine.tts_engine import TTSEngine


class TTSTool:
    """Narzędzie TTS zgodne z protokołem MCP."""

    def __init__(self, name: str, description: str, tts_engine: TTSEngine):
        """
        Inicjalizuje narzędzie TTS.

        Args:
            name: Nazwa narzędzia
            description: Opis narzędzia
            tts_engine: Silnik TTS
        """
        self.name = name
        self.description = description
        self.tts_engine = tts_engine

    def get_schema(self) -> Dict[str, Any]:
        """
        Zwraca schemat narzędzia.

        Returns:
            Schemat narzędzia w formacie MCP
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Tekst do konwersji na mowę"
                    },
                    "voice": {
                        "type": "string",
                        "description": "Identyfikator głosu",
                        "default": "default"
                    },
                    "language": {
                        "type": "string",
                        "description": "Kod języka",
                        "default": "en-US"
                    }
                },
                "required": ["text"]
            },
            "returns": {
                "type": "object",
                "properties": {
                    "audio_url": {
                        "type": "string",
                        "description": "URL do wygenerowanego pliku audio"
                    }
                }
            }
        }

    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Wykonuje konwersję tekstu na mowę.

        Args:
            parameters: Parametry dla narzędzia

        Returns:
            Wynik działania narzędzia
        """
        text = parameters.get("text", "")
        voice_config = {
            "voice": parameters.get("voice", "default"),
            "language": parameters.get("language", "en-US")
        }

        # Wykonanie syntezy mowy
        audio_data = self.tts_engine.synthesize(text, voice_config)

        # W prawdziwej implementacji tutaj byłoby zapisywanie pliku audio
        # i zwracanie URL, ale dla uproszczenia zwracamy tylko placeholder
        return {
            "audio_url": f"audio://generated/{hash(text)}.mp3"
        }


class TTSToolProvider:
    """Dostawca narzędzi TTS dla MCP."""

    def __init__(self, config: Dict[str, Any]):
        """
        Inicjalizuje dostawcę narzędzi TTS.

        Args:
            config: Konfiguracja dostawcy
        """
        self.config = config
        # Inicjalizacja silnika TTS
        from tts_engine.tts_engine import DefaultTTSEngine
        self.tts_engine = DefaultTTSEngine(config)

    def get_tools(self) -> List[TTSTool]:
        """
        Zwraca listę dostępnych narzędzi TTS.

        Returns:
            Lista narzędzi TTS
        """
        return [
            TTSTool(
                name="text_to_speech",
                description="Konwertuje tekst na mowę",
                tts_engine=self.tts_engine
            )
        ]