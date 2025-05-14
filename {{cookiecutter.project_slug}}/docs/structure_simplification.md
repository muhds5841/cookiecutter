# Project Structure Simplification

This document outlines the proposed simplifications to the Process project structure, comparing the current implementation with the simplified approach.

## 1. Dependency Management

### Current Structure
Each component has its own `pyproject.toml` file, leading to duplication and potential version conflicts.

```
project/
├── pyproject.toml           # Root project dependencies
├── process/
│   └── pyproject.toml       # Process-specific dependencies
├── grpc/
│   └── pyproject.toml       # gRPC-specific dependencies
├── rest/
│   └── pyproject.toml       # REST-specific dependencies
└── mcp/
    └── pyproject.toml       # MCP-specific dependencies
```

### Simplified Structure
A single `pyproject.toml` file with dependency groups for each component.

```
project/
└── pyproject.toml           # All dependencies in groups
```

```toml
# Example of unified pyproject.toml
[tool.poetry.dependencies]
python = "^3.8"
# Core dependencies here

[tool.poetry.group.process.dependencies]
# Process-specific dependencies

[tool.poetry.group.grpc.dependencies]
grpcio = "^1.50.0"
protobuf = "^4.21.0"

[tool.poetry.group.rest.dependencies]
fastapi = "^0.95.0"
uvicorn = "^0.22.0"

[tool.poetry.group.mcp.dependencies]
# MCP-specific dependencies
```

**Benefits:**
- Single source of truth for dependencies
- Easier to manage version compatibility
- Simplified installation process
- Reduced duplication

## 2. Service Structure

### Current Structure
Separate top-level directories for each service interface with duplicated patterns.

```
project/
├── grpc/                    # gRPC Service
│   ├── Dockerfile
│   ├── server.py
│   ├── client.py
│   └── proto/
├── rest/                    # REST API Service
│   ├── Dockerfile
│   ├── server.py
│   ├── client.py
│   └── models/
└── mcp/                     # Model Context Protocol
    ├── Dockerfile
    ├── mcp_server.py
    ├── tools/
    ├── resources/
    └── transports/
```

### Simplified Structure
A unified `services` directory with subdirectories for each interface.

```
project/
└── services/
    ├── common/              # Shared service code
    │   ├── auth.py
    │   ├── middleware.py
    │   └── logging.py
    ├── grpc/                # gRPC implementation
    │   ├── server.py
    │   ├── client.py
    │   └── proto/
    ├── rest/                # REST implementation
    │   ├── server.py
    │   ├── client.py
    │   └── models/
    └── mcp/                 # MCP implementation
        ├── server.py
        ├── tools.py
        └── resources.py
```

**Benefits:**
- Logical grouping of service interfaces
- Shared code for common service functionality
- Consistent patterns across interfaces
- Clearer separation of concerns

## 3. Configuration Management

### Current Structure
Each component has its own `.env.example` file with potential duplication.

```
project/
├── process/
│   └── .env.example         # Process environment variables
├── grpc/
│   └── .env.example         # gRPC environment variables
├── rest/
│   └── .env.example         # REST environment variables
└── mcp/
    └── .env.example         # MCP environment variables
```

### Simplified Structure
A unified configuration system with component-specific sections.

```
project/
├── config/
│   ├── default.yaml         # Default configuration
│   ├── development.yaml     # Development overrides
│   └── production.yaml      # Production overrides
└── .env.example             # Single environment file with namespaced variables
```

```
# Example of unified .env file
# Core settings
CORE_LOG_LEVEL=INFO
CORE_TEMP_DIR=/tmp

# Process settings
PROCESS_ENGINE_TYPE=default
PROCESS_CACHE_SIZE=100

# Service settings
SERVICE_HOST=0.0.0.0
SERVICE_GRPC_PORT=50051
SERVICE_REST_PORT=8000
SERVICE_MCP_PORT=4000
```

**Benefits:**
- Single source of truth for configuration
- Clear namespacing to avoid conflicts
- Easier to manage environment variables
- Consistent configuration access pattern

## 4. Docker Setup

### Current Structure
Separate Dockerfiles for each component.

```
project/
├── process/
│   └── Dockerfile           # Process Dockerfile
├── grpc/
│   └── Dockerfile           # gRPC Dockerfile
├── rest/
│   └── Dockerfile           # REST Dockerfile
├── mcp/
│   └── Dockerfile           # MCP Dockerfile
└── docker-compose.yml       # Docker Compose configuration
```

### Simplified Structure
A multi-stage Dockerfile that can build different components.

```
project/
├── Dockerfile               # Multi-stage Dockerfile
├── docker/
│   ├── process.dockerfile   # Process-specific layers
│   ├── grpc.dockerfile      # gRPC-specific layers
│   ├── rest.dockerfile      # REST-specific layers
│   └── mcp.dockerfile       # MCP-specific layers
└── docker-compose.yml       # Docker Compose configuration
```

