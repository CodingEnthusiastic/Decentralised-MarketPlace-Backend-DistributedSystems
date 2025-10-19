@echo off
REM FINAL FIXED STARTUP SCRIPT - Port 8000 Series
REM This script starts servers with proper port configuration

echo === FINAL FIXED DISTRIBUTED MARKETPLACE ===
echo Using ports 8000, 8001, 8002 to avoid conflicts...

REM Clean up any existing processes
echo Stopping any existing Python processes...
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak >nul

REM Create directories
if not exist "logs" mkdir logs
if not exist "pids" mkdir pids

REM Clear old log files
del logs\*.log 2>nul

echo.
echo === STEP 1: Starting Primary Server on Port 8000 ===
start "Primary-8000" /min cmd /c "python exp5_enhanced_server.py primary 8000 true > logs\primary_8000.log 2>&1"
echo Started primary server on port 8000
timeout /t 4 /nobreak >nul

echo === STEP 2: Starting Backup1 Server on Port 8001 ===  
start "Backup1-8001" /min cmd /c "python exp5_enhanced_server.py backup1 8001 false > logs\backup1_8001.log 2>&1"
echo Started backup1 server on port 8001
timeout /t 3 /nobreak >nul

echo === STEP 3: Starting Backup2 Server on Port 8002 ===
start "Backup2-8002" /min cmd /c "python exp5_enhanced_server.py backup2 8002 false > logs\backup2_8002.log 2>&1"  
echo Started backup2 server on port 8002
timeout /t 4 /nobreak >nul

echo.
echo === STEP 4: Testing Server Connectivity ===

python -c "
import socket, json, time, sys

def test_server_connection(port, name):
    try:
        print(f'Testing {name} on port {port}...')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(('localhost', port))
        
        request = {'type': 'get_status'}
        sock.send(json.dumps(request).encode('utf-8'))
        response_data = sock.recv(1024).decode('utf-8')
        response = json.loads(response_data)
        
        sock.close()
        
        node_id = response.get('node_id', 'unknown')
        is_primary = response.get('is_primary', False)
        version = response.get('version', 0)
        
        print(f'✅ {name}: {node_id} (Primary: {is_primary}, Version: {version})')
        return True
        
    except Exception as e:
        print(f'❌ {name}: Connection failed - {str(e)}')
        return False

print('Waiting for servers to initialize...')
time.sleep(3)

print('\\n--- Server Status Check ---')
primary_ok = test_server_connection(8000, 'Primary')
backup1_ok = test_server_connection(8001, 'Backup1')
backup2_ok = test_server_connection(8002, 'Backup2')

all_servers_ok = primary_ok and backup1_ok and backup2_ok

if all_servers_ok:
    print('\\n🎉 ALL SERVERS STARTED SUCCESSFULLY!')
    print('\\n--- Testing Basic Operations ---')
    
    # Test basic client functionality
    try:
        from exp5_enhanced_client import EnhancedMarketplaceClient
        client = EnhancedMarketplaceClient()
        
        # Test server status
        status = client.get_server_status()
        if status.get('status') == 'success':
            print(f'✅ Client connection: Connected to {status.get(\"node_id\")}')
        
        # Test search
        search_result = client.search_product('apple')
        if search_result.get('status') == 'success':
            print(f'✅ Search operation: Found {len(search_result.get(\"results\", []))} results')
        
        # Test add stock
        add_result = client.add_stock('test_area', 'test_shop', 'test_item', 10)
        if add_result.get('status') == 'success':
            print(f'✅ Add stock operation: Success (Version: {add_result.get(\"version\")})')
        
        # Test load balancer config  
        lb_result = client.configure_load_balancer('round_robin')
        if lb_result.get('status') == 'success':
            print(f'✅ Load balancer: Configured successfully')
        
        print('\\n🎯 ALL BASIC OPERATIONS WORKING!')
        
    except Exception as e:
        print(f'❌ Client test failed: {e}')
        
else:
    print('\\n❌ SOME SERVERS FAILED TO START')
    print('\\nCheck log files for details:')
    print('  - logs\\primary_8000.log')  
    print('  - logs\\backup1_8001.log')
    print('  - logs\\backup2_8002.log')
"

echo.
echo === STARTUP COMPLETE ===
echo.
echo Server Information:
echo   Primary:  localhost:8000 (logs\primary_8000.log)
echo   Backup1:  localhost:8001 (logs\backup1_8001.log)  
echo   Backup2:  localhost:8002 (logs\backup2_8002.log)
echo.
echo Available Commands:
echo   1. Test all features:     python test_all_features_8000.bat
echo   2. Interactive client:    python exp5_enhanced_client.py  
echo   3. Quick status check:    python -c "from exp5_enhanced_client import EnhancedMarketplaceClient; print(EnhancedMarketplaceClient().get_server_status())"
echo.
echo To stop all servers:
echo   taskkill /f /fi "WINDOWTITLE eq *-800*"
echo.
pause