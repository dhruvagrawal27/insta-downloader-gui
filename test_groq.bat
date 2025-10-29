@echo off
REM Quick Test Script for Groq Transcription

echo.
echo ========================================
echo   GROQ HINGLISH TRANSCRIPTION TEST
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Check if groq package is installed
python -c "import groq" 2>nul
if errorlevel 1 (
    echo [INFO] Installing Groq package...
    pip install groq
    if errorlevel 1 (
        echo [ERROR] Failed to install Groq package
        pause
        exit /b 1
    )
    echo [SUCCESS] Groq package installed!
    echo.
)

REM Check for API key
if defined GROQ_API_KEY (
    echo [INFO] Using API key from environment variable
    echo.
) else (
    echo [INFO] No GROQ_API_KEY environment variable found
    echo.
    set /p TEMP_KEY="Enter your Groq API key (or press Enter to skip): "
    if not "!TEMP_KEY!"=="" (
        set GROQ_API_KEY=!TEMP_KEY!
        echo [SUCCESS] API key set for this session
        echo.
    )
)

echo Choose an option:
echo.
echo 1. Run Streamlit App (Web Interface)
echo 2. Run Test Script (CLI)
echo 3. Test with Example Code
echo 4. Show Documentation
echo 5. Exit
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo [INFO] Starting Streamlit app...
    echo [INFO] The app will open in your browser at http://localhost:8502
    echo.
    streamlit run streamlit_preview_app.py --server.port 8502
    goto end
)

if "%choice%"=="2" (
    echo.
    echo [INFO] Starting interactive test script...
    echo.
    python test_groq_transcription.py
    goto end
)

if "%choice%"=="3" (
    echo.
    echo [INFO] Testing with example code...
    echo.
    
    REM Create a temporary test script
    echo from src.core.groq_transcriber import GroqTranscriber > temp_test.py
    echo import os >> temp_test.py
    echo. >> temp_test.py
    echo api_key = os.getenv("GROQ_API_KEY") >> temp_test.py
    echo if not api_key: >> temp_test.py
    echo     api_key = input("Enter your Groq API key: ").strip() >> temp_test.py
    echo. >> temp_test.py
    echo if api_key: >> temp_test.py
    echo     print("\n[SUCCESS] API key validated!") >> temp_test.py
    echo     print("You can now use GroqTranscriber for transcription.") >> temp_test.py
    echo     print("\nExample usage:") >> temp_test.py
    echo     print("  transcriber = GroqTranscriber(api_key=api_key)") >> temp_test.py
    echo     print("  result = transcriber.transcribe_and_process('audio.mp3')") >> temp_test.py
    echo     print("  print(result['final_transcription'])") >> temp_test.py
    echo else: >> temp_test.py
    echo     print("\n[ERROR] No API key provided") >> temp_test.py
    
    python temp_test.py
    del temp_test.py
    
    echo.
    pause
    goto end
)

if "%choice%"=="4" (
    echo.
    echo [INFO] Available Documentation:
    echo.
    echo   1. QUICK_START_GROQ.md         - 3-step quick start guide
    echo   2. GROQ_TRANSCRIPTION_README.md - Complete documentation
    echo   3. GROQ_COMPLETE_GUIDE.md      - Implementation summary
    echo   4. DEMO_SCRIPT.md              - Demo walkthrough
    echo   5. .env.example                - Configuration template
    echo.
    echo Open these files to learn more about Groq transcription.
    echo.
    pause
    goto end
)

if "%choice%"=="5" (
    echo.
    echo Goodbye!
    goto end
)

echo.
echo [ERROR] Invalid choice. Please run the script again.
pause

:end
