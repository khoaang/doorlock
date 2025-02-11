import time
from typing import Dict, List, Optional
from models import db, Device, Script, ScriptQueue
import logging

logger = logging.getLogger(__name__)


def load_devices() -> Dict[str, Device]:
    """Load all devices from the database."""
    try:
        devices = Device.query.all()
        return {device.mac_address: device for device in devices}
    except Exception as e:
        logger.error(f"Error loading devices: {str(e)}")
        return {}


def add_device(mac_address: str, name: str = "Unknown", emoji: str = "", scripts: Dict[str, str] = None) -> bool:
    """Add a new device to the database."""
    try:
        if Device.query.filter_by(mac_address=mac_address).first():
            logger.warning(f"Device with MAC {mac_address} already exists")
            return False

        device = Device(mac_address=mac_address, name=name, emoji=emoji)
        db.session.add(device)

        if scripts:
            for script_name, script_content in scripts.items():
                script = Script(name=script_name,
                                content=script_content, device=device)
                db.session.add(script)

        db.session.commit()
        logger.info(f"Successfully added device with MAC {mac_address}")
        return True

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding device: {str(e)}")
        return False


def remove_device(mac_address: str) -> bool:
    """Remove a device from the database."""
    try:
        device = Device.query.filter_by(mac_address=mac_address).first()
        if device:
            db.session.delete(device)
            db.session.commit()
            logger.info(f"Successfully removed device with MAC {mac_address}")
            return True
        return False
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error removing device: {str(e)}")
        return False


def fetch_scripts_for_device(mac_address: str) -> Dict[str, str]:
    """Fetch all scripts for a device."""
    try:
        device = Device.query.filter_by(mac_address=mac_address).first()
        if device:
            return {script.name: script.content for script in device.scripts}
        logger.warning(f"Device with MAC {mac_address} not found")
        return {}
    except Exception as e:
        logger.error(f"Error fetching scripts: {str(e)}")
        return {}


def add_script_to_device(mac_address: str, script_name: str, script_content: str) -> bool:
    """Add a script to a device."""
    try:
        device = Device.query.filter_by(mac_address=mac_address).first()
        if not device:
            logger.warning(f"Device with MAC {mac_address} not found")
            return False

        existing_script = Script.query.filter_by(
            device_id=device.id, name=script_name).first()
        if existing_script:
            existing_script.content = script_content
        else:
            script = Script(name=script_name,
                            content=script_content, device=device)
            db.session.add(script)

        db.session.commit()
        logger.info(
            f"Successfully added/updated script {script_name} for device {mac_address}")
        return True

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding script: {str(e)}")
        return False


def remove_script_from_device(mac_address: str, script_name: str) -> bool:
    """Remove a script from a device."""
    try:
        device = Device.query.filter_by(mac_address=mac_address).first()
        if not device:
            logger.warning(f"Device with MAC {mac_address} not found")
            return False

        script = Script.query.filter_by(
            device_id=device.id, name=script_name).first()
        if script:
            db.session.delete(script)
            db.session.commit()
            logger.info(
                f"Successfully removed script {script_name} from device {mac_address}")
            return True
        return False

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error removing script: {str(e)}")
        return False


def enqueue_script(mac_address: str, script_name: str) -> bool:
    """Add a script to the device's execution queue."""
    try:
        device = Device.query.filter_by(mac_address=mac_address).first()
        if not device:
            logger.warning(f"Device with MAC {mac_address} not found")
            return False

        script = Script.query.filter_by(
            device_id=device.id, name=script_name).first()
        if not script:
            logger.warning(
                f"Script {script_name} not found for device {mac_address}")
            return False

        # Get the highest position in the queue
        last_queue_item = ScriptQueue.query.filter_by(
            device_id=device.id).order_by(ScriptQueue.position.desc()).first()
        next_position = (last_queue_item.position +
                         1) if last_queue_item else 0

        queue_item = ScriptQueue(
            device=device, script=script, position=next_position)
        db.session.add(queue_item)
        db.session.commit()
        logger.info(
            f"Successfully enqueued script {script_name} for device {mac_address}")
        return True

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error enqueuing script: {str(e)}")
        return False


def dequeue_script(mac_address: str, script_name: str) -> bool:
    """Remove a script from the device's execution queue."""
    try:
        device = Device.query.filter_by(mac_address=mac_address).first()
        if not device:
            logger.warning(f"Device with MAC {mac_address} not found")
            return False

        script = Script.query.filter_by(
            device_id=device.id, name=script_name).first()
        if not script:
            logger.warning(
                f"Script {script_name} not found for device {mac_address}")
            return False

        queue_item = ScriptQueue.query.filter_by(
            device_id=device.id, script_id=script.id).first()
        if queue_item:
            removed_position = queue_item.position
            db.session.delete(queue_item)

            # Update positions of remaining items
            remaining_items = ScriptQueue.query.filter(
                ScriptQueue.device_id == device.id,
                ScriptQueue.position > removed_position
            ).all()

            for item in remaining_items:
                item.position -= 1

            db.session.commit()
            logger.info(
                f"Successfully dequeued script {script_name} from device {mac_address}")
            return True
        return False

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error dequeuing script: {str(e)}")
        return False


def update_last_ping_time(mac_address: str) -> bool:
    """Update the last ping time for a device."""
    try:
        device = Device.query.filter_by(mac_address=mac_address).first()
        if device:
            device.last_ping_time = time.time()
            db.session.commit()
            logger.info(f"Updated last ping time for device {mac_address}")
            return True
        logger.warning(f"Device with MAC {mac_address} not found")
        return False
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating ping time: {str(e)}")
        return False


def get_last_ping_time(mac_address: str) -> float:
    """Get the last ping time for a device."""
    try:
        device = Device.query.filter_by(mac_address=mac_address).first()
        if device:
            return device.last_ping_time
        logger.warning(f"Device with MAC {mac_address} not found")
        return 0.0
    except Exception as e:
        logger.error(f"Error getting ping time: {str(e)}")
        return 0.0


def example_usage():
    add_device("00:1B:44:11:3A:B7", "Test Device", "📱",
               {"script1": "print('Hello World')"})
    devices = load_devices()


example_usage()
