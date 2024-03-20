from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import device_manager
from werkzeug.utils import secure_filename
app = Flask(__name__)
# Enable CORS for all domains on all routes, adjust as necessary for production.
CORS(app)
socketio = SocketIO(app)


@app.route('/api/devices', methods=['GET'])
def get_devices():
    devices_dict = device_manager.load_devices()
    # Convert each Device instance into a dictionary
    devices_serializable = [device.to_dict()
                            for device in devices_dict.values()]
    print(devices_serializable)
    return jsonify(devices_serializable)


@app.route('/api/devices', methods=['POST'])
def api_add_device():
    data = request.get_json()
    mac_address = data['mac_address']
    name = data.get('name', 'Unknown')  # Default to 'Unknown' if not provided
    emoji = data.get('emoji', '')  # Default to empty string if not provided
    # Expect scripts as a dictionary, default to empty if not provided
    scripts = data.get('scripts', {})

    success = device_manager.add_device(mac_address, name, emoji, scripts)
    if success:
        # Fetch the updated devices list
        devices = device_manager.load_devices()
        devices_serializable = [device.to_dict()
                                for device in devices.values()]
        return jsonify({'success': True, 'devices': devices_serializable}), 201
    else:
        return jsonify({'error': 'Device already exists'}), 409


@app.route('/api/devices/<mac_address>', methods=['DELETE'])
def delete_device(mac_address):
    if device_manager.remove_device(mac_address):
        return jsonify({'success': True, 'message': 'Device removed'}), 200
    else:
        return jsonify({'error': 'Device not found'}), 404


@app.route('/api/scripts/<mac_address>', methods=['POST'])
def api_upload_script(mac_address):
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        script_content = file.read().decode("utf-8")

        device_manager.add_script_to_device(
            mac_address, filename, script_content)
        return jsonify({'success': True, 'message': f'Script {filename} uploaded successfully'}), 200


@app.route('/api/scripts/<mac_address>/<script_name>', methods=['DELETE'])
def api_remove_script(mac_address, script_name):
    try:
        device_manager.remove_script_from_device(mac_address, script_name)
        return jsonify({'success': True, 'message': f'Script {script_name} removed from device {mac_address}'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/enqueue-script/<mac_address>', methods=['POST'])
def api_enqueue_script(mac_address):
    data = request.get_json()
    script_name = data['name']

    device_manager.enqueue_script(mac_address, script_name)
    return jsonify({'success': True, 'message': 'Script enqueued'}), 200


@app.route('/api/dequeue-script/<mac_address>', methods=['POST'])
def api_dequeue_script(mac_address):
    data = request.get_json()
    script_name = data['name']

    device_manager.dequeue_script(mac_address, script_name)
    return jsonify({'success': True, 'message': 'Script dequeued'}), 200


@app.route('/api/fetch-scripts/<mac_address>', methods=['GET'])
def api_fetch_scripts(mac_address):
    scripts = device_manager.fetch_scripts_for_device(mac_address)
    return jsonify(scripts), 200


@app.route('/api/scripts-queue/<mac_address>', methods=['GET'])
def api_fetch_script_queue(mac_address: str):
    script_queue = device_manager.load_script_queue()
    if mac_address in script_queue:
        return jsonify(script_queue[mac_address]), 200
    else:
        return jsonify({'error': f'Script queue not found for device with MAC {mac_address}'}), 404


@app.route('/api/update-last-ping-time/<mac_address>', methods=['POST'])
def update_last_ping_time(mac_address):
    device_manager.update_last_ping_time(mac_address)
    print(device_manager.get_last_ping_time(mac_address))
    socketio.emit('ping_received', {
                  'mac_address': mac_address})
    return jsonify({'success': True, 'message': 'Last ping time updated'}), 200


@app.route('/api/get-last-ping-time/<mac_address>', methods=['GET'])
def get_last_ping_time(mac_address):
    last_ping_time = device_manager.get_last_ping_time(mac_address)
    return jsonify({'last_ping_time': last_ping_time}), 200


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
