from typing import Dict, Any, Optional, List
import colorsys
import logging
from models import Device, DeviceCapability

logger = logging.getLogger(__name__)


class SmartLightDriver:
    """Driver for smart light devices."""

    # Supported manufacturers and their specific implementations
    SUPPORTED_MANUFACTURERS = {
        'philips': 'PhilipsHueLight',
        'lifx': 'LifxLight',
        'tplink': 'TPLinkLight',
        'yeelight': 'YeelightLight',
        'generic': 'GenericLight'
    }

    def __init__(self, device: Device):
        self.device = device
        self.protocol_handler = self._get_protocol_handler()

        # Set default capabilities if none specified
        if not self.device.capabilities:
            self.device.capabilities = [
                DeviceCapability.ON_OFF.value,
                DeviceCapability.BRIGHTNESS.value
            ]

            # Add color capability if supported
            if self._supports_color():
                self.device.capabilities.append(DeviceCapability.COLOR.value)

    def _get_protocol_handler(self):
        """Get the appropriate protocol handler for the device."""
        from protocols.mqtt_handler import MQTTHandler
        # Add more protocol handlers as needed
        handlers = {
            'mqtt': MQTTHandler,
            # 'zigbee': ZigbeeHandler,
            # 'wifi': WiFiHandler,
        }
        return handlers.get(self.device.protocol)()

    def _supports_color(self) -> bool:
        """Check if device supports color based on manufacturer and model."""
        color_supported_models = {
            'philips': ['hue_color', 'hue_gradient'],
            'lifx': ['color', 'color_br30', 'color_plus'],
            'tplink': ['lb130', 'kb130', 'kl130'],
            'yeelight': ['color', 'strip']
        }

        manufacturer = self.device.manufacturer.lower()
        if manufacturer in color_supported_models:
            return any(model in self.device.model.lower()
                       for model in color_supported_models[manufacturer])
        return False

    def turn_on(self) -> bool:
        """Turn the light on."""
        try:
            command = {
                'type': 'turn_on'
            }
            return self.protocol_handler.send_command(self.device, command)
        except Exception as e:
            logger.error(f"Error turning on light: {str(e)}")
            return False

    def turn_off(self) -> bool:
        """Turn the light off."""
        try:
            command = {
                'type': 'turn_off'
            }
            return self.protocol_handler.send_command(self.device, command)
        except Exception as e:
            logger.error(f"Error turning off light: {str(e)}")
            return False

    def set_brightness(self, brightness: int) -> bool:
        """Set light brightness (0-100)."""
        try:
            if not 0 <= brightness <= 100:
                logger.error("Brightness must be between 0 and 100")
                return False

            command = {
                'type': 'set_brightness',
                'brightness': brightness
            }
            return self.protocol_handler.send_command(self.device, command)
        except Exception as e:
            logger.error(f"Error setting brightness: {str(e)}")
            return False

    def set_color(self, r: int, g: int, b: int) -> bool:
        """Set light color using RGB values (0-255)."""
        try:
            if not all(0 <= x <= 255 for x in (r, g, b)):
                logger.error("RGB values must be between 0 and 255")
                return False

            if DeviceCapability.COLOR.value not in self.device.capabilities:
                logger.error("Device does not support color")
                return False

            command = {
                'type': 'set_color',
                'r': r,
                'g': g,
                'b': b
            }

            # Add manufacturer-specific color transformations
            if self.device.manufacturer.lower() == 'philips':
                # Convert RGB to Hue's color space
                h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
                command['hue'] = int(h * 65535)
                command['sat'] = int(s * 255)

            return self.protocol_handler.send_command(self.device, command)
        except Exception as e:
            logger.error(f"Error setting color: {str(e)}")
            return False

    def set_color_temperature(self, temperature: int) -> bool:
        """Set light color temperature in Kelvin (2000-6500K)."""
        try:
            if not 2000 <= temperature <= 6500:
                logger.error(
                    "Color temperature must be between 2000K and 6500K")
                return False

            command = {
                'type': 'set_temperature',
                'temperature': temperature
            }

            # Add manufacturer-specific temperature transformations
            if self.device.manufacturer.lower() == 'philips':
                # Convert Kelvin to Hue's mired scale
                command['mired'] = int(1000000 / temperature)

            return self.protocol_handler.send_command(self.device, command)
        except Exception as e:
            logger.error(f"Error setting color temperature: {str(e)}")
            return False

    def set_effect(self, effect: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """Set light effect (e.g., pulse, rainbow, etc.)."""
        try:
            command = {
                'type': 'set_effect',
                'effect': effect
            }
            if params:
                command['params'] = params

            return self.protocol_handler.send_command(self.device, command)
        except Exception as e:
            logger.error(f"Error setting effect: {str(e)}")
            return False

    def get_state(self) -> Dict[str, Any]:
        """Get current light state."""
        return self.device.state or {}

    @staticmethod
    def get_supported_effects(manufacturer: str, model: str) -> List[str]:
        """Get list of supported effects for specific device model."""
        effects = {
            'philips': {
                'default': ['colorloop', 'pulse', 'flash'],
                'hue_gradient': ['colorloop', 'pulse', 'flash', 'gradient', 'rainbow'],
            },
            'lifx': {
                'default': ['pulse', 'breathe', 'morph'],
                'strip': ['pulse', 'breathe', 'morph', 'move', 'flame'],
            },
            'yeelight': {
                'default': ['smooth', 'sudden', 'disco', 'strobe'],
            }
        }

        manufacturer = manufacturer.lower()
        if manufacturer in effects:
            model_effects = effects[manufacturer].get(model.lower(),
                                                      effects[manufacturer]['default'])
            return model_effects
        return []
