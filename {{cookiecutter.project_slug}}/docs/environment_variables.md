# Environment Variables

This document provides a comprehensive list of all environment variables used by the Process system. The variables are organized by component and use consistent prefixes to avoid conflicts.

## Global Environment Variables

These variables can be used in a single `.env` file at the project root to configure all components:

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `LOG_LEVEL` | Global logging level | `INFO` | `DEBUG` |
| `ENVIRONMENT` | Deployment environment | `development` | `production` |

## Core Framework (`CORE_*`)

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `CORE_LOG_LEVEL` | Core framework logging level | `INFO` | `DEBUG` |
| `CORE_TEMP_DIR` | Directory for temporary files | `/tmp` | `/app/temp` |
| `CORE_CONFIG_DIR` | Directory for configuration files | `./config` | `/app/config` |
| `CORE_MAX_WORKERS` | Maximum number of worker threads | `4` | `8` |
| `CORE_ENABLE_METRICS` | Enable metrics collection | `false` | `true` |
| `CORE_METRICS_PORT` | Port for metrics server | `9090` | `9091` |

## Process Engine (`PROCESS_*`)

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `PROCESS_HOST` | Process engine host | `0.0.0.0` | `process` |
| `PROCESS_PORT` | Process engine port | `8000` | `8001` |
| `PROCESS_LOG_LEVEL` | Process engine logging level | `INFO` | `DEBUG` |
| `PROCESS_ENGINE_TYPE` | Type of process engine to use | `default` | `custom` |
| `PROCESS_CACHE_SIZE` | Size of the process cache (MB) | `100` | `500` |
| `PROCESS_CACHE_TTL` | Cache time-to-live (seconds) | `3600` | `7200` |
| `PROCESS_MAX_WORKERS` | Maximum number of worker processes | `4` | `8` |
| `PROCESS_PLUGIN_DIR` | Directory for plugins | `./plugins` | `/app/plugins` |
| `PROCESS_DEFAULT_LANGUAGE` | Default language for processing | `en-US` | `pl-PL` |
| `PROCESS_DEFAULT_RESOURCE` | Default resource for processing | `default` | `custom` |
| `PROCESS_DEFAULT_FORMAT` | Default output format | `wav` | `mp3` |

## gRPC Service (`GRPC_*`)

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `GRPC_HOST` | gRPC server host | `0.0.0.0` | `grpc` |
| `GRPC_PORT` | gRPC server port | `50051` | `50052` |
| `GRPC_LOG_LEVEL` | gRPC service logging level | `INFO` | `DEBUG` |
| `GRPC_MAX_WORKERS` | Maximum number of gRPC workers | `10` | `20` |
| `GRPC_MAX_CONCURRENT_RPCS` | Maximum concurrent RPCs | `100` | `200` |
| `GRPC_PROCESS_HOST` | Process engine host | `process` | `localhost` |
| `GRPC_PROCESS_PORT` | Process engine port | `8000` | `8001` |
| `GRPC_ENABLE_REFLECTION` | Enable gRPC reflection | `true` | `false` |
| `GRPC_ENABLE_HEALTH_CHECK` | Enable health check service | `true` | `false` |
| `GRPC_TLS_ENABLED` | Enable TLS | `false` | `true` |
| `GRPC_TLS_CERT_PATH` | Path to TLS certificate | `` | `/certs/server.crt` |
| `GRPC_TLS_KEY_PATH` | Path to TLS key | `` | `/certs/server.key` |

