#!/bin/bash
# COMPREHENSIVE FEATURE TESTING - Port 8000 Series
echo "=== COMPREHENSIVE FEATURE TESTING - Port 8000 Series ==="
echo "Testing all three main features of the distributed marketplace..."
echo ""

# Test 1: Primary-Backup Replication
echo "=== TEST 1: PRIMARY-BACKUP REPLICATION ==="
python3 << 'EOF'
from exp5_enhanced_client import EnhancedMarketplaceClient
import time

client = EnhancedMarketplaceClient()
print('Testing replication across servers...')

print('\n1. Adding stock on primary server:')
result = client.add_stock('test_area', 'test_shop', 'replication_test_item', 50)
if result.get('status') == 'success':
    version = result.get('version')
    print(f'   Added item successfully. Version: {version}')
else:
    print(f'   Failed: {result}')

print('\n2. Checking if data replicated to all servers:')
time.sleep(2)  # Wait for replication

# Check each server individually
for port in [8000, 8001, 8002]:
    try:
        import socket, json
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect(('localhost', port))
        
        request = {'type': 'search_product', 'query': 'replication_test_item'}
        sock.send(json.dumps(request).encode('utf-8'))
        response_data = sock.recv(1024).decode('utf-8')
        response = json.loads(response_data)
        sock.close()
        
        if response.get('status') == 'success' and len(response.get('results', [])) > 0:
            print(f'   Port {port}: ✅ Data replicated successfully')
        else:
            print(f'   Port {port}: ❌ Data not found')
    except Exception as e:
        print(f'   Port {port}: ❌ Connection failed: {e}')

print('\n✅ REPLICATION TEST COMPLETE')
EOF

echo ""
echo "=== TEST 2: FAULT TOLERANCE ==="
python3 << 'EOF'
from exp5_enhanced_client import EnhancedMarketplaceClient
import time
import subprocess
import os

client = EnhancedMarketplaceClient()
print('Testing fault tolerance with server failure simulation...')

print('\n1. Current server status:')
status = client.get_server_status()
if status.get('status') == 'success':
    current_node = status.get('node_id')
    print(f'   Connected to: {current_node}')
    print(f'   Is Primary: {status.get("is_primary", False)}')

print('\n2. Adding test data before failure:')
result = client.add_stock('fault_test_area', 'fault_test_shop', 'fault_test_item', 25)
if result.get('status') == 'success':
    print(f'   Added test data successfully. Version: {result.get("version")}')
else:
    print(f'   Failed to add test data: {result}')

print('\n3. Simulating server failure (killing primary server):')
try:
    # Kill primary server process using pkill
    subprocess.run(['pkill', '-f', 'python.*exp5_enhanced_server.*primary'], 
                   capture_output=True, text=True)
    print('   Primary server terminated')
    time.sleep(3)  # Wait for failover
except Exception as e:
    print(f'   Could not terminate primary: {e}')

print('\n4. Testing automatic failover:')
for i in range(3):
    status = client.get_server_status()
    if status.get('status') == 'success':
        new_node = status.get('node_id')
        print(f'   Attempt {i+1}: Connected to {new_node}')
        if new_node != current_node:
            print('   ✅ Failover successful! Connected to backup server.')
            break
    else:
        print(f'   Attempt {i+1}: No response, retrying...')
    time.sleep(2)

print('\n5. Testing data persistence after failover:')
search_result = client.search_product('fault_test_item')
if search_result.get('status') == 'success' and len(search_result.get('results', [])) > 0:
    print('   ✅ Data survived server failure! Backup working correctly.')
else:
    print('   ❌ Data lost or backup not responding properly')

print('\n✅ FAULT TOLERANCE TEST COMPLETE')
EOF

echo ""
echo "=== TEST 3: LOAD BALANCING ==="
python3 << 'EOF'
from exp5_enhanced_client import EnhancedMarketplaceClient
import time

client = EnhancedMarketplaceClient()
print('Testing all load balancing algorithms...')

algorithms = ['round_robin', 'weighted', 'least_connections', 'hash_based']

