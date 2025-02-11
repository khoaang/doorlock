from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import device_manager
import logging
from models import db, User, Device
from config import config
from auth import requires_roles, device_access_required, validate_registration_data, init_admin_user
import os


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    socketio = SocketIO(app, cors_allowed_origins=app.config['CORS_ORIGINS'])
    jwt = JWTManager(app)
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri=app.config['RATELIMIT_STORAGE_URL']
    )

    # Set up logging
    logging.basicConfig(
        level=app.config['LOG_LEVEL'],
        format=app.config['LOG_FORMAT'],
        handlers=[
            logging.FileHandler(app.config['LOG_FILE']),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)

    # Create database tables and admin user
    with app.app_context():
        db.create_all()
        init_admin_user(app)

    # Authentication routes
    @app.route('/api/auth/register', methods=['POST'])
    @limiter.limit("5 per hour")
    def register():
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        errors = validate_registration_data(data)
        if errors:
            return jsonify({"errors": errors}), 400

        if User.query.filter_by(username=data['username']).first():
            return jsonify({"error": "Username already exists"}), 409

        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email already registered"}), 409

        user = User(
            username=data['username'],
            email=data['email'],
            role='viewer'  # Default role for new users
        )
        user.set_password(data['password'])

        try:
            db.session.add(user)
            db.session.commit()
            logger.info(f"New user registered: {user.username}")
            return jsonify({"message": "User registered successfully"}), 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error registering user: {str(e)}")
            return jsonify({"error": "Registration failed"}), 500

    @app.route('/api/auth/login', methods=['POST'])
    @limiter.limit("5 per minute")
    def login():
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Missing username or password'}), 400

        user = User.query.filter_by(username=data['username']).first()
        if user and user.check_password(data['password']):
            if not user.is_active:
                return jsonify({'error': 'Account is inactive'}), 403

            access_token = create_access_token(identity=user.username)
            logger.info(f"User logged in: {user.username}")
            return jsonify({
                'access_token': access_token,
                'user': user.to_dict()
            }), 200

        return jsonify({'error': 'Invalid credentials'}), 401

    # User management routes
    @app.route('/api/users', methods=['GET'])
    @jwt_required()
    @requires_roles('admin')
    @limiter.limit("30/minute")
    def get_users():
        users = User.query.all()
        return jsonify([user.to_dict() for user in users])

    @app.route('/api/users/<int:user_id>', methods=['PUT'])
    @jwt_required()
    @requires_roles('admin')
    def update_user(user_id):
        user = User.query.get_or_404(user_id)
        data = request.get_json()

        if 'role' in data and data['role'] in ['admin', 'device_manager', 'viewer']:
            user.role = data['role']
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])

        try:
            db.session.commit()
            logger.info(f"User updated: {user.username}")
            return jsonify(user.to_dict())
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating user: {str(e)}")
            return jsonify({"error": "Update failed"}), 500

    # Device routes
    @app.route('/api/devices', methods=['GET'])
    @jwt_required()
    @limiter.limit("30/minute")
    def get_devices():
        user = User.query.filter_by(username=get_jwt_identity()).first()
        if user.role == 'admin':
            devices = Device.query.all()
        else:
            devices = Device.query.filter_by(owner_id=user.id).all()
        return jsonify([device.to_dict() for device in devices])

    @app.route('/api/devices', methods=['POST'])
    @jwt_required()
    @requires_roles('admin', 'device_manager')
    @limiter.limit("10/minute")
    def api_add_device():
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        try:
            mac_address = data.get('mac_address')
            if not mac_address or not Device.validate_mac_address(mac_address):
                return jsonify({'error': 'Invalid MAC address'}), 400

            user = User.query.filter_by(username=get_jwt_identity()).first()
            device = Device(
                mac_address=mac_address,
                name=data.get('name', 'Unknown'),
                emoji=data.get('emoji', ''),
                description=data.get('description'),
                owner_id=user.id
            )

            db.session.add(device)
            db.session.commit()
            logger.info(f"New device added: {mac_address}")
            return jsonify(device.to_dict()), 201

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding device: {str(e)}")
            return jsonify({'error': str(e)}), 400

    @app.route('/api/devices/<mac_address>', methods=['DELETE'])
    @jwt_required()
    @device_access_required
    @limiter.limit("10/minute")
    def delete_device(mac_address):
        device = Device.query.filter_by(mac_address=mac_address).first()
        if device:
            try:
                db.session.delete(device)
                db.session.commit()
                logger.info(f"Device deleted: {mac_address}")
                return jsonify({'success': True, 'message': 'Device removed'}), 200
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error deleting device: {str(e)}")
                return jsonify({'error': 'Failed to delete device'}), 500
        return jsonify({'error': 'Device not found'}), 404

    # Script management routes
    @app.route('/api/scripts/<mac_address>', methods=['POST'])
    @jwt_required()
    @device_access_required
    @limiter.limit("20/minute")
    def api_upload_script(mac_address):
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file:
            try:
                filename = secure_filename(file.filename)
                script_content = file.read().decode("utf-8")

                success = device_manager.add_script_to_device(
                    mac_address, filename, script_content)
                if success:
                    logger.info(
                        f"Script uploaded: {filename} to device {mac_address}")
                    return jsonify({'success': True, 'message': f'Script {filename} uploaded successfully'}), 200
                else:
                    return jsonify({'error': 'Failed to upload script'}), 400
            except Exception as e:
                logger.error(f"Error uploading script: {str(e)}")
                return jsonify({'error': str(e)}), 400

    @app.route('/api/scripts/<mac_address>/<script_name>', methods=['DELETE'])
    @jwt_required()
    @device_access_required
    @limiter.limit("20/minute")
    def api_remove_script(mac_address, script_name):
        try:
            success = device_manager.remove_script_from_device(
                mac_address, script_name)
            if success:
                return jsonify({'success': True, 'message': f'Script {script_name} removed from device {mac_address}'}), 200
            else:
                return jsonify({'error': 'Script or device not found'}), 404
        except Exception as e:
            logger.error(f"Error removing script: {str(e)}")
            return jsonify({'error': str(e)}), 500

    # Script queue routes
    @app.route('/api/enqueue-script/<mac_address>', methods=['POST'])
    @jwt_required()
    @device_access_required
    @limiter.limit("30/minute")
    def api_enqueue_script(mac_address):
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Script name is required'}), 400

        script_name = data['name']
        success = device_manager.enqueue_script(mac_address, script_name)

        if success:
            return jsonify({'success': True, 'message': 'Script enqueued'}), 200
        else:
            return jsonify({'error': 'Failed to enqueue script'}), 400

    @app.route('/api/dequeue-script/<mac_address>', methods=['POST'])
    @jwt_required()
    @device_access_required
    @limiter.limit("30/minute")
    def api_dequeue_script(mac_address):
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Script name is required'}), 400

        script_name = data['name']
        success = device_manager.dequeue_script(mac_address, script_name)

        if success:
            return jsonify({'success': True, 'message': 'Script dequeued'}), 200
        else:
            return jsonify({'error': 'Failed to dequeue script'}), 400

    # Device status routes
    @app.route('/api/update-last-ping-time/<mac_address>', methods=['POST'])
    @device_access_required
    @limiter.limit("60/minute")
    def update_last_ping_time(mac_address):
        success = device_manager.update_last_ping_time(mac_address)
        if success:
            socketio.emit('ping_received', {'mac_address': mac_address})
            return jsonify({'success': True, 'message': 'Last ping time updated'}), 200
        else:
            return jsonify({'error': 'Device not found'}), 404

    @app.route('/api/get-last-ping-time/<mac_address>', methods=['GET'])
    @device_access_required
    @limiter.limit("60/minute")
    def get_last_ping_time(mac_address):
        last_ping_time = device_manager.get_last_ping_time(mac_address)
        return jsonify({'last_ping_time': last_ping_time}), 200

    return app


if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_CONFIG', 'default'))
    socketio = SocketIO(app)
    socketio.run(app, debug=app.config['DEBUG'], host='0.0.0.0')
