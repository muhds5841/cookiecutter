"""
Klient gRPC dla usługi Process.
"""

import argparse
import base64
import os
import sys
from typing import Any, Dict, List, Optional

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić import z core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importy wewnętrzne - będą dostępne po wygenerowaniu projektu
try:
    from core.config import Config
    from core.logging import configure_logging, get_logger
except ImportError:
    # Fallback dla testów
    Config = object
    configure_logging = lambda *args, **kwargs: None
    get_logger = lambda name: print

# Importy bibliotek zewnętrznych - tylko jeśli grpc jest zainstalowane
try:
    import grpc
except ImportError:
    # Fallback dla przypadku, gdy grpc nie jest zainstalowane
    class grpc:
        class RpcError(Exception):
            def code(self): return "UNAVAILABLE"
            def details(self): return "gRPC nie jest zainstalowane"
        
        @staticmethod
        def insecure_channel(*args, **kwargs):
            return None

# Importy wygenerowane z proto (będą dostępne po wygenerowaniu kodu z proto)
# from proto.generated import process_pb2, process_pb2_grpc


# Tymczasowa implementacja klas protobuf do czasu wygenerowania ich z pliku .proto
class ProcessRequest:
    """Klasa reprezentująca żądanie przetwarzania."""
    def __init__(self, text="", language="", resource="", output_format="wav"):
        self.text = text
        self.language = language
        self.resource = resource
        self.output_format = output_format


class ServiceRequest:
    """Klasa reprezentująca żądanie do serwisu."""
    def __init__(self, text="", language="", voice="", format="wav"):
        self.text = text
        self.language = language
        self.voice = voice
        self.format = format


class EmptyRequest:
    """Klasa reprezentująca puste żądanie."""
    def __init__(self):
        """Inicjalizacja pustego żądania."""
        # Puste żądanie nie ma żadnych parametrów


class ServiceClient:
    """Klient gRPC dla usługi przetwarzania danych."""

    def __init__(self, host: str = "localhost", port: int = 50051):
        """Inicjalizuje klienta gRPC.

        Args:
            host: Adres hosta serwera gRPC
            port: Port serwera gRPC
        """
        self.logger = get_logger("grpc.client")
        self.channel = grpc.insecure_channel(f"{host}:{port}")

        # Utwórz stub klienta
        # self.stub = service_pb2_grpc.ServiceStub(self.channel)

        self.logger.info(f"Klient gRPC połączony z {host}:{port}")

    def process(
        self,
        text: str,
        language: Optional[str] = None,
        voice: Optional[str] = None,
        output_format: str = "wav",
    ) -> Dict[str, Any]:
        """Przetwarza dane wejściowe.

        Args:
            text: Tekst do przetworzenia
            language: Kod języka (np. 'en-US', 'pl-PL')
            voice: Nazwa głosu/zasobu do użycia
            output_format: Format wyjściowy (wav, mp3, json, itp.)

        Returns:
            Słownik z wynikiem przetwarzania
        """
        self.logger.info(f"Wysyłanie żądania przetwarzania: {text[:50]}...")

        # Utwórz żądanie
        service_request = ServiceRequest(text=text, language=language or "", voice=voice or "", format=output_format)

        try:
            # Wywołaj metodę zdalną
            # response = self.stub.Process(service_request)

            # Tymczasowa implementacja do czasu wygenerowania kodu z proto
            response = type(
                "obj",
                (object,),
                {"id": "sample-result-id", "format": output_format, "base64": "sample-base64-data"},
            )

            return {
                "id": response.id,
                "format": response.format,
                "base64": response.base64,
            }
        except grpc.RpcError as e:
            self.logger.error(f"Błąd gRPC podczas syntezy: {e.code()}: {e.details()}")
            raise
        except Exception as e:
            self.logger.error(f"Błąd podczas syntezy: {str(e)}")
            raise

    def get_resources(self) -> List[Dict[str, Any]]:
        """Pobiera listę dostępnych zasobów.

        Returns:
            Lista dostępnych zasobów z metadanymi
        """
        self.logger.info("Pobieranie dostępnych zasobów...")

        try:
            # Wywołaj metodę zdalną
            # response = self.stub.GetResources(EmptyRequest())

            # Tymczasowa implementacja do czasu wygenerowania kodu z proto
            response = type(
                "obj",
                (object,),
                {
                    "resources": [
                        {"id": "resource1", "type": "voice", "language": "en-US", "properties": {"gender": "female"}},
                        {"id": "resource2", "type": "voice", "language": "pl-PL", "properties": {"gender": "male"}},
                        {"id": "resource3", "type": "model", "language": "de-DE", "properties": {"size": "medium"}},
                    ]
                },
            )

            return response.resources
        except grpc.RpcError as e:
            self.logger.error(f"Błąd gRPC podczas pobierania zasobów: {e.code()}: {e.details()}")
            raise
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania zasobów: {str(e)}")
            raise

    def get_formats(self) -> List[str]:
        """Pobiera listę dostępnych formatów wyjściowych.

        Returns:
            Lista dostępnych formatów
        """
        self.logger.info("Pobieranie dostępnych formatów...")

        try:
            # Wywołaj metodę zdalną
            # response = self.stub.GetFormats(EmptyRequest())

            # Tymczasowa implementacja do czasu wygenerowania kodu z proto
            response = type(
                "obj", (object,), {"formats": ["wav", "mp3", "json", "text", "xml"]}
            )

            return response.formats
        except grpc.RpcError as e:
            self.logger.error(f"Błąd gRPC podczas pobierania formatów: {e.code()}: {e.details()}")
            raise
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania formatów: {str(e)}")
            raise

    def close(self):
        """Zamyka połączenie z serwerem gRPC."""
        self.channel.close()
        self.logger.info("Połączenie gRPC zamknięte")


