# Process System

A modular and extensible processing system with multiple service interfaces including gRPC, REST API, and Model Context Protocol (MCP) integration.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Key Features](#key-features)
- [Getting Started](#getting-started)
  - [Quick Start](#quick-start)
  - [Manual Setup](#manual-setup)
  - [Environment Configuration](#environment-configuration)
- [Usage Examples](#usage-examples)
- [Development](#development)
  - [Adding New Plugins](#adding-new-plugins)
  - [Creating New Service Interfaces](#creating-new-service-interfaces)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Overview

The Process system provides a flexible framework for text processing with a plugin architecture that allows for easy extension. It includes multiple service interfaces for integration with various systems and a comprehensive configuration and error handling system.

## Architecture

The system is built with a modular architecture that separates concerns and allows components to be deployed independently:

- **Core Process Engine**: The central component responsible for text processing
- **Service Interfaces**: Multiple interfaces (gRPC, REST, MCP) for accessing the Process functionality
- **Plugin System**: Extensible architecture for adding new processing capabilities
- **Core Framework**: Common utilities for configuration, logging, and error handling

## Project Structure

```
project/
├── process/                  # Core Process Engine
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── __init__.py
│   ├── process.py            # Main Process implementation
│   ├── process_base.py       # Abstract base class
│   ├── plugin_system.py      # Plugin architecture
│   └── adapters/             # Adapters for different implementations
├── grpc/                    # gRPC Service
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── server.py             # gRPC server implementation
│   ├── client.py             # gRPC client
│   └── proto/                # Protocol buffer definitions
├── rest/                    # REST API Service
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── server.py             # REST server implementation
│   └── client.py             # REST client
├── mcp/                     # Model Context Protocol
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── mcp_server.py         # MCP server
│   ├── transports/           # Transport implementations
│   ├── protocol/             # Protocol handling
│   ├── tools/                # MCP tools
│   └── resources/            # MCP resources
├── core/                    # Core framework
│   ├── __init__.py
│   ├── config.py             # Basic configuration
│   ├── config_manager.py     # Enhanced configuration management
│   ├── logging.py            # Logging utilities
│   ├── utils.py              # Common utilities
│   └── error_handling.py     # Standardized error handling
├── tests/                   # Tests
│   ├── process_tests/        # Process engine tests
│   ├── grpc_tests/           # gRPC service tests
│   ├── rest_tests/           # REST API tests
│   ├── mcp_tests/            # MCP tests
│   └── e2e_tests/            # End-to-end tests
├── docker-compose.yml        # Docker Compose configuration
├── dev_setup.py             # Development environment setup
└── README.md                # This file
```

## Key Features

- **Modular Architecture**: Each component can be deployed and scaled independently
- **Multiple Interfaces**: gRPC, REST API, and MCP for integration with various systems
- **Plugin System**: Easily extend functionality with plugins
- **Unified Configuration**: Centralized configuration management with environment overlays
- **Standardized Error Handling**: Consistent error reporting across all components
- **Comprehensive Logging**: Structured logging throughout the system
- **Docker Support**: Containerized deployment with Docker Compose
- **Development Tools**: Simplified development environment setup

## Getting Started

### Quick Start

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