import socket
import threading
import json
import logging
from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
from typing import Dict, List, Optional
from models import Device, db
from protocols.mqtt_handler import MQTTHandler

logger = logging.getLogger(__name__)


class DeviceDiscoveryService:
    """Service for discovering IoT devices on the network."""

    def __init__(self):
        self.mqtt_handler = MQTTHandler()
        self.zeroconf = Zeroconf()
        self.discovered_devices: Dict[str, Dict] = {}
        self.discovery_thread = None
        self.is_discovering = False

    def start_discovery(self):
        """Start device discovery across all supported protocols."""
        if self.is_discovering:
            logger.warning("Discovery already in progress")
            return

        self.is_discovering = True
        self.discovery_thread = threading.Thread(target=self._discover_devices)
        self.discovery_thread.daemon = True
        self.discovery_thread.start()

    def stop_discovery(self):
        """Stop device discovery."""
        self.is_discovering = False
        if self.discovery_thread:
            self.discovery_thread.join()
        self.zeroconf.close()

    def _discover_devices(self):
        """Run device discovery on all protocols."""
        try:
            # Start MQTT discovery
            self.mqtt_handler.discover_devices()

            # Start mDNS discovery
            browser = ServiceBrowser(self.zeroconf, "_iot._tcp.local.",
                                     DeviceServiceListener(self._handle_discovered_device))

            # Start direct UDP discovery
            self._discover_udp_devices()

        except Exception as e:
            logger.error(f"Error during device discovery: {str(e)}")
            self.is_discovering = False

    def _discover_udp_devices(self):
        """Discover devices using UDP broadcast."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(1.0)

            # Send discovery broadcast
            discovery_message = json.dumps({
                "action": "discover",
                "protocol": "udp"
            }).encode()

            sock.sendto(discovery_message, ('<broadcast>', 5353))

            # Listen for responses
            while self.is_discovering:
                try:
                    data, addr = sock.recvfrom(1024)
                    self._handle_udp_response(data, addr)
                except socket.timeout:
                    continue

        except Exception as e:
            logger.error(f"Error in UDP discovery: {str(e)}")
        finally:
            sock.close()

    def _handle_udp_response(self, data: bytes, addr: tuple):
        """Handle UDP discovery response."""
        try:
            response = json.loads(data.decode())
            device_info = {
                'protocol': 'udp',
                'ip_address': addr[0],
                'port': addr[1],
                **response
            }
            self._handle_discovered_device(device_info)

        except Exception as e:
            logger.error(f"Error handling UDP response: {str(e)}")

    def _handle_discovered_device(self, device_info: Dict):
        """Process discovered device information."""
        try:
            # Extract device identifier (MAC address or unique ID)
            device_id = device_info.get('mac_address') or device_info.get('id')
            if not device_id:
                logger.warning("Device missing identifier")
                return

            # Check if device already exists
            device = Device.query.filter_by(mac_address=device_id).first()
            if device:
                # Update existing device
                self._update_device(device, device_info)
            else:
                # Create new device
                self._create_device(device_id, device_info)

        except Exception as e:
            logger.error(f"Error handling discovered device: {str(e)}")

    def _update_device(self, device: Device, device_info: Dict):
        """Update existing device with discovered information."""
        try:
            device.ip_address = device_info.get(
                'ip_address', device.ip_address)
            device.protocol = device_info.get('protocol', device.protocol)
            device.manufacturer = device_info.get(
                'manufacturer', device.manufacturer)
            device.model = device_info.get('model', device.model)
            device.firmware_version = device_info.get(
                'firmware_version', device.firmware_version)

            if 'capabilities' in device_info:
                device.capabilities = device_info['capabilities']

            db.session.commit()
            logger.info(f"Updated device: {device.name}")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating device: {str(e)}")

    def _create_device(self, device_id: str, device_info: Dict):
        """Create new device from discovered information."""
        try:
            device = Device(
                mac_address=device_id,
                name=device_info.get('name', 'New Device'),
                device_type=device_info.get('type', 'CUSTOM'),
                capabilities=device_info.get('capabilities', []),
                protocol=device_info.get('protocol'),
                manufacturer=device_info.get('manufacturer'),
                model=device_info.get('model'),
                firmware_version=device_info.get('firmware_version'),
                ip_address=device_info.get('ip_address'),
                status='online'
            )

            db.session.add(device)
            db.session.commit()
            logger.info(f"Created new device: {device.name}")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating device: {str(e)}")


class DeviceServiceListener(ServiceListener):
    """mDNS service listener for IoT devices."""

    def __init__(self, callback):
        self.callback = callback

    def add_service(self, zc: Zeroconf, type_: str, name: str):
        info = zc.get_service_info(type_, name)
        if info:
            try:
                # Parse service information
                device_info = {
                    'protocol': 'mdns',
                    'ip_address': str(socket.inet_ntoa(info.addresses[0])),
                    'port': info.port,
                    'name': name.split('.')[0],
                    'type': type_,
                    'properties': {
                        k.decode(): v.decode() if isinstance(v, bytes) else v
                        for k, v in info.properties.items()
                    }
                }

                # Extract additional information from properties
                props = device_info['properties']
                if 'mac' in props:
                    device_info['mac_address'] = props['mac']
                if 'manufacturer' in props:
                    device_info['manufacturer'] = props['manufacturer']
                if 'model' in props:
                    device_info['model'] = props['model']
                if 'capabilities' in props:
                    try:
                        device_info['capabilities'] = json.loads(
                            props['capabilities'])
                    except:
                        pass

                self.callback(device_info)

            except Exception as e:
                logger.error(f"Error processing mDNS service: {str(e)}")

    def remove_service(self, zc: Zeroconf, type_: str, name: str):
        """Handle removed services."""
        pass

    def update_service(self, zc: Zeroconf, type_: str, name: str):
        """Handle updated services."""
        self.add_service(zc, type_, name)
