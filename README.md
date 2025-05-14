# Cookiecutter Project

Szablon cookiecutter do generowania projektów z najlepszymi praktykami jakości kodu.

Repozytorium: [https://github.com/pyfunc/cookiecutter.git](https://github.com/pyfunc/cookiecutter.git)
Autor: Tom Sapletta

---

## Spis treści
- [Opis](#opis)
- [Struktura projektu](#struktura-projektu)
- [Instalacja](#instalacja)
- [Uruchamianie](#uruchamianie)
- [Funkcjonalności](#funkcjonalności)
- [Konfiguracja](#konfiguracja)
- [Testy](#testy)
- [Jakość kodu](#jakość-kodu)
- [FAQ i przydatne polecenia](#faq-i-przydatne-polecenia)
- [Generowanie projektu](#generowanie-projektu)

---

## Opis

Szablon cookiecutter do generowania projektów z najlepszymi praktykami jakości kodu.

## Struktura projektu

```
cookiecutter-project/
├── cookiecutter.json                  # Konfiguracja szablonu
├── README.md                          # Dokumentacja szablonu
├── hooks/                             # Skrypty hook
│   ├── pre_gen_project.py             # Uruchamiany przed generowaniem
│   └── post_gen_project.py            # Uruchamiany po wygenerowaniu projektu
└── {{cookiecutter.project_slug}}/     # Katalog szablonu projektu
    ├── docker-compose.yml
    ├── Makefile                       # Główny Makefile
    ├── pyproject.toml                 # Konfiguracja Poetry
    ├── README.md                      # Dokumentacja projektu
    ├── .gitignore                     # Pliki ignorowane przez Git
    ├── core/                           # Rdzeń frameworka
    │   ├── __init__.py
    │   ├── config.py                    # Podstawowa konfiguracja
    │   ├── config_manager.py            # Zaawansowane zarządzanie konfiguracją
    │   ├── logging.py                   # Narzędzia logowania
    │   ├── utils.py                     # Wspólne narzędzia
    │   └── error_handling.py            # Standardowa obsługa błędów
    ├── grpc/                         # Usługa gRPC
    │   ├── Dockerfile
    │   ├── pyproject.toml
    │   ├── server.py                    # Implementacja serwera gRPC
    │   ├── client.py                    # Klient gRPC
    │   └── proto/                       # Definicje Protocol Buffer
    ├── rest/                         # Usługa REST API
    │   ├── Dockerfile
    │   ├── pyproject.toml
    │   ├── server.py                    # Implementacja serwera REST
    │   └── client.py                    # Klient REST
    ├── mcp/                          # Model Context Protocol
    │   ├── Dockerfile
    │   ├── pyproject.toml
    │   ├── mcp_server.py                # Serwer MCP
    │   ├── tools/                       # Narzędzia MCP
    │   ├── resources/                   # Zasoby MCP
    │   └── transports/                  # Implementacje transportów
    ├── mqtt/                         # Usługa MQTT
    │   ├── Dockerfile
    │   ├── server.py                    # Serwer MQTT
    │   └── client.py                    # Klient MQTT
    ├── websocket/                    # Usługa WebSocket
    │   ├── Dockerfile
    │   ├── server.py                    # Serwer WebSocket
    │   └── client.py                    # Klient WebSocket
    ├── langchain/                    # Integracja z LangChain dla LLM
    │   ├── Dockerfile
    │   ├── tools.py                     # Narzędzia LangChain
    │   └── chains.py                    # Łańcuchy LangChain
    ├── quality/                      # Narzędzia jakości kodu
    │   ├── __init__.py
    │   ├── lint.py
    │   ├── format.py
    │   ├── security.py
    │   └── complexity.py
    ├── process/                       # Silnik Process
    │   ├── Dockerfile
    │   ├── pyproject.toml
    │   ├── __init__.py
    │   ├── process.py                   # Główna implementacja Process
    │   ├── process_base.py              # Klasa bazowa abstrakcyjna
    │   ├── plugin_system.py             # Architektura wtyczek
    │   └── adapters/                    # Adaptery dla różnych implementacji
    │   ├── __init__.py
    │   ├── process.py
    ├── tests/                         # Testy
        ├── __init__.py
        ├── conftest.py
        └── mcp_tests/                 # Testy komponentów MCP
            ├── __init__.py
            ├── test_transports.py
            ├── test_protocol.py
            └── test_tools.py
```

## Instalacja

```bash
# Instalacja zależności (jeśli nie została wykonana automatycznie)
poetry install
```

## Uruchamianie

```bash
# Ustaw uprawnienia wykonywania dla skryptów
chmod +x hooks/pre_gen_project.py
chmod +x hooks/post_gen_project.py
```
```bash
# Uruchomienie serwisów w kontenerach
make up
```

{% if cookiecutter.components.mcp %}
Aby uruchomić serwer MCP:
```bash
cd mcp
poetry run python mcp_server.py
```
{% endif %}

## Funkcjonalności

- Modularny system z wieloma komponentami
- Wsparcie dla różnych protokołów komunikacyjnych (gRPC, REST, WebRTC, MCP, MQTT, WebSocket)
- Integracja z Model Context Protocol (MCP)
- Narzędzia zapewnienia jakości kodu (Black, isort, Flake8, mypy)
- Automatyczna konfiguracja pre-commit hooks
- Comprehensive Makefile for common tasks
- Konfiguracja Docker i docker-compose (opcjonalnie)

## Konfiguracja

### Konfiguracja szablonu

- Konfiguracja projektu znajduje się w pliku `cookiecutter.json`.

### Konfiguracja środowiska

Wygenerowany projekt używa spójnego systemu zmiennych środowiskowych z prefiksami dla każdego komponentu:

- `CORE_*` - Ustawienia rdzenia frameworka
- `PROCESS_*` - Ustawienia silnika Process
- `GRPC_*` - Ustawienia usługi gRPC
- `REST_*` - Ustawienia usługi REST API
- `MCP_*` - Ustawienia usługi MCP
- `MQTT_*` - Ustawienia usługi MQTT
- `WEBSOCKET_*` - Ustawienia usługi WebSocket
- `LANGCHAIN_*` - Ustawienia integracji LangChain

Można używać jednego pliku `.env` dla całego projektu lub oddzielnych plików dla każdego komponentu:

```bash
# Kopiowanie przykładowych plików środowiskowych
cp .env.example .env

# Lub dla poszczególnych komponentów
cp process/.env.example process/.env
cp grpc/.env.example grpc/.env
cp rest/.env.example rest/.env
cp mcp/.env.example mcp/.env
cp mqtt/.env.example mqtt/.env
cp websocket/.env.example websocket/.env
```

Szczegółowa dokumentacja zmiennych środowiskowych znajduje się w pliku `docs/environment_variables.md`.

## Testy

```bash
make test
```

## Jakość kodu

```bash
make quality
```

## FAQ i przydatne polecenia

- Aktualizacja zależności: `poetry update`
- Sprawdzenie statusu kontenerów: `docker ps`
- Restart wybranego serwisu: `docker-compose restart <nazwa>`

## Generowanie projektu

Aby wygenerować nowy projekt na podstawie tego szablonu, wykonaj następujące kroki:

```bash
# Instalacja cookiecutter
pip install cookiecutter

# Generowanie projektu
cookiecutter https://github.com/pyfunc/cookiecutter.git
```

Następnie odpowiedz na pytania dotyczące konfiguracji projektu.

## Architektura modularna

Wygenerowany projekt ma modularną architekturę, która pozwala na:

1. **Niezależne komponenty**: Każdy serwis (gRPC, REST, MCP, MQTT, WebSocket) może działać jako niezależne repozytorium.
2. **Niezależność językowa**: Usługi mogą być implementowane w różnych językach (Python, Go, itp.).
3. **Minimalne zależności**: Każda usługa ma minimalne zależności od innych komponentów.
4. **Standaryzowane interfejsy**: Jasne definicje kontraktów między komponentami.
5. **Wspólne narzędzia**: Funkcjonalność wspólna dostępna, ale niewymagana.

Szczegółowa dokumentacja architektury znajduje się w pliku `docs/modular_architecture.md`.

## Integracja z LLM

Projekt zawiera komponenty do integracji z dużymi modelami językowymi (LLM):

1. **MCP (Model Context Protocol)**: Protokół do integracji z LLM jako narzędzie.
2. **LangChain**: Integracja z bibliotekami LangChain do tworzenia aplikacji opartych na LLM.
3. **MQTT i WebSocket**: Protokoły komunikacyjne do integracji z różnymi systemami.

Szczegółowa dokumentacja integracji z LLM znajduje się w pliku `docs/llm_integration.md`.

## 6. Analiza optymalności dla generowania kodu

### 6.1. Zalety zaktualizowanej struktury

1. **Oddzielne Dockerfile dla każdej usługi** - pozwala na dokładne dopasowanie środowiska do wymagań poszczególnych komponentów
2. **Modularność** - każdy serwis działa w swoim kontenerze, co ułatwia niezależny rozwój i wdrażanie
3. **Jasna integracja MCP** - dedykowany komponent MCP z własnymi narzędziami i zasobami
4. **Spójne konwencje** - każdy moduł ma podobną strukturę, co ułatwia generowanie kodu

### 6.2. Optymalizacja dla generatywnego kodu

Ta struktura jest optymalna dla generowania kodu przez AI z następujących powodów:

1. **Jasno zdefiniowane granice** - każda usługa ma swój własny katalog, co ułatwia generowanie kodu dla konkretnej części systemu
2. **Powtarzalne wzorce** - podobna struktura dla wszystkich serwisów pozwala na użycie szablonów
3. **Modularność** - możliwość generowania kodu dla jednego komponentu bez konieczności zrozumienia całego systemu
4. **Jawne zależności** - jasno określone zależności między komponentami ułatwiają generowanie kodu integracyjnego

### 6.3. Przystosowanie dla MCP

Dodanie komponentu MCP pozwala na:

1. **Łatwą integrację z LLM** - standaryzowany protokół komunikacji z modelami językowymi
2. **Udostępnianie Process jako narzędzia** - modele mogą wykorzystywać syntezę mowy w swoich odpowiedziach
3. **Rozszerzalność** - możliwość dodawania nowych narzędzi i zasobów MCP w przyszłości

## 7. Wnioski

Zaktualizowana struktura projektu, z indywidualnymi Dockerfile dla każdego serwisu i komponentem MCP, jest dobrze dostosowana do:

1. **Efektywnego generowania kodu** - jasna struktura i granice między komponentami
2. **Łatwego wdrażania** - niezależne kontenery dla każdej usługi
3. **Elastycznej integracji** - różne protokoły komunikacji (gRPC, REST, WebRTC, MCP)
4. **Skalowalności** - możliwość skalowania poszczególnych komponentów niezależnie

Taka architektura pozwala na szybkie generowanie kodu dla poszczególnych komponentów, 
zachowując jednocześnie modularność i elastyczność całego systemu.

