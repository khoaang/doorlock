from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
import device_manager

app = Flask(__name__)
# This enables CORS for all domains on all routes. Adjust as necessary for production.
CORS(app)


@app.route('/')
def home():
    devices = device_manager.list_devices()
    return render_template('index.html', devices=devices)


@app.route('/api/devices', methods=['GET'])
def get_devices():
    devices = device_manager.list_devices()
    serialized_devices = [device.to_dict() for device in devices]
    return jsonify(serialized_devices)


@app.route('/api/devices', methods=['POST'])
def api_add_device():
    data = request.get_json()
    mac_address = data['mac_address']
    name = data.get('name', 'Unknown')  # Default to 'Unknown' if not provided
    emoji = data.get('emoji', '')  # Default to empty string if not provided

    device_manager.add_device(mac_address, name, emoji)
    return jsonify({'success': True, 'mac_address': mac_address, 'name': name, 'emoji': emoji}), 201


@app.route('/api/devices/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    # Implement the logic to remove a device based on its ID or MAC address
    # Assume this function is implemented in device_manager
    if device_manager.remove_device(device_id):
        return jsonify({'success': True, 'message': 'Device removed'}), 200
    else:
        return jsonify({'error': 'Device not found'}), 404@app.route('/api/devices/<device_id>', methods=['DELETE'])


@app.route('/ping/<ip_address>')
def ping(ip_address):
    is_online = device_manager.ping_device(ip_address)
    return jsonify({'ip_address': ip_address, 'online': is_online})


@app.route('/api/run-script/<device_id>', methods=['POST'])
def run_script_on_device(device_id):
    if 'script' not in request.files:
        return jsonify({'error': 'No script file provided'}), 400

    script_file = request.files['script']
    script_content = script_file.read()

    # Execute the script (safely, in your actual implementation)
    if device_manager.execute_script_on_device(device_id, script_content):
        return jsonify({'message': 'Script executed successfully'}), 200
    else:
        return jsonify({'error': 'Script execution failed'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
