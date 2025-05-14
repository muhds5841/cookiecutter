#!/usr/bin/env python
"""
Klient WebRTC.

Ten moduł implementuje klienta WebRTC, który umożliwia nawiązywanie
połączeń peer-to-peer z innymi klientami za pośrednictwem serwera sygnalizacyjnego.
"""

import asyncio
import json
import logging
from typing import Any, Callable, Dict, List, Optional, Set, Union

import websockets
from websockets.client import WebSocketClientProtocol

from core.logging import get_logger

logger = get_logger(__name__)


class WebRTCClient:
    """Klient WebRTC.

    Umożliwia nawiązywanie połączeń WebRTC z innymi klientami za pośrednictwem
    serwera sygnalizacyjnego. Klient obsługuje wymianę ofert SDP i kandydatów ICE,
    a także zarządzanie pokojami i uczestnikami.
    """

    def __init__(
        self,
        signaling_url: str = "ws://localhost:8765",
        on_message: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_peer_connected: Optional[Callable[[str], None]] = None,
        on_peer_disconnected: Optional[Callable[[str], None]] = None,
    ):
        """Inicjalizacja klienta WebRTC.

        Args:
            signaling_url: URL serwera sygnalizacyjnego.
            on_message: Callback wywoływany po otrzymaniu wiadomości.
            on_peer_connected: Callback wywoływany po połączeniu z peerem.
            on_peer_disconnected: Callback wywoływany po rozłączeniu peera.
        """
        self.signaling_url = signaling_url
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.client_id: Optional[str] = None
        self.peers: Set[str] = set()
        self.current_room: Optional[str] = None
        self.on_message = on_message
        self.on_peer_connected = on_peer_connected
        self.on_peer_disconnected = on_peer_disconnected
        self.running = False
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.task: Optional[asyncio.Task] = None

    async def connect(self) -> bool:
        """Połączenie z serwerem sygnalizacyjnym.

        Returns:
            True, jeśli połączenie zostało nawiązane pomyślnie, False w przeciwnym razie.
        """
        try:
            self.websocket = await websockets.connect(self.signaling_url)
            self.running = True
            self.task = asyncio.create_task(self._message_handler())
            logger.info(f"Połączono z serwerem sygnalizacyjnym: {self.signaling_url}")
            return True
        except (websockets.exceptions.WebSocketException, ConnectionRefusedError) as e:
            logger.error(f"Nie można połączyć się z serwerem sygnalizacyjnym: {e}")
            return False

    async def disconnect(self) -> None:
        """Rozłączenie z serwerem sygnalizacyjnym."""
        self.running = False
        if self.current_room:
            await self.leave_room()
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None
        self.client_id = None
        self.peers.clear()
        logger.info("Rozłączono z serwerem sygnalizacyjnym")

    async def join_room(self, room_id: str) -> bool:
        """Dołączenie do pokoju.

        Args:
            room_id: Identyfikator pokoju.

        Returns:
            True, jeśli dołączenie do pokoju powiodło się, False w przeciwnym razie.
        """
        if not self.websocket or not self.client_id:
            logger.error("Nie można dołączyć do pokoju - brak połączenia z serwerem")
            return False

        if self.current_room:
            await self.leave_room()

        await self._send_message({"type": "join", "room_id": room_id})
        self.current_room = room_id
        logger.info(f"Dołączono do pokoju: {room_id}")
        return True

    async def leave_room(self) -> bool:
        """Opuszczenie pokoju.

        Returns:
            True, jeśli opuszczenie pokoju powiodło się, False w przeciwnym razie.
        """
        if not self.websocket or not self.client_id or not self.current_room:
            logger.error("Nie można opuścić pokoju - brak połączenia lub nie jesteś w pokoju")
            return False

        await self._send_message({"type": "leave", "room_id": self.current_room})
        room_id = self.current_room
        self.current_room = None
        self.peers.clear()
        logger.info(f"Opuszczono pokój: {room_id}")
        return True

    async def send_offer(self, target_id: str, offer: Dict[str, Any]) -> bool:
        """Wysłanie oferty SDP do innego klienta.

        Args:
            target_id: Identyfikator docelowego klienta.
            offer: Oferta SDP.

        Returns:
            True, jeśli wysłanie oferty powiodło się, False w przeciwnym razie.
        """
        if not self.websocket or not self.client_id:
            logger.error("Nie można wysłać oferty - brak połączenia z serwerem")
            return False

        await self._send_message(
            {"type": "offer", "target": target_id, "sdp": offer}
        )
        logger.debug(f"Wysłano ofertę do klienta: {target_id}")
        return True

    async def send_answer(self, target_id: str, answer: Dict[str, Any]) -> bool:
        """Wysłanie odpowiedzi SDP do innego klienta.

        Args:
            target_id: Identyfikator docelowego klienta.
            answer: Odpowiedź SDP.

        Returns:
            True, jeśli wysłanie odpowiedzi powiodło się, False w przeciwnym razie.
        """
        if not self.websocket or not self.client_id:
            logger.error("Nie można wysłać odpowiedzi - brak połączenia z serwerem")
            return False

        await self._send_message(
            {"type": "answer", "target": target_id, "sdp": answer}
        )
        logger.debug(f"Wysłano odpowiedź do klienta: {target_id}")
        return True

    async def send_ice_candidate(
        self, target_id: str, candidate: Dict[str, Any]
    ) -> bool:
        """Wysłanie kandydata ICE do innego klienta.

        Args:
            target_id: Identyfikator docelowego klienta.
            candidate: Kandydat ICE.

        Returns:
            True, jeśli wysłanie kandydata powiodło się, False w przeciwnym razie.
        """
        if not self.websocket or not self.client_id:
            logger.error("Nie można wysłać kandydata ICE - brak połączenia z serwerem")
            return False

        await self._send_message(
            {"type": "ice-candidate", "target": target_id, "candidate": candidate}
        )
        logger.debug(f"Wysłano kandydata ICE do klienta: {target_id}")
        return True

    async def broadcast_message(self, message: Dict[str, Any]) -> bool:
        """Rozgłoszenie wiadomości do wszystkich klientów w pokoju.

        Args:
            message: Wiadomość do rozgłoszenia.

        Returns:
            True, jeśli rozgłoszenie wiadomości powiodło się, False w przeciwnym razie.
        """
        if not self.websocket or not self.client_id or not self.current_room:
            logger.error("Nie można rozgłosić wiadomości - brak połączenia lub nie jesteś w pokoju")
            return False

        message["room_id"] = self.current_room
        message["type"] = "broadcast"
        await self._send_message(message)
        logger.debug(f"Rozgłoszono wiadomość do pokoju: {self.current_room}")
        return True

    async def send_direct_message(
        self, target_id: str, message: Dict[str, Any]
    ) -> bool:
        """Wysłanie bezpośredniej wiadomości do innego klienta.

        Args:
            target_id: Identyfikator docelowego klienta.
            message: Wiadomość do wysłania.

        Returns:
            True, jeśli wysłanie wiadomości powiodło się, False w przeciwnym razie.
        """
        if not self.websocket or not self.client_id:
            logger.error("Nie można wysłać wiadomości - brak połączenia z serwerem")
            return False

        message["type"] = "direct"
        message["target"] = target_id
        await self._send_message(message)
        logger.debug(f"Wysłano bezpośrednią wiadomość do klienta: {target_id}")
        return True

    async def _send_message(self, message: Dict[str, Any]) -> None:
        """Wysłanie wiadomości do serwera sygnalizacyjnego.

        Args:
            message: Wiadomość do wysłania.
        """
        if self.websocket:
            await self.websocket.send(json.dumps(message))
        else:
            logger.error("Nie można wysłać wiadomości - brak połączenia z serwerem")

    async def _message_handler(self) -> None:
        """Obsługa wiadomości przychodzących od serwera sygnalizacyjnego."""
        if not self.websocket:
            return

        try:
            async for message_str in self.websocket:
                try:
                    message = json.loads(message_str)
                    await self._handle_message(message)
                except json.JSONDecodeError:
                    logger.error(f"Otrzymano nieprawidłowy format JSON: {message_str}")
        except websockets.exceptions.ConnectionClosed:
            logger.info("Połączenie z serwerem sygnalizacyjnym zostało zamknięte")
            self.running = False
            if self.on_peer_disconnected:
                for peer_id in self.peers:
                    self.on_peer_disconnected(peer_id)
            self.peers.clear()
            self.current_room = None
            self.client_id = None

    async def _handle_message(self, message: Dict[str, Any]) -> None:
        """Obsługa wiadomości od serwera sygnalizacyjnego.

        Args:
            message: Wiadomość od serwera.
        """
        message_type = message.get("type")

        if message_type == "register":
            self.client_id = message.get("client_id")
            logger.info(f"Zarejestrowano jako klient: {self.client_id}")

        elif message_type == "room_clients":
            room_id = message.get("room_id")
            clients = message.get("clients", [])
            if room_id == self.current_room:
                for client_id in clients:
                    self.peers.add(client_id)
                    if self.on_peer_connected:
                        self.on_peer_connected(client_id)
                logger.info(f"Otrzymano listę klientów w pokoju {room_id}: {clients}")

        elif message_type == "join":
            client_id = message.get("client_id")
            if client_id and client_id != self.client_id:
                self.peers.add(client_id)
                if self.on_peer_connected:
                    self.on_peer_connected(client_id)
                logger.info(f"Klient {client_id} dołączył do pokoju")

        elif message_type == "leave" or message_type == "disconnect":
            client_id = message.get("client_id")
            if client_id and client_id in self.peers:
                self.peers.remove(client_id)
                if self.on_peer_disconnected:
                    self.on_peer_disconnected(client_id)
                logger.info(f"Klient {client_id} opuścił pokój")

        # Przekazanie wiadomości do callbacka użytkownika
        if self.on_message:
            self.on_message(message)


