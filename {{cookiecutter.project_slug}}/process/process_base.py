"""Base abstract class for all Process implementations."""

import abc
from typing import Any, Dict, List, Optional


class ProcessBase(abc.ABC):
    """Abstract base class for all Process implementations.

    This class defines the standard interface that all Process implementations
    must follow, ensuring consistency across different backends and implementations.
    """

    @abc.abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the Process with the given configuration.

        Args:
            config: Configuration dictionary for the Process
        """
        pass

    @abc.abstractmethod
    def run(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Run the Process with the given parameters.

        Args:
            parameters: Dictionary containing the parameters for the process
                Must include 'text' key with the input text
                May include other parameters specific to the implementation

        Returns:
            Dictionary containing the results of the process
                Must include 'result_id' key with a unique identifier
                Other keys depend on the specific implementation
        """
        pass

    @abc.abstractmethod
    def get_available_resources(self) -> List[Dict[str, Any]]:
        """Get a list of available resources for this Process.

        Returns:
            List of dictionaries, each representing a resource
            Each dictionary must include 'name' and 'type' keys
        """
        pass

    @abc.abstractmethod
    def get_resource_by_id(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific resource by its ID.

        Args:
            resource_id: Unique identifier for the resource

        Returns:
            Dictionary containing the resource data, or None if not found
        """
        pass

    @abc.abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the Process.

        Returns:
            Dictionary containing status information
                Must include 'status' key with a string value
                Must include 'version' key with the version string
                May include other status information
        """
        pass
