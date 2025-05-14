# Process Component

The Process component is the core of the system, providing a flexible and extensible framework for text processing. It follows a modular design with a plugin architecture that allows for easy extension of functionality.

## Architecture

### Core Components

- **ProcessBase** (`process_base.py`): Abstract base class that defines the standard interface for all Process implementations
- **Process** (`process.py`): Main implementation of the Process interface
- **Plugin System** (`plugin_system.py`): Framework for extending Process functionality through plugins

## Using the Process Component

### Basic Usage

```python
from process.process import Process

# Create a Process instance
process = Process()

# Process text
result = process.run({
    "text": "Hello, world!",
    "config": {
        "language": "en-US",
        "resource": "default"
    },
    "output_format": "wav"
})

# Access the result
result_id = result["result_id"]
base64_data = result["base64"]
```

### Configuration

The Process component can be configured through environment variables, configuration files, or directly in code:

```python
from core.config_manager import create_config_manager
from process.process import Process

# Create a configuration manager
config = create_config_manager("process")

# Set configuration values
config.set("PROCESS_ENGINE", "custom")
config.set("PROCESS_LANGUAGE", "pl-PL")

# Create a Process instance with the configuration
process = Process()
process.initialize(config.as_dict())
```

## Plugin System

The Process component includes a plugin system that allows for easy extension of functionality.

### Creating a Plugin

To create a plugin, extend the `PluginBase` class from `plugin_system.py`:

```python
from process.plugin_system import PluginBase
from typing import Dict, Any, List, Optional

class MyCustomPlugin(PluginBase):
    # Plugin metadata
    PLUGIN_NAME = "my_custom_plugin"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "My custom processing plugin"
    PLUGIN_AUTHOR = "Your Name"
    
    def run(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        # Process the text
        text = parameters.get("text", "")
        processed_text = text.upper()  # Example processing
        
        # Return the result
        return {
            "result_id": "custom-result",
            "text": processed_text,
            "format": "text"
        }
    
    def get_available_resources(self) -> List[Dict[str, Any]]:
        return [
            {"name": "custom-resource", "type": "text", "description": "Custom text processor"}
        ]
    
    def get_resource_by_id(self, resource_id: str) -> Optional[Dict[str, Any]]:
        if resource_id == "custom-resource":
            return {"id": resource_id, "type": "text"}
        return None
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "status": "running",
            "version": self.PLUGIN_VERSION,
            "name": self.PLUGIN_NAME
        }
```

### Registering a Plugin

Plugins can be registered manually or discovered automatically:

```python
from process.plugin_system import get_plugin_registry
from my_plugin import MyCustomPlugin

# Get the plugin registry
registry = get_plugin_registry()

# Register a plugin manually
registry.register_plugin("my_custom_plugin", MyCustomPlugin)

# Or discover plugins from a directory
registry.discover_plugins("path/to/plugins")
```

### Using Plugins

Once registered, plugins can be used through the plugin registry:

```python
from process.plugin_system import get_plugin_registry

# Get the plugin registry
registry = get_plugin_registry()

# Get a plugin instance
plugin = registry.get_plugin_instance("my_custom_plugin")

# Use the plugin
result = plugin.run({"text": "Hello, world!"})
```

### Plugin Hooks

Plugins can also define hooks that are called at specific points in the processing flow:

```python
from process.plugin_system import PluginBase

class MyHookPlugin(PluginBase):
    PLUGIN_NAME = "my_hook_plugin"
    
    @staticmethod
    def pre_process_hook(text: str, config: Dict[str, Any]) -> str:
        # Modify the text before processing
        return text.strip()
    
    # Register hooks
    HOOKS = {
        "pre_process": pre_process_hook
    }
```

## Error Handling

The Process component includes standardized error handling through the `lib.error_handling` module:

```python
from core.error_handling import ProcessError, ValidationError

def my_function():
    try:
        # Some code that might fail
        if invalid_condition:
            raise ValidationError("Invalid input", details={"field": "text"})
    except Exception as e:
        # Convert to a standardized error
        raise ProcessError("Processing failed", code=ErrorCode.PROCESS_ENGINE_ERROR, cause=e)
```

## Advanced Features

### Custom Engine Implementation

You can create custom engine implementations by implementing the `Engine` protocol:

```python
from typing import Dict, Any, List, Optional
from process.process import Engine

class MyCustomEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def process(self, text: str, config: Optional[Dict[str, Any]] = None) -> bytes:
        # Custom processing logic
        return b"CUSTOM_RESULT"
    
    def get_available_resources(self) -> List[Dict[str, Any]]:
        # Return available resources
        return [{"name": "custom", "type": "text"}]
    
    def get_available_languages(self) -> List[str]:
        # Return available languages
        return ["en-US", "pl-PL"]
```

### Resource Caching

The Process component includes a resource cache for efficient retrieval of previously processed results:

```python
from process.process import Process

process = Process()

# Process text
result = process.run({"text": "Hello, world!"})
result_id = result["result_id"]

# Retrieve the resource later
resource = process.get_resource_by_id(result_id)
```
