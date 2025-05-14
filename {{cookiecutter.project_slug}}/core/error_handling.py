"""Standardized error handling system for Process components."""

import sys
import traceback
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type

from lib.logging import get_logger


class ErrorCode(Enum):
    """Standard error codes for Process components."""

    # General errors (1-99)
    UNKNOWN_ERROR = 1
    CONFIGURATION_ERROR = 2
    INITIALIZATION_ERROR = 3
    VALIDATION_ERROR = 4
    RESOURCE_NOT_FOUND = 5
    PERMISSION_DENIED = 6
    TIMEOUT_ERROR = 7

    # Process-specific errors (100-199)
    PROCESS_ENGINE_ERROR = 100
    TEXT_PROCESSING_ERROR = 101
    RESOURCE_UNAVAILABLE = 102
    UNSUPPORTED_FORMAT = 103

    # Service-specific errors (200-299)
    SERVICE_UNAVAILABLE = 200
    INVALID_REQUEST = 201
    SERIALIZATION_ERROR = 202
    COMMUNICATION_ERROR = 203

    # Plugin-specific errors (300-399)
    PLUGIN_NOT_FOUND = 300
    PLUGIN_INITIALIZATION_ERROR = 301
    PLUGIN_EXECUTION_ERROR = 302

    # External service errors (400-499)
    EXTERNAL_SERVICE_ERROR = 400
    NETWORK_ERROR = 401
    AUTHENTICATION_ERROR = 402
    RATE_LIMIT_EXCEEDED = 403


class ProcessError(Exception):
    """Base exception class for all Process errors."""

    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize a Process error.

        Args:
            message: Error message
            code: Error code
            details: Additional error details
            cause: Original exception that caused this error
        """
        self.message = message
        self.code = code
        self.details = details or {}
        self.cause = cause

        # Construct the full error message
        full_message = f"[{code.name}] {message}"
        if cause:
            full_message += f" (Caused by: {type(cause).__name__}: {str(cause)})"

        super().__init__(full_message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary representation.

        Returns:
            Dictionary representation of the error
        """
        result = {
            "error": True,
            "code": self.code.value,
            "code_name": self.code.name,
            "message": self.message,
        }

        if self.details:
            result["details"] = self.details

        if self.cause:
            result["cause"] = {"type": type(self.cause).__name__, "message": str(self.cause)}

        return result


# Specific error classes
class ConfigurationError(ProcessError):
    """Error raised when there's a configuration issue."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message, ErrorCode.CONFIGURATION_ERROR, details, cause)


class ValidationError(ProcessError):
    """Error raised when input validation fails."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message, ErrorCode.VALIDATION_ERROR, details, cause)


class ResourceNotFoundError(ProcessError):
    """Error raised when a requested resource is not found."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message, ErrorCode.RESOURCE_NOT_FOUND, details, cause)


class ProcessEngineError(ProcessError):
    """Error raised when the Process engine encounters an error."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message, ErrorCode.PROCESS_ENGINE_ERROR, details, cause)


class ErrorHandler:
    """Error handler for Process components."""

    def __init__(self, component_name: str):
        """Initialize the error handler.

        Args:
            component_name: Name of the component
        """
        self.logger = get_logger(f"{component_name}.errors")
        self.component_name = component_name
        self.error_hooks: Dict[ErrorCode, List[Callable]] = {}

    def register_error_hook(self, error_code: ErrorCode, hook: Callable) -> None:
        """Register a hook to be called when a specific error occurs.

        Args:
            error_code: Error code to hook
            hook: Function to call when the error occurs
        """
        if error_code not in self.error_hooks:
            self.error_hooks[error_code] = []

        self.error_hooks[error_code].append(hook)
        self.logger.debug(f"Registered error hook for {error_code.name}: {hook.__name__}")

    def handle_error(self, error: Exception, log_level: str = "error") -> ProcessError:
        """Handle an exception by converting it to a ProcessError.

        Args:
            error: Exception to handle
            log_level: Log level to use

        Returns:
            ProcessError instance
        """
        # If it's already a ProcessError, just log it
        if isinstance(error, ProcessError):
            getattr(self.logger, log_level)(
                f"Error in {self.component_name}: {error.code.name} - {error.message}"
            )

            # Call any registered hooks for this error code
            if error.code in self.error_hooks:
                for hook in self.error_hooks[error.code]:
                    try:
                        hook(error)
                    except Exception as hook_error:
                        self.logger.error(f"Error in error hook {hook.__name__}: {hook_error}")

            return error

        # Convert other exceptions to ProcessError
        error_message = str(error)
        error_type = type(error).__name__

        # Determine the appropriate error code based on the exception type
        error_code = ErrorCode.UNKNOWN_ERROR

        if error_type == "ValueError":
            error_code = ErrorCode.VALIDATION_ERROR
        elif error_type == "KeyError" or error_type == "AttributeError":
            error_code = ErrorCode.RESOURCE_NOT_FOUND
        elif error_type == "TimeoutError":
            error_code = ErrorCode.TIMEOUT_ERROR
        elif error_type == "ConnectionError" or error_type == "ConnectionRefusedError":
            error_code = ErrorCode.NETWORK_ERROR

        # Create a ProcessError
        process_error = ProcessError(
            message=error_message,
            code=error_code,
            details={"type": error_type, "component": self.component_name},
            cause=error,
        )

        # Log the error with stack trace
        getattr(self.logger, log_level)(
            f"Error in {self.component_name}: {process_error.code.name} - {process_error.message}"
        )

        if log_level in ["error", "critical"]:
            self.logger.debug(f"Stack trace: {''.join(traceback.format_tb(error.__traceback__))}")

        # Call any registered hooks for this error code
        if process_error.code in self.error_hooks:
            for hook in self.error_hooks[process_error.code]:
                try:
                    hook(process_error)
                except Exception as hook_error:
                    self.logger.error(f"Error in error hook {hook.__name__}: {hook_error}")

        return process_error

    def create_error_response(self, error: Exception) -> Dict[str, Any]:
        """Create a standardized error response.

        Args:
            error: Exception to convert to response

        Returns:
            Error response dictionary
        """
        process_error = self.handle_error(error)
        return process_error.to_dict()


def create_error_handler(component_name: str) -> ErrorHandler:
    """Create an error handler for a component.

    Args:
        component_name: Name of the component

    Returns:
        ErrorHandler instance
    """
    return ErrorHandler(component_name)


def error_to_response(error: Exception, component_name: str = "process") -> Dict[str, Any]:
    """Convert an exception to a standardized error response.

    Args:
        error: Exception to convert
        component_name: Name of the component

    Returns:
        Error response dictionary
    """
    handler = create_error_handler(component_name)
    return handler.create_error_response(error)
