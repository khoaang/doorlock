# DoorLock IoT System

A complete, self-hosted IoT system for managing smart devices in your home network. Built with security, reliability, and ease of use in mind.

## Features

- 🔐 Secure authentication and authorization
- 📱 Modern, responsive web interface
- 🌙 Dark/Light theme support
- 🔄 Real-time updates via WebSocket
- 📊 Device monitoring and management
- 🤖 Automation support
- 📜 Script management
- 🔌 Multi-protocol support (MQTT, HTTP, etc.)
- 🐳 Docker-based deployment
- 📦 Easy installation

## System Requirements

- Docker
- Docker Compose
- 2GB RAM (minimum)
- 10GB disk space
- Network access to your IoT devices

## Quick Start

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/doorlock.git
   cd doorlock
   ```

2. Run the installation script:

   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. Access the web interface at http://localhost:3000

Default credentials:

- Email: admin@doorlock.local
- Password: admin123

**Important**: Change these credentials after first login!

## Architecture

The system consists of several components:

- **Frontend**: React-based web interface
- **Backend**: Flask API server
- **Database**: PostgreSQL for data persistence
- **Cache**: Redis for session management and caching
- **MQTT Broker**: Mosquitto for IoT device communication

## Development

### Frontend Development

```bash
cd frontend
npm install
npm start
```

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
flask run
```

## Configuration

### Environment Variables

Backend:

- `FLASK_ENV`: production/development
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `MQTT_BROKER_HOST`: MQTT broker hostname
- `MQTT_BROKER_PORT`: MQTT broker port

Frontend:

- `REACT_APP_API_URL`: Backend API URL
- `REACT_APP_SOCKET_URL`: WebSocket server URL

## Adding Devices

1. Navigate to the Devices page
2. Click "Add Device"
3. Select the device type
4. Configure device settings
5. Test the connection

Supported device types:

- MQTT devices
- HTTP devices
- Custom protocol devices (via plugins)

## Security Considerations

1. Change default credentials immediately
2. Use HTTPS in production
3. Configure firewall rules
4. Enable MQTT authentication in production
5. Regularly update system components

## Backup and Recovery

1. Database backup:

   ```bash
   docker-compose exec db pg_dump -U doorlock > backup.sql
   ```

2. Restore from backup:
   ```bash
   docker-compose exec -T db psql -U doorlock < backup.sql
   ```

## Troubleshooting

1. Check logs:

   ```bash
   docker-compose logs -f [service_name]
   ```

2. Restart services:

   ```bash
   docker-compose restart [service_name]
   ```

3. Reset system:
   ```bash
   docker-compose down -v
   ./install.sh
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details

## Support

- GitHub Issues: [Report a bug](https://github.com/yourusername/doorlock/issues)
- Documentation: [Wiki](https://github.com/yourusername/doorlock/wiki)
- Community: [Discussions](https://github.com/yourusername/doorlock/discussions)
