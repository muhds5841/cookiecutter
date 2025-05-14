"""Unified configuration management system for Process components."""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from lib.logging import get_logger


class ConfigManager:
    """Centralized configuration management for all Process components.

    This class provides a unified interface for accessing configuration settings
    from various sources (environment variables, config files, defaults) with
    support for environment-specific overlays.
    """

    def __init__(
        self,
        component_name: str,
        config_path: Optional[Union[str, Path]] = None,
        env_prefix: Optional[str] = None,
    ):
        """Initialize the configuration manager.

        Args:
            component_name: Name of the component (e.g., 'process', 'grpc', 'rest')
            config_path: Path to the configuration file or directory
            env_prefix: Prefix for environment variables (defaults to component name uppercase)
        """
        self.component_name = component_name
        self.logger = get_logger(f"{component_name}.config")
        self.env_prefix = env_prefix or component_name.upper()
        self.config: Dict[str, Any] = {}

        # Load configuration in the correct order (each step overrides previous ones)
        self._load_defaults()

        if config_path:
            self._load_from_file(config_path)

        self._load_from_env()

        # Load environment-specific overrides if specified
        self._apply_environment_overrides()

        self.logger.info(f"Configuration loaded for {component_name}")

    def _load_defaults(self) -> None:
        """Load default configuration values."""
        # Common defaults for all components
        self.config = {
            "LOG_LEVEL": "info",
            "ENVIRONMENT": os.environ.get("PROCESS_ENVIRONMENT", "development"),
        }

        # Component-specific defaults
        if self.component_name == "process":
            self.config.update(
                {
                    "PROCESS_ENGINE": "default",
                    "PROCESS_LANGUAGE": "en-US",
                    "PROCESS_RESOURCE": "default",
                }
            )
        elif self.component_name == "grpc":
            self.config.update(
                {
                    "HOST": "0.0.0.0",
                    "PORT": 50051,
                    "MAX_WORKERS": 10,
                }
            )
        elif self.component_name == "rest":
            self.config.update(
                {
                    "HOST": "0.0.0.0",
                    "PORT": 5000,
                    "WORKERS": 4,
                }
            )
        elif self.component_name == "mcp":
            self.config.update(
                {
                    "HOST": "0.0.0.0",
                    "PORT": 4000,
                    "TRANSPORTS_SSE": True,
                    "TRANSPORTS_STDIO": True,
                    "TRANSPORTS_GRPC": False,
                }
            )

    def _load_from_file(self, config_path: Union[str, Path]) -> None:
        """Load configuration from a file.

        Args:
            config_path: Path to the configuration file or directory
        """
        if isinstance(config_path, str):
            config_path = Path(config_path)

        # If path is a directory, look for component-specific config file
        if config_path.is_dir():
            config_file = config_path / f"{self.component_name}.json"
            if not config_file.exists():
                config_file = config_path / "config.json"
        else:
            config_file = config_path

        if not config_file.exists():
            self.logger.warning(f"Configuration file not found: {config_file}")
            return

        try:
            with open(config_file, "r") as f:
                file_config = json.load(f)
                self.config.update(file_config)
                self.logger.info(f"Loaded configuration from {config_file}")
        except Exception as e:
            self.logger.error(f"Error loading configuration from {config_file}: {e}")

    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        prefix = f"{self.env_prefix}_"
        env_config = {}

        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix) :]

                # Try to parse boolean values
                if value.lower() in ("true", "yes", "1"):
                    env_config[config_key] = True
                elif value.lower() in ("false", "no", "0"):
                    env_config[config_key] = False
                # Try to parse numeric values
                elif value.isdigit():
                    env_config[config_key] = int(value)
                elif value.replace(".", "", 1).isdigit() and value.count(".") == 1:
                    env_config[config_key] = float(value)
                else:
                    env_config[config_key] = value

        self.config.update(env_config)
        if env_config:
            self.logger.info(f"Loaded {len(env_config)} settings from environment variables")

    def _apply_environment_overrides(self) -> None:
        """Apply environment-specific configuration overrides."""
        environment = self.config.get("ENVIRONMENT", "development")

        # Look for environment-specific section in config
        env_config = self.config.get(f"ENV_{environment.upper()}", {})
        if env_config:
            self.config.update(env_config)
            self.logger.info(f"Applied configuration overrides for environment: {environment}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key is not found

        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
        self.logger.debug(f"Set configuration {key}={value}")

    def as_dict(self) -> Dict[str, Any]:
        """Get the entire configuration as a dictionary.

        Returns:
            Configuration dictionary
        """
        return self.config.copy()

    def validate(self, schema: Dict[str, Any]) -> List[str]:
        """Validate the configuration against a schema.

        Args:
            schema: JSON Schema for validation

        Returns:
            List of validation errors, empty if valid
        """
        # Simple validation implementation
        errors = []

        # Check required fields
        for field in schema.get("required", []):
            if field not in self.config:
                errors.append(f"Missing required field: {field}")

        # Check field types
        properties = schema.get("properties", {})
        for key, value in self.config.items():
            if key in properties:
                prop_schema = properties[key]
                expected_type = prop_schema.get("type")

                if expected_type == "string" and not isinstance(value, str):
                    errors.append(f"Field {key} should be a string, got {type(value).__name__}")
                elif expected_type == "integer" and not isinstance(value, int):
                    errors.append(f"Field {key} should be an integer, got {type(value).__name__}")
                elif expected_type == "number" and not isinstance(value, (int, float)):
                    errors.append(f"Field {key} should be a number, got {type(value).__name__}")
                elif expected_type == "boolean" and not isinstance(value, bool):
                    errors.append(f"Field {key} should be a boolean, got {type(value).__name__}")
                elif expected_type == "array" and not isinstance(value, list):
                    errors.append(f"Field {key} should be an array, got {type(value).__name__}")
                elif expected_type == "object" and not isinstance(value, dict):
                    errors.append(f"Field {key} should be an object, got {type(value).__name__}")

        return errors


def create_config_manager(
    component_name: str,
    config_path: Optional[Union[str, Path]] = None,
    env_prefix: Optional[str] = None,
) -> ConfigManager:
    """Create a configuration manager for a component.

    Args:
        component_name: Name of the component
        config_path: Path to the configuration file or directory
        env_prefix: Prefix for environment variables

    Returns:
        ConfigManager instance
    """
    return ConfigManager(component_name, config_path, env_prefix)
