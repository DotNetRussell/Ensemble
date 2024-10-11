#!/bin/bash

# Function to start the server
start_server() {
    python3 ./ensemble_web.py --debug &
    SERVER_PID=$!
    echo "Started ensemble_web.py with PID $SERVER_PID"
    sleep 3
}

# Function to stop the server
stop_server() {
    if kill -0 $SERVER_PID 2>/dev/null; then
        echo "Stopping server with PID $SERVER_PID"
        kill $SERVER_PID
        wait $SERVER_PID 2>/dev/null
    fi
}

# Start the server
start_server

# Give the server a moment to start
sleep 2

while true; do

    # Try to ping the server
    curl --insecure --connect-timeout 5 https://127.0.0.1:5000/ping

    # Check if the curl command was successful
    if [ $? -ne 0 ]; then
        echo "Server did not respond within 5 seconds. Restarting..."
        stop_server
        # Wait before restarting
        sleep 5
	start_server
    else
        echo "Server is responding."
	sleep 5
    fi

done
