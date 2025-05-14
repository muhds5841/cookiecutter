# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

## Spis treści

- [Przegląd](#przegląd)
- [Architektura](#architektura)
- [Struktura projektu](#struktura-projektu)
- [Główne funkcje](#główne-funkcje)
- [Rozpoczęcie pracy](#rozpoczęcie-pracy)
  - [Szybki start](#szybki-start)
  - [Konfiguracja ręczna](#konfiguracja-ręczna)
  - [Konfiguracja środowiska](#konfiguracja-środowiska)
- [Przykłady użycia](#przykłady-użycia)
- [Rozwój](#rozwój)
- [Dokumentacja](#dokumentacja)
- [Licencja](#licencja)

## Przegląd

{{ cookiecutter.project_name }} to modułowy system zaprojektowany do elastycznej integracji z różnymi protokołami komunikacyjnymi i usługami. Projekt został wygenerowany przy użyciu szablonu cookiecutter i zawiera tylko wybrane przez Ciebie moduły.

## Architektura

System jest zbudowany z modułową architekturą, która oddziela poszczególne komponenty i pozwala na ich niezależne wdrażanie:

- **Core Framework**: Wspólne narzędzia do konfiguracji, logowania i obsługi błędów
{% if cookiecutter.use_process == 'yes' %}
- **Process Engine**: Centralny komponent odpowiedzialny za przetwarzanie
{% endif %}
{% if cookiecutter.use_grpc == 'yes' %}
- **gRPC Interface**: Interfejs gRPC do komunikacji między usługami
{% endif %}
{% if cookiecutter.use_rest == 'yes' %}
- **REST API**: Interfejs REST API dla integracji webowej
{% endif %}
{% if cookiecutter.use_mcp == 'yes' %}
- **MCP (Machine Communication Protocol)**: Protokół do komunikacji między maszynami
{% endif %}
{% if cookiecutter.use_mqtt == 'yes' %}
- **MQTT Client/Server**: Implementacja protokołu MQTT dla IoT
{% endif %}
{% if cookiecutter.use_websocket == 'yes' %}
- **WebSocket**: Komunikacja w czasie rzeczywistym przez WebSocket
{% endif %}
{% if cookiecutter.use_webrtc == 'yes' %}
- **WebRTC**: Peer-to-peer komunikacja audio/wideo/danych
{% endif %}
{% if cookiecutter.use_ftp == 'yes' %}
- **FTP Client/Server**: Obsługa protokołu FTP
{% endif %}
{% if cookiecutter.use_ssh == 'yes' %}
- **SSH Client/Server**: Bezpieczna komunikacja przez SSH
{% endif %}
{% if cookiecutter.use_imap == 'yes' or cookiecutter.use_smtp == 'yes' or cookiecutter.use_pop3 == 'yes' %}
- **Email Protocols**: Obsługa protokołów email ({% if cookiecutter.use_imap == 'yes' %}IMAP{% endif %}{% if cookiecutter.use_smtp == 'yes' %}{% if cookiecutter.use_imap == 'yes' %}, {% endif %}SMTP{% endif %}{% if cookiecutter.use_pop3 == 'yes' %}{% if cookiecutter.use_imap == 'yes' or cookiecutter.use_smtp == 'yes' %}, {% endif %}POP3{% endif %})
{% endif %}
{% if cookiecutter.use_shell == 'yes' %}
- **Shell Interface**: Interaktywna powłoka do zarządzania systemem
{% endif %}

## Struktura projektu

```
{{ cookiecutter.project_slug }}/
├── core/                    # Podstawowy framework
│   ├── __init__.py
│   ├── config.py            # Podstawowa konfiguracja
│   ├── logging.py           # Narzędzia do logowania
│   ├── monitoring.py        # Monitorowanie i metryki
│   └── utils.py             # Wspólne narzędzia
{% if cookiecutter.use_process == 'yes' %}
├── process/                 # Silnik procesów
│   ├── __init__.py
│   ├── process.py           # Główna implementacja
│   ├── plugin_system.py     # System wtyczek
│   └── tests/               # Testy jednostkowe
{% endif %}
{% if cookiecutter.use_grpc == 'yes' %}
├── grpc/                    # Usługa gRPC
│   ├── __init__.py
│   ├── server.py            # Implementacja serwera gRPC
│   ├── client.py            # Klient gRPC
│   ├── proto/               # Definicje Protocol Buffer
│   └── tests/               # Testy jednostkowe
{% endif %}
{% if cookiecutter.use_rest == 'yes' %}
├── rest/                    # Usługa REST API
│   ├── __init__.py
│   ├── server.py            # Implementacja serwera REST
│   ├── client.py            # Klient REST
│   ├── routes/              # Definicje tras API
│   └── tests/               # Testy jednostkowe
{% endif %}
{% if cookiecutter.use_mcp == 'yes' %}
├── mcp/                     # Machine Communication Protocol
│   ├── __init__.py
│   ├── server.py            # Serwer MCP
│   ├── client.py            # Klient MCP
│   ├── protocol/            # Obsługa protokołu
│   └── tests/               # Testy jednostkowe
{% endif %}
{% if cookiecutter.use_mqtt == 'yes' %}
├── mqtt/                    # MQTT
│   ├── __init__.py
│   ├── client.py            # Klient MQTT
│   ├── handler.py           # Obsługa wiadomości
│   └── tests/               # Testy jednostkowe
{% endif %}
{% if cookiecutter.use_websocket == 'yes' %}
├── websocket/               # WebSocket
│   ├── __init__.py
│   ├── server.py            # Serwer WebSocket
│   ├── client.py            # Klient WebSocket
│   └── tests/               # Testy jednostkowe
{% endif %}
{% if cookiecutter.use_webrtc == 'yes' %}
├── webrtc/                  # WebRTC
│   ├── __init__.py
│   ├── signaling.py         # Serwer sygnalizacyjny
│   ├── client.py            # Klient WebRTC
│   ├── session.py           # Zarządzanie sesjami
│   └── tests/               # Testy jednostkowe
{% endif %}
{% if cookiecutter.use_ftp == 'yes' %}
├── ftp/                     # FTP
│   ├── __init__.py
│   ├── server.py            # Serwer FTP
│   ├── client.py            # Klient FTP
│   └── tests/               # Testy jednostkowe
{% endif %}
{% if cookiecutter.use_ssh == 'yes' %}
├── ssh/                     # SSH
│   ├── __init__.py
│   ├── server.py            # Serwer SSH
│   ├── client.py            # Klient SSH
│   └── tests/               # Testy jednostkowe
{% endif %}
{% if cookiecutter.use_imap == 'yes' %}
├── imap/                    # IMAP
│   ├── __init__.py
│   ├── client.py            # Klient IMAP
│   └── tests/               # Testy jednostkowe
{% endif %}
{% if cookiecutter.use_smtp == 'yes' %}
├── smtp/                    # SMTP
│   ├── __init__.py
│   ├── client.py            # Klient SMTP
│   └── tests/               # Testy jednostkowe
{% endif %}
{% if cookiecutter.use_pop3 == 'yes' %}
├── pop3/                    # POP3
│   ├── __init__.py
│   ├── client.py            # Klient POP3
│   └── tests/               # Testy jednostkowe
{% endif %}
{% if cookiecutter.use_shell == 'yes' %}
├── shell/                   # Interfejs powłoki
│   ├── __init__.py
│   ├── client.py            # Klient powłoki
│   ├── interactive.py       # Interaktywna powłoka
│   ├── main.py              # Punkt wejścia
│   └── tests/               # Testy jednostkowe
{% endif %}
├── quality/                 # Narzędzia jakości kodu
│   ├── __init__.py
│   └── hooks.py             # Hooki pre-commit
├── scripts/                 # Skrypty pomocnicze
│   └── quality.sh           # Skrypt do sprawdzania jakości kodu
{% if cookiecutter.use_docker == 'yes' %}
├── docker/                  # Konfiguracja Docker
│   ├── Dockerfile           # Główny Dockerfile
│   └── docker-entrypoint.sh # Skrypt wejściowy dla kontenera
├── docker-compose.yml       # Konfiguracja Docker Compose (dev)
├── docker-compose.prod.yml  # Konfiguracja Docker Compose (prod)
{% endif %}
├── pyproject.toml          # Konfiguracja Poetry i narzędzi
├── .pre-commit-config.yaml  # Konfiguracja pre-commit
└── README.md               # Ten plik
```

## Główne funkcje

- **Modułowa architektura**: Każdy komponent może być wdrażany i skalowany niezależnie
{% if cookiecutter.use_grpc == 'yes' or cookiecutter.use_rest == 'yes' or cookiecutter.use_mcp == 'yes' %}
- **Wiele interfejsów**: {% if cookiecutter.use_grpc == 'yes' %}gRPC{% endif %}{% if cookiecutter.use_rest == 'yes' %}{% if cookiecutter.use_grpc == 'yes' %}, {% endif %}REST API{% endif %}{% if cookiecutter.use_mcp == 'yes' %}{% if cookiecutter.use_grpc == 'yes' or cookiecutter.use_rest == 'yes' %}, {% endif %}MCP{% endif %} do integracji z różnymi systemami
{% endif %}
{% if cookiecutter.use_process == 'yes' %}
- **System wtyczek**: Łatwe rozszerzanie funkcjonalności za pomocą wtyczek
{% endif %}
- **Ujednolicona konfiguracja**: Scentralizowane zarządzanie konfiguracją
- **Standardowa obsługa błędów**: Spójna obsługa błędów we wszystkich komponentach
- **Kompleksowe logowanie**: Strukturalne logowanie w całym systemie
{% if cookiecutter.use_docker == 'yes' %}
- **Wsparcie dla Docker**: Konteneryzowane wdrażanie z Docker Compose
{% endif %}
- **Narzędzia deweloperskie**: Uproszczona konfiguracja środowiska deweloperskiego

## Rozpoczęcie pracy

### Szybki start

Najłatwiejszym sposobem na rozpoczęcie pracy jest użycie Poetry do instalacji zależności i uruchomienia projektu:

```bash
# Instalacja zależności
poetry install

# Aktywacja środowiska wirtualnego
poetry shell

# Sprawdzenie jakości kodu
./scripts/quality.sh
```

### Konfiguracja ręczna

Jeśli wolisz ręczną konfigurację, możesz wykonać następujące kroki:

```bash
# Utworzenie wirtualnego środowiska
python -m venv venv

# Aktywacja środowiska (Linux/Mac)
source venv/bin/activate

# Aktywacja środowiska (Windows)
# venv\Scripts\activate

# Instalacja zależności
pip install -e .
```

### Konfiguracja środowiska

Projekt używa zmiennych środowiskowych do konfiguracji. Możesz utworzyć plik `.env` w katalogu głównym projektu z następującymi zmiennymi:

```
# Podstawowa konfiguracja
LOG_LEVEL=INFO
ENVIRONMENT=development

{% if cookiecutter.use_process == 'yes' %}
# Konfiguracja Process
PROCESS_TIMEOUT=30
{% endif %}

{% if cookiecutter.use_grpc == 'yes' %}
# Konfiguracja gRPC
GRPC_HOST=0.0.0.0
GRPC_PORT=50051
{% endif %}

{% if cookiecutter.use_rest == 'yes' %}
# Konfiguracja REST API
REST_HOST=0.0.0.0
REST_PORT=8000
{% endif %}

{% if cookiecutter.use_mqtt == 'yes' %}
# Konfiguracja MQTT
MQTT_BROKER=localhost
MQTT_PORT=1883
{% endif %}

{% if cookiecutter.use_websocket == 'yes' %}
# Konfiguracja WebSocket
WEBSOCKET_HOST=0.0.0.0
WEBSOCKET_PORT=8765
{% endif %}

{% if cookiecutter.use_webrtc == 'yes' %}
# Konfiguracja WebRTC
SIGNALING_HOST=0.0.0.0
SIGNALING_PORT=8080
{% endif %}
```

## Przykłady użycia

{% if cookiecutter.use_grpc == 'yes' %}
### Klient gRPC

```python
from {{ cookiecutter.project_slug }}.grpc.client import ServiceClient

# Utworzenie klienta
client = ServiceClient("localhost:50051")

# Wywołanie metody
response = client.process_request("Przykładowe dane")
print(f"Odpowiedź: {response}")

# Zamknięcie połączenia
client.close()
```
{% endif %}

{% if cookiecutter.use_rest == 'yes' %}
### Klient REST API

```python
from {{ cookiecutter.project_slug }}.rest.client import ServiceClient

# Utworzenie klienta
client = ServiceClient("http://localhost:8000")

# Wywołanie metody
response = client.process_request("Przykładowe dane")
print(f"Odpowiedź: {response}")
```
{% endif %}

{% if cookiecutter.use_mqtt == 'yes' %}
### Klient MQTT

```python
from {{ cookiecutter.project_slug }}.mqtt.client import MqttClient

# Utworzenie klienta
client = MqttClient("localhost", 1883)

# Funkcja callback dla odbieranych wiadomości
def on_message(topic, payload):
    print(f"Otrzymano wiadomość na temacie {topic}: {payload}")

# Połączenie i subskrypcja
client.connect()
client.subscribe("temat/testowy", on_message)

# Publikacja wiadomości
client.publish("temat/testowy", "Testowa wiadomość")

# Rozłączenie
client.disconnect()
```
{% endif %}

{% if cookiecutter.use_webrtc == 'yes' %}
### Klient WebRTC

```python
import asyncio
from {{ cookiecutter.project_slug }}.webrtc.client import WebRTCClient

async def main():
    # Utworzenie klienta
    client = WebRTCClient("ws://localhost:8080")
    
    # Połączenie z serwerem sygnalizacyjnym
    await client.connect()
    
    # Dołączenie do pokoju
    await client.join_room("pokój_testowy")
    
    # Oczekiwanie na połączenia
    await asyncio.sleep(60)
    
    # Zamknięcie połączenia
    await client.close()

asyncio.run(main())
```
{% endif %}

{% if cookiecutter.use_shell == 'yes' %}
### Interaktywna powłoka

```bash
# Uruchomienie interaktywnej powłoki
python -m {{ cookiecutter.project_slug }}.shell.main

# W powłoce możesz używać komend takich jak:
# help - wyświetla dostępne komendy
# run <command> - uruchamia polecenie systemowe
# list - wyświetla listę procesów
# kill <pid> - kończy proces o podanym PID
```
{% endif %}

## Rozwój

Aby rozwijać projekt, zalecamy następujące kroki:

```bash
# Instalacja zależności deweloperskich
poetry install --with dev

# Konfiguracja pre-commit hooków
pre-commit install

# Uruchomienie testów
pytest

# Sprawdzenie jakości kodu
./scripts/quality.sh
```

{% if cookiecutter.use_process == 'yes' %}
### Dodawanie nowych wtyczek

Aby dodać nową wtyczkę do systemu:

1. Utwórz nową klasę w katalogu `process/plugins/`
2. Zaimplementuj interfejs `ProcessPlugin`
3. Zarejestruj wtyczkę w systemie

Przykład:

```python
from {{ cookiecutter.project_slug }}.process.plugin_system import ProcessPlugin, register_plugin

@register_plugin
class MyPlugin(ProcessPlugin):
    """Moja własna wtyczka."""
    
    def __init__(self):
        super().__init__("my_plugin")
    
    def process(self, data):
        """Przetwarzanie danych."""
        return f"Przetworzone: {data}"
```
{% endif %}

{% if cookiecutter.use_grpc == 'yes' or cookiecutter.use_rest == 'yes' %}
### Tworzenie nowych interfejsów usług

Aby dodać nowy interfejs usługi:

{% if cookiecutter.use_grpc == 'yes' %}
#### gRPC

1. Zdefiniuj nowy serwis w pliku `.proto` w katalogu `grpc/proto/`
2. Wygeneruj kod za pomocą `grpcio-tools`
3. Zaimplementuj serwer w `grpc/server.py`
4. Zaimplementuj klienta w `grpc/client.py`
{% endif %}

{% if cookiecutter.use_rest == 'yes' %}
#### REST API

1. Dodaj nową trasę w katalogu `rest/routes/`
2. Zaimplementuj odpowiedni endpoint w `rest/server.py`
3. Zaktualizuj klienta w `rest/client.py`
{% endif %}
{% endif %}

## Dokumentacja

Dokumentacja projektu jest dostępna w katalogu `docs/`. Zawiera ona szczegółowe informacje na temat:

- Architektury systemu
- Konfiguracji poszczególnych modułów
- API dla każdego interfejsu usługi
- Przykładów użycia
- Przewodnika rozwijania projektu

Aby wygenerować dokumentację w formacie HTML, możesz użyć następującego polecenia:

```bash
# Instalacja zależności do generowania dokumentacji
pip install mkdocs mkdocs-material

# Generowanie dokumentacji
mkdocs build
```

## Licencja

Ten projekt jest udostępniany na licencji {{ cookiecutter.license }}. Zobacz plik LICENSE, aby uzyskać więcej informacji.