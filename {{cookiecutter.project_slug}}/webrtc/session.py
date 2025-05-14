#!/usr/bin/env python
"""
Sesja WebRTC.

Ten moduł implementuje sesję WebRTC, która umożliwia przesyłanie
strumieni audio/wideo oraz kanałów danych między klientami.
"""

import asyncio
import json
import logging
from typing import Any, Callable, Dict, List, Optional, Set, Union

from core.logging import get_logger
from webrtc.client import WebRTCClient

logger = get_logger(__name__)


class WebRTCSession:
    """Sesja WebRTC.

    Umożliwia zarządzanie połączeniem WebRTC, w tym wymianą ofert SDP,
    kandydatów ICE, oraz przesyłaniem strumieni audio/wideo i danych.
    """

    def __init__(
        self,
        signaling_url: str = "ws://localhost:8765",
        room_id: Optional[str] = None,
        on_data_channel_message: Optional[Callable[[str, Any], None]] = None,
        on_stream_added: Optional[Callable[[str, Any], None]] = None,
        on_stream_removed: Optional[Callable[[str], None]] = None,
        on_connection_state_change: Optional[Callable[[str, str], None]] = None,
    ):
        """Inicjalizacja sesji WebRTC.

        Args:
            signaling_url: URL serwera sygnalizacyjnego.
            room_id: Identyfikator pokoju, do którego dołączyć automatycznie.
            on_data_channel_message: Callback wywoływany po otrzymaniu wiadomości przez kanał danych.
            on_stream_added: Callback wywoływany po dodaniu strumienia.
            on_stream_removed: Callback wywoływany po usunięciu strumienia.
            on_connection_state_change: Callback wywoływany po zmianie stanu połączenia.
        """
        self.signaling_url = signaling_url
        self.room_id = room_id
        self.on_data_channel_message = on_data_channel_message
        self.on_stream_added = on_stream_added
        self.on_stream_removed = on_stream_removed
        self.on_connection_state_change = on_connection_state_change
        
        # Inicjalizacja klienta WebRTC
        self.client = WebRTCClient(
            signaling_url=signaling_url,
            on_message=self._handle_signaling_message,
            on_peer_connected=self._handle_peer_connected,
            on_peer_disconnected=self._handle_peer_disconnected,
        )
        
        # Słowniki do przechowywania połączeń peer i kanałów danych
        self.peer_connections: Dict[str, Any] = {}
        self.data_channels: Dict[str, Dict[str, Any]] = {}
        
        # Flagi stanu
        self.is_connected = False
        self.local_stream: Optional[Any] = None

    async def connect(self) -> bool:
        """Połączenie z serwerem sygnalizacyjnym i dołączenie do pokoju.

        Returns:
            True, jeśli połączenie zostało nawiązane pomyślnie, False w przeciwnym razie.
        """
        if await self.client.connect():
            self.is_connected = True
            if self.room_id:
                return await self.join_room(self.room_id)
            return True
        return False

    async def disconnect(self) -> None:
        """Rozłączenie z serwerem sygnalizacyjnym i zamknięcie wszystkich połączeń."""
        # Zamknięcie wszystkich połączeń peer
        for peer_id in list(self.peer_connections.keys()):
            await self._close_peer_connection(peer_id)
        
        # Rozłączenie z serwerem sygnalizacyjnym
        await self.client.disconnect()
        self.is_connected = False
        logger.info("Sesja WebRTC zakończona")

    async def join_room(self, room_id: str) -> bool:
        """Dołączenie do pokoju.

        Args:
            room_id: Identyfikator pokoju.

        Returns:
            True, jeśli dołączenie do pokoju powiodło się, False w przeciwnym razie.
        """
        if not self.is_connected:
            logger.error("Nie można dołączyć do pokoju - brak połączenia z serwerem")
            return False
        
        result = await self.client.join_room(room_id)
        if result:
            self.room_id = room_id
        return result

    async def leave_room(self) -> bool:
        """Opuszczenie pokoju.

        Returns:
            True, jeśli opuszczenie pokoju powiodło się, False w przeciwnym razie.
        """
        if not self.is_connected or not self.room_id:
            logger.error("Nie można opuścić pokoju - brak połączenia lub nie jesteś w pokoju")
            return False
        
        # Zamknięcie wszystkich połączeń peer przed opuszczeniem pokoju
        for peer_id in list(self.peer_connections.keys()):
            await self._close_peer_connection(peer_id)
        
        result = await self.client.leave_room()
        if result:
            self.room_id = None
        return result

    async def set_local_stream(self, stream: Any) -> None:
        """Ustawienie lokalnego strumienia audio/wideo.

        Args:
            stream: Lokalny strumień audio/wideo.
        """
        self.local_stream = stream
        
        # Dodanie strumienia do istniejących połączeń
        for peer_id, pc in self.peer_connections.items():
            await self._add_stream_to_peer_connection(peer_id, stream)
            
            # Jeśli już mamy połączenie, wyślij nową ofertę
            if pc.get("connection_state") == "connected":
                await self._create_and_send_offer(peer_id)

    def create_data_channel(self, peer_id: str, channel_id: str) -> Optional[Any]:
        """Utworzenie kanału danych dla połączenia peer.

        Args:
            peer_id: Identyfikator peera.
            channel_id: Identyfikator kanału danych.

        Returns:
            Utworzony kanał danych lub None, jeśli nie udało się utworzyć kanału.
        """
        if peer_id not in self.peer_connections:
            logger.error(f"Nie można utworzyć kanału danych - brak połączenia z peerem {peer_id}")
            return None
        
        pc = self.peer_connections[peer_id]
        
        # Utworzenie kanału danych
        data_channel = pc.get("connection").createDataChannel(channel_id)
        
        # Konfiguracja zdarzeń kanału danych
        self._setup_data_channel(peer_id, channel_id, data_channel)
        
        # Zapisanie kanału danych
        if peer_id not in self.data_channels:
            self.data_channels[peer_id] = {}
        self.data_channels[peer_id][channel_id] = data_channel
        
        logger.info(f"Utworzono kanał danych {channel_id} dla peera {peer_id}")
        return data_channel

    async def send_data(self, peer_id: str, channel_id: str, data: Any) -> bool:
        """Wysłanie danych przez kanał danych.

        Args:
            peer_id: Identyfikator peera.
            channel_id: Identyfikator kanału danych.
            data: Dane do wysłania.

        Returns:
            True, jeśli wysłanie danych powiodło się, False w przeciwnym razie.
        """
        if (
            peer_id not in self.data_channels
            or channel_id not in self.data_channels[peer_id]
        ):
            logger.error(f"Nie można wysłać danych - brak kanału danych {channel_id} dla peera {peer_id}")
            return False
        
        data_channel = self.data_channels[peer_id][channel_id]
        
        # Sprawdzenie stanu kanału danych
        if data_channel.readyState != "open":
            logger.error(f"Nie można wysłać danych - kanał danych {channel_id} nie jest otwarty")
            return False
        
        # Konwersja danych do formatu JSON, jeśli to nie jest string
        if not isinstance(data, str):
            data = json.dumps(data)
        
        # Wysłanie danych
        data_channel.send(data)
        logger.debug(f"Wysłano dane przez kanał {channel_id} do peera {peer_id}")
        return True

    async def broadcast_data(self, channel_id: str, data: Any) -> bool:
        """Rozgłoszenie danych do wszystkich połączonych peerów.

        Args:
            channel_id: Identyfikator kanału danych.
            data: Dane do rozgłoszenia.

        Returns:
            True, jeśli rozgłoszenie danych powiodło się dla co najmniej jednego peera,
            False w przeciwnym razie.
        """
        if not self.peer_connections:
            logger.error("Nie można rozgłosić danych - brak połączeń z peerami")
            return False
        
        success = False
        for peer_id in self.peer_connections:
            if await self.send_data(peer_id, channel_id, data):
                success = True
        
        return success

    async def _handle_signaling_message(self, message: Dict[str, Any]) -> None:
        """Obsługa wiadomości od serwera sygnalizacyjnego.

        Args:
            message: Wiadomość od serwera.
        """
        message_type = message.get("type")
        
        if message_type == "offer":
            # Otrzymano ofertę SDP od innego klienta
            sender_id = message.get("sender")
            sdp = message.get("sdp")
            if sender_id and sdp:
                await self._handle_offer(sender_id, sdp)
        
        elif message_type == "answer":
            # Otrzymano odpowiedź SDP od innego klienta
            sender_id = message.get("sender")
            sdp = message.get("sdp")
            if sender_id and sdp:
                await self._handle_answer(sender_id, sdp)
        
        elif message_type == "ice-candidate":
            # Otrzymano kandydata ICE od innego klienta
            sender_id = message.get("sender")
            candidate = message.get("candidate")
            if sender_id and candidate:
                await self._handle_ice_candidate(sender_id, candidate)

    async def _handle_peer_connected(self, peer_id: str) -> None:
        """Obsługa zdarzenia połączenia z peerem.

        Args:
            peer_id: Identyfikator peera.
        """
        # Utworzenie nowego połączenia peer
        await self._create_peer_connection(peer_id)
        
        # Utworzenie i wysłanie oferty SDP
        await self._create_and_send_offer(peer_id)

    async def _handle_peer_disconnected(self, peer_id: str) -> None:
        """Obsługa zdarzenia rozłączenia peera.

        Args:
            peer_id: Identyfikator peera.
        """
        # Zamknięcie połączenia peer
        await self._close_peer_connection(peer_id)

    async def _create_peer_connection(self, peer_id: str) -> None:
        """Utworzenie nowego połączenia peer.

        Args:
            peer_id: Identyfikator peera.
        """
        # Utworzenie nowego połączenia RTCPeerConnection
        pc = {
            "connection": None,  # Tu w rzeczywistej implementacji byłby obiekt RTCPeerConnection
            "connection_state": "new",
            "ice_gathering_state": "new",
            "ice_connection_state": "new",
            "signaling_state": "stable",
        }
        
        # Konfiguracja zdarzeń połączenia
        self._setup_peer_connection_events(peer_id, pc)
        
        # Dodanie lokalnego strumienia, jeśli istnieje
        if self.local_stream:
            await self._add_stream_to_peer_connection(peer_id, self.local_stream)
        
        # Zapisanie połączenia
        self.peer_connections[peer_id] = pc
        logger.info(f"Utworzono nowe połączenie peer dla {peer_id}")

    async def _close_peer_connection(self, peer_id: str) -> None:
        """Zamknięcie połączenia peer.

        Args:
            peer_id: Identyfikator peera.
        """
        if peer_id in self.peer_connections:
            pc = self.peer_connections[peer_id]
            
            # Zamknięcie kanałów danych
            if peer_id in self.data_channels:
                for channel_id, channel in self.data_channels[peer_id].items():
                    channel.close()
                del self.data_channels[peer_id]
            
            # Zamknięcie połączenia
            if pc.get("connection"):
                pc["connection"].close()
            
            # Usunięcie połączenia
            del self.peer_connections[peer_id]
            
            # Wywołanie callbacka usunięcia strumienia
            if self.on_stream_removed:
                self.on_stream_removed(peer_id)
            
            logger.info(f"Zamknięto połączenie peer dla {peer_id}")

    async def _create_and_send_offer(self, peer_id: str) -> None:
        """Utworzenie i wysłanie oferty SDP do peera.

        Args:
            peer_id: Identyfikator peera.
        """
        if peer_id not in self.peer_connections:
            logger.error(f"Nie można utworzyć oferty - brak połączenia z peerem {peer_id}")
            return
        
        pc = self.peer_connections[peer_id]
        
        # W rzeczywistej implementacji tutaj byłoby tworzenie oferty SDP
        # i ustawienie jej jako lokalny opis
        offer = {"type": "offer", "sdp": "dummy_sdp_offer"}
        
        # Wysłanie oferty do peera
        await self.client.send_offer(peer_id, offer)
        logger.debug(f"Wysłano ofertę SDP do peera {peer_id}")

    async def _handle_offer(self, peer_id: str, offer: Dict[str, Any]) -> None:
        """Obsługa otrzymanej oferty SDP.

        Args:
            peer_id: Identyfikator peera.
            offer: Oferta SDP.
        """
        # Utworzenie połączenia peer, jeśli nie istnieje
        if peer_id not in self.peer_connections:
            await self._create_peer_connection(peer_id)
        
        pc = self.peer_connections[peer_id]
        
        # W rzeczywistej implementacji tutaj byłoby ustawienie zdalnego opisu
        # i utworzenie odpowiedzi SDP
        
        # Utworzenie odpowiedzi
        answer = {"type": "answer", "sdp": "dummy_sdp_answer"}
        
        # Wysłanie odpowiedzi do peera
        await self.client.send_answer(peer_id, answer)
        logger.debug(f"Wysłano odpowiedź SDP do peera {peer_id}")

    async def _handle_answer(self, peer_id: str, answer: Dict[str, Any]) -> None:
        """Obsługa otrzymanej odpowiedzi SDP.

        Args:
            peer_id: Identyfikator peera.
            answer: Odpowiedź SDP.
        """
        if peer_id not in self.peer_connections:
            logger.error(f"Nie można obsłużyć odpowiedzi - brak połączenia z peerem {peer_id}")
            return
        
        pc = self.peer_connections[peer_id]
        
        # W rzeczywistej implementacji tutaj byłoby ustawienie zdalnego opisu
        logger.debug(f"Otrzymano odpowiedź SDP od peera {peer_id}")

    async def _handle_ice_candidate(self, peer_id: str, candidate: Dict[str, Any]) -> None:
        """Obsługa otrzymanego kandydata ICE.

        Args:
            peer_id: Identyfikator peera.
            candidate: Kandydat ICE.
        """
        if peer_id not in self.peer_connections:
            logger.error(f"Nie można obsłużyć kandydata ICE - brak połączenia z peerem {peer_id}")
            return
        
        pc = self.peer_connections[peer_id]
        
        # W rzeczywistej implementacji tutaj byłoby dodanie kandydata ICE
        logger.debug(f"Otrzymano kandydata ICE od peera {peer_id}")

    async def _add_stream_to_peer_connection(self, peer_id: str, stream: Any) -> None:
        """Dodanie strumienia do połączenia peer.

        Args:
            peer_id: Identyfikator peera.
            stream: Strumień audio/wideo.
        """
        if peer_id not in self.peer_connections:
            logger.error(f"Nie można dodać strumienia - brak połączenia z peerem {peer_id}")
            return
        
        pc = self.peer_connections[peer_id]
        
        # W rzeczywistej implementacji tutaj byłoby dodanie strumienia do połączenia
        logger.debug(f"Dodano strumień do połączenia z peerem {peer_id}")

    def _setup_peer_connection_events(self, peer_id: str, pc: Dict[str, Any]) -> None:
        """Konfiguracja zdarzeń połączenia peer.

        Args:
            peer_id: Identyfikator peera.
            pc: Połączenie peer.
        """
        # W rzeczywistej implementacji tutaj byłaby konfiguracja zdarzeń
        # takich jak onicecandidate, ontrack, ondatachannel, itp.
        pass

    def _setup_data_channel(self, peer_id: str, channel_id: str, data_channel: Any) -> None:
        """Konfiguracja zdarzeń kanału danych.

        Args:
            peer_id: Identyfikator peera.
            channel_id: Identyfikator kanału danych.
            data_channel: Kanał danych.
        """
        # W rzeczywistej implementacji tutaj byłaby konfiguracja zdarzeń
        # takich jak onopen, onclose, onmessage, onerror, itp.
        pass


