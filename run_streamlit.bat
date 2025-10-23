@echo off
REM Instagram Downloader - Streamlit Deployment Script for Windows

echo 🚀 Starting Instagram Downloader Web Application...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Install requirements
echo 📦 Installing dependencies...
pip install -r requirements_streamlit.txt

if errorlevel 1 (
    echo ❌ Failed to install dependencies. Please check your internet connection and try again.
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully!

REM Create downloads directory
if not exist "downloads" mkdir downloads
echo 📁 Created downloads directory

REM Ask user which version to run
echo.
echo Which version would you like to run?
echo 1) Single URL Downloader
echo 2) Batch URL Downloader
echo.
set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" (
    echo 🌐 Starting Single URL Downloader...
    streamlit run streamlit_app.py
) else if "%choice%"=="2" (
    echo 🌐 Starting Batch URL Downloader...
    streamlit run streamlit_batch_app.py
) else (
    echo ❌ Invalid choice. Starting Single URL Downloader...
    streamlit run streamlit_app.py
)

pause
