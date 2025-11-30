@echo off
setlocal enabledelayedexpansion

:: Set up environment variables
set MPV_DIR=C:\mpv
set DELUGE_EXE="C:\Program Files\Deluge\deluged.exe"
set DELUGE_WEB_EXE="C:\Program Files\Deluge\deluge-web.exe"
set DELUGE_CONFIG_DIR=%APPDATA%\deluge
set DELUGE_AUTH=%~dp0config\deluge_auth
set DELUGE_CONF=%~dp0config\deluge.conf

:: Create required directories
if not exist "%DELUGE_CONFIG_DIR%" (
    mkdir "%DELUGE_CONFIG_DIR%"
)

:: Create fresh auth file
echo Creating Deluge auth file...
echo deluge:deluge:10 > "%DELUGE_CONFIG_DIR%\auth"

:: Create core config
(
    echo {
    echo     "file": 1,
    echo     "format": 1
    echo } {
    echo     "auth_anonymous_download": false,
    echo     "daemon_port": 58846,
    echo     "allow_remote": true,
    echo     "download_location": "C:\\Users\\%USERNAME%\\Downloads",
    echo     "listen_ports": [6881, 6891],
    echo     "dht_ports": [6881, 6881],
    echo     "random_port": false,
    echo     "random_outgoing_ports": false,
    echo     "enabled_plugins": ["Label", "AutoAdd"],
    echo     "enabled_plugins": ["Label"],
    echo     "autoadd_enable": true,
    echo     "autoadd_location": "C:\\Users\\%USERNAME%\\Downloads"
    echo }
) > "%DELUGE_CONFIG_DIR%\core.conf"

:: Add MPV to PATH
set PATH=%MPV_DIR%;%PATH%

:: Copy Deluge configuration files
echo Configuring Deluge...
copy /Y "%DELUGE_AUTH%" "%DELUGE_CONFIG_DIR%\auth" >nul 2>&1
copy /Y "%DELUGE_CONF%" "%DELUGE_CONFIG_DIR%\core.conf" >nul 2>&1

:: Stop any running Deluge instances
echo Stopping any running Deluge instances...
taskkill /F /IM deluged.exe >nul 2>&1
taskkill /F /IM deluge-web.exe >nul 2>&1
timeout /t 2 /nobreak >nul

:: Start Deluge daemon
echo Starting Deluge daemon...
start "" %DELUGE_EXE% -c "%DELUGE_CONFIG_DIR%" -l "%DELUGE_CONFIG_DIR%\deluged.log" -L info

echo Waiting for Deluge daemon to start...
timeout /t 15 /nobreak >nul

:: Start Deluge Web UI
echo Starting Deluge Web UI...
start "" %DELUGE_WEB_EXE% -c "%DELUGE_CONFIG_DIR%" -l "%DELUGE_CONFIG_DIR%\deluge-web.log" -L info

echo Waiting for Web UI to start...
timeout /t 3 /nobreak >nul

:: Run the application
echo Running application...
python "%~dp0main.py"

:: Clean up on exit
echo Cleaning up...
taskkill /F /IM deluged.exe >nul 2>&1
taskkill /F /IM deluge-web.exe >nul 2>&1

echo.
echo Deluge Web UI: http://localhost:8112
echo Default credentials: deluge/deluge
echo.
pause
