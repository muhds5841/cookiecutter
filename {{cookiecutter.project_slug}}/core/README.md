# Core Framework

This directory contains core framework components and utilities used across all parts of the Process system.

## Overview

The core framework provides a foundation for consistent behavior across all components, including:

- Configuration management
- Logging
- Error handling
- Common utilities

## Components

### Configuration Management

The configuration system provides a unified way to manage configuration across all components:

#### Basic Configuration (`config.py`)

Simple configuration loading from environment variables and files.

```python
from core.config import load_config

# Load configuration
config = load_config()

# Access configuration values
value = config.get("KEY", "default_value")
```

#### Enhanced Configuration (`config_manager.py`)

Advanced configuration management with environment-specific overlays and validation.

```python
from core.config_manager import create_config_manager

# Create a configuration manager for a component
config = create_config_manager("process")

# Access configuration values
value = config.get("KEY", "default_value")

# Set configuration values
config.set("KEY", "value")

# Validate configuration against a schema
errors = config.validate(schema)

# Get the entire configuration as a dictionary
config_dict = config.as_dict()
```

### Logging (`logging.py`)

Structured logging with consistent formatting across all components.

```python
from core.logging import get_logger

# Get a logger for a component
logger = get_logger("component_name")

# Log messages at different levels
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")

# Log with context
logger.info("Message with context", extra={"key": "value"})
```

### Error Handling (`error_handling.py`)

Standardized error handling with consistent error codes and reporting.

```python
from core.error_handling import ProcessError, ValidationError, ErrorCode, create_error_handler

# Create an error handler for a component
error_handler = create_error_handler("component_name")

# Handle an exception
try:
    # Some code that might fail
    pass
except Exception as e:
    # Convert to a standardized error
    process_error = error_handler.handle_error(e)
    
    # Create a standardized error response
    response = error_handler.create_error_response(e)

# Create specific error types
validation_error = ValidationError("Invalid input", details={"field": "text"})
```

#### Error Codes

The system defines standard error codes for consistent error reporting:

- **General errors (1-99)**
  - `UNKNOWN_ERROR = 1`
  - `CONFIGURATION_ERROR = 2`
  - `INITIALIZATION_ERROR = 3`
  - `VALIDATION_ERROR = 4`
  - `RESOURCE_NOT_FOUND = 5`
  - `PERMISSION_DENIED = 6`
  - `TIMEOUT_ERROR = 7`

- **Process-specific errors (100-199)**
  - `PROCESS_ENGINE_ERROR = 100`
  - `TEXT_PROCESSING_ERROR = 101`
  - `RESOURCE_UNAVAILABLE = 102`
  - `UNSUPPORTED_FORMAT = 103`

- **Service-specific errors (200-299)**
  - `SERVICE_UNAVAILABLE = 200`
  - `INVALID_REQUEST = 201`
  - `SERIALIZATION_ERROR = 202`
  - `COMMUNICATION_ERROR = 203`

- **Plugin-specific errors (300-399)**
  - `PLUGIN_NOT_FOUND = 300`
  - `PLUGIN_INITIALIZATION_ERROR = 301`
  - `PLUGIN_EXECUTION_ERROR = 302`

- **External service errors (400-499)**
  - `EXTERNAL_SERVICE_ERROR = 400`
  - `NETWORK_ERROR = 401`
  - `AUTHENTICATION_ERROR = 402`
  - `RATE_LIMIT_EXCEEDED = 403`

### Utilities (`utils.py`)

Common utility functions used across all components.

```python
from core.utils import generate_id, create_temp_file, calculate_hash

# Generate a unique ID
id = generate_id("prefix-")

# Create a temporary file
file_path = create_temp_file(data, suffix=".txt")

# Calculate a hash
hash_value = calculate_hash(data)
```

## Best Practices

### Configuration

1. Use the `core.config_manager` module for all configuration needs
2. Define clear environment variable names with component prefixes
3. Validate configuration against a schema before using it
4. Use environment-specific overlays for different deployment environments

### Logging

1. Get a logger for each module with a specific name
2. Use appropriate log levels for different types of messages
3. Include relevant context in log messages
4. Configure logging at the application level

