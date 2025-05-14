"""Implementacja procesu konwersji tekstu na mowę (Text-to-Speech)."""

import os
import uuid
import base64
from typing import Dict, Any, Optional, List, Protocol, Union
from pathlib import Path

from lib.config import load_config
from lib.logging import get_logger
from lib.utils import generate_id, create_temp_file


class Engine(Protocol):
    """Protokół dla silnika Text-to-Speech."""

    def synthesize(self, text: str, voice_config: Optional[Dict[str, Any]] = None) -> bytes:
        """
        Konwertuje tekst na mowę.

        Args:
            text: Tekst do konwersji
            voice_config: Konfiguracja głosu

        Returns:
            Dane audio w formacie bytes
        """
        ...

    def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Pobiera listę dostępnych głosów.

        Returns:
            Lista dostępnych głosów z metadanymi
        """
        ...
        
    def get_available_languages(self) -> List[str]:
        """
        Pobiera listę dostępnych języków.

        Returns:
            Lista kodów języków (np. 'en-US', 'pl-PL')
        """
        ...


class AudioResult:
    """Klasa reprezentująca wynik syntezy mowy."""

    def __init__(self, audio_data: bytes, format: str = "wav", sample_rate: int = 22050):
        """
        Inicjalizuje wynik syntezy mowy.

        Args:
            audio_data: Dane audio w formacie bytes
            format: Format audio (wav, mp3, etc.)
            sample_rate: Częstotliwość próbkowania
        """
        self.id = generate_id("audio-")
        self.audio_data = audio_data
        self.format = format
        self.sample_rate = sample_rate
        self._file_path = None

    def save_to_file(self, directory: Optional[Union[str, Path]] = None) -> str:
        """
        Zapisuje dane audio do pliku.

        Args:
            directory: Katalog, w którym ma być zapisany plik

        Returns:
            Ścieżka do zapisanego pliku
        """
        if directory:
            os.makedirs(directory, exist_ok=True)
            file_path = os.path.join(directory, f"{self.id}.{self.format}")
        else:
            file_path = create_temp_file(self.audio_data, suffix=f".{self.format}")

        if not isinstance(file_path, str):
            file_path = str(file_path)

        with open(file_path, "wb") as f:
            f.write(self.audio_data)

        self._file_path = file_path
        return file_path

    def get_base64(self) -> str:
        """
        Zwraca dane audio jako string base64.

        Returns:
            Dane audio zakodowane w base64
        """
        return base64.b64encode(self.audio_data).decode("utf-8")

    def get_file_path(self) -> Optional[str]:
        """
        Zwraca ścieżkę do pliku, jeśli został zapisany.

        Returns:
            Ścieżka do pliku lub None, jeśli plik nie został zapisany
        """
        return self._file_path

    def __str__(self) -> str:
        return f"AudioResult(id={self.id}, format={self.format}, size={len(self.audio_data)} bytes)"


class DefaultEngine:
    """Domyślna implementacja silnika Text-to-Speech."""

    def __init__(self, config: Dict[str, Any]):
        """Inicjalizuje silnik Text-to-Speech.

        Args:
            config: Konfiguracja silnika
        """
        self.config = config
        self.logger = get_logger("process.tts")
        self.logger.info("Inicjalizacja domyślnego silnika TTS")

    def synthesize(self, text: str, voice_config: Optional[Dict[str, Any]] = None) -> bytes:
        """Konwertuje tekst na mowę.

        Args:
            text: Tekst do konwersji
            voice_config: Konfiguracja głosu

        Returns:
            Dane audio w formacie bytes
        """
        if voice_config is None:
            voice_config = {}

        language = voice_config.get("language", self.config.get("TTS_LANGUAGE", "en-US"))
        voice = voice_config.get("voice", self.config.get("TTS_VOICE", "default"))

        self.logger.info(f"Synteza tekstu: '{text}' (język: {language}, głos: {voice})")

        # W rzeczywistej implementacji tutaj byłoby wywołanie silnika TTS
        # Na potrzeby przykładu zwracamy przykładowe dane audio
        return b"SAMPLE_AUDIO_DATA"

    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Pobiera listę dostępnych głosów.

        Returns:
            Lista dostępnych głosów z metadanymi
        """
        return [
            {"name": "default", "language": "en-US", "gender": "female"},
            {"name": "male1", "language": "en-US", "gender": "male"},
            {"name": "female1", "language": "pl-PL", "gender": "female"}
        ]

    def get_available_languages(self) -> List[str]:
        """Pobiera listę dostępnych języków.

        Returns:
            Lista kodów języków (np. 'en-US', 'pl-PL')
        """
        return ["en-US", "pl-PL", "de-DE", "fr-FR", "es-ES"]


class Process:
    """Główna klasa procesu Text-to-Speech."""

    def __init__(self):
        """Inicjalizuje proces Text-to-Speech."""
        self.config = load_config()
        self.logger = get_logger("process")
        self.engine = self._create_engine()

    def _create_engine(self) -> Engine:
        """Tworzy silnik Text-to-Speech na podstawie konfiguracji.

        Returns:
            Instancja silnika Text-to-Speech
        """
        engine_type = self.config.get("TTS_ENGINE", "default")
        self.logger.info(f"Tworzenie silnika TTS typu: {engine_type}")

        # W rzeczywistej implementacji tutaj byłoby ładowanie odpowiedniego adaptera
        # Na potrzeby przykładu zawsze zwracamy domyślny silnik
        return DefaultEngine(self.config.as_dict())

    @staticmethod
    def get_parameters_schema() -> Dict[str, Any]:
        """Zwraca schemat parametrów procesu.

        Returns:
            Schemat parametrów w formacie JSON Schema
        """
        return {
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
        }

    @staticmethod
    def get_returns_schema() -> Dict[str, Any]:
        """Zwraca schemat wyników procesu.

        Returns:
            Schemat wyników w formacie JSON Schema
        """
        return {
            "type": "object",
            "properties": {
                "audio_id": {
                    "type": "string",
                    "description": "Identyfikator wygenerowanego audio"
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

    def run(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Uruchamia proces konwersji tekstu na mowę.

        Args:
            parameters: Parametry procesu

        Returns:
            Wynik procesu
        """
        self.logger.info(f"Uruchamianie procesu TTS z parametrami: {parameters}")

        text = parameters.get("text", "")
        if not text:
            raise ValueError("Parametr 'text' jest wymagany")

        voice_config = {
            "language": parameters.get("language"),
            "voice": parameters.get("voice"),
            "format": parameters.get("format", "wav")
        }

        # Usuń None z konfiguracji
        voice_config = {k: v for k, v in voice_config.items() if v is not None}

        # Synteza mowy
        audio_data = self.engine.synthesize(text, voice_config)
        audio_format = voice_config.get("format", "wav")

        # Utworzenie wyniku
        result = AudioResult(audio_data, format=audio_format)
        self.logger.info(f"Wygenerowano audio: {result}")

        # Zwróć wynik
        return {
            "audio_id": result.id,
            "format": result.format,
            "base64": result.get_base64()
        }

    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Pobiera listę dostępnych głosów.

        Returns:
            Lista dostępnych głosów z metadanymi
        """
        return self.engine.get_available_voices()

    def get_available_languages(self) -> List[str]:
        """Pobiera listę dostępnych języków.

        Returns:
            Lista kodów języków
        """
        return self.engine.get_available_languages()


class DefaultProcess(Process):
    """Domyślna implementacja procesu Text-to-Speech."""
    pass