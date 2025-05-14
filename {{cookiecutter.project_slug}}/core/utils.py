"""
Utility functions for the TTS system.

This module provides common utility functions that can be used
across all components of the TTS system.
"""

import os
import json
import time
import uuid
import hashlib
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Callable, TypeVar, cast

# Type variables for generic functions
T = TypeVar('T')
U = TypeVar('U')


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID.
    
    Args:
        prefix: Optional prefix for the ID.
    
    Returns:
        A unique ID string.
    """
    unique_id = str(uuid.uuid4())
    return f"{prefix}{unique_id}" if prefix else unique_id


def calculate_hash(content: Union[str, bytes], algorithm: str = "sha256") -> str:
    """Calculate hash of content.
    
    Args:
        content: Content to hash (string or bytes).
        algorithm: Hash algorithm to use.
    
    Returns:
        Hexadecimal hash string.
    """
    if isinstance(content, str):
        content = content.encode("utf-8")
    
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(content)
    return hash_obj.hexdigest()


def create_temp_file(content: Union[str, bytes], suffix: str = ".wav") -> str:
    """Create a temporary file with the given content.
    
    Args:
        content: Content to write to the file.
        suffix: File suffix/extension.
    
    Returns:
        Path to the temporary file.
    """
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
        if isinstance(content, str):
            temp_file.write(content.encode("utf-8"))
        else:
            temp_file.write(content)
        return temp_file.name


def safe_delete_file(file_path: Union[str, Path]) -> bool:
    """Safely delete a file if it exists.
    
    Args:
        file_path: Path to the file to delete.
    
    Returns:
        True if the file was deleted, False otherwise.
    """
    try:
        file_path = Path(file_path)
        if file_path.exists():
            file_path.unlink()
            return True
    except Exception:
        pass
    return False


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0,
          exceptions: Union[Exception, tuple] = Exception) -> Callable:
    """Retry decorator for functions that might fail.
    
    Args:
        max_attempts: Maximum number of attempts.
        delay: Initial delay between attempts (seconds).
        backoff: Backoff multiplier (how much to increase delay after each failure).
        exceptions: Exception or tuple of exceptions to catch.
    
    Returns:
        Decorated function.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:  # Don't sleep after the last attempt
                        time.sleep(current_delay)
                        current_delay *= backoff
            
            # If we get here, all attempts failed
            raise last_exception or Exception("All retry attempts failed")
        
        return wrapper
    
    return decorator


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any], 
                overwrite: bool = True) -> Dict[str, Any]:
    """Recursively merge two dictionaries.
    
    Args:
        dict1: First dictionary.
        dict2: Second dictionary.
        overwrite: Whether to overwrite values in dict1 with values from dict2.
    
    Returns:
        Merged dictionary.
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = merge_dicts(result[key], value, overwrite)
        elif key not in result or overwrite:
            # Add new key or overwrite existing value
            result[key] = value
    
    return result


def to_snake_case(text: str) -> str:
    """Convert text to snake_case.
    
    Args:
        text: Text to convert.
    
    Returns:
        Text in snake_case.
    """
    import re
    # Replace non-alphanumeric characters with underscores
    s1 = re.sub(r'[^a-zA-Z0-9]', '_', text)
    # Insert underscore between lowercase and uppercase letters
    s2 = re.sub(r'([a-z])([A-Z])', r'\1_\2', s1)
    # Convert to lowercase
    return s2.lower()


def to_camel_case(text: str) -> str:
    """Convert text to camelCase.
    
    Args:
        text: Text to convert.
    
    Returns:
        Text in camelCase.
    """
    import re
    # Replace non-alphanumeric characters with spaces
    s1 = re.sub(r'[^a-zA-Z0-9]', ' ', text)
    # Split by spaces and join with first word lowercase, rest capitalized
    words = s1.split()
    if not words:
        return ""
    return words[0].lower() + ''.join(word.capitalize() for word in words[1:])


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds.
    
    Returns:
        Formatted duration string (e.g., "1h 2m 3s").
    """
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or hours > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    
    return " ".join(parts)


def get_file_size_str(size_bytes: int) -> str:
    """Convert file size in bytes to human-readable string.
    
    Args:
        size_bytes: File size in bytes.
    
    Returns:
        Formatted file size string (e.g., "1.23 MB").
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024 or unit == 'TB':
            break
        size_bytes /= 1024.0
    
    return f"{size_bytes:.2f} {unit}"