async def run_client_example() -> None:
    """Przykład użycia klienta WebRTC."""
    # Funkcje callback
    def on_message(message: Dict[str, Any]) -> None:
        print(f"Otrzymano wiadomość: {message}")

    def on_peer_connected(peer_id: str) -> None:
        print(f"Połączono z peerem: {peer_id}")

    def on_peer_disconnected(peer_id: str) -> None:
        print(f"Rozłączono z peerem: {peer_id}")

    # Utworzenie klienta
    client = WebRTCClient(
        signaling_url="ws://localhost:8765",
        on_message=on_message,
        on_peer_connected=on_peer_connected,
        on_peer_disconnected=on_peer_disconnected,
    )

    # Połączenie z serwerem sygnalizacyjnym
    if await client.connect():
        # Dołączenie do pokoju
        room_id = "example-room"
        if await client.join_room(room_id):
            print(f"Dołączono do pokoju: {room_id}")

            # Wysłanie wiadomości do wszystkich klientów w pokoju
            await client.broadcast_message({"content": "Cześć wszystkim!"})

            # Czekanie na wiadomości
            try:
                await asyncio.sleep(60)  # Czekaj 60 sekund
            except asyncio.CancelledError:
                pass

            # Opuszczenie pokoju
            await client.leave_room()

        # Rozłączenie z serwerem
        await client.disconnect()


def main() -> None:
    """Punkt wejścia dla przykładu użycia klienta WebRTC."""
    import argparse

    parser = argparse.ArgumentParser(description="Przykład klienta WebRTC")
    parser.add_argument(
        "--signaling-url",
        type=str,
        default="ws://localhost:8765",
        help="URL serwera sygnalizacyjnego (domyślnie: ws://localhost:8765)",
    )
    parser.add_argument(
        "--room-id",
        type=str,
        default="example-room",
        help="Identyfikator pokoju (domyślnie: example-room)",
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

    # Uruchomienie przykładu
    asyncio.run(run_client_example())


if __name__ == "__main__":
    main()
