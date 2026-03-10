@echo off
REM ===========================================
REM ADMA Healthcare Chatbot - Setup & Run
REM ===========================================

echo.
echo ========================================
echo ADMA Healthcare Chatbot
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [1/3] Creating virtual environment...
    python -m venv venv
    echo.
)

echo [2/3] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [3/3] Installing dependencies...
pip install --quiet fastapi uvicorn sqlalchemy python-dotenv python-multipart

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Running the chatbot...
echo.

REM Kill any process on port 8000
netstat -ano | findstr :8000 > temp_port.txt 2>nul
for /f "tokens=5" %%a in (temp_port.txt) do taskkill /F /PID %%a 2>nul
del temp_port.txt 2>nul

REM Run the chatbot
python -m chatbot.main

pause