def main():
    """Funkcja główna klienta gRPC."""
    # Parsowanie argumentów wiersza poleceń
    parser = argparse.ArgumentParser(description="Klient gRPC dla usługi przetwarzania danych")
    parser.add_argument("--host", default="localhost", help="Adres hosta serwera gRPC")
    parser.add_argument("--port", type=int, default=50051, help="Port serwera gRPC")
    parser.add_argument("--text", help="Tekst do przetworzenia")
    parser.add_argument("--language", help="Kod języka (np. 'en-US', 'pl-PL')")
    parser.add_argument("--resource", help="Identyfikator zasobu do użycia")
    parser.add_argument(
        "--format", default="wav", choices=["wav", "mp3", "json", "text"], help="Format wyjściowy"
    )
    parser.add_argument("--list-resources", action="store_true", help="Wyświetl dostępne zasoby")
    parser.add_argument("--list-formats", action="store_true", help="Wyświetl dostępne formaty")
    parser.add_argument("--output", help="Ścieżka do pliku wyjściowego")

    args = parser.parse_args()

    # Załaduj konfigurację
    try:
        config = Config.load_from_env()
    except Exception:
        # Fallback dla przypadku, gdy Config nie jest dostępny
        config = {"GRPC_CLIENT_LOG_LEVEL": "info"}

    # Skonfiguruj logowanie
    configure_logging(
        level=config.get("GRPC_CLIENT_LOG_LEVEL", "info"), component_name="grpc_client"
    )

    # Utwórz klienta gRPC
    client = ServiceClient(host=args.host, port=args.port)

    try:
        # Obsłuż żądania
        if args.list_resources:
            resources = client.get_resources()
            print("Dostępne zasoby:")
            for resource in resources:
                print(f"  - {resource['id']} (typ: {resource['type']}, język: {resource['language']})")

        elif args.list_formats:
            formats = client.get_formats()
            print("Dostępne formaty:")
            for format_name in formats:
                print(f"  - {format_name}")

        elif args.text:
            result = client.process(
                text=args.text, language=args.language, voice=args.resource, output_format=args.format
            )

            print(f"Wygenerowano wynik: {result['id']} (format: {result['format']})")

            # Zapisz do pliku, jeśli podano ścieżkę wyjściową
            if args.output:
                with open(args.output, "wb") as f:
                    f.write(base64.b64decode(result["base64"]))

                print(f"Zapisano wynik do pliku: {args.output}")

        else:
            parser.print_help()

    finally:
        # Zamknij połączenie
        client.close()


if __name__ == "__main__":
    main()
