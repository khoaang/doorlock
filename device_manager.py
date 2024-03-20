import json
import time
from typing import Dict, List

DEVICES_FILE_PATH = 'devices.json'
SCRIPT_QUEUE_FILE_PATH = 'script_queue.json'


class Device:
    def __init__(self, mac_address: str, name: str = "Unknown", emoji: str = "", scripts: Dict[str, str] = None, last_ping_time: float = 0.0):
        self.mac_address = mac_address
        self.name = name
        self.emoji = emoji
        self.scripts = scripts if scripts else {}
        self.last_ping_time = last_ping_time

    def to_dict(self) -> Dict:
        return {
            'mac_address': self.mac_address,
            'name': self.name,
            'emoji': self.emoji,
            'scripts': self.scripts,
            'last_ping_time': self.last_ping_time
        }

    def add_script(self, script_name: str, script_content: str) -> None:
        """Adds or updates a script for this device."""
        self.scripts[script_name] = script_content

    def remove_script(self, script_name: str) -> bool:
        """Removes a script from this device if it exists."""
        if script_name in self.scripts:
            del self.scripts[script_name]
            return True
        return False

    @classmethod
    def from_dict(cls, data: Dict) -> 'Device':
        return cls(data['mac_address'], data.get('name', 'Unknown'), data.get('emoji', ''), data.get('scripts', {}), data.get('last_ping_time', 0.0))


def load_devices() -> Dict[str, Device]:
    try:
        with open(DEVICES_FILE_PATH, 'r') as file:
            devices_data = json.load(file)
        return {data['mac_address']: Device.from_dict(data) for data in devices_data}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_devices(devices: Dict[str, Device]) -> None:
    with open(DEVICES_FILE_PATH, 'w') as file:
        json.dump([device.to_dict()
                   for device in devices.values()], file, indent=4)


def add_device(mac_address: str, name: str = "Unknown", emoji: str = "", scripts: Dict[str, str] = None) -> bool:
    devices = load_devices()
    if mac_address not in devices:
        devices[mac_address] = Device(mac_address, name, emoji, scripts)
        save_devices(devices)
        return True
    else:
        print("Device already exists.")
        return False


# Define fetch_scripts_for_device function here
def fetch_scripts_for_device(mac_address: str) -> Dict[str, str]:
    devices = load_devices()
    if mac_address in devices:
        return devices[mac_address].scripts
    else:
        print(f"Device with MAC {mac_address} not found.")
        return {}


def remove_device(mac_address: str) -> bool:
    devices = load_devices()
    if mac_address in devices:
        del devices[mac_address]
        save_devices(devices)
        return True
    return False


def add_script_to_device(mac_address: str, script_name: str, script_content: str):
    print(f"Adding script {script_name} to device {mac_address}")
    devices = load_devices()
    if mac_address in devices:
        device = devices[mac_address]
        device.add_script(script_name, script_content)
        save_devices(devices)
    else:
        print(f"Device with MAC {mac_address} not found.")


def remove_script_from_device(mac_address: str, script_name: str):
    devices = load_devices()
    if mac_address in devices:
        device = devices[mac_address]
        device.remove_script(script_name)
        save_devices(devices)
    else:
        print(f"Device with MAC {mac_address} not found.")


def load_script_queue() -> Dict[str, List[Dict[str, str]]]:
    try:
        with open(SCRIPT_QUEUE_FILE_PATH, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_script_queue(script_queue: Dict[str, List[Dict[str, str]]]) -> None:
    with open(SCRIPT_QUEUE_FILE_PATH, 'w') as file:
        json.dump(script_queue, file, indent=4)


def enqueue_script(mac_address: str, script_name: str) -> None:
    script_queue = load_script_queue()
    if mac_address not in script_queue:
        script_queue[mac_address] = []
    script_queue[mac_address].append(
        {'name': script_name, 'content': fetch_scripts_for_device(mac_address)[script_name]})
    save_script_queue(script_queue)


def dequeue_script(mac_address: str, script_name: str) -> None:
    script_queue = load_script_queue()
    if mac_address in script_queue:
        script_queue[mac_address] = [
            script for script in script_queue[mac_address] if script['name'] != script_name]
        save_script_queue(script_queue)


def update_last_ping_time(mac_address: str) -> None:
    """Update the last ping time for a device."""
    devices = load_devices()
    if mac_address in devices:
        devices[mac_address].last_ping_time = time.time()
        save_devices(devices)


# Add this function to fetch last ping time of a device
def get_last_ping_time(mac_address: str) -> float:
    devices = load_devices()
    if mac_address in devices:
        return devices[mac_address].last_ping_time
    return 0.0


def example_usage():
    add_device("00:1B:44:11:3A:B7", "Test Device", "📱",
               {"script1": "print('Hello World')"})
    devices = load_devices()


example_usage()
