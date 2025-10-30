# Complete Setup Guide - Instagram Media Downloader v2.0

This guide covers the complete setup for both backend and frontend.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Backend Setup (FastAPI)](#backend-setup)
3. [Frontend Setup (React)](#frontend-setup)
4. [Environment Configuration](#environment-configuration)
5. [Running the Application](#running-the-application)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** (for backend)
- **Node.js 18+** (for frontend)
- **Git** (for cloning)

### One-Command Setup (Windows)

```powershell
# 1. Clone the repository
git clone https://github.com/dhruvagrawal27/insta-downloader-gui.git
cd insta-downloader-gui

# 2. Backend setup
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements-api.txt

# 3. Frontend setup
cd frontend
npm install
cp .env.example .env
cd ..

# 4. Start everything
# Terminal 1 - Backend
python api_server.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

---

## 🔧 Backend Setup

### Option 1: FastAPI Server (Recommended for React Frontend)

The FastAPI server provides REST API endpoints for the React frontend while maintaining all existing functionality.

#### Installation

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements-api.txt
```

#### Running FastAPI Server

```powershell
# Development mode (with auto-reload)
python api_server.py

# Or using uvicorn directly
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

**Access Points:**
- 🏠 API Root: http://localhost:8000/
- 📚 API Docs: http://localhost:8000/api/docs
- 🏥 Health Check: http://localhost:8000/health
- 🎯 Download Endpoint: POST http://localhost:8000/api/download

#### Features
- ✅ RESTful API endpoints
- ✅ CORS enabled for React frontend
- ✅ Automatic API documentation (Swagger UI)
- ✅ Base64 file encoding (no server storage)
- ✅ Groq AI transcription support
- ✅ Automatic fallback between downloaders

---

### Option 2: Streamlit Apps (Original Web Interface)

The Streamlit apps provide a ready-to-use web UI without needing the React frontend.

#### Running Streamlit Apps

```powershell
# Single download mode
streamlit run streamlit_app.py --server.port 8501

# Batch download mode
streamlit run streamlit_batch_app.py --server.port 8502

# Preview mode
streamlit run streamlit_preview_app.py --server.port 8503
```

**Note:** Streamlit apps can work independently but are NOT designed to be API endpoints for the React frontend. Use FastAPI for that purpose.

---

## 🎨 Frontend Setup

### Installation

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env and set backend URL
# VITE_API_URL=http://localhost:8000
```

### Development Server

```powershell
# Start development server
npm run dev

# Opens at http://localhost:3000
```

### Build for Production

```powershell
# Create production build
npm run build

# Preview production build
npm run preview
```

---

## 🔑 Environment Configuration

### Backend Environment Variables

The backend reads Groq API key from environment variables (optional, can be provided per request):

```powershell
# Windows PowerShell
$env:GROQ_API_KEY = "your-groq-api-key-here"

# Windows CMD
set GROQ_API_KEY=your-groq-api-key-here

# Linux/Mac
export GROQ_API_KEY=your-groq-api-key-here
```

Or create a `.env` file in the root directory:

```env
GROQ_API_KEY=your-groq-api-key-here
```

### Frontend Environment Variables

Create `frontend/.env` file:

```env
# Backend API URL
VITE_API_URL=http://localhost:8000

# For production deployment
# VITE_API_URL=https://your-api-domain.com
```

**Important:** Use `.env` (not `.env.local`) for simplicity. Both work, but `.env` is cleaner.

---

## 🏃 Running the Application

### Development Mode (Full Stack)

You need **TWO terminals**:

#### Terminal 1: Backend (FastAPI)
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start FastAPI server
python api_server.py
```

#### Terminal 2: Frontend (React)
```powershell
# Navigate to frontend
cd frontend

# Start development server
npm run dev
```

Then open http://localhost:3000 in your browser.

---

### Production Mode

#### Backend Deployment Options

1. **Railway.app** (Recommended)
   ```yaml
   # railway.toml
   [build]
   builder = "NIXPACKS"
   
   [deploy]
   startCommand = "uvicorn api_server:app --host 0.0.0.0 --port $PORT"
   ```

2. **Render.com**
   - Build Command: `pip install -r requirements-api.txt`
   - Start Command: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`

3. **Heroku**
   ```
   web: uvicorn api_server:app --host 0.0.0.0 --port $PORT
   ```

#### Frontend Deployment (Vercel)

```powershell
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel

# Set environment variable in Vercel dashboard:
# VITE_API_URL = https://your-backend-url.com
```

---

## 🐛 Troubleshooting

### Backend Issues

#### Port Already in Use
```powershell
# Change port
uvicorn api_server:app --reload --port 8001
```

#### Import Errors
```powershell
# Reinstall dependencies
pip install --upgrade -r requirements-api.txt
```

#### CORS Errors
- Check that `VITE_API_URL` in frontend `.env` matches backend URL
- Ensure FastAPI CORS middleware includes your frontend URL

### Frontend Issues

#### Dependencies Not Installing
```powershell
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### API Connection Failed
1. Check backend is running: http://localhost:8000/health
2. Verify `VITE_API_URL` in `.env` file
3. Check browser console for CORS errors

#### Build Errors
```powershell
# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

### Common Issues

#### "Module not found" errors
```powershell
# Backend: Activate virtual environment
.\venv\Scripts\Activate.ps1

# Frontend: Reinstall dependencies
cd frontend
npm install
```

#### Transcription not working
- Ensure Groq API key is set (in request or environment)
- Check `transcribe` option is enabled
- Verify internet connection

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Browser                          │
│                    http://localhost:3000                     │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ HTTP Requests
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   React Frontend (Vite)                      │
│  • Beautiful gradient UI                                     │
│  • Dark mode support                                         │
│  • State management (Zustand)                                │
│  • No local file storage                                     │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ REST API Calls
                            │ POST /api/download
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI Backend Server                       │
│                  http://localhost:8000                       │
│  • REST API endpoints                                        │
│  • CORS enabled                                              │
│  • Auto documentation                                        │
│  • File → Base64 conversion                                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ Uses
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Core Download Logic                         │
│  • yt-dlp agent                                              │
│  • Instaloader agent                                         │
│  • Session manager                                           │
│  • Audio transcriber (Whisper + Groq)                        │
│  • URL validator                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📚 Additional Resources

- **Frontend Documentation:** `frontend/README.md`
- **Quick Start Guide:** `frontend/QUICKSTART.md`
- **API Integration:** `INTEGRATION_GUIDE.md`
- **Main Documentation:** `docs/README.md`
- **Usage Guide:** `docs/USAGE.md`
- **Changelog:** `docs/CHANGELOG.md`

---

## 💡 Tips

1. **Always activate virtual environment** before running backend
2. **Use `.env` for environment variables** (simpler than `.env.local`)
3. **Run backend on port 8000** and frontend on 3000 for consistency
4. **Check API docs** at `/api/docs` for endpoint testing
5. **Use yt-dlp as default downloader** (more reliable for Instagram)

---

## 🆘 Need Help?

1. Check the [Troubleshooting](#troubleshooting) section
2. Read the error message carefully
3. Check backend logs in terminal
4. Check browser console for frontend errors
5. Verify all environment variables are set correctly

---

**Version:** 2.0.0  
**Author:** Dhruv Agrawal  
**Repository:** https://github.com/dhruvagrawal27/insta-downloader-gui  
**License:** MIT
