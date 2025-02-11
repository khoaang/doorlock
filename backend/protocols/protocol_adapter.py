from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
from models import Device


class ProtocolAdapter(ABC):
    """Abstract base class for protocol adapters."""

    @abstractmethod
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the protocol adapter with specific settings."""
        pass

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the protocol network/broker."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the protocol network/broker."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to the protocol network/broker."""
        pass

    @abstractmethod
    def register_device(self, device: Device, state_callback: Callable[[Dict[str, Any]], None]) -> bool:
        """Register a device for state updates.

        Args:
            device: The device to register
            state_callback: Callback function to handle device state updates

        Returns:
            bool: True if registration successful, False otherwise
        """
        pass

    @abstractmethod
    def unregister_device(self, device: Device) -> bool:
        """Unregister a device from state updates.

        Args:
            device: The device to unregister

        Returns:
            bool: True if unregistration successful, False otherwise
        """
        pass

    @abstractmethod
    def send_command(self, device: Device, command: Dict[str, Any]) -> bool:
        """Send a command to a device.

        Args:
            device: The target device
            command: The command to send

        Returns:
            bool: True if command sent successfully, False otherwise
        """
        pass

    @abstractmethod
    def get_device_state(self, device: Device) -> Optional[Dict[str, Any]]:
        """Get the current state of a device.

        Args:
            device: The device to get state for

        Returns:
            Optional[Dict[str, Any]]: Device state if available, None otherwise
        """
        pass

    @abstractmethod
    def discover_devices(self) -> bool:
        """Discover devices on the protocol network.

        Returns:
            bool: True if discovery initiated successfully, False otherwise
        """
        pass

    @abstractmethod
    def validate_command(self, device: Device, command: Dict[str, Any]) -> bool:
        """Validate a command against device capabilities.

        Args:
            device: The target device
            command: The command to validate

        Returns:
            bool: True if command is valid, False otherwise
        """
        pass

    @abstractmethod
    def handle_error(self, error: Exception, context: str) -> None:
        """Handle protocol-specific errors.

        Args:
            error: The error that occurred
            context: Context information about where the error occurred
        """
        pass

    @abstractmethod
    def get_protocol_info(self) -> Dict[str, Any]:
        """Get information about the protocol implementation.

        Returns:
            Dict[str, Any]: Protocol information including version, capabilities, etc.
        """
        pass
