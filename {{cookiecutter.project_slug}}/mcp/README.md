# Model Context Protocol (MCP) Integration

This directory contains the integration with the Model Context Protocol (MCP), which allows the Process system to be used with Large Language Models (LLMs).

## Overview

The MCP integration provides a standardized way for LLMs to interact with the Process system, allowing them to:

1. Discover available tools and resources
2. Process text through the Process engine
3. Access and manage resources

## Components

### MCP Server (`mcp_server.py`)

The main entry point for the MCP integration, which handles protocol negotiation, tool discovery, and request routing.

### Process Tool (`tools/process_tool.py`)

A tool that exposes the Process functionality to LLMs through the MCP.

### Resource Providers

Components that provide access to resources such as available processing options, languages, and results.

## Using the MCP Integration

### Starting the MCP Server

```bash
# Start the MCP server
python -m mcp.mcp_server
```

Or using Docker:

```bash
# Build and start the MCP service
docker-compose up -d mcp
```

### Connecting to the MCP Server

The MCP server supports multiple transport mechanisms:

- **Server-Sent Events (SSE)**: Connect to `http://localhost:4000/sse`
- **Standard I/O**: Use the `--stdio` flag when starting the server
- **gRPC**: Connect to `localhost:4000` using the MCP gRPC protocol

### Protocol Flow

1. **Negotiation**: The client and server negotiate the protocol version
2. **Discovery**: The client discovers available tools and resources
3. **Execution**: The client executes tools and accesses resources

## Tool Reference

### `process_text` Tool

Process text using the Process engine.

#### Parameters

```json
{
  "text": "Text to process",
  "config": {
    "language": "en-US",
    "resource": "default"
  },
  "output_format": "wav"
}
```

#### Returns

```json
{
  "result_id": "result-123456",
  "format": "wav",
  "base64": "base64-encoded-data"
}
```

## Resource Reference

### `resources://` URI Template

Access available resources for the Process engine.

#### Example

```
resources://voices
resources://languages
```

### `resource://{resource_id}` URI Template

Access a specific resource by its ID.

#### Example

```
resource://result-123456
```

## Implementing Custom Tools

You can extend the MCP integration with custom tools by creating new tool classes in the `tools` directory:

```python
class CustomTool:
    def __init__(self, config):
        self.config = config
    
    def get_schema(self):
        return {
            "name": "custom_tool",
            "description": "A custom tool",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "Parameter 1"
                    }
                },
                "required": ["param1"]
            },
            "returns": {
                "type": "object",
                "properties": {
                    "result": {
                        "type": "string",
                        "description": "Result"
                    }
                }
            }
        }
    
    async def execute(self, parameters):
        # Implement tool logic
        return {"result": "Custom result"}
```

Then register the tool in the `mcp_server.py` file:

```python
from mcp.tools.custom_tool import CustomTool

# In the MCPServer.__init__ method
self.tool_providers = [
    ProcessToolProvider(config.get("process_config", {})),
    CustomTool(config.get("custom_config", {}))
]
```

## Implementing Custom Resource Providers

You can extend the MCP integration with custom resource providers:

```python
class CustomResourceProvider:
    def __init__(self, config):
        self.config = config
    
    def get_schema(self):
        return {
            "uri_template": "custom://{resource_id}",
            "description": "Custom resources",
            "returns": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Resource ID"
                    },
                    "data": {
                        "type": "string",
                        "description": "Resource data"
                    }
                }
            }
        }
    
    async def get_resource(self, uri):
        # Extract resource ID from URI
        resource_id = uri.split("://")[1]
        
        # Return resource data
        return {
            "id": resource_id,
            "data": "Custom resource data"
        }
```

Then register the resource provider in the `mcp_server.py` file:

```python
from mcp.resources.custom_provider import CustomResourceProvider

# In the MCPServer.__init__ method
self.resource_providers = [
    CustomResourceProvider(config.get("custom_config", {}))
]
```

## Best Practices

1. **Tool Design**: Design tools with clear, specific functionality
2. **Parameter Validation**: Validate parameters before executing tools
3. **Error Handling**: Use the standardized error handling system
4. **Resource Management**: Use the resource system for managing large data
5. **Asynchronous Operations**: Implement tools as async functions for better performance
6. **Documentation**: Document tools and resources clearly

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure the MCP server is running and the port is accessible
2. **Protocol Negotiation Failed**: Check that the client and server support compatible protocol versions
3. **Tool Not Found**: Verify that the tool name is correct and the tool is registered
4. **Resource Not Found**: Check that the resource URI is correct and the resource exists
5. **Execution Error**: Check the server logs for details on the error

### Debugging

Enable debug logging to get more information:

```bash
# Set log level to debug
export MCP_LOG_LEVEL=debug

# Start the MCP server
python -m mcp.mcp_server
```
