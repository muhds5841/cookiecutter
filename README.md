# Cookiecutter  Project

Szablon cookiecutter do generowania projektów Text-to-Speech z najlepszymi praktykami jakości kodu.

## Możliwości

- Modularny system  z wieloma komponentami
- Wsparcie dla różnych protokołów komunikacyjnych (gRPC, REST, WebRTC)
- Integracja z Model Context Protocol (MCP)
- Narzędzia zapewnienia jakości kodu (Black, isort, Flake8, mypy)
- Automatyczna konfiguracja pre-commit hooks
- Comprehensive Makefile for common tasks
- Konfiguracja Docker i docker-compose (opcjonalnie)

## Wymagania

- Python 3.9+
- pip
- cookiecutter (`pip install cookiecutter`)
- git




# Inicjalizacja projektu TTS z wykorzystaniem cookiecutter

Cookiecutter to narzędzie do generowania projektów z szablonów, które idealnie nadaje się do tworzenia szkieletu dla projektu TTS. Poniżej przedstawiam kompletny przewodnik jak przygotować repozytorium szablonu cookiecutter oraz jak go używać do tworzenia nowych projektów TTS.

## 1. Struktura repozytorium cookiecutter dla projektu TTS

Najpierw przyjrzyjmy się, jak powinno wyglądać repozytorium z szablonem cookiecutter:

```
cookiecutter-tts-project/
├── cookiecutter.json               # Konfiguracja szablonu
├── README.md                       # Dokumentacja szablonu
├── hooks/                          # Skrypty uruchamiane przed/po generowaniu
│   ├── pre_gen_project.py          # Uruchamiany przed generowaniem
│   └── post_gen_project.py         # Uruchamiany po wygenerowaniu projektu
└── {{cookiecutter.project_slug}}/  # Katalog szablonu projektu
    ├── docker-compose.yml
    ├── Makefile                    # Główny Makefile
    ├── pyproject.toml              # Konfiguracja Poetry
    ├── README.md                   # Dokumentacja projektu
    ├── .gitignore                  # Pliki ignorowane przez Git
    ├── quality/                    # Konfiguracje QA
    │   ├── .pre-commit-config.yaml
    │   ├── tox.ini
    │   ├── .pylintrc
    │   ├── .flake8
    │   └── conftest.py
    ├── lib/                        # Wspólne biblioteki
    │   ├── __init__.py
    │   ├── config.py
    │   ├── logging.py
    │   ├── utils.py
    │   └── quality/                # Narzędzia jakości kodu
    │       ├── __init__.py
    │       ├── linters.py
    │       ├── formatters.py
    │       └── testers.py
    ├── tts_engine/                 # Silnik TTS (jeśli wybrano)
    │   ├── Dockerfile
    │   ├── pyproject.toml
    │   ├── __init__.py
    │   ├── tts_engine.py
    │   └── ...
    ├── grpc/                       # Serwis gRPC (jeśli wybrano)
    │   ├── Dockerfile
    │   ├── pyproject.toml
    │   ├── __init__.py
    │   ├── server.py
    │   └── ...
    ├── rest/                       # Serwis REST (jeśli wybrano)
    │   ├── ...
    ├── webrtc/                     # Serwis WebRTC (jeśli wybrano)
    │   ├── ...
    ├── mcp/                        # Model Context Protocol (jeśli wybrano)
    │   ├── ...
    ├── shell/                      # CLI (jeśli wybrano)
    │   ├── ...
    └── tests/                      # Testy
        ├── __init__.py
        ├── conftest.py
        └── ...
```
## Użycie

### Uruchamianie komponentów

```bash
# Uruchomienie serwisów w kontenerach
make up

# Zatrzymanie serwisów
make down
```

### Zapewnienie jakości kodu

```bash
# Formatowanie kodu
make format

# Sprawdzanie stylu kodu
make lint

# Sprawdzanie typów
make type-check

# Uruchamianie testów
make test

# Wszystkie sprawdzenia jakości
make quality
```


## Opcje

Podczas generowania projektu cookiecutter zapyta o następujące parametry:

- `project_name`: Nazwa projektu
- `project_slug`: Identyfikator projektu (automatycznie generowany z nazwy)
- `project_description`: Krótki opis projektu
- `author_name`: Imię i nazwisko autora
- `author_email`: Adres email autora
- `python_version`: Wersja Pythona (3.9, 3.10, 3.11)
- `use_docker`: Czy generować konfigurację Docker (yes/no)
- `components`: Wybór komponentów do wygenerowania:
  - `tts_engine`: Silnik TTS
  - `grpc`: Serwis gRPC
  - `rest`: Serwis REST API
  - `webrtc`: Serwis WebRTC
  - `mcp`: Model Context Protocol
  - `shell`: Interfejs CLI
- `init_git`: Czy inicjalizować repozytorium Git (yes/no)
- `use_pre_commit`: Czy konfigurować pre-commit hooks (yes/no)
- `install_dependencies`: Czy automatycznie instalować zależności (yes/no)

