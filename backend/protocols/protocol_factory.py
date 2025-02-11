import logging
from typing import Dict, Type, Optional
from .protocol_adapter import ProtocolAdapter
from .mqtt_handler import MQTTHandler

logger = logging.getLogger(__name__)


class ProtocolFactory:
    """Factory for creating protocol adapters."""

    # Registry of supported protocols
    _protocols: Dict[str, Type[ProtocolAdapter]] = {
        'mqtt': MQTTHandler,
        # Add more protocols as they are implemented
        # 'zigbee': ZigbeeHandler,
        # 'zwave': ZWaveHandler,
        # 'wifi': WiFiHandler,
    }

    @classmethod
    def register_protocol(cls, protocol_name: str, protocol_class: Type[ProtocolAdapter]) -> None:
        """Register a new protocol implementation.

        Args:
            protocol_name: Name of the protocol
            protocol_class: Protocol adapter class implementation
        """
        if not issubclass(protocol_class, ProtocolAdapter):
            raise ValueError(
                f"Protocol class must implement ProtocolAdapter interface")

        cls._protocols[protocol_name.lower()] = protocol_class
        logger.info(f"Registered protocol: {protocol_name}")

    @classmethod
    def unregister_protocol(cls, protocol_name: str) -> None:
        """Unregister a protocol implementation.

        Args:
            protocol_name: Name of the protocol to unregister
        """
        if protocol_name.lower() in cls._protocols:
            del cls._protocols[protocol_name.lower()]
            logger.info(f"Unregistered protocol: {protocol_name}")

    @classmethod
    def create_adapter(cls, protocol_name: str, config: Optional[Dict] = None) -> ProtocolAdapter:
        """Create and configure a protocol adapter instance.

        Args:
            protocol_name: Name of the protocol to create
            config: Optional configuration for the protocol

        Returns:
            ProtocolAdapter: Configured protocol adapter instance

        Raises:
            ValueError: If protocol is not supported
        """
        protocol_class = cls._protocols.get(protocol_name.lower())
        if not protocol_class:
            raise ValueError(f"Unsupported protocol: {protocol_name}")

        try:
            adapter = protocol_class()
            if config:
                adapter.configure(config)
            return adapter
        except Exception as e:
            logger.error(f"Error creating protocol adapter: {str(e)}")
            raise

    @classmethod
    def get_supported_protocols(cls) -> Dict[str, Dict]:
        """Get information about all supported protocols.

        Returns:
            Dict[str, Dict]: Dictionary of protocol information
        """
        protocols = {}
        for protocol_name, protocol_class in cls._protocols.items():
            try:
                # Create temporary instance to get protocol info
                adapter = protocol_class()
                protocols[protocol_name] = adapter.get_protocol_info()
            except Exception as e:
                logger.error(
                    f"Error getting protocol info for {protocol_name}: {str(e)}")
                protocols[protocol_name] = {"error": str(e)}
        return protocols

    @classmethod
    def validate_protocol_config(cls, protocol_name: str, config: Dict) -> bool:
        """Validate protocol configuration.

        Args:
            protocol_name: Name of the protocol
            config: Configuration to validate

        Returns:
            bool: True if configuration is valid, False otherwise
        """
        protocol_class = cls._protocols.get(protocol_name.lower())
        if not protocol_class:
            return False

        try:
            # Create temporary instance to validate config
            adapter = protocol_class()
            adapter.configure(config)
            return True
        except Exception as e:
            logger.error(f"Invalid protocol configuration: {str(e)}")
            return False
