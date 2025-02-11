from datetime import datetime
import pytz
from models import db, Automation, Device, DeviceEvent
import logging

logger = logging.getLogger(__name__)


def check_time_trigger(trigger_data, timezone='UTC'):
    """Check if a time-based trigger should fire."""
    current_time = datetime.now(pytz.timezone(timezone))

    # Handle different time trigger types
    trigger_type = trigger_data.get('type')
    if trigger_type == 'exact':
        # Exact time trigger (e.g., "at 7:00 AM")
        target_time = datetime.strptime(trigger_data['time'], '%H:%M').time()
        return current_time.time().replace(second=0, microsecond=0) == target_time

    elif trigger_type == 'sunrise':
        # Sunrise trigger with optional offset
        # Would need to calculate actual sunrise time based on location
        pass

    elif trigger_type == 'sunset':
        # Sunset trigger with optional offset
        # Would need to calculate actual sunset time based on location
        pass

    elif trigger_type == 'interval':
        # Interval trigger (e.g., "every 30 minutes")
        interval = trigger_data.get('interval', 0)
        if interval > 0:
            last_run = trigger_data.get('last_run')
            if not last_run or (current_time - last_run).total_seconds() >= interval:
                return True

    return False


def check_condition_trigger(trigger_data, device=None, old_state=None, new_state=None):
    """Check if a condition-based trigger should fire."""
    condition_type = trigger_data.get('type')

    if condition_type == 'state_change':
        # Check if specific state changed
        if not device or not old_state or not new_state:
            return False

        target_state = trigger_data.get('state')
        if not target_state:
            return False

        # Check if the state changed to the target state
        for key, value in target_state.items():
            if new_state.get(key) == value and old_state.get(key) != value:
                return True

    elif condition_type == 'threshold':
        # Check if value crosses a threshold
        if not device or not new_state:
            return False

        value = new_state.get(trigger_data.get('property'))
        if value is None:
            return False

        threshold = trigger_data.get('threshold')
        operator = trigger_data.get('operator', '>')

        if operator == '>':
            return value > threshold
        elif operator == '<':
            return value < threshold
        elif operator == '>=':
            return value >= threshold
        elif operator == '<=':
            return value <= threshold
        elif operator == '==':
            return value == threshold

    return False


def execute_action(action, device=None):
    """Execute an automation action."""
    try:
        action_type = action.get('type')

        if action_type == 'device_command':
            if not device:
                device = Device.query.get(action.get('device_id'))
            if device:
                command = action.get('command', {})
                # Execute device command through appropriate protocol handler
                protocol_handler = get_protocol_handler(device.protocol)
                if protocol_handler:
                    protocol_handler.send_command(device, command)

        elif action_type == 'scene':
            scene_id = action.get('scene_id')
            if scene_id:
                execute_scene(scene_id)

        elif action_type == 'notification':
            # Send notification through configured notification service
            notification_service.send(
                title=action.get('title', 'Home Automation'),
                message=action.get('message', ''),
                priority=action.get('priority', 'normal')
            )

        elif action_type == 'delay':
            # Add delay between actions
            time.sleep(action.get('duration', 0))

        return True

    except Exception as e:
        logger.error(f"Error executing action: {str(e)}")
        return False


def check_device_triggers(device, old_state, new_state):
    """Check and execute automation triggers for device state changes."""
    try:
        # Get all enabled automations for the device's home
        automations = Automation.query.filter_by(
            home_id=device.room.home_id,
            is_enabled=True
        ).all()

        for automation in automations:
            should_trigger = False

            if automation.trigger_type == 'condition':
                should_trigger = check_condition_trigger(
                    automation.trigger_data,
                    device=device,
                    old_state=old_state,
                    new_state=new_state
                )

            if should_trigger:
                # Execute all actions in sequence
                for action in automation.actions:
                    if not execute_action(action):
                        break

                # Update last triggered time
                automation.last_triggered = datetime.utcnow()
                db.session.commit()

                # Create automation event
                event = DeviceEvent(
                    device_id=device.id,
                    event_type='automation_triggered',
                    message=f"Automation '{automation.name}' triggered",
                    old_state=old_state,
                    new_state=new_state
                )
                db.session.add(event)
                db.session.commit()

    except Exception as e:
        logger.error(f"Error checking device triggers: {str(e)}")
        db.session.rollback()


def execute_scene(scene_id):
    """Execute all actions in a scene."""
    try:
        scene = Scene.query.get(scene_id)
        if not scene or not scene.is_enabled:
            return False

        # Execute all scene actions in parallel or sequence based on configuration
        for action in scene.actions:
            execute_action(action)

        return True

    except Exception as e:
        logger.error(f"Error executing scene: {str(e)}")
        return False

# Protocol handlers (to be implemented)


def get_protocol_handler(protocol):
    """Get the appropriate protocol handler for a device."""
    handlers = {
        'mqtt': MQTTHandler(),
        'zwave': ZWaveHandler(),
        'zigbee': ZigbeeHandler(),
        'wifi': WiFiHandler(),
    }
    return handlers.get(protocol)
