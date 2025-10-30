@echo off
echo ========================================
echo  Instagram Downloader - React Frontend
echo  Quick Setup Script
echo ========================================
echo.

echo [1/3] Navigating to frontend directory...
cd frontend
if errorlevel 1 (
    echo ERROR: frontend directory not found!
    pause
    exit /b 1
)

echo [2/3] Installing dependencies...
echo This may take 2-3 minutes...
call npm install
if errorlevel 1 (
    echo ERROR: npm install failed!
    pause
    exit /b 1
)

echo [3/3] Setting up environment...
if not exist .env.local (
    copy .env.example .env.local
    echo Created .env.local file
) else (
    echo .env.local already exists
)

echo.
echo ========================================
echo  Setup Complete! 
echo ========================================
echo.
echo Next steps:
echo   1. Edit frontend\.env.local with your backend URL
echo   2. Run: cd frontend && npm run dev
echo   3. Open: http://localhost:3000
echo.
echo To deploy to Vercel:
echo   1. npm i -g vercel
echo   2. cd frontend && vercel
echo.
pause
