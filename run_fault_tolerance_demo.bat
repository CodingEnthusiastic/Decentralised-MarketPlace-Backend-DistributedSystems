@echo off
REM Fault Tolerance Demonstration Script for Windows
REM This script demonstrates primary failure and automatic failover

echo === DISTRIBUTED MARKETPLACE FAULT TOLERANCE DEMO ===
echo This script will start servers and simulate primary failure

REM Create directories
if not exist "logs" mkdir logs
if not exist "pids" mkdir pids

echo.
echo Step 1: Starting Primary and Backup servers...

REM Start primary server
echo Starting primary server on port 6000...
start "Primary Server" cmd /c "python exp5_primary_backup_server.py primary 6000 true > logs\primary.log 2>&1"
timeout /t 3 /nobreak >nul

REM Start backup servers
echo Starting backup1 server on port 6001...
start "Backup1 Server" cmd /c "python exp5_primary_backup_server.py backup1 6001 false > logs\backup1.log 2>&1"
timeout /t 2 /nobreak >nul

echo Starting backup2 server on port 6002...
start "Backup2 Server" cmd /c "python exp5_primary_backup_server.py backup2 6002 false > logs\backup2.log 2>&1"
timeout /t 3 /nobreak >nul

echo.
echo Step 2: Testing normal operations...
echo Running client tests...

REM Test normal operations
python -c "from exp5_client import MarketplaceClient; client = MarketplaceClient(); print('Testing search...'); result = client.search_product('apple'); print(f'Search result: {result.get(\"status\")}'); print('Testing buy operation...'); result = client.buy_product('borivali', 'Fresh_Mart', 'apple', 2); print(f'Buy result: {result.get(\"status\")}'); print('Getting server status...'); result = client.get_server_status(); print(f'Primary server: {result.get(\"node_id\")} (Port: {result.get(\"port\")})')"

echo.
echo Step 3: Simulating primary failure...
echo Stopping primary server in 5 seconds...
timeout /t 5 /nobreak >nul

REM Stop primary server (close the window)
taskkill /fi "WindowTitle eq Primary Server" /f >nul 2>&1
echo Primary server stopped!

echo.
echo Step 4: Testing failover...
echo Waiting for failover to complete...
timeout /t 8 /nobreak >nul

REM Test operations during failover
echo Testing operations during failover...
python -c "from exp5_client import MarketplaceClient; import time; client = MarketplaceClient(); [print(f'\nFailover test {i+1}:') or client.search_product('banana') and print(f'Search: {client.search_product(\"banana\").get(\"status\")}') or client.buy_product('borivali', 'Fresh_Mart', 'banana', 1) and print(f'Buy: {client.buy_product(\"borivali\", \"Fresh_Mart\", \"banana\", 1).get(\"status\")}') or client.get_server_status().get('status') == 'success' and print(f'Current server: {client.get_server_status().get(\"node_id\")} (Primary: {client.get_server_status().get(\"is_primary\")})') or time.sleep(2) for i in range(3)]"

echo.
echo Step 5: Demonstrating data consistency...
python -c "from exp5_client import MarketplaceClient; import time; client = MarketplaceClient(); print('Adding test inventory...'); result = client.add_stock('test_area', 'test_shop', 'consistency_test', 50); print(f'Add stock: {result.get(\"status\")} - Version: {result.get(\"version\")}'); time.sleep(2); print('\nTesting consistency with multiple operations...'); [client.buy_product('test_area', 'test_shop', 'consistency_test', 5) and print(f'Buy {i+1}: Success - Remaining: {client.buy_product(\"test_area\", \"test_shop\", \"consistency_test\", 5).get(\"remaining_quantity\")} - Version: {client.buy_product(\"test_area\", \"test_shop\", \"consistency_test\", 5).get(\"version\")}') if client.buy_product('test_area', 'test_shop', 'consistency_test', 5).get('status') == 'success' else print(f'Buy {i+1}: {client.buy_product(\"test_area\", \"test_shop\", \"consistency_test\", 5).get(\"status\")}') or time.sleep(1) for i in range(3)]"

echo.
echo Step 6: Final status check...
python -c "from exp5_client import MarketplaceClient; client = MarketplaceClient(); result = client.get_server_status(); print(f'Active server: {result.get(\"node_id\")}') if result.get('status') == 'success' else print('No servers available'); print(f'Port: {result.get(\"port\")}') if result.get('status') == 'success' else ''; print(f'Is Primary: {result.get(\"is_primary\")}') if result.get('status') == 'success' else ''; print(f'Version: {result.get(\"version\")}') if result.get('status') == 'success' else ''; print(f'Transaction count: {result.get(\"transaction_count\")}') if result.get('status') == 'success' else ''"

echo.
echo === DEMONSTRATION COMPLETE ===
echo Demonstrated:
echo 1. Normal distributed operations
echo 2. Primary server failure
echo 3. Automatic failover to backup
echo 4. Data consistency maintenance
echo 5. Continued operations post-failover

echo.
echo Cleaning up remaining processes...
taskkill /fi "WindowTitle eq Backup1 Server" /f >nul 2>&1
taskkill /fi "WindowTitle eq Backup2 Server" /f >nul 2>&1

echo.
echo Press any key to exit...
pause >nul