# doorLock 🚪🔒

doorLock is an open-source platform designed to turn Raspberry Pi devices into smart home automation hubs. It provides a user-friendly web interface for managing IoT devices and running scripts to automate various tasks.

## Features 🌟

- **Device Management:** Easily add, remove, and configure IoT devices from a centralized dashboard.
- **Script Execution:** Upload and execute scripts on individual devices to automate actions like controlling lights, locks, or sensors.
- **Cross-Platform Compatibility:** Works seamlessly on Raspberry Pi devices, enabling users to create their own smart home automation systems.
- **User-Friendly Interface:** Intuitive web interface for managing devices and scripts, suitable for both beginners and advanced users.
- **Customizable:** Extendable architecture allows users to add custom scripts and integrations tailored to their specific needs.

## How It Works 🛠️

1. **Setup doorLock:** Start the doorLock server on your local computer.
2. **Access the Web Interface:** Open a web browser and navigate to the doorLock server's address.
3. **Manage Devices:** Add new IoT devices by entering their MAC addresses and names.
4. **Upload Scripts:** Upload scripts to automate tasks on individual devices.
5. **Execute Scripts:** Run uploaded scripts to trigger actions on the connected devices.

## Hosting Requirements 🖥️

- Raspberry Pi running Raspbian or any compatible operating system.
- Python installed on the Raspberry Pi.
- Access to the internet for fetching dependencies and updates.

## Installation Steps 🚀

1. **Clone the Repository:** `git clone https://github.com/khoaang/doorLock.git`
2. **Navigate to the Project Directory:** `cd doorLock`
3. **Install Dependencies:** `pip install -r requirements.txt`
4. **Run the Server:** `python app.py`
5. **Access the Web Interface:** Open a web browser and go to `http://localhost:5000` (or the appropriate IP address of your Raspberry Pi).

## How to Prepare Raspberry Pi for Script Execution 💡

1. **Ensure Python is Installed:** Check if Python is installed on your Raspberry Pi by running `python --version` in the terminal. If not installed, follow [official documentation](https://www.python.org/downloads/) to install Python.
2. **Install Required Libraries:** Install necessary libraries using `pip install -r requirements.txt` in the project directory.
3. **Configure Environment:** Set up any environment variables required for your scripts or the doorLock application.
4. **Run Scripts:** Use the doorLock web interface to upload and execute scripts on your Raspberry Pi devices.

## Contributing 🤝

We welcome contributions from the open-source community to improve and enhance doorLock. Here's how you can contribute:

- **Bug Reports:** Report any bugs or issues you encounter while using doorLock.
- **Feature Requests:** Suggest new features or improvements to enhance the functionality of doorLock.
- **Pull Requests:** Submit pull requests with fixes, enhancements, or new features.

To contribute, fork the repository, make your changes, and submit a pull request. Be sure to follow the contribution guidelines outlined in the project's repository.

## License 📜

doorLock is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

**Note:** doorLock is a project created for educational and experimental purposes. Use it responsibly and ensure that your IoT devices are secure and properly configured to avoid any potential risks. 🧠💡
```
