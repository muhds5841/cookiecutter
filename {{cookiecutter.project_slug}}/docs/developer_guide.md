# Process System - Developer Guide

## Spis treści

1. [Wprowadzenie](#wprowadzenie)
2. [Architektura systemu](#architektura-systemu)
3. [Rozpoczęcie pracy](#rozpoczęcie-pracy)
4. [Główne komponenty](#główne-komponenty)
   - [Process Engine](#process-engine)
   - [Interfejsy usług](#interfejsy-usług)
   - [System wtyczek](#system-wtyczek)
5. [Przewodniki implementacji](#przewodniki-implementacji)
   - [Tworzenie nowego procesu](#tworzenie-nowego-procesu)
   - [Dodawanie wtyczki](#dodawanie-wtyczki)
   - [Implementacja nowego interfejsu usługi](#implementacja-nowego-interfejsu-usługi)
6. [Najlepsze praktyki](#najlepsze-praktyki)
7. [Rozwiązywanie problemów](#rozwiązywanie-problemów)
8. [Referencje API](#referencje-api)

## Wprowadzenie

Process System to modułowa i rozszerzalna platforma do przetwarzania tekstu z wieloma interfejsami usług, w tym gRPC, REST API i integracją z Model Context Protocol (MCP). System został zaprojektowany z myślą o elastyczności, umożliwiając łatwe rozszerzanie funkcjonalności i integrację z różnymi systemami.

### Główne cechy

- **Modułowa architektura**: Każdy komponent może być wdrażany i skalowany niezależnie
- **Wiele interfejsów**: gRPC, REST API i MCP do integracji z różnymi systemami
- **System wtyczek**: Łatwe rozszerzanie funkcjonalności za pomocą wtyczek
- **Ujednolicona konfiguracja**: Scentralizowane zarządzanie konfiguracją
- **Standardowa obsługa błędów**: Spójna obsługa błędów we wszystkich komponentach
- **Kompleksowe logowanie**: Ustrukturyzowane logowanie w całym systemie
- **Wsparcie dla Dockera**: Konteneryzacja z Docker Compose

## Architektura systemu

System Process składa się z następujących głównych komponentów:

```
project/
├── process/                  # Silnik Process
│   ├── process.py            # Główna implementacja Process
│   ├── process_base.py       # Klasa bazowa abstrakcyjna
│   └── plugin_system.py      # System wtyczek
├── core/                     # Rdzeń frameworka
│   ├── config.py             # Podstawowa konfiguracja
│   ├── config_manager.py     # Zaawansowane zarządzanie konfiguracją
│   ├── logging.py            # Narzędzia logowania
│   ├── utils.py              # Wspólne narzędzia
│   └── error_handling.py     # Standardowa obsługa błędów
├── grpc/                     # Usługa gRPC
│   ├── server.py             # Implementacja serwera gRPC
│   ├── client.py             # Klient gRPC
│   └── proto/                # Definicje Protocol Buffer
├── rest/                     # Usługa REST API
│   ├── server.py             # Implementacja serwera REST
│   └── client.py             # Klient REST
└── mcp/                      # Model Context Protocol
    ├── mcp_server.py         # Serwer MCP
    ├── tools/                # Narzędzia MCP
    └── resources/            # Zasoby MCP
```

Każdy komponent jest zaprojektowany tak, aby mógł działać niezależnie, umożliwiając elastyczne wdrażanie i skalowanie.

## Rozpoczęcie pracy

### Wymagania wstępne

- Python 3.8 lub nowszy
- Docker i Docker Compose (opcjonalnie, do konteneryzacji)
- Poetry (do zarządzania zależnościami)

### Instalacja

Najłatwiejszym sposobem rozpoczęcia pracy jest użycie skryptu konfiguracji środowiska deweloperskiego:

```bash
# Konfiguracja środowiska deweloperskiego
python dev_setup.py

# Uruchomienie usług
docker-compose up -d
```

### Ręczna konfiguracja

Jeśli wolisz ręcznie skonfigurować środowisko:

```bash
# Instalacja zależności dla każdego komponentu
cd process && poetry install
cd ../grpc && poetry install
cd ../rest && poetry install
cd ../mcp && poetry install

# Konfiguracja hooków pre-commit
pip install pre-commit
pre-commit install
```

### Konfiguracja środowiska

Każdy komponent ma plik `.env.example`, który można skopiować do `.env` i dostosować:

```bash
cp process/.env.example process/.env
cp grpc/.env.example grpc/.env
cp rest/.env.example rest/.env
cp mcp/.env.example mcp/.env
```

## Główne komponenty

### Process Engine

Process Engine to centralny komponent odpowiedzialny za przetwarzanie tekstu. Jest zbudowany wokół abstrakcyjnej klasy bazowej `ProcessBase`, która definiuje standardowy interfejs dla wszystkich implementacji Process.

#### Używanie Process Engine

```python
from process.process import Process

# Inicjalizacja silnika Process
process = Process()

# Przetwarzanie tekstu
result = process.process_text("Tekst do przetworzenia", language="pl-PL")

# Dostęp do wyniku
output_data = result.data
output_format = result.format
```

#### Konfiguracja Process Engine

Process Engine można skonfigurować za pomocą pliku konfiguracyjnego lub zmiennych środowiskowych:

```python
from core.config_manager import create_config_manager

# Utworzenie menedżera konfiguracji dla komponentu
config = create_config_manager("process")

# Dostęp do wartości konfiguracyjnych
value = config.get("KEY", "default_value")
```

### Interfejsy usług

System Process udostępnia trzy główne interfejsy usług:

#### gRPC

Interfejs gRPC zapewnia wydajną komunikację między usługami:

```python
# Klient gRPC
from grpc.client import ProcessClient

client = ProcessClient("localhost:50051")
result = client.process_text("Tekst do przetworzenia", language="pl-PL")
```

#### REST API

Interfejs REST API zapewnia łatwą integrację z aplikacjami webowymi:

```python
# Klient REST
from rest.client import ProcessClient

client = ProcessClient("http://localhost:5000")
result = client.process_text("Tekst do przetworzenia", language="pl-PL")
```

#### Model Context Protocol (MCP)

Interfejs MCP umożliwia integrację z dużymi modelami językowymi (LLM):

```python
# Uruchomienie serwera MCP
python -m mcp.mcp_server

# Połączenie z serwerem MCP
# (zazwyczaj używane przez LLM poprzez protokół MCP)
```

### System wtyczek

System Process można rozszerzyć za pomocą wtyczek, które dodają nowe funkcje przetwarzania.

#### Struktura wtyczki

```python
from process.process_base import ProcessBase

class CustomPlugin(ProcessBase):
    """Niestandardowa wtyczka przetwarzania."""
    
    def __init__(self, config=None):
        super().__init__(config)
        # Inicjalizacja wtyczki
    
    def process_text(self, text, **options):
        # Implementacja przetwarzania tekstu
        return processed_text
    
    def get_resources(self):
        # Zwraca dostępne zasoby dla tej wtyczki
        return resources
```

#### Rejestracja wtyczki

```python
from process.plugin_system import PluginRegistry

# Rejestracja wtyczki
registry = PluginRegistry()
registry.register_plugin("custom", CustomPlugin)

# Użycie wtyczki
plugin = registry.get_plugin("custom")
result = plugin.process_text("Tekst do przetworzenia")
```

## Przewodniki implementacji

### Tworzenie nowego procesu

Aby utworzyć nową implementację procesu:

1. Utwórz nową klasę, która dziedziczy po `ProcessBase`:

```python
from process.process_base import ProcessBase

class MyProcess(ProcessBase):
    """Moja implementacja procesu."""
    
    def __init__(self, config=None):
        super().__init__(config)
        # Inicjalizacja
    
    def process_text(self, text, **options):
        # Implementacja przetwarzania tekstu
        return self.create_result(data, format="text")
    
    def get_resources(self):
        # Zwraca dostępne zasoby
        return {"resources": [...]}
```

2. Zarejestruj proces w systemie wtyczek (opcjonalnie):

```python
from process.plugin_system import PluginRegistry

registry = PluginRegistry()
registry.register_plugin("my_process", MyProcess)
```

### Dodawanie wtyczki

Aby dodać nową wtyczkę:

1. Utwórz nowy moduł w katalogu wtyczek:

```
process/plugins/my_plugin.py
```

2. Zaimplementuj klasę wtyczki:

```python
from process.process_base import ProcessBase

class MyPlugin(ProcessBase):
    """Moja wtyczka przetwarzania."""
    
    def process_text(self, text, **options):
        # Implementacja przetwarzania
        return self.create_result(processed_data, format="text")
```

3. Dodaj plik `__init__.py` do katalogu wtyczek, który rejestruje wtyczkę:

```python
from process.plugin_system import PluginRegistry
from .my_plugin import MyPlugin

def register_plugins():
    registry = PluginRegistry()
    registry.register_plugin("my_plugin", MyPlugin)
```

### Implementacja nowego interfejsu usługi

Aby zaimplementować nowy interfejs usługi (np. WebSocket):

1. Utwórz nowy katalog dla usługi:

```
websocket/
├── __init__.py
├── server.py
└── client.py
```

2. Zaimplementuj serwer:

```python
import asyncio
import websockets
import json
import sys
import os

# Dodaj katalog nadrzędny do ścieżki
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from process.process import Process
from core.logging import get_logger

class WebSocketServer:
    def __init__(self, host="0.0.0.0", port=6789):
        self.host = host
        self.port = port
        self.logger = get_logger("websocket.server")
        self.process = Process()
    
    async def handle_client(self, websocket, path):
        async for message in websocket:
            try:
                data = json.loads(message)
                text = data.get("text", "")
                options = data.get("options", {})
                
                result = self.process.process_text(text, **options)
                
                await websocket.send(json.dumps({
                    "result_id": result.result_id,
                    "format": result.format,
                    "data": result.data
                }))
            except Exception as e:
                self.logger.error(f"Error: {e}")
                await websocket.send(json.dumps({"error": str(e)}))
    
    async def start(self):
        self.server = await websockets.serve(
            self.handle_client, self.host, self.port
        )
        self.logger.info(f"WebSocket server running on {self.host}:{self.port}")
        await self.server.wait_closed()

def main():
    server = WebSocketServer()
    asyncio.run(server.start())

if __name__ == "__main__":
    main()
```

3. Zaimplementuj klienta:

```python
import asyncio
import websockets
import json
import sys
import os

# Dodaj katalog nadrzędny do ścieżki
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.logging import get_logger

class WebSocketClient:
    def __init__(self, url="ws://localhost:6789"):
        self.url = url
        self.logger = get_logger("websocket.client")
    
    async def process_text(self, text, **options):
        async with websockets.connect(self.url) as websocket:
            request = {
                "text": text,
                "options": options
            }
            
            await websocket.send(json.dumps(request))
            response = await websocket.recv()
            
            return json.loads(response)
    
    def process_text_sync(self, text, **options):
        return asyncio.run(self.process_text(text, **options))
```

4. Dodaj plik Dockerfile:

```dockerfile
FROM python:3.8-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

COPY . .

CMD ["python", "-m", "websocket.server"]
```

## Najlepsze praktyki

### Konfiguracja

1. Używaj modułu `core.config_manager` do wszystkich potrzeb konfiguracyjnych
2. Definiuj jasne nazwy zmiennych środowiskowych z prefiksami komponentów
3. Waliduj konfigurację przed jej użyciem
4. Używaj nakładek konfiguracyjnych dla różnych środowisk

### Logowanie

1. Pobieraj logger dla każdego modułu z określoną nazwą
2. Używaj odpowiednich poziomów logowania dla różnych typów komunikatów
3. Dołączaj odpowiedni kontekst w komunikatach logowania
4. Konfiguruj logowanie na poziomie aplikacji

### Obsługa błędów

1. Definiuj konkretne typy błędów dla różnych warunków
2. Używaj standardowych kodów błędów dla spójnego raportowania
3. Dołączaj istotne szczegóły w komunikatach o błędach
4. Obsługuj błędy na odpowiednim poziomie
5. Konwertuj wyjątki na standardowe błędy przed zwróceniem do klientów

### Narzędzia

1. Używaj dostarczonych funkcji narzędziowych zamiast reimplementowania wspólnej funkcjonalności
2. Utrzymuj funkcje narzędziowe skupione na jednej odpowiedzialności
3. Jasno dokumentuj funkcje narzędziowe

## Rozwiązywanie problemów

### Typowe problemy

#### Problem: Usługa nie uruchamia się

**Rozwiązanie**: Sprawdź:
- Czy wszystkie zależności są zainstalowane
- Czy pliki konfiguracyjne istnieją i są poprawne
- Czy wymagane porty są dostępne
- Logi błędów w konsoli lub plikach logów

#### Problem: Błędy komunikacji między usługami

**Rozwiązanie**: Sprawdź:
- Czy wszystkie usługi są uruchomione
- Czy adresy URL/porty są poprawne
- Czy sieci Docker są poprawnie skonfigurowane
- Czy zapory ogniowe nie blokują komunikacji

#### Problem: Wtyczka nie jest wykrywana

**Rozwiązanie**: Sprawdź:
- Czy wtyczka jest poprawnie zarejestrowana
- Czy struktura katalogów jest poprawna
- Czy pliki `__init__.py` zawierają kod rejestracji
- Logi na poziomie DEBUG, aby zobaczyć proces ładowania wtyczek

### Debugowanie

Włącz logowanie na poziomie DEBUG, aby uzyskać więcej informacji:

```bash
# Ustaw poziom logowania na DEBUG
export LOG_LEVEL=debug

# Uruchom usługę
python -m rest.server
```

## Referencje API

### Process Engine

#### `ProcessBase`

Abstrakcyjna klasa bazowa dla wszystkich implementacji Process.

```python
class ProcessBase:
    def __init__(self, config=None):
        """Inicjalizuje bazową klasę Process."""
        
    def process_text(self, text, **options):
        """Przetwarza tekst z podanymi opcjami."""
        
    def get_resources(self):
        """Zwraca dostępne zasoby."""
        
    def create_result(self, data, format="text", metadata=None):
        """Tworzy obiekt wyniku."""
```

#### `Process`

Główna implementacja silnika Process.

```python
class Process(ProcessBase):
    def __init__(self, config=None):
        """Inicjalizuje silnik Process."""
        
    def process_text(self, text, **options):
        """Przetwarza tekst z podanymi opcjami."""
        
    def get_resources(self):
        """Zwraca dostępne zasoby."""
```

### Core Framework

#### `ConfigManager`

Zarządza konfiguracją dla komponentów.

```python
class ConfigManager:
    def __init__(self, component_name, config_path=None):
        """Inicjalizuje menedżera konfiguracji."""
        
    def get(self, key, default=None):
        """Pobiera wartość konfiguracyjną."""
        
    def set(self, key, value):
        """Ustawia wartość konfiguracyjną."""
        
    def validate(self, schema):
        """Waliduje konfigurację względem schematu."""
        
    def as_dict(self):
        """Zwraca całą konfigurację jako słownik."""
```

#### `ErrorHandling`

Standardowa obsługa błędów.

```python
class ProcessError(Exception):
    """Bazowa klasa dla wszystkich błędów Process."""
    
    def __init__(self, message, code=None, details=None):
        """Inicjalizuje błąd Process."""

def create_error_handler(component_name):
    """Tworzy handler błędów dla komponentu."""
```

### System wtyczek

#### `PluginRegistry`

Rejestruje i zarządza wtyczkami.

```python
class PluginRegistry:
    def register_plugin(self, name, plugin_class):
        """Rejestruje wtyczkę."""
        
    def get_plugin(self, name):
        """Pobiera wtyczkę według nazwy."""
        
    def get_all_plugins(self):
        """Zwraca wszystkie zarejestrowane wtyczki."""
        
    def discover_plugins(self, directory):
        """Odkrywa wtyczki w katalogu."""
```

### Interfejsy usług

#### gRPC

```python
class ProcessClient:
    def __init__(self, server_address):
        """Inicjalizuje klienta gRPC."""
        
    def process_text(self, text, **options):
        """Przetwarza tekst za pomocą serwera gRPC."""
        
    def get_resources(self):
        """Pobiera dostępne zasoby."""
```

#### REST

```python
class ProcessClient:
    def __init__(self, base_url):
        """Inicjalizuje klienta REST."""
        
    def process_text(self, text, **options):
        """Przetwarza tekst za pomocą serwera REST."""
        
    def get_resources(self):
        """Pobiera dostępne zasoby."""
```

#### MCP

```python
class ProcessTool:
    def __init__(self, config):
        """Inicjalizuje narzędzie Process dla MCP."""
        
    def get_schema(self):
        """Zwraca schemat narzędzia."""
        
    def execute(self, parameters):
        """Wykonuje narzędzie z podanymi parametrami."""
```

---

To jest podstawowa dokumentacja dla deweloperów systemu Process. Dla bardziej szczegółowych informacji na temat konkretnych komponentów, zapoznaj się z dokumentacją w odpowiednich katalogach.
