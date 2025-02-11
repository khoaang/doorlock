#!/bin/bash

# Make script exit on error
set -e

echo "Setting up DoorLock IoT System..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "Docker is required but not installed. Visit https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is required but not installed. Visit https://docs.docker.com/compose/install/"
    exit 1
fi

# Create directories
echo "Creating directories..."
mkdir -p {mosquitto/{config,data,log},uploads}

# Copy Mosquitto config
echo "Configuring MQTT broker..."
cat > mosquitto/config/mosquitto.conf << EOL
persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
log_dest stdout

listener 1883
protocol mqtt

listener 9001
protocol websockets

allow_anonymous true
EOL

# Generate secret key
echo "Generating secret key..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
JWT_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Create .env file
cat > .env << EOL
SECRET_KEY=${SECRET_KEY}
JWT_SECRET_KEY=${JWT_KEY}
FLASK_ENV=production
EOL

echo "Starting services..."
docker-compose up -d

echo "Waiting for database..."
sleep 10

echo "Running database migrations..."
docker-compose exec backend flask db upgrade

echo "Installation complete!"
echo
echo "Access your IoT system at:"
echo "- Web Interface: http://localhost:3000"
echo "- MQTT Broker: localhost:1883"
echo
echo "Default credentials:"
echo "Email: admin@doorlock.local"
echo "Password: admin123"
echo
echo "IMPORTANT: Change these credentials after first login!" 