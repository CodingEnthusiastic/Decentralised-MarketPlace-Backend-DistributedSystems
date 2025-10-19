#!/bin/bash

# Fault Tolerance Demonstration Script
# This script demonstrates primary failure and automatic failover

echo "=== DISTRIBUTED MARKETPLACE FAULT TOLERANCE DEMO ==="
echo "This script will start servers and simulate primary failure"

# Function to check if a port is in use
check_port() {
    netstat -an | grep ":$1 " > /dev/null 2>&1
}

# Function to start a server
start_server() {
    local node_id=$1
    local port=$2
    local is_primary=$3
    local log_file="logs/${node_id}.log"
    
    echo "Starting $node_id on port $port (Primary: $is_primary)"
    python exp5_primary_backup_server.py $node_id $port $is_primary > $log_file 2>&1 &
    local pid=$!
    echo $pid > "pids/${node_id}.pid"
    echo "Started $node_id with PID $pid"
    sleep 2
}

# Function to stop a server
stop_server() {
    local node_id=$1
    local pid_file="pids/${node_id}.pid"
    
    if [ -f $pid_file ]; then
        local pid=$(cat $pid_file)
        echo "Stopping $node_id (PID: $pid)"
        kill $pid 2>/dev/null
        rm $pid_file
    fi
}

# Function to cleanup
cleanup() {
    echo "Cleaning up..."
    stop_server "primary"
    stop_server "backup1"
    stop_server "backup2"
    echo "Cleanup complete"
}

# Create directories
mkdir -p logs pids

# Trap to cleanup on exit
trap cleanup EXIT

echo ""
echo "Step 1: Starting Primary and Backup servers..."

# Start primary server
start_server "primary" 6000 "true"

# Start backup servers
start_server "backup1" 6001 "false"
start_server "backup2" 6002 "false"

echo ""
echo "Step 2: Testing normal operations..."
echo "Running client tests..."

# Test normal operations
python -c "
from exp5_client import MarketplaceClient
import time

client = MarketplaceClient()

print('Testing search...')
result = client.search_product('apple')
print(f'Search result: {result.get(\"status\")}')

print('Testing buy operation...')
result = client.buy_product('borivali', 'Fresh_Mart', 'apple', 2)
print(f'Buy result: {result.get(\"status\")}')

print('Getting server status...')
result = client.get_server_status()
print(f'Primary server: {result.get(\"node_id\")} (Port: {result.get(\"port\")})')
"

echo ""
echo "Step 3: Simulating primary failure..."
echo "Stopping primary server in 5 seconds..."
sleep 5

# Stop primary server to simulate failure
stop_server "primary"
echo "Primary server stopped!"

echo ""
echo "Step 4: Testing failover..."
echo "Waiting for failover to complete..."
sleep 8

# Test operations during failover
python -c "
from exp5_client import MarketplaceClient
import time

client = MarketplaceClient()

for i in range(3):
    print(f'\\nFailover test {i+1}:')
    
    # Test search
    result = client.search_product('banana')
    print(f'Search: {result.get(\"status\")}')
    
    # Test buy
    result = client.buy_product('borivali', 'Fresh_Mart', 'banana', 1)
    print(f'Buy: {result.get(\"status\")}')
    
    # Check which server is handling requests
    result = client.get_server_status()
    if result.get('status') == 'success':
        print(f'Current server: {result.get(\"node_id\")} (Primary: {result.get(\"is_primary\")})')
    
    time.sleep(2)
"

echo ""
echo "Step 5: Demonstrating data consistency..."

python -c "
from exp5_client import MarketplaceClient
import time

client = MarketplaceClient()

print('Adding test inventory...')
result = client.add_stock('test_area', 'test_shop', 'consistency_test', 50)
print(f'Add stock: {result.get(\"status\")} - Version: {result.get(\"version\")}')

time.sleep(2)

print('\\nTesting consistency with multiple operations...')
for i in range(3):
    result = client.buy_product('test_area', 'test_shop', 'consistency_test', 5)
    if result.get('status') == 'success':
        print(f'Buy {i+1}: Success - Remaining: {result.get(\"remaining_quantity\")} - Version: {result.get(\"version\")}')
    else:
        print(f'Buy {i+1}: {result.get(\"status\")}')
    time.sleep(1)
"

echo ""
echo "Step 6: Final status check..."

python -c "
from exp5_client import MarketplaceClient

client = MarketplaceClient()
result = client.get_server_status()

if result.get('status') == 'success':
    print(f'Active server: {result.get(\"node_id\")}')
    print(f'Port: {result.get(\"port\")}')
    print(f'Is Primary: {result.get(\"is_primary\")}')
    print(f'Version: {result.get(\"version\")}')
    print(f'Transaction count: {result.get(\"transaction_count\")}')
else:
    print('No servers available')
"

echo ""
echo "=== DEMONSTRATION COMPLETE ==="
echo "Demonstrated:"
echo "1. Normal distributed operations"
echo "2. Primary server failure"
echo "3. Automatic failover to backup"
echo "4. Data consistency maintenance"
echo "5. Continued operations post-failover"

echo ""
echo "Press Enter to exit..."
read