```dockerfile
# Example of multi-stage Dockerfile
FROM python:3.8-slim AS base
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry config virtualenvs.create false

# Process stage
FROM base AS process
RUN poetry install --only process
COPY . .
CMD ["python", "-m", "process.server"]

# gRPC stage
FROM base AS grpc
RUN poetry install --only grpc
COPY . .
CMD ["python", "-m", "services.grpc.server"]

# REST stage
FROM base AS rest
RUN poetry install --only rest
COPY . .
CMD ["python", "-m", "services.rest.server"]

# MCP stage
FROM base AS mcp
RUN poetry install --only mcp
COPY . .
CMD ["python", "-m", "services.mcp.server"]
```

**Benefits:**
- Shared base image for all components
- Reduced duplication in Dockerfiles
- Consistent build process
- Smaller image sizes through multi-stage builds

## 5. Plugin Architecture

### Current Structure
Custom plugin system with complex registration and discovery.

```
project/
└── process/
    ├── plugin_system.py     # Plugin system implementation
    └── adapters/            # Plugin implementations
```

### Simplified Structure
Standardized entry point mechanism with reduced boilerplate.

```
project/
└── process/
    ├── plugins/
    │   ├── __init__.py      # Plugin registry
    │   ├── base.py          # Plugin base class
    │   └── builtin/         # Built-in plugins
    └── adapters/            # Adapter implementations
```

```python
# Example of simplified plugin system
# In plugins/base.py
class ProcessPlugin:
    """Base class for all Process plugins."""
    
    @classmethod
    def register(cls):
        """Register the plugin with the system."""
        from process.plugins import registry
        registry.register_plugin(cls)
    
    def process(self, text, **options):
        """Process text with this plugin."""
        raise NotImplementedError

# In a plugin implementation
from process.plugins.base import ProcessPlugin

class CustomPlugin(ProcessPlugin):
    """A custom processing plugin."""
    
    def process(self, text, **options):
        # Implementation here
        return processed_text

# Automatic registration
CustomPlugin.register()
```

**Benefits:**
- Simpler plugin creation and registration
- Standardized interface for all plugins
- Clearer discovery mechanism
- Reduced boilerplate code

## 6. Testing Structure

### Current Structure
Tests organized by component type.

```
project/
└── tests/
    ├── process_tests/       # Process engine tests
    ├── grpc_tests/          # gRPC service tests
    ├── rest_tests/          # REST API tests
    ├── mcp_tests/           # MCP tests
    └── e2e_tests/           # End-to-end tests
```

### Simplified Structure
Tests that mirror the source code structure.

```
project/
└── tests/
    ├── unit/                # Unit tests
    │   ├── core/            # Core framework tests
    │   ├── process/         # Process engine tests
    │   └── services/        # Service tests
    ├── integration/         # Integration tests
    │   ├── process/         # Process integration tests
    │   └── services/        # Service integration tests
    └── e2e/                 # End-to-end tests
        └── scenarios/       # Test scenarios
```

**Benefits:**
- Clear mapping between source code and tests
- Easier to find tests for specific components
- Consistent testing patterns
- Better organization of test types

## 7. MCP Implementation

### Current Structure
Complex nested directory structure for MCP.

```
project/
└── mcp/
    ├── mcp_server.py        # MCP server
    ├── protocol/            # Protocol handling
    │   ├── negotiation.py
    │   └── messages.py
    ├── tools/               # MCP tools
    │   ├── tts_tool.py
    │   └── resource_tool.py
    ├── resources/           # Resource providers
    │   ├── voices.py
    │   └── results.py
    └── transports/          # Transport implementations
        ├── sse.py
        ├── stdio.py
        └── grpc.py
```

### Simplified Structure
Flattened directory structure with clearer organization.

```
project/
└── services/
    └── mcp/
        ├── server.py        # Main server
        ├── protocol.py      # Protocol handling
        ├── tools.py         # Tool implementations
        ├── resources.py     # Resource providers
        └── transports/      # Transport implementations
            ├── sse.py
            ├── stdio.py
            └── grpc.py
```

**Benefits:**
- Reduced nesting for easier navigation
- Clearer component boundaries
- Simplified imports
- More maintainable codebase

## 8. Consistent Naming

### Current Structure
Mixed naming conventions with some TTS-specific terminology.

```
project/
└── mcp/
    └── tools/
        └── tts_tool.py      # TTS-specific naming
```

### Simplified Structure
Consistent naming using the generic "process" terminology.

```
project/
└── services/
    └── mcp/
        └── tools/
            └── process_tool.py  # Generic naming
```

**Benefits:**
- Consistent terminology throughout the codebase
- Easier to understand the purpose of components
- Better alignment with the project's goals
- Reduced cognitive load for developers

## Summary of Benefits

The simplified structure provides several key benefits:

1. **Reduced Duplication**: Shared code and configuration across components
2. **Improved Organization**: Logical grouping of related functionality
3. **Simplified Development**: Clearer patterns and reduced boilerplate
4. **Better Maintainability**: Consistent naming and structure
5. **Enhanced Developer Experience**: Easier to navigate and understand
6. **Scalability**: Better foundation for adding new features and components

These simplifications maintain all the functionality of the original structure while making the codebase more maintainable and developer-friendly.