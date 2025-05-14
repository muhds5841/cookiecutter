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
    ├── lib/                           # Wspólne biblioteki
    │   ├── __init__.py
    │   ├── config.py
    │   ├── logging.py
    │   ├── utils.py
    │   └── quality/                   # Narzędzia jakości kodu
    ├── process/                       # Główny proces (dowolny)
    │   ├── Dockerfile
    │   ├── pyproject.toml
    │   ├── __init__.py
    │   ├── process.py
    │   └── adapters/                  # Adaptery dla różnych implementacji
    ├── mcp/                           # Komponent MCP (nowy/rozszerzony)
    │   ├── Dockerfile
    │   ├── pyproject.toml
    │   ├── mcp_server.py              # Serwer MCP
    │   ├── transports/                # Implementacje transportu
    │   │   ├── __init__.py
    │   │   ├── sse.py                 # Server-Sent Events
    │   │   ├── stdio.py               # Komunikacja przez stdout/stdin
    │   │   └── hybrid.py              # Wieloprotokołowy serwer
    │   ├── protocol/                  # Obsługa protokołu MCP
    │   │   ├── __init__.py
    │   │   ├── negotiation.py         # Negocjacja wersji
    │   │   └── discovery.py           # Wykrywanie narzędzi
    │   ├── tools/                     # Narzędzia MCP
    │   │   ├── __init__.py
    │   │   └── process_tool.py        # Narzędzie ogólne (dowolny proces)
    │   ├── resources/                 # Zasoby MCP
    │   │   ├── __init__.py
    │   │   └── uri_templates.py       # Definicje URI templates
    │   └── sampling/                  # Strategie próbkowania dla LLM
    │       ├── __init__.py
    │       └── adaptive.py            # Adaptacyjne próbkowanie
    ├── grpc/                          # Serwis gRPC
    ├── rest/                          # Serwis REST
    ├── webrtc/                        # Serwis WebRTC
    ├── shell/                         # CLI
    └── tests/                         # Testy
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

```aiignore
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
- Wsparcie dla różnych protokołów komunikacyjnych (gRPC, REST, WebRTC)
- Integracja z Model Context Protocol (MCP)
- Narzędzia zapewnienia jakości kodu (Black, isort, Flake8, mypy)
- Automatyczna konfiguracja pre-commit hooks
- Comprehensive Makefile for common tasks
- Konfiguracja Docker i docker-compose (opcjonalnie)

## Konfiguracja

- Plik `cookiecutter.json` pozwala na wybór komponentów oraz ustawienia projektu.
- Szczegółowe opcje konfiguracyjne opisane są w dokumentacji każdego komponentu.

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

Generowanie projektu z minimalną konfiguracją:

```bash
cookiecutter path/to/cookiecutter-project
```

---

2. **Oszczędność czasu** - szybkie tworzenie nowych projektów z gotowym zestawem narzędzi
3. **Najlepsze praktyki** - wbudowane narzędzia zapewniające wysoką jakość kodu
4. **Elastyczność** - możliwość wyboru komponentów i konfiguracji
