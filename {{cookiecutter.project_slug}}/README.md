# Process System

A modular and extensible processing system with multiple service interfaces including gRPC, REST API, and Model Context Protocol (MCP) integration.

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