async def run_session_example() -> None:
    """Przykład użycia sesji WebRTC."""
    # Funkcje callback
    def on_data_channel_message(peer_id: str, data: Any) -> None:
        print(f"Otrzymano wiadomość od peera {peer_id}: {data}")

    def on_stream_added(peer_id: str, stream: Any) -> None:
        print(f"Dodano strumień od peera {peer_id}")

    def on_stream_removed(peer_id: str) -> None:
        print(f"Usunięto strumień od peera {peer_id}")

    def on_connection_state_change(peer_id: str, state: str) -> None:
        print(f"Zmiana stanu połączenia z peerem {peer_id}: {state}")

    # Utworzenie sesji WebRTC
    session = WebRTCSession(
        signaling_url="ws://localhost:8765",
        room_id="example-room",
        on_data_channel_message=on_data_channel_message,
        on_stream_added=on_stream_added,
        on_stream_removed=on_stream_removed,
        on_connection_state_change=on_connection_state_change,
    )

    # Połączenie z serwerem sygnalizacyjnym
    if await session.connect():
        print(f"Połączono z serwerem sygnalizacyjnym i dołączono do pokoju {session.room_id}")

        # Czekanie na połączenia
        try:
            await asyncio.sleep(60)  # Czekaj 60 sekund
        except asyncio.CancelledError:
            pass

        # Rozłączenie
        await session.disconnect()


def main() -> None:
    """Punkt wejścia dla przykładu użycia sesji WebRTC."""
    import argparse

    parser = argparse.ArgumentParser(description="Przykład sesji WebRTC")
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
    asyncio.run(run_session_example())


if __name__ == "__main__":
    main()
