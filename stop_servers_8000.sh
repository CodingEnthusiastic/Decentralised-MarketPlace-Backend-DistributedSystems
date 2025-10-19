#!/bin/bash
# STOPPING ALL SERVERS - Port 8000 Series

echo "=== STOPPING ALL SERVERS - Port 8000 Series ==="
echo ""

echo "Stopping distributed marketplace servers..."

# Kill all Python processes running exp5_enhanced_server
echo "Terminating server processes..."
pkill -f "python.*exp5_enhanced_server" 2>/dev/null
pkill -f "python3.*exp5_enhanced_server" 2>/dev/null

# Wait a moment for processes to terminate
sleep 3

echo "Checking if servers are stopped..."

# Function to check if port is in use
check_port_usage() {
    local port=$1
    if command -v netstat >/dev/null 2>&1; then
        if netstat -an 2>/dev/null | grep ":$port " >/dev/null 2>&1; then
            echo "WARNING: Port $port still in use"
        else
            echo "Port $port: FREE"
        fi
    else
        if timeout 1 bash -c "</dev/tcp/localhost/$port" >/dev/null 2>&1; then
            echo "WARNING: Port $port still in use"
        else
            echo "Port $port: FREE"
        fi
    fi
}

# Check if ports are still in use
check_port_usage 8000
check_port_usage 8001 
check_port_usage 8002

# Clean up PID files
rm -f pids/primary_8000.pid 2>/dev/null
rm -f pids/backup1_8001.pid 2>/dev/null
rm -f pids/backup2_8002.pid 2>/dev/null

echo ""
echo "Cleanup complete!"
echo "All servers should now be stopped."
echo ""
echo "To restart servers, run:"
echo "  bash start_servers_8000.sh"
echo ""