import requests
import time
import subprocess
import re
import uuid

SERVER_URL = "http://localhost:5000"  # Replace with your server URL
# Replace with your device's MAC address
DEVICE_MAC_ADDRESS = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
print("Device running with MAC address: ", DEVICE_MAC_ADDRESS)

def fetch_script_queue():
    try:
        response = requests.get(
            f"{SERVER_URL}/api/scripts-queue/{DEVICE_MAC_ADDRESS}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch script queue: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching script queue: {e}")
        return None


def dequeue_script(script_name):
    try:
        response = requests.post(
            f"{SERVER_URL}/api/dequeue-script/{DEVICE_MAC_ADDRESS}", json={'name': script_name})
        if response.status_code != 200:
            print(f"Failed to dequeue script: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error dequeuing script: {e}")


def execute_script(script_content):
    try:
        # Execute the script content as a Python script
        exec(script_content)
        print("Script executed successfully")
    except Exception as e:
        print(f"Error executing script: {e}")


def send_ping():
    try:
        response = requests.post(
            f"{SERVER_URL}/api/update-last-ping-time/{DEVICE_MAC_ADDRESS}")
        if response.status_code != 200:
            print(f"Failed to send ping: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending ping: {e}")


def main():
    while True:
        # Send a ping to the server
        send_ping()

        # Fetch and execute scripts from the server
        script_queue = fetch_script_queue()
        if script_queue:
            for script_info in script_queue:
                script_name = script_info.get("name")
                script_content = script_info.get("content")
                print(f"Executing script: {script_name}")
                execute_script(script_content)
                dequeue_script(script_name)
        time.sleep(10)  # Request every 10 seconds


if __name__ == "__main__":
    main()
