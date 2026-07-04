#!/bin/bash

#1. Pull code from main
echo "Pull code from Github..."
git pull origin main

#2. Get Arduino Port
echo "Scanning for arduino port..."
ARDUINO_CLI="/home/pi/.local/bin/arduino-cli"
PORT=$($ARDUINO_CLI board list | grep "arduino:avr:uno" | awk '{print $1}')

if [ -z "$PORT" ]; then
    echo "Port not found."
    exit 1
fi
echo "Found arduino port: $PORT"

#3. Compile Code
echo "Compiling code..."

if $ARDUINO_CLI compile --fqbn arduino:avr:uno ./arduino_code/arduino_code.ino; then
    echo "Compile successful."
else
    echo "Error: compile failed."
    exit 1
fi

#4. Flash to board
echo "Flash to arduino..."
if $ARDUINO_CLI upload -p "$PORT" --fqbn arduino:avr:uno ./arduino_code/arduino_code.ino; then
    echo "Flash complete."
else
    echo "Error: Failed to flash."
    exit 1
fi

#5. Docker Rebuild

echo -e "Rebuilding Docker Container..."
cd docker_setup || exit
sudo docker compose down
sudo docker compose up -d --build
cd ..
echo "Docker container is live."
echo ""

#6. Starting python nodes
echo "Restarting Python Nodes..."

pkill -f vision_sender.py
pkill -f gas_reader.py
sleep 2

VENV_PYTHON="./.venv/bin/python"
nohup $VENV_PYTHON ./camera_code/vision_sender.py > vision_node.log 2>&1 &
VISION_PID=$!


nohup $VENV_PYTHON ./arduino_code/gas_reader.py > gas_node.log 2>&1 &
GAS_PID=$!

echo "Python nodes activated."
echo "Camera Node PID: $VISION_PID"
echo "Gas Node PID: $GAS_PID"
echo""

# 7. Start Ngrok
echo "Start Ngrok Tunnel"
pkill -f ngrok
sleep 2

nohup ngrok http 5000 > ngrok_status.log 2>&1 &
NGROK_PID=$!

echo "Ngrok tunnel activated"
echo "Ngrok PID: $NGROK_PID"
echo ""

#8. Completed
echo "Deployment Completed"