## Struktura wygenerowanego projektu

```
my-tts-project/
├── docker-compose.yml          # Jeśli wybrano use_docker=yes
├── Makefile                    # Główny Makefile
├── pyproject.toml              # Konfiguracja Poetry
├── README.md                   # Dokumentacja projektu
├── .gitignore                  # Pliki ignorowane przez Git
├── quality/                    # Konfiguracje QA
├── lib/                        # Wspólne biblioteki
├── tts_engine/                 # Jeśli wybrano components.tts_engine=true
├── grpc/                       # Jeśli wybrano components.grpc=true
├── rest/                       # Jeśli wybrano components.rest=true
├── webrtc/                     # Jeśli wybrano components.webrtc=true
├── mcp/                        # Jeśli wybrano components.mcp=true
├── shell/                      # Jeśli wybrano components.shell=true
└── tests/                      # Testy
```

## Następne kroki po wygenerowaniu projektu

```bash
# Wejdź do katalogu projektu
cd my-tts-project

# Instalacja zależności (jeśli nie wybrano automatycznej instalacji)
poetry install

# Uruchomienie testów
make test

# Sprawdzenie jakości kodu
make quality
```


## 4. Użycie szablonu cookiecutter

Po opublikowaniu szablonu na GitHubie, można go używać do generowania nowych projektów TTS:

### 4.1. Instalacja cookiecutter

```bash
pip install cookiecutter
```

### 4.2. Generowanie projektu z szablonu

```bash
# Bezpośrednio z GitHub
cookiecutter gh:yourusername/cookiecutter-tts-project

# Alternatywnie, po pobraniu lokalnie
git clone https://github.com/yourusername/cookiecutter-tts-project.git
cookiecutter cookiecutter-tts-project/
```

### 4.3. Generowanie z określonymi parametrami bez interakcji

Można również generować projekt bez interakcji, podając z góry wszystkie parametry:

```bash
cookiecutter gh:yourusername/cookiecutter-tts-project \
  --no-input \
  project_name="My TTS System" \
  author_name="Jan Kowalski" \
  author_email="jan@example.com" \
  python_version="3.11" \
  use_docker="yes" \
  components.tts_engine="true" \
  components.grpc="true" \
  components.rest="true" \
  init_git="yes" \
  use_pre_commit="yes"
```

## 5. Dodatkowe wskazówki i dobre praktyki

### 5.1. Testowanie szablonu

Przed opublikowaniem szablonu warto go przetestować:

```bash
# Tworzenie testowego projektu
cookiecutter --no-input . \
  project_name="Test TTS Project"

# Sprawdzenie struktury wygenerowanego projektu
ls -la test_tts_project/

# Sprawdzenie, czy projekt można zainstalować i uruchomić testy
cd test_tts_project/
make setup
make test
```

### 5.2. Utrzymywanie szablonu

1. **Regularne aktualizacje**: Aktualizuj zależności i konfiguracje zgodnie z najnowszymi praktykami
2. **Obsługa zgłoszeń (issues)**: Zachęcaj użytkowników do zgłaszania błędów i sugestii
3. **Wersjonowanie**: Używaj tagów dla stabilnych wersji szablonu
4. **Dokumentacja**: Utrzymuj dokumentację aktualną

### 5.3. Ciągła integracja

Można skonfigurować GitHub Actions do testowania szablonu przy każdym pushu:


## 6. Jak rozszerzyć szablon w przyszłości

Szablon cookiecutter można rozszerzać na wiele sposobów:

### 6.1. Dodawanie nowych komponentów

Możesz dodać nowe komponenty do szablonu, tworząc odpowiednie katalogi w `{{cookiecutter.project_slug}}/` i aktualizując `cookiecutter.json`.

### 6.2. Dodawanie opcji konfiguracyjnych

Aby dodać nowe opcje konfiguracyjne, zaktualizuj plik `cookiecutter.json` i dodaj obsługę tych opcji w szablonie.

### 6.3. Integracja z nowymi narzędziami

Jeśli chcesz zintegrować szablon z nowymi narzędziami (np. framework CI/CD, narzędzia analizy kodu), dodaj odpowiednie pliki konfiguracyjne i zaktualizuj skrypty hook.

## Podsumowanie

Cookiecutter to potężne narzędzie do generowania projektów z szablonów, które idealnie nadaje się do tworzenia szkieletu projektów TTS. Opisany powyżej proces pozwala na utworzenie, utrzymanie i używanie szablonu cookiecutter dla projektów TTS, zapewniając:

1. **Standaryzację** - wszystkie projekty mają tę samą strukturę i narzędzia
2. **Oszczędność czasu** - szybkie tworzenie nowych projektów z gotowym zestawem narzędzi
3. **Najlepsze praktyki** - wbudowane narzędzia zapewniające wysoką jakość kodu
4. **Elastyczność** - możliwość wyboru komponentów i konfiguracji

