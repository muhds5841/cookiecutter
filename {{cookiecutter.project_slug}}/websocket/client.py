"""
Klient WebSocket dla usługi Process.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any, Optional, Union, Callable
from pathlib import Path

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić import z core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import websockets
from websockets.client import WebSocketClientProtocol

from core.config import load_config
from core.logging import get_logger, configure_logging


class ProcessClient:
    """Klient WebSocket dla usługi Process."""
    
    def __init__(self, host: str = None, port: int = None, config: Dict[str, Any] = None):
        """Inicjalizuje klienta WebSocket.
        
        Args:
            host: Host serwera WebSocket
            port: Port serwera WebSocket
            config: Konfiguracja klienta
        """
        self.config = config or load_config("websocket")
        self.logger = get_logger("websocket.client")
        
        # Konfiguracja WebSocket
        self.host = host or os.environ.get("WEBSOCKET_HOST", "localhost")
        self.port = port or int(os.environ.get("WEBSOCKET_PORT", "6789"))
        self.uri = f"ws://{self.host}:{self.port}"
        
        self.logger.info(f"Klient WebSocket zainicjalizowany dla {self.uri}")
    
    async def connect(self) -> WebSocketClientProtocol:
        """Łączy z serwerem WebSocket.
        
        Returns:
            Obiekt połączenia WebSocket
        """
        try:
            websocket = await websockets.connect(self.uri)
            self.logger.info(f"Połączono z serwerem WebSocket {self.uri}")
            return websocket
        except Exception as e:
            self.logger.error(f"Błąd podczas łączenia z serwerem WebSocket: {str(e)}")
            raise
    
    async def process_text(self, text: str, **options) -> Dict[str, Any]:
        """Przetwarza tekst za pomocą usługi Process.
        
        Args:
            text: Tekst do przetworzenia
            **options: Dodatkowe opcje przetwarzania
        
        Returns:
            Wynik przetwarzania
        """
        try:
            # Przygotuj żądanie
            request_id = options.pop("request_id", str(hash(text + str(options))))
            request = {
                "type": "process",
                "request_id": request_id,
                "text": text,
                "options": options
            }
            
            # Połącz z serwerem
            async with websockets.connect(self.uri) as websocket:
                # Wyślij żądanie
                self.logger.info(f"Wysyłanie żądania przetwarzania, request_id: {request_id}")
                await websocket.send(json.dumps(request))
                
                # Odbierz odpowiedź
                response = await websocket.recv()
                response_data = json.loads(response)
                
                # Sprawdź, czy wystąpił błąd
                if "error" in response_data:
                    self.logger.error(f"Błąd przetwarzania: {response_data['error']}")
                    raise Exception(response_data["error"])
                
                self.logger.info(f"Otrzymano odpowiedź dla request_id: {request_id}")
                return response_data
        
        except Exception as e:
            self.logger.error(f"Błąd podczas przetwarzania tekstu: {str(e)}")
            raise
    
    async def get_resources(self) -> Dict[str, Any]:
        """Pobiera dostępne zasoby.
        
        Returns:
            Dostępne zasoby
        """
        try:
            # Przygotuj żądanie
            request_id = str(hash("get_resources" + str(time.time())))
            request = {
                "type": "resources",
                "request_id": request_id
            }
            
            # Połącz z serwerem
            async with websockets.connect(self.uri) as websocket:
                # Wyślij żądanie
                self.logger.info(f"Wysyłanie żądania pobrania zasobów, request_id: {request_id}")
                await websocket.send(json.dumps(request))
                
                # Odbierz odpowiedź
                response = await websocket.recv()
                response_data = json.loads(response)
                
                # Sprawdź, czy wystąpił błąd
                if "error" in response_data:
                    self.logger.error(f"Błąd pobierania zasobów: {response_data['error']}")
                    raise Exception(response_data["error"])
                
                self.logger.info(f"Otrzymano odpowiedź dla request_id: {request_id}")
                return response_data["resources"]
        
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania zasobów: {str(e)}")
            raise
    
    def process_text_sync(self, text: str, **options) -> Dict[str, Any]:
        """Synchroniczna wersja metody process_text.
        
        Args:
            text: Tekst do przetworzenia
            **options: Dodatkowe opcje przetwarzania
        
        Returns:
            Wynik przetwarzania
        """
        return asyncio.run(self.process_text(text, **options))
    
    def get_resources_sync(self) -> Dict[str, Any]:
        """Synchroniczna wersja metody get_resources.
        
        Returns:
            Dostępne zasoby
        """
        return asyncio.run(self.get_resources())


async def main_async():
    """Funkcja główna asynchroniczna klienta WebSocket."""
    # Konfiguracja logowania
    log_level = os.environ.get("WEBSOCKET_LOG_LEVEL", "INFO")
    configure_logging(level=log_level)
    
    # Przykład użycia klienta
    client = ProcessClient()
    
    try:
        # Pobierz zasoby
        resources = await client.get_resources()
        print(f"Dostępne zasoby: {json.dumps(resources, indent=2)}")
        
        # Przetwórz tekst
        text = "Przykładowy tekst do przetworzenia"
        result = await client.process_text(text, language="pl-PL")
        print(f"Wynik przetwarzania: {json.dumps(result, indent=2)}")
    
    except Exception as e:
        print(f"Błąd: {str(e)}")


def main():
    """Funkcja główna klienta WebSocket."""
    asyncio.run(main_async())


if __name__ == "__main__":
    import time  # Dodane dla funkcji get_resources
    main()
