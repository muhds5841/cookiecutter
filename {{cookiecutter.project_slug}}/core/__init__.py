"""
Lib package for the TTS system.

This package provides shared utilities, configuration, and logging
functionality for all components of the TTS system.
"""

# Import key functions and classes from modules
from .config import Config, load_config
from .logging import (
    configure_logging, 
    get_logger, 
    configure_from_config,
    DEFAULT_LOG_FORMAT,
    DEFAULT_LOG_LEVEL,
    LOG_LEVELS
)
from .utils import (
    generate_id,
    calculate_hash,
    create_temp_file,
    safe_delete_file,
    retry,
    merge_dicts,
    to_snake_case,
    to_camel_case,
    format_duration,
    get_file_size_str
)

# Define what's available when using "from lib import *"
__all__ = [
    # From config
    'Config', 'load_config',
    
    # From logging
    'configure_logging', 'get_logger', 'configure_from_config',
    'DEFAULT_LOG_FORMAT', 'DEFAULT_LOG_LEVEL', 'LOG_LEVELS',
    
    # From utils
    'generate_id', 'calculate_hash', 'create_temp_file', 'safe_delete_file',
    'retry', 'merge_dicts', 'to_snake_case', 'to_camel_case',
    'format_duration', 'get_file_size_str'
]

# Package version
__version__ = "0.1.0"
