"""Plugin system for extending Process functionality."""

import importlib
import inspect
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Type

from core.logging import get_logger
from process.process_base import ProcessBase


class PluginRegistry:
    """Registry for Process plugins.

    This class manages the registration, discovery, and instantiation of plugins
    that extend the core Process functionality.
    """

    def __init__(self):
        """Initialize the plugin registry."""
        self.logger = get_logger("process.plugins")
        self.plugins: Dict[str, Type[ProcessBase]] = {}
        self.plugin_instances: Dict[str, ProcessBase] = {}
        self.hooks: Dict[str, List[Callable]] = {}

    def register_plugin(self, name: str, plugin_class: Type[ProcessBase]) -> None:
        """Register a plugin class.

        Args:
            name: Unique name for the plugin
            plugin_class: Plugin class that extends ProcessBase
        """
        if name in self.plugins:
            self.logger.warning(f"Plugin '{name}' is already registered, overwriting")

        self.plugins[name] = plugin_class
        self.logger.info(f"Registered plugin: {name}")

    def register_hook(self, hook_name: str, hook_function: Callable) -> None:
        """Register a hook function.

        Args:
            hook_name: Name of the hook point
            hook_function: Function to call at the hook point
        """
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []

        self.hooks[hook_name].append(hook_function)
        self.logger.info(f"Registered hook '{hook_name}': {hook_function.__name__}")

    def get_plugin(self, name: str) -> Optional[Type[ProcessBase]]:
        """Get a plugin class by name.

        Args:
            name: Plugin name

        Returns:
            Plugin class or None if not found
        """
        return self.plugins.get(name)

    def get_plugin_instance(
        self, name: str, config: Optional[Dict[str, Any]] = None
    ) -> Optional[ProcessBase]:
        """Get or create a plugin instance.

        Args:
            name: Plugin name
            config: Configuration for the plugin

        Returns:
            Plugin instance or None if plugin not found
        """
        if name not in self.plugins:
            self.logger.error(f"Plugin not found: {name}")
            return None

        # Return existing instance if already created
        if name in self.plugin_instances:
            return self.plugin_instances[name]

        # Create new instance
        plugin_class = self.plugins[name]
        try:
            instance = plugin_class()
            if config:
                instance.initialize(config)
            self.plugin_instances[name] = instance
            self.logger.info(f"Created instance of plugin: {name}")
            return instance
        except Exception as e:
            self.logger.error(f"Error creating plugin instance '{name}': {e}")
            return None

    def call_hooks(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Call all registered hooks for a hook point.

        Args:
            hook_name: Name of the hook point
            *args: Positional arguments to pass to hook functions
            **kwargs: Keyword arguments to pass to hook functions

        Returns:
            List of results from hook functions
        """
        if hook_name not in self.hooks:
            return []

        results = []
        for hook_function in self.hooks[hook_name]:
            try:
                result = hook_function(*args, **kwargs)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error in hook '{hook_name}:{hook_function.__name__}': {e}")

        return results

    def discover_plugins(self, plugin_dir: str) -> Set[str]:
        """Discover and register plugins from a directory.

        Args:
            plugin_dir: Directory containing plugin modules

        Returns:
            Set of discovered plugin names
        """
        discovered = set()
        plugin_path = Path(plugin_dir)

        if not plugin_path.exists() or not plugin_path.is_dir():
            self.logger.warning(f"Plugin directory not found: {plugin_dir}")
            return discovered

        # Find all Python files in the directory
        for file_path in plugin_path.glob("*.py"):
            if file_path.name.startswith("_"):
                continue

            module_name = file_path.stem
            full_module_path = f"process.plugins.{module_name}"

            try:
                # Import the module
                module = importlib.import_module(full_module_path)

                # Find all ProcessBase subclasses in the module
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, ProcessBase) and obj != ProcessBase:

                        # Use class name as plugin name if not explicitly defined
                        plugin_name = getattr(obj, "PLUGIN_NAME", name.lower())
                        self.register_plugin(plugin_name, obj)
                        discovered.add(plugin_name)

                        # Register any hooks defined in the plugin
                        for hook_name, hook_func in getattr(obj, "HOOKS", {}).items():
                            self.register_hook(hook_name, hook_func)

            except Exception as e:
                self.logger.error(f"Error loading plugin module '{module_name}': {e}")

        self.logger.info(f"Discovered {len(discovered)} plugins in {plugin_dir}")
        return discovered


# Singleton instance of the plugin registry
_plugin_registry = PluginRegistry()


def get_plugin_registry() -> PluginRegistry:
    """Get the global plugin registry instance.

    Returns:
        PluginRegistry instance
    """
    return _plugin_registry


class PluginBase(ProcessBase):
    """Base class for Process plugins.

    Extend this class to create a new plugin that can be discovered
    and registered by the plugin system.
    """

    # Plugin metadata - override in subclasses
    PLUGIN_NAME: str = ""
    PLUGIN_VERSION: str = "1.0.0"
    PLUGIN_DESCRIPTION: str = ""
    PLUGIN_AUTHOR: str = ""

    # Hook definitions - override in subclasses
    HOOKS: Dict[str, Callable] = {}

    def __init__(self):
        """Initialize the plugin."""
        self.logger = get_logger(
            f"process.plugins.{self.PLUGIN_NAME or self.__class__.__name__.lower()}"
        )
        self.config = {}

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the plugin with configuration.

        Args:
            config: Plugin configuration
        """
        self.config = config
        self.logger.info(f"Initialized plugin: {self.PLUGIN_NAME or self.__class__.__name__}")


# Example plugin implementation
class ExamplePlugin(PluginBase):
    """Example plugin implementation."""

    PLUGIN_NAME = "example"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "Example plugin for demonstration"
    PLUGIN_AUTHOR = "Process Team"

    def run(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Run the plugin process.

        Args:
            parameters: Process parameters

        Returns:
            Process result
        """
        self.logger.info(f"Running example plugin with parameters: {parameters}")
        return {
            "result_id": "example-result",
            "message": "Example plugin executed successfully",
            "parameters": parameters,
        }

    def get_available_resources(self) -> List[Dict[str, Any]]:
        """Get available resources for this plugin.

        Returns:
            List of available resources
        """
        return [{"name": "example-resource", "type": "example", "description": "Example resource"}]

    def get_resource_by_id(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get a resource by ID.

        Args:
            resource_id: Resource ID

        Returns:
            Resource data or None if not found
        """
        if resource_id == "example-resource":
            return {"id": resource_id, "type": "example", "data": "Example resource data"}
        return None

    def get_status(self) -> Dict[str, Any]:
        """Get plugin status.

        Returns:
            Plugin status information
        """
        return {
            "status": "running",
            "version": self.PLUGIN_VERSION,
            "name": self.PLUGIN_NAME,
            "description": self.PLUGIN_DESCRIPTION,
        }

    # Example hook function
    @staticmethod
    def pre_process_hook(text: str, config: Dict[str, Any]) -> str:
        """Example hook that runs before text processing.

        Args:
            text: Input text
            config: Process configuration

        Returns:
            Modified text
        """
        return text.strip()

    # Register hooks
    HOOKS = {"pre_process": pre_process_hook}
