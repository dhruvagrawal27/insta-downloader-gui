@echo off
REM Quick start script for Instagram Media Downloader v2.0
REM This script installs FastAPI dependencies and starts the backend server

echo ================================
echo Instagram Media Downloader v2.0
echo Backend Setup (FastAPI)
echo ================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo Installing/Updating dependencies...
pip install -r requirements-api.txt
echo.

echo ================================
echo Starting FastAPI Server...
echo ================================
echo.
echo API Documentation: http://localhost:8000/api/docs
echo Health Check: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
echo ================================
echo.

python api_server.py

pause
