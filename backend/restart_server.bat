@echo off
echo ========================================
echo Dr. Martens Backend Server Restart
echo ========================================
echo.

REM Kill any existing Python processes using port 5000
echo Checking for processes using port 5000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
    echo Killing process %%a...
    taskkill /F /PID %%a 2>nul
)

echo.
echo Waiting 2 seconds for port to be released...
timeout /t 2 /nobreak >nul

echo.
echo Starting Flask server...
echo.
python app.py

pause
