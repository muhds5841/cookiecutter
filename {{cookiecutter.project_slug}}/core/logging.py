"""
Logging module for the TTS system.

This module provides utilities for configuring and using logging
across all components of the TTS system.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Default log format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Default log level
DEFAULT_LOG_LEVEL = logging.INFO

# Available log levels
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def configure_logging(
    level: Union[str, int] = DEFAULT_LOG_LEVEL,
    log_format: str = DEFAULT_LOG_FORMAT,
    log_file: Optional[Union[str, Path]] = None,
    log_dir: Optional[Union[str, Path]] = None,
    component_name: str = "tts",
    console: bool = True,
    file_rotation: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
) -> logging.Logger:
    """Configure logging for a component of the TTS system.

    Args:
        level: Log level (debug, info, warning, error, critical) or logging level constant.
        log_format: Format string for log messages.
        log_file: Path to log file. If None and log_dir is provided, a default name is used.
        log_dir: Directory to store log files. If None, logs are only sent to console.
        component_name: Name of the component (used for logger name and default log file).
        console: Whether to log to console.
        file_rotation: Whether to use rotating file handler.
        max_bytes: Maximum size of each log file before rotation.
        backup_count: Number of backup log files to keep.

    Returns:
        Configured logger instance.
    """
    # Convert string level to logging level constant
    if isinstance(level, str):
        level = level.lower()
        level = LOG_LEVELS.get(level, DEFAULT_LOG_LEVEL)

    # Create logger
    logger = logging.getLogger(component_name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:  # Make a copy of the list
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(log_format)

    # Add console handler if requested
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Add file handler if log_file or log_dir is provided
    if log_file or log_dir:
        if log_dir:
            log_dir = Path(log_dir)
            os.makedirs(log_dir, exist_ok=True)

            if not log_file:
                log_file = log_dir / f"{component_name}.log"

        if file_rotation:
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8",
            )
        else:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name.

    If a logger with this name already exists, it is returned.
    Otherwise, a new logger is created with default configuration.

    Args:
        name: Logger name.

    Returns:
        Logger instance.
    """
    logger = logging.getLogger(name)

    # If logger doesn't have handlers, configure it with defaults
    if not logger.handlers:
        # Use the root logger's level if it has been configured
        root_logger = logging.getLogger()
        if root_logger.level != logging.WARNING:  # Default level
            logger.setLevel(root_logger.level)
        else:
            logger.setLevel(DEFAULT_LOG_LEVEL)

        # Add a console handler with default format
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
        logger.addHandler(handler)

    return logger


def configure_from_config(config: Dict[str, Any], component_name: str = "tts") -> logging.Logger:
    """Configure logging from a configuration dictionary.

    Args:
        config: Configuration dictionary with logging settings.
        component_name: Name of the component.

    Returns:
        Configured logger instance.
    """
    log_config = config.get("logging", {})

    return configure_logging(
        level=log_config.get("level", DEFAULT_LOG_LEVEL),
        log_format=log_config.get("format", DEFAULT_LOG_FORMAT),
        log_file=log_config.get("file"),
        log_dir=log_config.get("dir"),
        component_name=component_name,
        console=log_config.get("console", True),
        file_rotation=log_config.get("file_rotation", True),
        max_bytes=log_config.get("max_bytes", 10 * 1024 * 1024),
        backup_count=log_config.get("backup_count", 5),
    )