### Error Handling

1. Define specific error types for different error conditions
2. Use standard error codes for consistent error reporting
3. Include relevant details in error messages
4. Handle errors at the appropriate level
5. Convert exceptions to standardized errors before returning to clients

### Utilities

1. Use the provided utility functions instead of reimplementing common functionality
2. Keep utility functions focused on a single responsibility
3. Document utility functions clearly





### 4.1. Modularność narzędzi jakości kodu

1. **Wszystkie narzędzia jako moduły Python** - każde narzędzie jest zaimplementowane jako oddzielny moduł Python, co ułatwia zrozumienie i modyfikację
2. **Wspólny interfejs** - wszystkie narzędzia mają spójny interfejs, zarówno jako moduły importowane jak i jako skrypty uruchamiane z wiersza poleceń
3. **Konfiguracja w jednym miejscu** - pliki konfiguracyjne dla wszystkich narzędzi są zgromadzone w katalogu `quality/`
4. **Dostęp przez API** - możliwość importowania i używania narzędzi jakości kodu bezpośrednio w kodzie, co umożliwia tworzenie niestandardowych skryptów

### 4.2. Elastyczność użycia

1. **Makefile jako interfejs** - wszystkie operacje są dostępne przez Makefile, który działa jak zunifikowany interfejs
2. **Możliwość bezpośredniego użycia** - każde narzędzie może być uruchamiane bezpośrednio jako moduł Python
3. **Konfigurowalność** - wszystkie narzędzia przyjmują parametry konfiguracyjne, co pozwala na ich dostosowanie do konkretnych potrzeb
4. **Granularne kontrole** - możliwość uruchamiania poszczególnych narzędzi osobno (np. tylko formatowanie, tylko lintery)

### 4.3. Przykład rozszerzenia narzędzi

Dodanie nowego narzędzia jakości kodu jest proste. Na przykład, aby dodać obsługę `bandit` (narzędzie do analizy bezpieczeństwa kodu):
ile


```bash
# Instalacja narzędzia
pip install tts-scaffold

# Generowanie projektu
scaffold-tts my-tts-project --with-docker --with-ci

# Wejście do katalogu projektu
cd my-tts-project

# Inicjalizacja projektu
make setup
```


# Generowanie testów dla nowo utworzonego adaptera
```bash
python -m lib.scaffold generate-tests --file process/adapters/amazon.py
```



Gdzie `lib/scaffold.py` to skrypt:

```python

```

### 6.2. Automatyczne generowanie testów

Możemy też zautomatyzować generowanie testów dla nowego kodu:

```bash

```

### 3.2. Jako narzędzie CLI

Możemy też zaimplementować dedykowane narzędzie CLI do inicjalizacji projektu:

#### `scaffold-tts` (pakiet CLI)

## 4. Transparentność i łatwość modyfikacji

Proponowana struktura została zaprojektowana z myślą o transparentności i łatwości modyfikacji:

### 4.1. Modularność narzędzi jakości kodu

1. **Wszystkie narzędzia jako moduły Python** - każde narzędzie jest zaimplementowane jako o
2. 
## 7. Podsumowanie

Przedstawiona pełna struktura projektu Process z zintegrowanymi narzędziami jakości kodu zapewnia:

1. **Kompletność** - wszystkie niezbędne komponenty są uwzględnione (silnik Process, serwisy komunikacyjne, narzędzia MCP, testy)
2. **Modularność** - każdy komponent jest niezależny i może być rozwijany osobno
3. **Jakość kodu** - wbudowane narzędzia zapewniają zgodność z najlepszymi praktykami
4. **Elastyczność** - łatwość dostosowania i rozszerzania o nowe funkcje
5. **Automatyzację** - zautomatyzowane procesy budowania, testowania i wdrażania
6. **Transparentność** - narzędzia jakości kodu są zaimplementowane jako biblioteka w `lib/quality`, co umożliwia ich łatwą modyfikację

Taka struktura stanowi solidną podstawę dla każdego projektu Process i może być łatwo dostosowana do specyficznych wymagań. Jednocześnie, dzi