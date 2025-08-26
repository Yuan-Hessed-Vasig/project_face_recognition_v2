@echo off
echo Starting Face Recognition App in Development Mode...
echo.
echo This will auto-reload the app after 10 file saves.
echo Press Ctrl+C to stop.
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking required packages...
python -c "import watchdog, psutil" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements-dev.txt
    if errorlevel 1 (
        echo Error: Failed to install required packages
        pause
        exit /b 1
    )
)

REM Run the development script
echo Starting development server...
python dev.py

pause
