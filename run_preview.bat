@echo off
REM Instagram Preview App - No Local Storage

echo 🚀 Starting Instagram Preview Application...

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

REM Ask user which version to run
echo.
echo Which version would you like to run?
echo 1) Preview Mode (No Local Storage)
echo 2) Single URL Downloader (Saves Files)
echo 3) Batch URL Downloader (Saves Files)
echo.
set /p choice="Enter your choice (1, 2, or 3): "

if "%choice%"=="1" (
    echo 🌐 Starting Preview Mode Application...
    streamlit run streamlit_preview_app.py --server.port 8502
) else if "%choice%"=="2" (
    echo 🌐 Starting Single URL Downloader...
    streamlit run streamlit_app.py --server.port 8501
) else if "%choice%"=="3" (
    echo 🌐 Starting Batch URL Downloader...
    streamlit run streamlit_batch_app.py --server.port 8503
) else (
    echo ❌ Invalid choice. Starting Preview Mode...
    streamlit run streamlit_preview_app.py --server.port 8502
)

pause
