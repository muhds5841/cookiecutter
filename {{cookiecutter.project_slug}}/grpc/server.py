"""
Serwer gRPC dla usługi Text-to-Speech.
"""

import os
import sys
import grpc
import time
from concurrent import futures
from typing import Dict, Any

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić import z process i lib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from process.process import Process
from lib.config import load_config
from lib.logging import get_logger, configure_logging

# Importy wygenerowane z proto (będą dostępne po wygenerowaniu kodu z proto)
# from proto.generated import tts_pb2, tts_pb2_grpc

# Tymczasowa implementacja klas protobuf do czasu wygenerowania ich z pliku .proto
class TtsRequest:
    def __init__(self, text="", language="", voice="", format="wav"):
        self.text = text
        self.language = language
        self.voice = voice
        self.format = format

class TtsResponse:
    def __init__(self, audio_id="", format="", base64=""):
        self.audio_id = audio_id
        self.format = format
        self.base64 = base64

class VoiceInfo:
    def __init__(self, name="", language="", gender=""):
        self.name = name
        self.language = language
        self.gender = gender

class VoicesResponse:
    def __init__(self, voices=None):
        self.voices = voices or []

class LanguagesResponse:
    def __init__(self, languages=None):
        self.languages = languages or []

class EmptyRequest:
    pass

# Tymczasowa implementacja serwisu gRPC do czasu wygenerowania kodu z proto
class TtsServiceServicer:
    """Implementacja serwisu TTS dla gRPC."""
    
    def __init__(self, process: Process):
        self.process = process
        self.logger = get_logger("grpc.server")
    
    def Synthesize(self, request, context):
        """Konwertuje tekst na mowę."""
        self.logger.info(f"Otrzymano żądanie syntezy: {request.text[:50]}...")
        
        try:
            parameters = {
                "text": request.text,
                "language": request.language if request.language else None,
                "voice": request.voice if request.voice else None,
                "format": request.format if request.format else "wav"
            }
            
            result = self.process.run(parameters)
            
            return TtsResponse(
                audio_id=result["audio_id"],
                format=result["format"],
                base64=result["base64"]
            )
        except Exception as e:
            self.logger.error(f"Błąd podczas syntezy: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return TtsResponse()
    
    def GetVoices(self, request, context):
        """Pobiera listę dostępnych głosów."""
        self.logger.info("Otrzymano żądanie pobrania głosów")
        
        try:
            voices = self.process.get_available_voices()
            voice_infos = []
            
            for voice in voices:
                voice_infos.append(VoiceInfo(
                    name=voice["name"],
                    language=voice["language"],
                    gender=voice["gender"]
                ))
            
            return VoicesResponse(voices=voice_infos)
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania głosów: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return VoicesResponse()
    
    def GetLanguages(self, request, context):
        """Pobiera listę dostępnych języków."""
        self.logger.info("Otrzymano żądanie pobrania języków")
        
        try:
            languages = self.process.get_available_languages()
            return LanguagesResponse(languages=languages)
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
        log_dir=config.get("GRPC_LOG_DIR")
    )
    
    # Utwórz instancję procesu
    process = Process()
    
    # Utwórz serwer gRPC
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Dodaj usługę TTS do serwera
    # tts_pb2_grpc.add_TtsServiceServicer_to_server(TtsServiceServicer(process), server)
    
    # Pobierz port z konfiguracji lub użyj domyślnego
    port = config.get("GRPC_PORT", 50051)
    server.add_insecure_port(f'[::]:{port}')
    
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
