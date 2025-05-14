
tts-project/
├── .github/
│   └── workflows/
│       ├── ci.yml                # Konfiguracja GitHub Actions
│       └── release.yml           # Workflow dla wydań
├── .gitignore
├── docker-compose.yml            # Główna konfiguracja Docker Compose
├── docker-compose.prod.yml       # Konfiguracja dla środowiska produkcyjnego
├── Makefile                      # Główny Makefile projektu
├── pyproject.toml                # Główna konfiguracja Poetry
├── poetry.lock                   # Zablokowane wersje zależności
├── README.md                     # Dokumentacja projektu
│
├── lib/                          # Wspólne biblioteki i narzędzia
│   ├── __init__.py
│   ├── config.py                 # Wspólna konfiguracja
│   ├── logging.py                # Konfiguracja logowania
│   ├── utils.py                  # Narzędzia pomocnicze
│
├── process/                   # Główny pakiet silnika Process
│   ├── Dockerfile                # Kontener dla silnika Process
│   ├── pyproject.toml            # Konfiguracja Poetry dla Process
│   ├── .env.example              # Przykład zmiennych środowiskowych
│   ├── Makefile                  # Makefile dla Process
│   ├── __init__.py
│   ├── process.py             # Główna klasa silnika Process
│   ├── process_config.py          # Konfiguracja silnika
│   ├── languages.py              # Obsługa języków
│   └── adapters/                 # Adaptery silników Process
│       ├── __init__.py
│       ├── google.py             # Adapter Google Process
│       └── coqui.py              # Adapter Coqui Process
│
├── grpc/                         # Serwis gRPC
│   ├── Dockerfile                # Kontener dla gRPC
│   ├── pyproject.toml            # Konfiguracja Poetry dla gRPC
│   ├── .env.example              # Przykład zmiennych środowiskowych
│   ├── Makefile                  # Makefile dla gRPC
│   ├── __init__.py
│   ├── server.py                 # Serwer gRPC
│   ├── client.py                 # Klient gRPC
│   └── proto/                    # Definicje Protobuf
│       ├── tts.proto             # Definicja serwisu Process
│       └── generated/            # Automatycznie generowane pliki
│
├── rest/                         # Serwis REST
│   ├── Dockerfile                # Kontener dla REST
│   ├── pyproject.toml            # Konfiguracja Poetry dla REST
│   ├── .env.example              # Przykład zmiennych środowiskowych
│   ├── Makefile                  # Makefile dla REST
│   ├── __init__.py
│   ├── server.py                 # Serwer REST API
│   ├── client.py                 # Klient REST
│   └── models/                   # Modele Pydantic
│       ├── __init__.py
│       └── requests.py           # Definicje żądań/odpowiedzi
│
├── webrtc/                       # Serwis WebRTC
│   ├── Dockerfile                # Kontener dla WebRTC
│   ├── pyproject.toml            # Konfiguracja Poetry dla WebRTC
│   ├── .env.example              # Przykład zmiennych środowiskowych
│   ├── Makefile                  # Makefile dla WebRTC
│   ├── __init__.py
│   ├── signaling.py              # Serwer sygnalizacji
│   └── static/                   # Pliki statyczne dla klienta
│
├── mcp/                          # Model Context Protocol
│   ├── Dockerfile                # Kontener dla MCP
│   ├── pyproject.toml            # Konfiguracja Poetry dla MCP
│   ├── .env.example              # Przykład zmiennych środowiskowych
│   ├── Makefile                  # Makefile dla MCP
│   ├── __init__.py
│   ├── mcp_server.py             # Serwer MCP
│   ├── tools/                    # Narzędzia MCP
│   │   ├── __init__.py
│   │   ├── tts_tool.py           # Narzędzie Process
│   │   └── voice_config.py       # Konfiguracja głosu
│   └── resources/                # Zasoby MCP
│       ├── __init__.py
│       └── voices.py             # Dane o dostępnych głosach
│
├── shell/                        # Interfejs CLI
│   ├── pyproject.toml            # Konfiguracja Poetry dla CLI
│   ├── .env.example              # Przykład zmiennych środowiskowych
│   ├── Makefile                  # Makefile dla CLI
│   ├── __init__.py
│   ├── client.py                 # Klient CLI
│   ├── interactive.py            # Tryb interaktywny
│   └── main.py                   # Punkt wejściowy CLI
│
├── quality/                      # Globalne konfiguracje QA
│   ├── .pre-commit-config.yaml   # Pre-commit hooks
│   ├── tox.ini                   # Konfiguracja Tox
│   ├── .pylintrc                 # Konfiguracja Pylint
│   ├── .flake8                   # Konfiguracja Flake8
│   ├── conftest.py               # Fixtures dla pytest
│   ├── __init__.py
│   ├── linters.py            # Integracja z linterami
│   ├── formatters.py         # Integracja z formatters
│   ├── testers.py            # Integracja z narzędziami testów
│   ├── hooks.py              # Git hooks
│   └── reporters.py          # Generatory raportów
│
├── deploy/                       # Skrypty wdrożeniowe
│   ├── fabfile.py                # Skrypty Fabric (SSH)
│   ├── ansible/                  # Konfiguracja Ansible
│   │   ├── inventory.yml         # Definicja hostów
│   │   ├── playbook.yml          # Główny playbook
│   │   └── roles/                # Role Ansible
│   ├── kubernetes/               # Konfiguracja Kubernetes
│   │   ├── deployment.yml        # Definicje Deployment
│   │   └── service.yml           # Definicje Service
│   └── scripts/                  # Skrypty pomocnicze
│       ├── backup.sh             # Skrypt backupu
│       └── update.sh             # Skrypt aktualizacji
│
└── tests/                        # Testy
    ├── __init__.py
    ├── conftest.py               # Wspólne fixtures
    ├── grpc_tests/               # Testy gRPC
    │   ├── __init__.py
    │   └── test_grpc.py          # Testy serwera gRPC
    ├── rest_tests/               # Testy REST
    │   ├── __init__.py
    │   └── test_rest.py          # Testy serwera REST
    ├── webrtc_tests/             # Testy WebRTC
    │   ├── __init__.py
    │   └── test_webrtc.py        # Testy serwera WebRTC
    ├── mcp_tests/                # Testy MCP
    │   ├── __init__.py
    │   └── test_mcp.py           # Testy serwera MCP
    ├── process_tests/         # Testy silnika Process
    │   ├── __init__.py
    │   └── test_process.py    # Testy głównego silnika
    └── e2e_tests/                # Testy end-to-end
        ├── __init__.py
        └── test_e2e.py           # Testy integracji całego systemu