"""
Klient IMAP dla usługi Process.
"""

import os
import sys
import json
import email
import imaplib
import logging
from email.header import decode_header
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić import z core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.config import load_config
from core.logging import get_logger, configure_logging


class IMAPClient:
    """Klient IMAP dla usługi Process."""
    
    def __init__(self, host: str = None, port: int = None, 
                 username: str = None, password: str = None, 
                 use_ssl: bool = None, config: Dict[str, Any] = None):
        """Inicjalizuje klienta IMAP.
        
        Args:
            host: Host serwera IMAP
            port: Port serwera IMAP
            username: Nazwa użytkownika
            password: Hasło
            use_ssl: Czy używać SSL
            config: Konfiguracja klienta
        """
        self.config = config or load_config("email/imap")
        self.logger = get_logger("email.imap.client")
        
        # Konfiguracja IMAP
        self.host = host or os.environ.get("EMAIL_IMAP_HOST", "localhost")
        self.port = port or int(os.environ.get("EMAIL_IMAP_SSL_PORT" if use_ssl else "EMAIL_IMAP_PORT", "993" if use_ssl else "143"))
        self.username = username or os.environ.get("EMAIL_IMAP_USERNAME", "")
        self.password = password or os.environ.get("EMAIL_IMAP_PASSWORD", "")
        self.use_ssl = use_ssl if use_ssl is not None else os.environ.get("EMAIL_IMAP_USE_SSL", "false").lower() == "true"
        self.default_folder = os.environ.get("EMAIL_IMAP_DEFAULT_FOLDER", "INBOX")
        self.attachment_dir = os.environ.get("EMAIL_IMAP_ATTACHMENT_DIR", "./attachments")
        
        # Utwórz katalog na załączniki, jeśli nie istnieje
        Path(self.attachment_dir).mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Klient IMAP zainicjalizowany dla {self.host}:{self.port}")
    
    def connect(self):
        """Łączy z serwerem IMAP.
        
        Returns:
            Obiekt połączenia IMAP
        """
        try:
            if self.use_ssl:
                conn = imaplib.IMAP4_SSL(self.host, self.port)
            else:
                conn = imaplib.IMAP4(self.host, self.port)
            
            conn.login(self.username, self.password)
            self.logger.info(f"Połączono z serwerem IMAP {self.host}:{self.port}")
            return conn
        
        except Exception as e:
            self.logger.error(f"Błąd podczas łączenia z serwerem IMAP: {str(e)}")
            raise
    
    def get_folders(self) -> List[str]:
        """Pobiera listę folderów.
        
        Returns:
            Lista folderów
        """
        try:
            conn = self.connect()
            result, folders = conn.list()
            
            folder_list = []
            for folder in folders:
                if folder:
                    # Dekoduj nazwę folderu
                    folder_parts = folder.decode().split(' "/" ')
                    if len(folder_parts) > 1:
                        folder_name = folder_parts[1].strip('"')
                        folder_list.append(folder_name)
            
            conn.logout()
            return folder_list
        
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania folderów: {str(e)}")
            raise
    
    def get_messages(self, folder: str = None, limit: int = 10, 
                     criteria: str = "ALL") -> List[Dict[str, Any]]:
        """Pobiera wiadomości z folderu.
        
        Args:
            folder: Folder do przeszukania
            limit: Maksymalna liczba wiadomości do pobrania
            criteria: Kryteria wyszukiwania (np. "UNSEEN", "ALL")
        
        Returns:
            Lista wiadomości
        """
        try:
            folder = folder or self.default_folder
            conn = self.connect()
            conn.select(folder)
            
            result, data = conn.search(None, criteria)
            if result != "OK":
                raise Exception(f"Błąd podczas wyszukiwania wiadomości: {result}")
            
            message_ids = data[0].split()
            messages = []
            
            # Pobierz ostatnie 'limit' wiadomości
            for msg_id in message_ids[-limit:]:
                result, data = conn.fetch(msg_id, "(RFC822)")
                if result != "OK":
                    self.logger.warning(f"Nie można pobrać wiadomości {msg_id}: {result}")
                    continue
                
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # Dekoduj temat
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                
                # Dekoduj nadawcę
                from_header = decode_header(msg["From"])[0][0]
                if isinstance(from_header, bytes):
                    from_header = from_header.decode()
                
                # Pobierz treść wiadomości
                body = ""
                attachments = []
                
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        
                        # Pobierz treść tekstową
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            payload = part.get_payload(decode=True)
                            charset = part.get_content_charset() or "utf-8"
                            body = payload.decode(charset, errors="replace")
                        
                        # Pobierz załączniki
                        elif "attachment" in content_disposition:
                            filename = part.get_filename()
                            if filename:
                                # Dekoduj nazwę pliku
                                filename_parts = decode_header(filename)
                                filename = ""
                                for part_bytes, charset in filename_parts:
                                    if isinstance(part_bytes, bytes):
                                        filename += part_bytes.decode(charset or "utf-8", errors="replace")
                                    else:
                                        filename += part_bytes
                                
                                # Zapisz załącznik
                                attachment_path = os.path.join(self.attachment_dir, filename)
                                with open(attachment_path, "wb") as f:
                                    f.write(part.get_payload(decode=True))
                                
                                attachments.append({
                                    "filename": filename,
                                    "path": attachment_path,
                                    "content_type": content_type
                                })
                else:
                    # Wiadomość nie jest wieloczęściowa
                    payload = msg.get_payload(decode=True)
                    charset = msg.get_content_charset() or "utf-8"
                    body = payload.decode(charset, errors="replace")
                
                # Dodaj wiadomość do listy
                messages.append({
                    "id": msg_id.decode(),
                    "subject": subject,
                    "from": from_header,
                    "date": msg["Date"],
                    "body": body,
                    "attachments": attachments
                })
            
            conn.logout()
            return messages
        
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania wiadomości: {str(e)}")
            raise
    
    def get_attachments(self, folder: str = None, limit: int = 10, 
                        criteria: str = "ALL") -> List[Dict[str, Any]]:
        """Pobiera załączniki z wiadomości.
        
        Args:
            folder: Folder do przeszukania
            limit: Maksymalna liczba wiadomości do przeszukania
            criteria: Kryteria wyszukiwania (np. "UNSEEN", "ALL")
        
        Returns:
            Lista załączników
        """
        try:
            messages = self.get_messages(folder, limit, criteria)
            
            attachments = []
            for message in messages:
                for attachment in message["attachments"]:
                    attachments.append({
                        "message_id": message["id"],
                        "message_subject": message["subject"],
                        "filename": attachment["filename"],
                        "path": attachment["path"],
                        "content_type": attachment["content_type"]
                    })
            
            return attachments
        
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania załączników: {str(e)}")
            raise
    
    def mark_as_read(self, message_id: str, folder: str = None):
        """Oznacza wiadomość jako przeczytaną.
        
        Args:
            message_id: ID wiadomości
            folder: Folder, w którym znajduje się wiadomość
        """
        try:
            folder = folder or self.default_folder
            conn = self.connect()
            conn.select(folder)
            
            conn.store(message_id.encode(), "+FLAGS", "\\Seen")
            conn.logout()
            
            self.logger.info(f"Wiadomość {message_id} oznaczona jako przeczytana")
        
        except Exception as e:
            self.logger.error(f"Błąd podczas oznaczania wiadomości jako przeczytanej: {str(e)}")
            raise
    
    def delete_message(self, message_id: str, folder: str = None):
        """Usuwa wiadomość.
        
        Args:
            message_id: ID wiadomości
            folder: Folder, w którym znajduje się wiadomość
        """
        try:
            folder = folder or self.default_folder
            conn = self.connect()
            conn.select(folder)
            
            conn.store(message_id.encode(), "+FLAGS", "\\Deleted")
            conn.expunge()
            conn.logout()
            
            self.logger.info(f"Wiadomość {message_id} usunięta")
        
        except Exception as e:
            self.logger.error(f"Błąd podczas usuwania wiadomości: {str(e)}")
            raise


def main():
    """Funkcja główna klienta IMAP."""
    # Konfiguracja logowania
    log_level = os.environ.get("EMAIL_IMAP_LOG_LEVEL", "INFO")
    configure_logging(level=log_level)
    
    # Przykład użycia klienta
    client = IMAPClient(
        host=os.environ.get("EMAIL_IMAP_HOST", "localhost"),
        port=int(os.environ.get("EMAIL_IMAP_PORT", "143")),
        username=os.environ.get("EMAIL_IMAP_USERNAME", "user"),
        password=os.environ.get("EMAIL_IMAP_PASSWORD", "password"),
        use_ssl=os.environ.get("EMAIL_IMAP_USE_SSL", "false").lower() == "true"
    )
    
    try:
        # Pobierz foldery
        folders = client.get_folders()
        print(f"Dostępne foldery: {folders}")
        
        # Pobierz wiadomości
        messages = client.get_messages(limit=5)
        print(f"Pobrano {len(messages)} wiadomości")
        
        # Pobierz załączniki
        attachments = client.get_attachments(limit=5)
        print(f"Pobrano {len(attachments)} załączników")
    
    except Exception as e:
        print(f"Błąd: {str(e)}")


if __name__ == "__main__":
    main()
