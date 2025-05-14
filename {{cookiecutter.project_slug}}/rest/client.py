"""\nKlient REST dla usługi Process.\n"""

import os
import sys
import json
import base64
import argparse
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić import z lib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from requests.exceptions import RequestException

from lib.config import load_config
from lib.logging import get_logger, configure_logging


class ProcessClient:
    """Klient REST dla usługi Process."""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """Inicjalizuje klienta REST.
        
        Args:
            base_url: Bazowy URL serwera REST
        """
        self.base_url = base_url.rstrip('/')
        self.logger = get_logger("rest.client")
        self.logger.info(f"Klient REST połączony z {base_url}")
    
    def synthesize(self, text: str, language: Optional[str] = None, 
                   voice: Optional[str] = None, format: str = "wav") -> Dict[str, Any]:
        """Konwertuje tekst na mowę.
        
        Args:
            text: Tekst do konwersji
            language: Kod języka (np. 'en-US', 'pl-PL')
            voice: Nazwa głosu do użycia
            format: Format wyjściowy audio (wav, mp3)
        
        Returns:
            Słownik z wynikiem syntezy (audio_id, format, base64)
        """
        self.logger.info(f"Wysyłanie żądania syntezy: {text[:50]}...")
        
        # Przygotuj dane żądania
        payload = {
            "text": text,
            "format": format
        }
        
        # Dodaj opcjonalne parametry
        if language:
            payload["language"] = language
        if voice:
            payload["voice"] = voice
        
        try:
            # Wyślij żądanie POST
            response = requests.post(
                f"{self.base_url}/api/v1/synthesize",
                json=payload
            )
            
            # Sprawdź, czy żądanie zakończyło się sukcesem
            response.raise_for_status()
            
            # Zwróć dane odpowiedzi
            return response.json()
        
        except RequestException as e:
            self.logger.error(f"Błąd podczas syntezy: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Treść odpowiedzi: {e.response.text}")
            raise
    
    def get_voices(self) -> List[Dict[str, Any]]:
        """Pobiera listę dostępnych głosów.
        
        Returns:
            Lista dostępnych głosów z metadanymi
        """
        self.logger.info("Pobieranie dostępnych głosów...")
        
        try:
            # Wyślij żądanie GET
            response = requests.get(f"{self.base_url}/api/v1/voices")
            
            # Sprawdź, czy żądanie zakończyło się sukcesem
            response.raise_for_status()
            
            # Zwróć listę głosów
            return response.json()["voices"]
        
        except RequestException as e:
            self.logger.error(f"Błąd podczas pobierania głosów: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Treść odpowiedzi: {e.response.text}")
            raise
    
    def get_languages(self) -> List[str]:
        """Pobiera listę dostępnych języków.
        
        Returns:
            Lista kodów języków
        """
        self.logger.info("Pobieranie dostępnych języków...")
        
        try:
            # Wyślij żądanie GET
            response = requests.get(f"{self.base_url}/api/v1/languages")
            
            # Sprawdź, czy żądanie zakończyło się sukcesem
            response.raise_for_status()
            
            # Zwróć listę języków
            return response.json()["languages"]
        
        except RequestException as e:
            self.logger.error(f"Błąd podczas pobierania języków: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Treść odpowiedzi: {e.response.text}")
            raise
    
    def download_audio(self, audio_id: str, output_path: Optional[Union[str, Path]] = None) -> str:
        """Pobiera audio na podstawie identyfikatora.
        
        Args:
            audio_id: Identyfikator audio
            output_path: Ścieżka do pliku wyjściowego
        
        Returns:
            Ścieżka do zapisanego pliku audio
        """
        self.logger.info(f"Pobieranie audio o ID: {audio_id}")
        
        try:
            # Wyślij żądanie GET
            response = requests.get(
                f"{self.base_url}/api/v1/audio/{audio_id}",
                stream=True  # Pobieranie strumieniowe
            )
            
            # Sprawdź, czy żądanie zakończyło się sukcesem
            response.raise_for_status()
            
            # Określ ścieżkę wyjściową
            if output_path is None:
                # Pobierz nazwę pliku z nagłówka Content-Disposition
                content_disposition = response.headers.get('Content-Disposition', '')
                filename = None
                
                if 'filename=' in content_disposition:
                    filename = content_disposition.split('filename=')[1].strip('"')
                
                if not filename:
                    filename = f"{audio_id}.wav"
                
                output_path = filename
            
            # Zapisz plik
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.logger.info(f"Zapisano audio do pliku: {output_path}")
            return str(output_path)
        
        except RequestException as e:
            self.logger.error(f"Błąd podczas pobierania audio: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Treść odpowiedzi: {e.response.text}")
            raise


def main():
    """Funkcja główna klienta REST."""
    # Parsowanie argumentów wiersza poleceń
    parser = argparse.ArgumentParser(description="Klient REST dla usługi Text-to-Speech")
    parser.add_argument("--url", default="http://localhost:5000", help="Bazowy URL serwera REST")
    parser.add_argument("--text", help="Tekst do konwersji na mowę")
    parser.add_argument("--language", help="Kod języka (np. 'en-US', 'pl-PL')")
    parser.add_argument("--voice", help="Nazwa głosu do użycia")
    parser.add_argument("--format", default="wav", choices=["wav", "mp3"], help="Format wyjściowy audio")
    parser.add_argument("--list-voices", action="store_true", help="Wyświetl dostępne głosy")
    parser.add_argument("--list-languages", action="store_true", help="Wyświetl dostępne języki")
    parser.add_argument("--output", help="Ścieżka do pliku wyjściowego")
    
    args = parser.parse_args()
    
    # Załaduj konfigurację
    config = load_config()
    
    # Skonfiguruj logowanie
    configure_logging(
        level=config.get("REST_CLIENT_LOG_LEVEL", "info"),
        component_name="rest_client"
    )
    
    # Utwórz klienta REST
    client = TtsClient(base_url=args.url)
    
    try:
        # Obsłuż żądania
        if args.list_voices:
            voices = client.get_voices()
            print("Dostępne głosy:")
            for voice in voices:
                print(f"  - {voice['name']} ({voice['language']}, {voice['gender']})")
        
        elif args.list_languages:
            languages = client.get_languages()
            print("Dostępne języki:")
            for language in languages:
                print(f"  - {language}")
        
        elif args.text:
            result = client.synthesize(
                text=args.text,
                language=args.language,
                voice=args.voice,
                format=args.format
            )
            
            print(f"Wygenerowano audio: {result['audio_id']} (format: {result['format']})")
            
            # Zapisz do pliku, jeśli podano ścieżkę wyjściową
            if args.output:
                with open(args.output, "wb") as f:
                    f.write(base64.b64decode(result["base64"]))
                
                print(f"Zapisano audio do pliku: {args.output}")
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"Błąd: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()