#!/usr/bin/env python
"""
Serwer sygnalizacyjny WebRTC.

Ten moduł implementuje serwer sygnalizacyjny dla WebRTC, który umożliwia
nawiązywanie połączeń między klientami. Serwer używa protokołu WebSocket
do komunikacji z klientami.
"""

import asyncio
import json
import logging
import uuid
from typing import Any, Dict, Optional, Set

import websockets
from websockets.server import WebSocketServerProtocol

from core.logging import get_logger

logger = get_logger(__name__)


class SignalingServer:
    """Serwer sygnalizacyjny WebRTC.

    Umożliwia klientom wymianę ofert SDP (Session Description Protocol)
    i kandydatów ICE (Interactive Connectivity Establishment) w celu
    nawiązania bezpośredniego połączenia peer-to-peer.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        """Inicjalizacja serwera sygnalizacyjnego.

        Args:
            host: Adres hosta, na którym nasłuchuje serwer.
            port: Port, na którym nasłuchuje serwer.
        """
        self.host = host
        self.port = port
        self.clients: Dict[str, WebSocketServerProtocol] = {}
        self.rooms: Dict[str, Set[str]] = {}
        self.server = None

    async def register(self, websocket: WebSocketServerProtocol) -> str:
        """Rejestracja nowego klienta.

        Args:
            websocket: Połączenie WebSocket klienta.

        Returns:
            Identyfikator klienta.
        """
        client_id = str(uuid.uuid4())
        self.clients[client_id] = websocket
        logger.info(f"Nowy klient zarejestrowany: {client_id}")
        return client_id

    async def unregister(self, client_id: str) -> None:
        """Wyrejestrowanie klienta.

        Args:
            client_id: Identyfikator klienta do wyrejestrowania.
        """
        if client_id in self.clients:
            del self.clients[client_id]
            # Usuń klienta ze wszystkich pokojów
            for room_id, clients in self.rooms.items():
                if client_id in clients:
                    clients.remove(client_id)
                    # Powiadom innych klientów w pokoju o rozłączeniu
                    await self.broadcast_to_room(
                        room_id,
                        {"type": "disconnect", "client_id": client_id},
                        exclude=client_id,
                    )
            logger.info(f"Klient wyrejestrowany: {client_id}")

    async def join_room(self, client_id: str, room_id: str) -> None:
        """Dołączenie klienta do pokoju.

        Args:
            client_id: Identyfikator klienta.
            room_id: Identyfikator pokoju.
        """
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
        self.rooms[room_id].add(client_id)
        # Powiadom innych klientów w pokoju o nowym uczestniku
        await self.broadcast_to_room(
            room_id,
            {"type": "join", "client_id": client_id},
            exclude=client_id,
        )
        # Wyślij listę klientów w pokoju do nowego uczestnika
        clients_in_room = list(self.rooms[room_id])
        clients_in_room.remove(client_id)  # Usuń samego siebie z listy
        await self.send_to_client(
            client_id,
            {
                "type": "room_clients",
                "room_id": room_id,
                "clients": clients_in_room,
            },
        )
        logger.info(f"Klient {client_id} dołączył do pokoju {room_id}")

    async def leave_room(self, client_id: str, room_id: str) -> None:
        """Opuszczenie pokoju przez klienta.

        Args:
            client_id: Identyfikator klienta.
            room_id: Identyfikator pokoju.
        """
        if room_id in self.rooms and client_id in self.rooms[room_id]:
            self.rooms[room_id].remove(client_id)
            # Powiadom innych klientów w pokoju o opuszczeniu
            await self.broadcast_to_room(
                room_id,
                {"type": "leave", "client_id": client_id},
                exclude=client_id,
            )
            # Usuń pokój, jeśli jest pusty
            if not self.rooms[room_id]:
                del self.rooms[room_id]
            logger.info(f"Klient {client_id} opuścił pokój {room_id}")

    async def send_to_client(self, client_id: str, message: Dict[str, Any]) -> None:
        """Wysłanie wiadomości do konkretnego klienta.

        Args:
            client_id: Identyfikator klienta.
            message: Wiadomość do wysłania.
        """
        if client_id in self.clients:
            try:
                await self.clients[client_id].send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                await self.unregister(client_id)
                logger.warning(f"Nie można wysłać wiadomości do klienta {client_id} - połączenie zamknięte")
        else:
            logger.warning(f"Próba wysłania wiadomości do niezarejestrowanego klienta: {client_id}")

    async def broadcast_to_room(
        self, room_id: str, message: Dict[str, Any], exclude: Optional[str] = None
    ) -> None:
        """Rozgłoszenie wiadomości do wszystkich klientów w pokoju.

        Args:
            room_id: Identyfikator pokoju.
            message: Wiadomość do rozgłoszenia.
            exclude: Opcjonalny identyfikator klienta do wykluczenia z rozgłoszenia.
        """
        if room_id in self.rooms:
            for client_id in self.rooms[room_id]:
                if exclude is None or client_id != exclude:
                    await self.send_to_client(client_id, message)

    async def handle_message(self, client_id: str, message: Dict[str, Any]) -> None:
        """Obsługa wiadomości od klienta.

        Args:
            client_id: Identyfikator klienta.
            message: Wiadomość od klienta.
        """
        message_type = message.get("type")

        if message_type == "join":
            room_id = message.get("room_id")
            if room_id:
                await self.join_room(client_id, room_id)

        elif message_type == "leave":
            room_id = message.get("room_id")
            if room_id:
                await self.leave_room(client_id, room_id)

        elif message_type == "offer" or message_type == "answer" or message_type == "ice-candidate":
            # Przekazanie oferty/odpowiedzi/kandydata ICE do docelowego klienta
            target_id = message.get("target")
            if target_id and target_id in self.clients:
                # Dodaj identyfikator nadawcy do wiadomości
                message["sender"] = client_id
                await self.send_to_client(target_id, message)
            else:
                logger.warning(f"Nie można przekazać wiadomości do klienta {target_id} - nie istnieje")

        elif message_type == "broadcast":
            # Rozgłoszenie wiadomości do wszystkich klientów w pokoju
            room_id = message.get("room_id")
            if room_id and room_id in self.rooms:
                # Dodaj identyfikator nadawcy do wiadomości
                message["sender"] = client_id
                await self.broadcast_to_room(room_id, message, exclude=client_id)

    async def connection_handler(self, websocket: WebSocketServerProtocol, path: str) -> None:
        """Obsługa nowego połączenia WebSocket.

        Args:
            websocket: Połączenie WebSocket.
            path: Ścieżka URL.
        """
        client_id = await self.register(websocket)

        # Wyślij identyfikator klienta
        await websocket.send(json.dumps({"type": "register", "client_id": client_id}))

        try:
            async for message_str in websocket:
                try:
                    message = json.loads(message_str)
                    await self.handle_message(client_id, message)
                except json.JSONDecodeError:
                    logger.error(f"Otrzymano nieprawidłowy format JSON: {message_str}")
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Połączenie z klientem {client_id} zostało zamknięte")
        finally:
            await self.unregister(client_id)

    async def start(self) -> None:
        """Uruchomienie serwera sygnalizacyjnego."""
        self.server = await websockets.serve(
            self.connection_handler, self.host, self.port
        )
        logger.info(f"Serwer sygnalizacyjny uruchomiony na {self.host}:{self.port}")

    async def stop(self) -> None:
        """Zatrzymanie serwera sygnalizacyjnego."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("Serwer sygnalizacyjny zatrzymany")


async def run_server(host: str = "0.0.0.0", port: int = 8765) -> None:
    """Uruchomienie serwera sygnalizacyjnego jako samodzielnej aplikacji.

    Args:
        host: Adres hosta, na którym nasłuchuje serwer.
        port: Port, na którym nasłuchuje serwer.
    """
    server = SignalingServer(host, port)
    await server.start()
    try:
        await asyncio.Future()  # Uruchom serwer w nieskończoność
    except asyncio.CancelledError:
        await server.stop()


def main() -> None:
    """Punkt wejścia dla uruchomienia serwera jako samodzielnej aplikacji."""
    import argparse

    parser = argparse.ArgumentParser(description="Serwer sygnalizacyjny WebRTC")
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Adres hosta (domyślnie: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8765, help="Port serwera (domyślnie: 8765)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Poziom logowania (domyślnie: INFO)",
    )

    args = parser.parse_args()

    # Konfiguracja logowania
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Uruchomienie serwera
    asyncio.run(run_server(args.host, args.port))


if __name__ == "__main__":
    main()
