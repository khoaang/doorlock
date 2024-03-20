import json
import subprocess
from typing import List, Dict, Union


class Device:
    def __init__(self, mac_address: str, name: str = "Unknown", emoji: str = "", scripts: List[Dict[str, str]] = None):
        self.mac_address = mac_address
        self.name = name
        self.emoji = emoji
        self.scripts = scripts if scripts else []

    def to_dict(self) -> Dict[str, Union[str, List[str]]]:
        return {
            'mac_address': self.mac_address,
            'name': self.name,
            'emoji': self.emoji,
            'scripts': self.scripts
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Union[str, List[str]]]) -> 'Device':
        return cls(data['mac_address'], data['name'], data['emoji'], data['scripts'])

    def add_script(self, script_name: str, script_content: str) -> None:
        self.scripts.append({"name": script_name, "content": script_content})

    def remove_script(self, script_name: str) -> None:
        self.scripts = [
            script for script in self.scripts if script['name'] != script_name]


DEVICES_FILE_PATH = 'devices.json'


def init_devices() -> None:
    try:
        with open(DEVICES_FILE_PATH, 'r') as file:
            devices_data = json.load(file)
            if not devices_data:  # If the file is empty or contains no devices
                create_test_device()
    except (FileNotFoundError, json.JSONDecodeError):
        create_test_device()


def load_devices() -> List[Device]:
    init_devices()
    with open(DEVICES_FILE_PATH, 'r') as file:
        devices_data = json.load(file)
        return [Device.from_dict(device_data) for device_data in devices_data]


def save_devices(devices: List[Device]) -> None:
    devices_data = [device.to_dict() for device in devices]
    with open(DEVICES_FILE_PATH, 'w') as file:
        json.dump(devices_data, file, indent=4)


def add_device(mac_address: str, name: str = "Unknown", emoji: str = "") -> None:
    devices = load_devices()
    if not any(device.mac_address == mac_address for device in devices):
        devices.append(Device(mac_address, name, emoji))
        save_devices(devices)


def remove_device(device_id: str) -> bool:
    devices = load_devices()
    for device in devices:
        if device.mac_address == device_id:
            devices.remove(device)
            save_devices(devices)
            return True
    return False


def list_devices() -> List[Device]:
    return load_devices()


def upload_script_to_device(device_id: str, script_name: str, script_content: str) -> bool:
    devices = load_devices()
    for device in devices:
        if device.mac_address == device_id:
            device.add_script(script_name, script_content)
            save_devices(devices)
            return True
    return False


def execute_script_on_device(device_id: str, script_name: str) -> bool:
    devices = load_devices()
    for device in devices:
        if device.mac_address == device_id:
            for script in device.scripts:
                if script['name'] == script_name:
                    script_content = script['content']
                    # Execute the script content on the device
                    try:
                        # Assuming the script content is a Python script
                        # You may adjust this command based on the type of script content
                        subprocess.run(['python', '-c', script_content], check=True)
                        print(f"Script '{script_name}' executed on device {device_id}")
                        return True
                    except subprocess.CalledProcessError as e:
                        print(f"Error executing script '{script_name}' on device {device_id}: {e}")
                        return False
            else:
                print(f"Script '{script_name}' not found on device {device_id}")
                return False
    print(f"Device {device_id} not found")
    return False


def create_test_device() -> None:
    default_script = generate_default_script()
    test_device = Device('00:1B:44:11:3A:B7',
                         'Test Device', '📱', [default_script])
    save_devices([test_device])


def generate_default_script() -> Dict[str, str]:
    return {"name": "default_script", "content": 'print("hello world")'}