## REST API Service (`REST_*`)

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `REST_HOST` | REST server host | `0.0.0.0` | `rest` |
| `REST_PORT` | REST server port | `5000` | `5001` |
| `REST_LOG_LEVEL` | REST service logging level | `INFO` | `DEBUG` |
| `REST_WORKERS` | Number of Uvicorn workers | `4` | `8` |
| `REST_PROCESS_HOST` | Process engine host | `process` | `localhost` |
| `REST_PROCESS_PORT` | Process engine port | `8000` | `8001` |
| `REST_CORS_ORIGINS` | Allowed CORS origins | `*` | `http://localhost:3000,https://example.com` |
| `REST_API_PREFIX` | API route prefix | `/api` | `/api/v1` |
| `REST_ENABLE_DOCS` | Enable API documentation | `true` | `false` |
| `REST_DOCS_URL` | URL for API documentation | `/docs` | `/swagger` |
| `REST_ENABLE_METRICS` | Enable Prometheus metrics | `false` | `true` |
| `REST_RATE_LIMIT_ENABLED` | Enable rate limiting | `false` | `true` |
| `REST_RATE_LIMIT` | Requests per minute limit | `60` | `100` |

## MCP Service (`MCP_*`)

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `MCP_HOST` | MCP server host | `0.0.0.0` | `mcp` |
| `MCP_PORT` | MCP server port | `4000` | `4001` |
| `MCP_LOG_LEVEL` | MCP service logging level | `INFO` | `DEBUG` |
| `MCP_PROCESS_HOST` | Process engine host | `process` | `localhost` |
| `MCP_PROCESS_PORT` | Process engine port | `8000` | `8001` |
| `MCP_TRANSPORTS_SSE` | Enable SSE transport | `true` | `false` |
| `MCP_TRANSPORTS_STDIO` | Enable STDIO transport | `false` | `true` |
| `MCP_TRANSPORTS_GRPC` | Enable gRPC transport | `false` | `true` |
| `MCP_TRANSPORTS_GRPC_PORT` | gRPC transport port | `4001` | `4002` |
| `MCP_MAX_REQUEST_SIZE` | Maximum request size (MB) | `10` | `50` |
| `MCP_ENABLE_RESOURCE_CACHE` | Enable resource caching | `true` | `false` |
| `MCP_RESOURCE_CACHE_SIZE` | Resource cache size (MB) | `100` | `500` |
| `MCP_RESOURCE_CACHE_TTL` | Resource cache TTL (seconds) | `3600` | `7200` |

## Using Environment Variables

### Single .env File

You can use a single `.env` file at the project root to configure all components:

```bash
# Global settings
LOG_LEVEL=INFO
ENVIRONMENT=development

# Core settings
CORE_TEMP_DIR=/tmp

# Process settings
PROCESS_HOST=0.0.0.0
PROCESS_PORT=8000

# gRPC settings
GRPC_HOST=0.0.0.0
GRPC_PORT=50051

# REST settings
REST_HOST=0.0.0.0
REST_PORT=5000

# MCP settings
MCP_HOST=0.0.0.0
MCP_PORT=4000
```

### Component-Specific .env Files

Alternatively, you can use separate `.env` files for each component:

```bash
# process/.env
PROCESS_HOST=0.0.0.0
PROCESS_PORT=8000
```

```bash
# grpc/.env
GRPC_HOST=0.0.0.0
GRPC_PORT=50051
GRPC_PROCESS_HOST=process
GRPC_PROCESS_PORT=8000
```

### Docker Compose

When using Docker Compose, you can specify environment variables in the `docker-compose.yml` file:

```yaml
services:
  process:
    environment:
      - PROCESS_HOST=0.0.0.0
      - PROCESS_PORT=8000
  
  grpc:
    environment:
      - GRPC_HOST=0.0.0.0
      - GRPC_PORT=50051
      - GRPC_PROCESS_HOST=process
      - GRPC_PROCESS_PORT=8000
```

### Kubernetes

For Kubernetes deployments, you can use ConfigMaps and Secrets:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: process-config
data:
  PROCESS_HOST: "0.0.0.0"
  PROCESS_PORT: "8000"
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: process
spec:
  template:
    spec:
      containers:
      - name: process
        envFrom:
        - configMapRef:
            name: process-config
```
