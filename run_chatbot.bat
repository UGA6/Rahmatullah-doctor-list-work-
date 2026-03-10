@echo off
REM ===========================================
REM ADMA Healthcare Chatbot - Run Script
REM ===========================================

echo.
echo Starting ADMA Healthcare Chatbot...
echo.

REM Kill any existing process on port 8000
echo Closing existing servers...
netstat -ano | findstr :8000 > temp_port.txt
for /f "tokens=5" %%a in (temp_port.txt) do (
    taskkill /F /PID %%a 2>nul
)
del temp_port.txt 2>nul

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Activate virtual environment and run
call venv\Scripts\activate.bat
python -m chatbot.main

pause
