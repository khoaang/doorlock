from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import re
from enum import Enum
import json

db = SQLAlchemy()


class User(db.Model):
    """User model for authentication and authorization.

    This model stores user information and handles password hashing and verification.
    Users can have different roles (admin, device_manager, viewer) and own multiple devices.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    # admin, device_manager, viewer
    role = db.Column(db.String(20), nullable=False, default='viewer')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    home_id = db.Column(db.Integer, db.ForeignKey('homes.id'))

    # Permissions
    can_control_devices = db.Column(db.Boolean, default=True)
    can_add_devices = db.Column(db.Boolean, default=False)
    can_manage_automations = db.Column(db.Boolean, default=False)

    # Relationships
    devices = db.relationship('Device', backref='owner', lazy=True)
    home = db.relationship('Home', backref='users')

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify the user's password."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_devices=False):
        """Convert user to dictionary representation."""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'permissions': {
                'can_control_devices': self.can_control_devices,
                'can_add_devices': self.can_add_devices,
                'can_manage_automations': self.can_manage_automations
            },
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_devices:
            data['devices'] = [device.to_dict() for device in self.devices]
        return data


class DeviceType(Enum):
    LIGHT = "light"
    SWITCH = "switch"
    THERMOSTAT = "thermostat"
    LOCK = "lock"
    CAMERA = "camera"
    SENSOR = "sensor"
    CUSTOM = "custom"


class DeviceCapability(Enum):
    ON_OFF = "on_off"
    BRIGHTNESS = "brightness"
    COLOR = "color"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    MOTION = "motion"
    LOCK_UNLOCK = "lock_unlock"
    VIDEO_STREAM = "video_stream"
    CUSTOM_SCRIPT = "custom_script"


class Room(db.Model):
    """Room model for organizing devices by location."""
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    floor = db.Column(db.Integer, default=1)
    home_id = db.Column(db.Integer, db.ForeignKey('homes.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    devices = db.relationship('Device', backref='room', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'floor': self.floor,
            'home_id': self.home_id,
            'created_at': self.created_at.isoformat()
        }


class Home(db.Model):
    """Home model for managing multiple locations."""
    __tablename__ = 'homes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    timezone = db.Column(db.String(50), default='UTC')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    rooms = db.relationship('Room', backref='home',
                            lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'timezone': self.timezone,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat(),
            'rooms': [room.to_dict() for room in self.rooms]
        }


class Device(db.Model):
    """Device model representing an IoT device.

    This model stores information about IoT devices including their MAC address,
    name, status, and associated scripts. Each device belongs to a user and can
    have multiple scripts and a queue of scripts to execute.
    """
    __tablename__ = 'devices'

    id = db.Column(db.Integer, primary_key=True)
    mac_address = db.Column(db.String(17), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False, default='Unknown')
    device_type = db.Column(db.Enum(DeviceType), nullable=False)
    # List of DeviceCapability
    capabilities = db.Column(db.JSON, nullable=False, default=list)
    state = db.Column(db.JSON, default=dict)  # Current device state
    config = db.Column(db.JSON, default=dict)  # Device configuration
    emoji = db.Column(db.String(10), default='')
    description = db.Column(db.Text)
    # online, offline, error
    status = db.Column(db.String(20), default='offline')
    last_ping_time = db.Column(db.Float, default=0.0)
    firmware_version = db.Column(db.String(50))
    ip_address = db.Column(db.String(45))  # Support both IPv4 and IPv6
    protocol = db.Column(db.String(20))  # mqtt, zwave, zigbee, wifi, etc.
    manufacturer = db.Column(db.String(100))
    model = db.Column(db.String(100))
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    scripts = db.relationship(
        'Script', backref='device', lazy=True, cascade='all, delete-orphan')
    queue_items = db.relationship(
        'ScriptQueue', backref='device', lazy=True, cascade='all, delete-orphan')
    events = db.relationship('DeviceEvent', backref='device', lazy=True)

    @staticmethod
    def validate_mac_address(mac_address):
        """Validate MAC address format."""
        pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
        return bool(pattern.match(mac_address))

    def update_state(self, new_state):
        """Update device state and create an event."""
        old_state = self.state.copy() if self.state else {}
        self.state.update(new_state)

        # Create state change event
        event = DeviceEvent(
            device_id=self.id,
            event_type='state_change',
            old_state=old_state,
            new_state=self.state
        )
        db.session.add(event)

        # Check automation triggers
        from automation_engine import check_device_triggers
        check_device_triggers(self, old_state, self.state)

    def to_dict(self, include_scripts=True):
        """Convert device to dictionary representation."""
        data = {
            'id': self.id,
            'mac_address': self.mac_address,
            'name': self.name,
            'device_type': self.device_type.value,
            'capabilities': [cap.value for cap in self.capabilities],
            'state': self.state,
            'config': self.config,
            'emoji': self.emoji,
            'description': self.description,
            'status': self.status,
            'last_ping_time': self.last_ping_time,
            'firmware_version': self.firmware_version,
            'ip_address': self.ip_address,
            'protocol': self.protocol,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'room_id': self.room_id,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_scripts:
            data['scripts'] = {
                script.name: script.content for script in self.scripts}
        return data


class Script(db.Model):
    """Script model for storing device scripts.

    This model stores scripts that can be executed on devices. Each script belongs
    to a specific device and can be queued for execution.
    """
    __tablename__ = 'scripts'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey(
        'devices.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    version = db.Column(db.String(20), default='1.0.0')
    is_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('device_id', 'name',
                            name='unique_script_name_per_device'),
    )

    def to_dict(self):
        """Convert script to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'content': self.content,
            'description': self.description,
            'version': self.version,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class ScriptQueue(db.Model):
    """Script queue model for managing script execution order.

    This model maintains the queue of scripts to be executed on each device,
    tracking their position in the queue and execution status.
    """
    __tablename__ = 'script_queue'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey(
        'devices.id'), nullable=False)
    script_id = db.Column(db.Integer, db.ForeignKey(
        'scripts.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    # pending, running, completed, failed
    status = db.Column(db.String(20), default='pending')
    result = db.Column(db.Text)
    scheduled_time = db.Column(db.DateTime)
    executed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    script = db.relationship('Script')

    def to_dict(self):
        """Convert queue item to dictionary representation."""
        return {
            'id': self.id,
            'script': self.script.to_dict(),
            'position': self.position,
            'status': self.status,
            'result': self.result,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'created_at': self.created_at.isoformat()
        }


class DeviceEvent(db.Model):
    """Model for tracking device state changes and events."""
    __tablename__ = 'device_events'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey(
        'devices.id'), nullable=False)
    # state_change, error, warning, info
    event_type = db.Column(db.String(50), nullable=False)
    old_state = db.Column(db.JSON)
    new_state = db.Column(db.JSON)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'event_type': self.event_type,
            'old_state': self.old_state,
            'new_state': self.new_state,
            'message': self.message,
            'created_at': self.created_at.isoformat()
        }