for algo in algorithms:
    print(f'\n--- Testing {algo.upper()} Algorithm ---')
    
    # Configure load balancer
    config_result = client.configure_load_balancer(algo)
    if config_result.get('status') == 'success':
        print(f'   Configured {algo} algorithm')
    else:
        print(f'   Failed to configure {algo}: {config_result}')
        continue
    
    # Test multiple requests to see load distribution
    print('   Testing load distribution across 5 requests:')
    servers_hit = set()
    
    for i in range(5):
        status = client.get_server_status()
        if status.get('status') == 'success':
            node = status.get('node_id')
            servers_hit.add(node)
            print(f'     Request {i+1}: Routed to {node}')
        else:
            print(f'     Request {i+1}: Failed')
        time.sleep(0.5)
    
    print(f'   Summary: Requests distributed across {len(servers_hit)} servers')
    print(f'   Servers used: {list(servers_hit)}')

print('\n✅ LOAD BALANCING TEST COMPLETE')
EOF

echo ""
echo "=== PERFORMANCE AND STRESS TESTING ==="
python3 << 'EOF'
from exp5_enhanced_client import EnhancedMarketplaceClient
import time
import threading

print('Running performance tests...')

client = EnhancedMarketplaceClient()

print('\n1. Response Time Test:')
start_time = time.time()
for i in range(10):
    client.get_server_status()
end_time = time.time()
avg_time = (end_time - start_time) / 10
print(f'   Average response time: {avg_time:.3f} seconds per request')

print('\n2. Concurrent Client Test:')
def concurrent_request(client_id):
    try:
        client = EnhancedMarketplaceClient()
        result = client.add_stock(f'area_{client_id}', f'shop_{client_id}', f'item_{client_id}', 10)
        return result.get('status') == 'success'
    except:
        return False

# Test with 5 concurrent clients
threads = []
results = []
for i in range(5):
    thread = threading.Thread(target=lambda i=i: results.append(concurrent_request(i)))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

successful = sum(1 for r in results if r)
print(f'   Concurrent clients: {successful}/5 successful')

print('\n3. High-Volume Search Test:')
start_time = time.time()
for i in range(20):
    client.search_product(f'test_query_{i % 5}')
end_time = time.time()
total_time = end_time - start_time
print(f'   20 searches completed in {total_time:.2f} seconds')
print(f'   Average: {total_time/20:.3f} seconds per search')

print('\n✅ PERFORMANCE TESTING COMPLETE')
EOF

echo ""
echo "=== FINAL SYSTEM STATUS ==="
python3 << 'EOF'
from exp5_enhanced_client import EnhancedMarketplaceClient
import socket, json

client = EnhancedMarketplaceClient()

print('=== Current System Status ===')

# Check each server
servers = [
    ('Primary', 8000),
    ('Backup1', 8001), 
    ('Backup2', 8002)
]

active_servers = 0
for name, port in servers:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(('localhost', port))
        
        request = {'type': 'get_status'}
        sock.send(json.dumps(request).encode('utf-8'))
        response_data = sock.recv(1024).decode('utf-8')
        response = json.loads(response_data)
        sock.close()
        
        node_id = response.get('node_id', 'unknown')
        is_primary = '(PRIMARY)' if response.get('is_primary') else '(BACKUP)'
        version = response.get('version', 0)
        
        print(f'✅ {name:8} (port {port}): {node_id} {is_primary} v{version}')
        active_servers += 1
        
    except Exception as e:
        print(f'❌ {name:8} (port {port}): OFFLINE - {str(e)[:30]}')

print(f'\nActive servers: {active_servers}/3')

# Test client connectivity
print('\n=== Client Connectivity ===')
try:
    status = client.get_server_status()
    if status.get('status') == 'success':
        connected_to = status.get('node_id')
        print(f'✅ Client connected to: {connected_to}')
        
        # Quick operation test
        search_result = client.search_product('test')
        if search_result.get('status') == 'success':
            print('✅ Search operations: WORKING')
        else:
            print('❌ Search operations: FAILED')
            
        add_result = client.add_stock('final_test', 'final_shop', 'final_item', 1)
        if add_result.get('status') == 'success':
            print('✅ Stock operations: WORKING')  
        else:
            print('❌ Stock operations: FAILED')
    else:
        print('❌ Client cannot connect to any server')
except Exception as e:
    print(f'❌ Client error: {e}')

print('\n' + '='*50)
print('🎯 COMPREHENSIVE TESTING COMPLETE!')
print('='*50)
EOF

echo ""
echo "Press Enter to continue..."
read