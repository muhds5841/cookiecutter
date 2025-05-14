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

The easiest way to get started is to use the development setup script:

```bash
# Set up the development environment
python dev_setup.py

# Start the services
docker-compose up -d
```

### Manual Setup

If you prefer to set up the environment manually:

```bash
# Install dependencies for each component
cd process && poetry install
cd ../grpc && poetry install
cd ../rest && poetry install
cd ../mcp && poetry install

# Set up pre-commit hooks
pip install pre-commit
pre-commit install
```

### Environment Configuration

Each component uses environment variables for configuration. We use a consistent naming convention with prefixes to avoid conflicts:

- `CORE_*` - Core framework settings
- `PROCESS_*` - Process engine settings
- `GRPC_*` - gRPC service settings
- `REST_*` - REST API service settings
- `MCP_*` - MCP service settings

Example configuration:

```bash
# Copy example environment files
cp .env.example .env

# Or for individual components
cp process/.env.example process/.env
cp grpc/.env.example grpc/.env
cp rest/.env.example rest/.env
cp mcp/.env.example mcp/.env
```

See the [Environment Variables Documentation](docs/environment_variables.md) for a complete list of available settings.

## Usage Examples

### Process Engine

```python
from process.process import Process

# Initialize the Process engine
process = Process()

# Process text
result = process.process_text("Text to process", language="en-US")

# Access the result
output_data = result.data
output_format = result.format
```

### REST API Client

```python
from rest.client import ProcessClient

# Initialize the REST client
client = ProcessClient("http://localhost:5000")

# Process text
result = client.process_text("Text to process", language="en-US")
```

### gRPC Client

```python
from grpc.client import ProcessClient

# Initialize the gRPC client
client = ProcessClient("localhost:50051")

# Process text
result = client.process_text("Text to process", language="en-US")
```

## Development

### Installing Poetry

This project uses Poetry for dependency management. To install Poetry:

#### On Linux/macOS:

```bash
# Method 1: Using the official installer
curl -sSL https://install.python-poetry.org | python3 -

# Method 2: Using pip
pip install poetry

# Method 3: On Ubuntu/Debian
sudo apt install python3-poetry
```

#### On Windows (PowerShell):

```powershell
# Method 1: Using the official installer
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Method 2: Using pip
pip install poetry
```

After installation, verify Poetry is installed correctly:

```bash
poetry --version
```

#### Alternative: Using virtualenv and pip

If you prefer not to install Poetry, you can use traditional virtualenv and pip:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies from requirements.txt
pip install -r requirements.txt
```

### Creating New Modules

The Process system is designed to be modular. Here's how to create and set up new modules:

#### 1. Create a new protocol module (e.g., for a new protocol like GraphQL):

```bash
# Create the directory structure
mkdir -p graphql
cd graphql

# Initialize Poetry for the module
poetry init

# Add dependencies
poetry add fastapi uvicorn graphql-core

# Add development dependencies
poetry add --group dev pytest black isort mypy

# Create basic files
touch server.py client.py .env.example
```

#### 2. Create a new plugin for the Process engine:

```bash
# Navigate to the process directory
cd process

# Create a plugin directory if it doesn't exist
mkdir -p plugins

# Create a new plugin file
touch plugins/my_plugin.py
```

Example plugin implementation in `plugins/my_plugin.py`:

```python
from process.process_base import ProcessBase
from process.plugin_system import register_plugin

class MyPlugin(ProcessBase):
    """Custom processing plugin."""
    
    def process_text(self, text, **options):
        """Process text with custom logic."""
        # Implement your processing logic here
        processed_text = text.upper()  # Example: convert to uppercase
        
        # Create and return a result
        return self.create_result(
            data=processed_text,
            format="text",
            metadata={"plugin": "my_plugin"}
        )

# Register the plugin
register_plugin("my_plugin", MyPlugin)
```

#### 3. Create a new service module with monitoring:

```bash
# Create the directory structure
mkdir -p my_service
cd my_service

# Initialize Poetry for the module
poetry init

# Add dependencies
poetry add prometheus-client healthcheck

# Create basic files
touch server.py client.py .env.example
```

Example `.env.example` for the new service:

```
# My Service Environment Variables
MY_SERVICE_HOST=0.0.0.0
MY_SERVICE_PORT=8080
MY_SERVICE_LOG_LEVEL=INFO
MY_SERVICE_PROCESS_HOST=process
MY_SERVICE_PROCESS_PORT=8000

# Monitoring settings
MY_SERVICE_ENABLE_METRICS=true
MY_SERVICE_METRICS_PORT=9101
MY_SERVICE_HEALTH_CHECK_INTERVAL=30

# Core settings
CORE_LOG_LEVEL=INFO
```

### Adding New Plugins

The Process system can be extended with plugins. To create a new plugin:

1. Create a new module in the `process/plugins/` directory
2. Implement a class that inherits from `ProcessBase`
3. Register the plugin with the `PluginRegistry`

See the [Developer Guide](docs/developer_guide.md) for detailed instructions.

### Creating New Service Interfaces

You can add new service interfaces (e.g., WebSocket) by following the pattern of existing services:

1. Create a new directory for your service
2. Implement a server that connects to the Process engine
3. Implement a client for easy integration

See the [Modular Architecture](docs/modular_architecture.md) documentation for details.

## Testing Modules

Each module in the Process system can be tested independently. Here's how to test different components:

### Testing the Process Engine

```bash
# Navigate to the process directory
cd process

# Run tests with Poetry
poetry run pytest

# Or with traditional pytest if not using Poetry
python -m pytest
```

### Testing Protocol Implementations

```bash
# Example: Testing the gRPC service
cd grpc
poetry run pytest

# Example: Testing the REST API
cd rest
poetry run pytest
```

### Testing Health Checks and Monitoring

Each service exposes health check and metrics endpoints that can be tested:

```bash
# Start the service
cd imap
poetry run python server.py

# In another terminal, test the health endpoint
curl http://localhost:8080/health

# Test the metrics endpoint
curl http://localhost:9101/metrics
```

### End-to-End Testing

Test the entire system with all services running:

```bash
# Start all services with Docker Compose
docker-compose up -d

# Run end-to-end tests
cd tests/e2e_tests
python -m pytest
```

## Documentation

Detailed documentation is available in the `docs/` directory:

- [Developer Guide](docs/developer_guide.md) - Comprehensive guide for developers
- [Modular Architecture](docs/modular_architecture.md) - Details on the system architecture
- [Environment Variables](docs/environment_variables.md) - List of all configuration options
- [API Reference](docs/api_reference.md) - API documentation for all components

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.