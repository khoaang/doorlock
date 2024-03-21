# DoorLock 🚪🔒

Welcome to DoorLock, a modern and efficient way to manage your IoT devices. This project allows you to add devices, upload scripts to them, and manage a queue of scripts to be executed on each device.

## Features 🚀

- **Device Management**: Add and remove devices with ease. Each device is identified by its MAC address. 📱💻
- **Script Management**: Upload scripts to devices and manage a queue of scripts to be executed on each device. 📄🔄
- **Dark Mode**: A sleek dark mode for those late-night coding sessions. 🌙💡
- **Real-time Updates**: The state of devices and scripts is updated in real-time. 🕒🔄

## Getting Started 🏁

### Prerequisites

- Node.js
- Python
- Flask
- React
- Raspberry Pi

### Installation

1. Clone the repo
   ```
   git clone https://github.com/khoaang/doorlock.git
   ```
2. Install NPM packages
   ```
   npm install
   ```
3. Install Python packages
   ```
   pip install -r requirements.txt
   ```

### Raspberry Pi Setup 🍓

1. Transfer the `pi.py` script to your Raspberry Pi.
2. Run the script using Python 3:
   ```
   python3 pi.py
   ```
3. To have the script run on startup, add a cron job:
   - Open the crontab file:
     ```
     crontab -e
     ```
   - Add the following line to the end of the file:
     ```
     @reboot python3 /path/to/pi.py &
     ```
   - Save and close the file. The script will now run on startup.

## Usage 🎮

Start the Flask server:

```
python app.py
```

Start the React app:

```
npm start
```

## Contributing 🤝

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄

DoorLock is distributed under the MIT License, which allows you to use, modify, and distribute the software for both commercial and non-commercial purposes. See the [LICENSE](LICENSE) file for more information.

## Contact 📬

Khoa Nguyen - khoan@berkeley.edu

Project Link: [https://github.com/khoaang/doorlock](https://github.com/khoaang/doorlock)

## Acknowledgements 🎉

- [React](https://reactjs.org/)
- [Flask](https://flask.palletsprojects.com/)
- [axios](https://github.com/axios/axios)
- [Socket.IO](https://socket.io/)
- [CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)

Enjoy your journey with DoorLock! 🎈🎈🎈
