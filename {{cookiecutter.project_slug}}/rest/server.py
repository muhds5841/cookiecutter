"""
Serwer REST dla usługi Text-to-Speech.
"""

import os
import sys
import json
from typing import Dict, Any, Optional, List

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić import z process i lib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
import uvicorn

from process.process import Process
from lib.config import load_config
from lib.logging import get_logger, configure_logging


# Modele danych
class TtsRequest(BaseModel):
    """Model żądania syntezy mowy."""
    text: str = Field(..., description="Tekst do konwersji na mowę")
    language: Optional[str] = Field(None, description="Kod języka (np. 'en-US', 'pl-PL')")
    voice: Optional[str] = Field(None, description="Nazwa głosu do użycia")
    format: str = Field("wav", description="Format wyjściowy audio (wav, mp3)")


class TtsResponse(BaseModel):
    """Model odpowiedzi z wynikiem syntezy mowy."""
    audio_id: str = Field(..., description="Identyfikator wygenerowanego audio")
    format: str = Field(..., description="Format audio (wav, mp3)")
    base64: str = Field(..., description="Dane audio zakodowane w base64")


class VoiceInfo(BaseModel):
    """Model informacji o głosie."""
    name: str = Field(..., description="Nazwa głosu")
    language: str = Field(..., description="Kod języka (np. 'en-US', 'pl-PL')")
    gender: str = Field(..., description="Płeć głosu (male, female)")


class VoicesResponse(BaseModel):
    """Model odpowiedzi z listą dostępnych głosów."""
    voices: List[VoiceInfo] = Field(..., description="Lista dostępnych głosów")


class LanguagesResponse(BaseModel):
    """Model odpowiedzi z listą dostępnych języków."""
    languages: List[str] = Field(..., description="Lista kodów języków (np. 'en-US', 'pl-PL')")


# Aplikacja FastAPI
app = FastAPI(
    title="Process TTS REST API",
    description="REST API dla usługi Text-to-Speech",
    version="0.1.0"
)

# Dodaj obsługę CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # W produkcji należy ograniczyć do konkretnych domen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Konfiguracja i inicjalizacja
config = load_config()
logger = get_logger("rest.server")
process = Process()


@app.post("/api/v1/synthesize", response_model=TtsResponse, tags=["TTS"])
async def synthesize(request: TtsRequest):
    """Konwertuje tekst na mowę."""
    logger.info(f"Otrzymano żądanie syntezy: {request.text[:50]}...")
    
    try:
        parameters = {
            "text": request.text,
            "language": request.language,
            "voice": request.voice,
            "format": request.format
        }
        
        # Usuń None z parametrów
        parameters = {k: v for k, v in parameters.items() if v is not None}
        
        result = process.run(parameters)
        
        return TtsResponse(
            audio_id=result["audio_id"],
            format=result["format"],
            base64=result["base64"]
        )
    except Exception as e:
        logger.error(f"Błąd podczas syntezy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/voices", response_model=VoicesResponse, tags=["TTS"])
async def get_voices():
    """Pobiera listę dostępnych głosów."""
    logger.info("Otrzymano żądanie pobrania głosów")
    
    try:
        voices = process.get_available_voices()
        
        # Konwersja do modelu Pydantic
        voice_infos = [
            VoiceInfo(
                name=voice["name"],
                language=voice["language"],
                gender=voice["gender"]
            )
            for voice in voices
        ]
        
        return VoicesResponse(voices=voice_infos)
    except Exception as e:
        logger.error(f"Błąd podczas pobierania głosów: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/languages", response_model=LanguagesResponse, tags=["TTS"])
async def get_languages():
    """Pobiera listę dostępnych języków."""
    logger.info("Otrzymano żądanie pobrania języków")
    
    try:
        languages = process.get_available_languages()
        return LanguagesResponse(languages=languages)
    except Exception as e:
        logger.error(f"Błąd podczas pobierania języków: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/audio/{audio_id}", tags=["TTS"])
async def get_audio(audio_id: str, response: Response):
    """Pobiera audio na podstawie identyfikatora."""
    logger.info(f"Otrzymano żądanie pobrania audio: {audio_id}")
    
    # W rzeczywistej implementacji tutaj byłoby pobieranie audio z bazy danych lub systemu plików
    # Na potrzeby przykładu zwracamy przykładowe dane audio
    
    # Symulacja błędu, gdy audio_id nie zaczyna się od "audio-"
    if not audio_id.startswith("audio-"):
        raise HTTPException(status_code=404, detail=f"Audio o ID {audio_id} nie zostało znalezione")
    
    # Przykładowe dane audio
    audio_data = b"SAMPLE_AUDIO_DATA"
    
    # Ustawienie nagłówków odpowiedzi
    response.headers["Content-Disposition"] = f"attachment; filename={audio_id}.wav"
    response.headers["Content-Type"] = "audio/wav"
    
    # Zwrócenie danych audio jako odpowiedź strumieniowa
    return StreamingResponse(iter([audio_data]), media_type="audio/wav")


@app.get("/health", tags=["System"])
async def health_check():
    """Sprawdza stan serwera."""
    return {"status": "ok"}


def main():
    """Funkcja główna serwera REST."""
    # Załaduj konfigurację
    config = load_config()
    
    # Skonfiguruj logowanie
    configure_logging(
        level=config.get("REST_LOG_LEVEL", "info"),
        component_name="rest",
        log_dir=config.get("REST_LOG_DIR")
    )
    
    # Pobierz port z konfiguracji lub użyj domyślnego
    host = config.get("REST_HOST", "0.0.0.0")
    port = int(config.get("REST_PORT", 5000))
    
    # Uruchom serwer
    logger.info(f"Uruchamianie serwera REST na {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
