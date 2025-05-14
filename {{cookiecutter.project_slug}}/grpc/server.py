"""
Serwer gRPC dla usługi Process.
"""

import os
import sys
import time
from concurrent import futures
from typing import Any, Dict

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić import z process i lib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importy bibliotek zewnętrznych
import grpc

# Importy wewnętrzne
from lib.config import load_config
from lib.logging import configure_logging, get_logger
from process.process import Process

# Importy wygenerowane z proto (będą dostępne po wygenerowaniu kodu z proto)
# from proto.generated import process_pb2, process_pb2_grpc


# Tymczasowa implementacja klas protobuf do czasu wygenerowania ich z pliku .proto
class ProcessRequest:
    def __init__(self, text="", language="", resource="", output_format="wav"):
        self.text = text
        self.language = language
        self.resource = resource
        self.output_format = output_format


class ProcessResponse:
    def __init__(self, result_id="", format="", data="", metadata=None):
        self.result_id = result_id
        self.format = format
        self.data = data
        self.metadata = metadata or {}


class ResourceInfo:
    def __init__(self, id="", name="", type="", metadata=None):
        self.id = id
        self.name = name
        self.type = type
        self.metadata = metadata or {}


class ResourcesResponse:
    def __init__(self, resources=None):
        self.resources = resources or []


class LanguagesResponse:
    def __init__(self, languages=None):
        self.languages = languages or []


class EmptyRequest:
    pass


# Tymczasowa implementacja klas protobuf do czasu wygenerowania ich z pliku .proto
class TtsRequest:
    """Klasa reprezentująca żądanie syntezy mowy."""
    def __init__(self, text="", language="", voice="", format="wav"):
        self.text = text
        self.language = language
        self.voice = voice
        self.format = format


class TtsResponse:
    """Klasa reprezentująca odpowiedź syntezy mowy."""
    def __init__(self, audio_id="", format="", base64="", error=""):
        self.audio_id = audio_id
        self.format = format
        self.base64 = base64
        self.error = error


class VoiceInfo:
    """Klasa reprezentująca informacje o głosie."""
    def __init__(self, name="", language="", gender=""):
        self.name = name
        self.language = language
        self.gender = gender


class VoicesResponse:
    """Klasa reprezentująca odpowiedź z listą dostępnych głosów."""
    def __init__(self, voices=None):
        self.voices = voices or []


# Tymczasowa implementacja serwisu gRPC do czasu wygenerowania kodu z proto
class ProcessServiceServicer:
    """Implementacja serwisu TTS dla gRPC.
    
    Klasa implementuje metody serwisu gRPC dla systemu TTS, umożliwiając
    konwersję tekstu na mowę oraz pobieranie informacji o dostępnych głosach i językach.
    """

    def __init__(self, process: Process):
        """Inicjalizuje serwis gRPC.
        
        Args:
            process: Instancja silnika Process do przetwarzania żądań.
        """
        self.process = process
        self.logger = get_logger("grpc.server")

    def synthesize(self, request, context):
        """Konwertuje tekst na mowę.
        
        Args:
            request: Żądanie zawierające tekst do konwersji i parametry.
            context: Kontekst gRPC.
            
        Returns:
            Odpowiedź zawierająca dane audio.
        """
        self.logger.info(f"Otrzymano żądanie syntezy: {request.text[:50]}...")

        try:
            parameters = {
                "text": request.text,
                "language": request.language if request.language else None,
                "voice": request.voice if request.voice else None,
                "format": request.format if request.format else "wav",
            }

            result = self.process.run(parameters)

            return TtsResponse(
                audio_id=result["audio_id"], format=result["format"], base64=result["base64"]
            )
        except ValueError as e:
            self.logger.error(f"Błąd walidacji parametrów: {str(e)}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return TtsResponse(error=str(e))
        except KeyError as e:
            self.logger.error(f"Błąd brakującego klucza: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Brakujący klucz w wynikach: {str(e)}")
            return TtsResponse(error=f"Błąd wewnętrzny: {str(e)}")
        except Exception as e:
            self.logger.error(f"Błąd podczas syntezy: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return TtsResponse(error=f"Błąd wewnętrzny: {str(e)}")

    def get_voices(self, request, context):
        """Pobiera listę dostępnych głosów.
        
        Args:
            request: Puste żądanie.
            context: Kontekst gRPC.
            
        Returns:
            Odpowiedź zawierająca listę dostępnych głosów.
        """
        self.logger.info("Otrzymano żądanie pobrania głosów")

        try:
            voices = self.process.get_available_voices()
            voice_infos = []

            for voice in voices:
                voice_infos.append(
                    VoiceInfo(
                        name=voice["name"], language=voice["language"], gender=voice["gender"]
                    )
                )

            return VoicesResponse(voices=voice_infos)
        except AttributeError as e:
            self.logger.error(f"Błąd atrybutu: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Błąd atrybutu: {str(e)}")
            return VoicesResponse()
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania głosów: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return VoicesResponse()

    def get_languages(self, request, context):
        """Pobiera listę dostępnych języków.
        
        Args:
            request: Puste żądanie.
            context: Kontekst gRPC.
            
        Returns:
            Odpowiedź zawierająca listę dostępnych języków.
        """
        self.logger.info("Otrzymano żądanie pobrania języków")

        try:
            languages = self.process.get_available_languages()
            return LanguagesResponse(languages=languages)
        except AttributeError as e:
            self.logger.error(f"Błąd atrybutu: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Błąd atrybutu: {str(e)}")
            return LanguagesResponse()
        except ValueError as e:
            self.logger.error(f"Błąd walidacji: {str(e)}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return LanguagesResponse()
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania języków: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return LanguagesResponse()


def serve():
    """Uruchamia serwer gRPC."""
    # Załaduj konfigurację
    config = load_config()

    # Skonfiguruj logowanie
    logger = configure_logging(
        level=config.get("GRPC_LOG_LEVEL", "info"),
        component_name="grpc",
        log_dir=config.get("GRPC_LOG_DIR"),
    )

    # Utwórz instancję procesu
    process = Process()

    # Utwórz serwer gRPC
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Dodaj usługę TTS do serwera
    # tts_pb2_grpc.add_TtsServiceServicer_to_server(TtsServiceServicer(process), server)

    # Pobierz port z konfiguracji lub użyj domyślnego
    port = config.get("GRPC_PORT", 50051)
    server.add_insecure_port(f"[::]:{port}")

    # Uruchom serwer
    server.start()
    logger.info(f"Serwer gRPC uruchomiony na porcie {port}")

    try:
        # Serwer działa w tle, więc musimy trzymać główny wątek aktywny
        while True:
            time.sleep(86400)  # Jeden dzień w sekundach
    except KeyboardInterrupt:
        logger.info("Zatrzymywanie serwera gRPC...")
        server.stop(0)
        logger.info("Serwer gRPC zatrzymany")


if __name__ == "__main__":
    serve()
