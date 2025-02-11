import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from models import Device, DeviceEvent, db
from protocols.protocol_factory import ProtocolFactory
from protocols.protocol_adapter import ProtocolAdapter

logger = logging.getLogger(__name__)


class DeviceManager:
    """Manager for IoT devices across different protocols."""

    def __init__(self):
        self._protocol_adapters: Dict[str, ProtocolAdapter] = {}
        # device_id -> protocol_name
        self._device_protocols: Dict[str, str] = {}

    def initialize(self, protocol_configs: Dict[str, Dict[str, Any]]) -> None:
        """Initialize protocol adapters with configurations.

        Args:
            protocol_configs: Dictionary of protocol configurations
                            {protocol_name: config_dict}
        """
        for protocol_name, config in protocol_configs.items():
            try:
                if ProtocolFactory.validate_protocol_config(protocol_name, config):
                    adapter = ProtocolFactory.create_adapter(
                        protocol_name, config)
                    if adapter.connect():
                        self._protocol_adapters[protocol_name] = adapter
                        logger.info(f"Initialized {protocol_name} adapter")
                    else:
                        logger.error(
                            f"Failed to connect {protocol_name} adapter")
            except Exception as e:
                logger.error(
                    f"Error initializing {protocol_name} adapter: {str(e)}")

    def cleanup(self) -> None:
        """Clean up all protocol adapters."""
        for protocol_name, adapter in self._protocol_adapters.items():
            try:
                adapter.disconnect()
                logger.info(f"Disconnected {protocol_name} adapter")
            except Exception as e:
                logger.error(
                    f"Error disconnecting {protocol_name} adapter: {str(e)}")

    def add_device(self, device_data: Dict[str, Any]) -> Optional[Device]:
        """Add a new device to the system.

        Args:
            device_data: Dictionary containing device information

        Returns:
            Optional[Device]: Added device if successful, None otherwise
        """
        try:
            # Create device instance
            device = Device(
                name=device_data['name'],
                type=device_data['type'],
                protocol=device_data['protocol'],
                mac_address=device_data['mac_address'],
                ip_address=device_data.get('ip_address'),
                manufacturer=device_data.get('manufacturer'),
                model=device_data.get('model'),
                capabilities=device_data.get('capabilities', []),
                config=device_data.get('config', {}),
                room_id=device_data.get('room_id')
            )

            # Get protocol adapter
            protocol_name = device_data['protocol'].lower()
            adapter = self._protocol_adapters.get(protocol_name)
            if not adapter:
                logger.error(
                    f"No adapter available for protocol: {protocol_name}")
                return None

            # Register device with protocol adapter
            if adapter.register_device(device, self._handle_device_state_update):
                db.session.add(device)
                db.session.commit()

                self._device_protocols[device.id] = protocol_name
                logger.info(f"Added device: {device.name} ({device.id})")
                return device
            else:
                logger.error(
                    f"Failed to register device with protocol adapter")
                return None

        except Exception as e:
            logger.error(f"Error adding device: {str(e)}")
            return None

    def remove_device(self, device_id: str) -> bool:
        """Remove a device from the system.

        Args:
            device_id: ID of the device to remove

        Returns:
            bool: True if removal successful, False otherwise
        """
        try:
            device = Device.query.get(device_id)
            if not device:
                logger.warning(f"Device not found: {device_id}")
                return False

            # Unregister from protocol adapter
            protocol_name = self._device_protocols.get(device_id)
            if protocol_name:
                adapter = self._protocol_adapters.get(protocol_name)
                if adapter:
                    adapter.unregister_device(device)
                del self._device_protocols[device_id]

            # Remove from database
            db.session.delete(device)
            db.session.commit()

            logger.info(f"Removed device: {device.name} ({device_id})")
            return True

        except Exception as e:
            logger.error(f"Error removing device: {str(e)}")
            return False

    def get_device(self, device_id: str) -> Optional[Device]:
        """Get device by ID.

        Args:
            device_id: ID of the device

        Returns:
            Optional[Device]: Device if found, None otherwise
        """
        return Device.query.get(device_id)

    def get_all_devices(self) -> List[Device]:
        """Get all registered devices.

        Returns:
            List[Device]: List of all devices
        """
        return Device.query.all()

    def get_devices_by_type(self, device_type: str) -> List[Device]:
        """Get devices by type.

        Args:
            device_type: Type of devices to get

        Returns:
            List[Device]: List of matching devices
        """
        return Device.query.filter_by(type=device_type).all()

    def get_devices_by_room(self, room_id: str) -> List[Device]:
        """Get devices in a room.

        Args:
            room_id: ID of the room

        Returns:
            List[Device]: List of devices in the room
        """
        return Device.query.filter_by(room_id=room_id).all()

    def send_command(self, device_id: str, command: Dict[str, Any]) -> bool:
        """Send command to device.

        Args:
            device_id: ID of the target device
            command: Command to send

        Returns:
            bool: True if command sent successfully, False otherwise
        """
        try:
            device = self.get_device(device_id)
            if not device:
                logger.warning(f"Device not found: {device_id}")
                return False

            protocol_name = self._device_protocols.get(device_id)
            if not protocol_name:
                logger.error(f"No protocol registered for device: {device_id}")
                return False

            adapter = self._protocol_adapters.get(protocol_name)
            if not adapter:
                logger.error(
                    f"No adapter available for protocol: {protocol_name}")
                return False

            if adapter.send_command(device, command):
                # Log command event
                event = DeviceEvent(
                    device_id=device_id,
                    event_type='command_sent',
                    message=f"Command sent: {command}"
                )
                db.session.add(event)
                db.session.commit()
                return True
            return False

        except Exception as e:
            logger.error(f"Error sending command: {str(e)}")
            return False

    def get_device_state(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get current state of device.

        Args:
            device_id: ID of the device

        Returns:
            Optional[Dict[str, Any]]: Device state if available, None otherwise
        """
        try:
            device = self.get_device(device_id)
            if not device:
                logger.warning(f"Device not found: {device_id}")
                return None

            protocol_name = self._device_protocols.get(device_id)
            if not protocol_name:
                logger.error(f"No protocol registered for device: {device_id}")
                return None

            adapter = self._protocol_adapters.get(protocol_name)
            if not adapter:
                logger.error(
                    f"No adapter available for protocol: {protocol_name}")
                return None

            return adapter.get_device_state(device)

        except Exception as e:
            logger.error(f"Error getting device state: {str(e)}")
            return None

    def discover_devices(self) -> bool:
        """Initiate device discovery across all protocols.

        Returns:
            bool: True if discovery initiated successfully, False otherwise
        """
        success = True
        for protocol_name, adapter in self._protocol_adapters.items():
            try:
                if not adapter.discover_devices():
                    logger.error(
                        f"Failed to start discovery for {protocol_name}")
                    success = False
            except Exception as e:
                logger.error(
                    f"Error during discovery for {protocol_name}: {str(e)}")
                success = False
        return success

    def _handle_device_state_update(self, device_id: str, state: Dict[str, Any]) -> None:
        """Handle device state updates from protocol adapters.

        Args:
            device_id: ID of the device
            state: New device state
        """
        try:
            device = self.get_device(device_id)
            if device:
                device.state = state
                device.last_seen = datetime.utcnow()
                db.session.commit()

                # Log state change event
                event = DeviceEvent(
                    device_id=device_id,
                    event_type='state_changed',
                    message=f"State updated: {state}"
                )
                db.session.add(event)
                db.session.commit()
            else:
                logger.warning(f"State update for unknown device: {device_id}")

        except Exception as e:
            logger.error(f"Error handling state update: {str(e)}")

    def get_device_events(self, device_id: str, limit: int = 100) -> List[DeviceEvent]:
        """Get recent events for a device.

        Args:
            device_id: ID of the device
            limit: Maximum number of events to return

        Returns:
            List[DeviceEvent]: List of device events
        """
        return DeviceEvent.query.filter_by(device_id=device_id)\
            .order_by(DeviceEvent.timestamp.desc())\
            .limit(limit)\
            .all()
