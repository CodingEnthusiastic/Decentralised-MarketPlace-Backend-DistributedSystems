@echo off
echo === STOPPING ALL SERVERS - Port 8000 Series ===
echo.

echo Stopping distributed marketplace servers...

REM Kill all Python processes running exp5_enhanced_server
echo Terminating server processes...
taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *exp5_enhanced_server*" >nul 2>&1
taskkill /F /FI "IMAGENAME eq python3.exe" /FI "WINDOWTITLE eq *exp5_enhanced_server*" >nul 2>&1
taskkill /F /FI "IMAGENAME eq py.exe" /FI "WINDOWTITLE eq *exp5_enhanced_server*" >nul 2>&1

REM Alternative method - kill by command line pattern
wmic process where "CommandLine like '%%exp5_enhanced_server%%'" delete >nul 2>&1

REM Wait a moment for processes to terminate
timeout /t 2 /nobreak >nul

echo Checking if servers are stopped...

REM Check if ports are still in use
netstat -an | findstr ":8000 " >nul
if %errorlevel% equ 0 (
    echo WARNING: Port 8000 still in use
) else (
    echo Port 8000: FREE
)

netstat -an | findstr ":8001 " >nul
if %errorlevel% equ 0 (
    echo WARNING: Port 8001 still in use
) else (
    echo Port 8001: FREE
)

netstat -an | findstr ":8002 " >nul
if %errorlevel% equ 0 (
    echo WARNING: Port 8002 still in use
) else (
    echo Port 8002: FREE
)

REM Clean up PID files
if exist pids\primary_8000.pid del pids\primary_8000.pid
if exist pids\backup1_8001.pid del pids\backup1_8001.pid
if exist pids\backup2_8002.pid del pids\backup2_8002.pid

echo.
echo Cleanup complete!
echo All servers should now be stopped.
echo.
echo To restart servers, run:
echo   start_servers_8000.bat
echo.

pause