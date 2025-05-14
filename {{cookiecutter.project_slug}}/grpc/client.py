"""
Klient gRPC dla usługi Process.
"""

import os
import sys
import grpc
import argparse
from typing import Dict, Any, Optional, List

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić import z lib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.config import load_config
from lib.logging import get_logger, configure_logging

# Importy wygenerowane z proto (będą dostępne po wygenerowaniu kodu z proto)
# from proto.generated import process_pb2, process_pb2_grpc

# Tymczasowa implementacja klas protobuf do czasu wygenerowania ich z pliku .proto
class ProcessRequest:
    def __init__(self, text="", language="", resource="", output_format="wav"):
        self.text = text
        self.language = language
        self.resource = resource
        self.output_format = output_format

class EmptyRequest:
    pass


class TtsClient:
    """Klient gRPC dla usługi Text-to-Speech."""
    
    def __init__(self, host: str = "localhost", port: int = 50051):
        """Inicjalizuje klienta gRPC.
        
        Args:
            host: Adres hosta serwera gRPC
            port: Port serwera gRPC
        """
        self.logger = get_logger("grpc.client")
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        
        # Utwórz stub klienta
        # self.stub = tts_pb2_grpc.TtsServiceStub(self.channel)
        
        self.logger.info(f"Klient gRPC połączony z {host}:{port}")
    
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
        
        # Utwórz żądanie
        request = TtsRequest(
            text=text,
            language=language or "",
            voice=voice or "",
            format=format
        )
        
        try:
            # Wywołaj metodę zdalną
            # response = self.stub.Synthesize(request)
            
            # Tymczasowa implementacja do czasu wygenerowania kodu z proto
            response = type('obj', (object,), {
                'audio_id': 'sample-audio-id',
                'format': format,
                'base64': 'sample-base64-data'
            })
            
            return {
                "audio_id": response.audio_id,
                "format": response.format,
                "base64": response.base64
            }
        except grpc.RpcError as e:
            self.logger.error(f"Błąd gRPC podczas syntezy: {e.code()}: {e.details()}")
            raise
        except Exception as e:
            self.logger.error(f"Błąd podczas syntezy: {str(e)}")
            raise
    
    def get_voices(self) -> List[Dict[str, Any]]:
        """Pobiera listę dostępnych głosów.
        
        Returns:
            Lista dostępnych głosów z metadanymi
        """
        self.logger.info("Pobieranie dostępnych głosów...")
        
        try:
            # Wywołaj metodę zdalną
            # response = self.stub.GetVoices(EmptyRequest())
            
            # Tymczasowa implementacja do czasu wygenerowania kodu z proto
            response = type('obj', (object,), {
                'voices': [
                    type('obj', (object,), {'name': 'default', 'language': 'en-US', 'gender': 'female'}),
                    type('obj', (object,), {'name': 'male1', 'language': 'en-US', 'gender': 'male'}),
                    type('obj', (object,), {'name': 'female1', 'language': 'pl-PL', 'gender': 'female'})
                ]
            })
            
            return [
                {
                    "name": voice.name,
                    "language": voice.language,
                    "gender": voice.gender
                }
                for voice in response.voices
            ]
        except grpc.RpcError as e:
            self.logger.error(f"Błąd gRPC podczas pobierania głosów: {e.code()}: {e.details()}")
            raise
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania głosów: {str(e)}")
            raise
    
    def get_languages(self) -> List[str]:
        """Pobiera listę dostępnych języków.
        
        Returns:
            Lista kodów języków
        """
        self.logger.info("Pobieranie dostępnych języków...")
        
        try:
            # Wywołaj metodę zdalną
            # response = self.stub.GetLanguages(EmptyRequest())
            
            # Tymczasowa implementacja do czasu wygenerowania kodu z proto
            response = type('obj', (object,), {
                'languages': ['en-US', 'pl-PL', 'de-DE', 'fr-FR', 'es-ES']
            })
            
            return response.languages
        except grpc.RpcError as e:
            self.logger.error(f"Błąd gRPC podczas pobierania języków: {e.code()}: {e.details()}")
            raise
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania języków: {str(e)}")
            raise
    
    def close(self):
        """Zamyka połączenie z serwerem gRPC."""
        self.channel.close()
        self.logger.info("Połączenie gRPC zamknięte")


def main():
    """Funkcja główna klienta gRPC."""
    # Parsowanie argumentów wiersza poleceń
    parser = argparse.ArgumentParser(description="Klient gRPC dla usługi Text-to-Speech")
    parser.add_argument("--host", default="localhost", help="Adres hosta serwera gRPC")
    parser.add_argument("--port", type=int, default=50051, help="Port serwera gRPC")
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
        level=config.get("GRPC_CLIENT_LOG_LEVEL", "info"),
        component_name="grpc_client"
    )
    
    # Utwórz klienta gRPC
    client = TtsClient(host=args.host, port=args.port)
    
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
                import base64
                
                with open(args.output, "wb") as f:
                    f.write(base64.b64decode(result["base64"]))
                
                print(f"Zapisano audio do pliku: {args.output}")
        
        else:
            parser.print_help()
    
    finally:
        # Zamknij połączenie
        client.close()


if __name__ == "__main__":
    main()
