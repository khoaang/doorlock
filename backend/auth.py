from functools import wraps
from flask import jsonify, request, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models import User, Device


def get_current_user():
    """Get the current authenticated user."""
    username = get_jwt_identity()
    return User.query.filter_by(username=username).first()


def requires_roles(*roles):
    """Decorator to check if user has required roles."""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user = get_current_user()

            if not user:
                return jsonify({"error": "User not found"}), 404

            if not user.is_active:
                return jsonify({"error": "User account is inactive"}), 403

            if user.role not in roles and 'admin' not in roles:
                return jsonify({"error": "Insufficient permissions"}), 403

            return fn(*args, **kwargs)
        return decorator
    return wrapper


def device_access_required(fn):
    """Decorator to check if user has access to the device."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        if not user.is_active:
            return jsonify({"error": "User account is inactive"}), 403

        # Get device MAC address from URL parameters
        mac_address = kwargs.get('mac_address')
        if not mac_address:
            return jsonify({"error": "Device MAC address not provided"}), 400

        # Check if user owns the device or is an admin
        device = Device.query.filter_by(mac_address=mac_address).first()
        if not device:
            return jsonify({"error": "Device not found"}), 404

        if device.owner_id != user.id and user.role != 'admin':
            return jsonify({"error": "Access to device denied"}), 403

        return fn(*args, **kwargs)
    return wrapper


def validate_registration_data(data):
    """Validate user registration data."""
    errors = []

    if not data.get('username'):
        errors.append("Username is required")
    elif len(data['username']) < 3:
        errors.append("Username must be at least 3 characters long")

    if not data.get('email'):
        errors.append("Email is required")
    # Add more email validation if needed

    if not data.get('password'):
        errors.append("Password is required")
    elif len(data['password']) < 8:
        errors.append("Password must be at least 8 characters long")

    return errors


def init_admin_user(app):
    """Initialize admin user if it doesn't exist."""
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email=app.config.get('ADMIN_EMAIL', 'admin@example.com'),
                role='admin',
                is_active=True
            )
            admin.set_password(app.config.get('ADMIN_PASSWORD', 'admin'))
            from models import db
            db.session.add(admin)
            db.session.commit()
            current_app.logger.info("Admin user created successfully")
