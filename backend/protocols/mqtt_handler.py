import json
import logging
from typing import Dict, Any, Optional, Callable
import paho.mqtt.client as mqtt
from models import Device, DeviceEvent, db
from datetime import datetime
from .protocol_adapter import ProtocolAdapter

logger = logging.getLogger(__name__)


class MQTTHandler(ProtocolAdapter):
    """MQTT protocol adapter for IoT devices."""

    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

        # Store callbacks for handling device messages
        self._message_callbacks = {}

        # Configure MQTT broker settings
        self.broker_host = "localhost"  # Default to local broker
        self.broker_port = 1883
        self.broker_keepalive = 60
        self.username = None
        self.password = None

        self._connect()

    def configure(self, config: Dict[str, Any]):
        """Configure MQTT broker settings."""
        self.broker_host = config.get('host', self.broker_host)
        self.broker_port = config.get('port', self.broker_port)
        self.broker_keepalive = config.get('keepalive', self.broker_keepalive)
        self.username = config.get('username')
        self.password = config.get('password')

        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)

        # Reconnect with new settings if already connected
        if self.client.is_connected():
            self.client.disconnect()
            self._connect()

    def _connect(self):
        """Connect to MQTT broker."""
        try:
            self.client.connect(
                self.broker_host,
                self.broker_port,
                self.broker_keepalive
            )
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {str(e)}")

    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when client connects to broker."""
        if rc == 0:
            logger.info("Connected to MQTT broker")
            # Resubscribe to all device topics
            for device_id in self._message_callbacks:
                self._subscribe_device(device_id)
        else:
            logger.error(f"Failed to connect to MQTT broker with code: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """Callback for when client disconnects from broker."""
        if rc != 0:
            logger.warning("Unexpected disconnection from MQTT broker")
            # Attempt to reconnect
            self._connect()

    def _on_message(self, client, userdata, message):
        """Callback for when message is received from broker."""
        try:
            topic = message.topic
            payload = json.loads(message.payload.decode())

            # Extract device ID from topic
            device_id = topic.split('/')[-1]

            if device_id in self._message_callbacks:
                self._message_callbacks[device_id](payload)
            else:
                logger.warning(
                    f"Received message for unknown device: {device_id}")

        except json.JSONDecodeError:
            logger.error("Failed to decode message payload as JSON")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {str(e)}")

    def _get_device_topic(self, device: Device, command: bool = False) -> str:
        """Get MQTT topic for device."""
        base_topic = f"home/{device.device_type.value}/{device.mac_address}"
        return f"{base_topic}/command" if command else f"{base_topic}/state"

    def _subscribe_device(self, device_id: str):
        """Subscribe to device state topic."""
        topic = f"home/+/+/{device_id}/state"
        self.client.subscribe(topic)
        logger.debug(f"Subscribed to topic: {topic}")

    def register_device(self, device: Device, callback):
        """Register device for state updates."""
        self._message_callbacks[device.id] = callback
        self._subscribe_device(device.id)

    def unregister_device(self, device: Device):
        """Unregister device from state updates."""
        if device.id in self._message_callbacks:
            topic = self._get_device_topic(device)
            self.client.unsubscribe(topic)
            del self._message_callbacks[device.id]

    def send_command(self, device: Device, command: Dict[str, Any]) -> bool:
        """Send command to device."""
        try:
            topic = self._get_device_topic(device, command=True)
            payload = json.dumps(command)

            result = self.client.publish(topic, payload)
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                logger.error(f"Failed to publish command: {result.rc}")
                return False

            # Create command event
            event = DeviceEvent(
                device_id=device.id,
                event_type='command_sent',
                message=f"Command sent: {payload}"
            )
            db.session.add(event)
            db.session.commit()

            return True
        except Exception as e:
            logger.error(f"Error sending command: {str(e)}")
            return False

    def get_last_state(self, device: Device) -> Optional[Dict[str, Any]]:
        """Get last known device state."""
        try:
            topic = self._get_device_topic(device)
            # Request state update
            self.client.publish(f"{topic}/get")
            # State will be received through message callback
            return None
        except Exception as e:
            logger.error(f"Error getting device state: {str(e)}")
            return None

    def __del__(self):
        """Clean up MQTT client connection."""
        if hasattr(self, 'client'):
            self.client.loop_stop()
            self.client.disconnect()

    def _handle_status_update(self, device: Device, payload: Dict[str, Any]):
        """Handle device status updates."""
        try:
            # Update device status
            device.status = payload.get('status', 'offline')
            device.last_ping_time = datetime.utcnow().timestamp()

            if 'firmware_version' in payload:
                device.firmware_version = payload['firmware_version']
            if 'ip_address' in payload:
                device.ip_address = payload['ip_address']

            db.session.commit()
            logger.info(f"Updated status for device {device.name}")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating device status: {str(e)}")

    def _handle_state_update(self, device: Device, payload: Dict[str, Any]):
        """Handle device state updates."""
        try:
            # Update device state
            device.update_state(payload)
            db.session.commit()
            logger.info(f"Updated state for device {device.name}")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating device state: {str(e)}")

    def discover_devices(self):
        """Discover MQTT devices."""
        try:
            # Send discovery message
            self.client.publish("home/discovery", json.dumps({
                "action": "discover",
                "timestamp": datetime.utcnow().isoformat()
            }))
            logger.info("Sent device discovery message")
            return True
        except Exception as e:
            logger.error(f"Error discovering devices: {str(e)}")
            return False
