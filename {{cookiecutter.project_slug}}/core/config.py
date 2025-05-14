"""
Configuration module for the Process system.

This module provides utilities for loading and managing configuration
from various sources (environment variables, config files, etc.)
and making it available to all components of the system.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for the Process system.

    Handles loading configuration from environment variables, config files,
    and provides a unified interface for accessing configuration values.
    """

    def __init__(self, config_dir: Optional[Union[str, Path]] = None):
        """Initialize the configuration manager.

        Args:
            config_dir: Directory containing configuration files.
                If None, uses the current directory.
        """
        self.config: Dict[str, Any] = {}
        self.config_dir = Path(config_dir) if config_dir else Path.cwd()

        # Load environment variables from .env file if it exists
        env_file = self.config_dir / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            logger.info(f"Loaded environment variables from {env_file}")

    def load_from_env(self, prefix: str = "") -> None:
        """Load configuration from environment variables.

        Args:
            prefix: Optional prefix for environment variables to load.
                If provided, only variables with this prefix will be loaded,
                and the prefix will be removed from the keys.
        """
        for key, value in os.environ.items():
            if prefix and not key.startswith(prefix):
                continue

            # Remove prefix if it exists
            config_key = key[len(prefix):] if prefix and key.startswith(prefix) else key

            # Try to parse as JSON if it looks like a JSON value
            if (
                value.startswith("{")
                or value.startswith("[")
                or value.lower() in ("true", "false", "null")
                or (value.replace(".", "").replace("-", "").isdigit())
            ):
                try:
                    self.config[config_key] = json.loads(value)
                    continue
                except json.JSONDecodeError:
                    pass  # Not valid JSON, treat as string

            self.config[config_key] = value

        logger.debug(f"Loaded {len(self.config)} configuration values from environment")

    def load_from_file(self, file_path: Union[str, Path]) -> None:
        """Load configuration from a JSON or environment file.

        Args:
            file_path: Path to the configuration file.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            logger.warning(f"Configuration file {file_path} not found")
            return

        if file_path.suffix.lower() == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                self.config.update(config_data)
            logger.info(f"Loaded configuration from {file_path}")
        elif file_path.name == ".env":
            # .env files are already loaded by load_dotenv
            pass
        else:
            logger.warning(f"Unsupported configuration file format: {file_path}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key.
            default: Default value to return if the key is not found.

        Returns:
            The configuration value, or the default if not found.
        """
        # First check if the key exists in the config dict
        if key in self.config:
            return self.config[key]

        # Then check if it exists as an environment variable
        if key in os.environ:
            return os.environ[key]

        # Return the default if not found
        return default

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key.
            value: Configuration value.
        """
        self.config[key] = value

    def as_dict(self) -> Dict[str, Any]:
        """Get the entire configuration as a dictionary.

        Returns:
            A dictionary containing all configuration values.
        """
        return self.config.copy()


def load_config(
    config_dir: Optional[Union[str, Path]] = None,
    config_files: Optional[List[Union[str, Path]]] = None,
    env_prefix: str = "",
) -> Config:
    """Load configuration from environment variables and config files.

    This is the main entry point for loading configuration in the Process system.

    Args:
        config_dir: Directory containing configuration files.
            If None, uses the current directory.
        config_files: List of configuration files to load.
            If None, tries to load default config files.
        env_prefix: Prefix for environment variables to load.

    Returns:
        A Config object containing the loaded configuration.
    """
    config = Config(config_dir)

    # Load from environment variables
    config.load_from_env(prefix=env_prefix)

    # Load from config files if provided
    if config_files:
        for file_path in config_files:
            config.load_from_file(file_path)
    else:
        # Try to load default config files
        default_files = ["config.json", ".env"]
        for file_name in default_files:
            file_path = config.config_dir / file_name
            if file_path.exists():
                config.load_from_file(file_path)

    return config
