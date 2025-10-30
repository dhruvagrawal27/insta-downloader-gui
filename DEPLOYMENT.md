# Deployment Guide: Instagram Downloader with Groq AI

This guide provides complete step-by-step instructions for deploying the Instagram Downloader application to production.

## Architecture Overview

- **Frontend**: React + TypeScript + Vite (deployed on Vercel)
- **Backend**: FastAPI + Python (deployed on Railway/Render due to Python runtime requirements)

> **Note**: Vercel has limitations with Python serverless functions (25MB limit, cold starts). Railway or Render are recommended for the FastAPI backend.

---

## Prerequisites

1. **Accounts Required**:
   - [GitHub](https://github.com) account (for code hosting)
   - [Vercel](https://vercel.com) account (for frontend)
   - [Railway](https://railway.app) OR [Render](https://render.com) account (for backend)
   - [Groq Cloud](https://console.groq.com) account (for AI transcription)

2. **Local Setup**:
   - Node.js 18+ and npm installed
   - Python 3.11+ installed
   - Git installed and configured

---

## Part 1: Backend Deployment (Railway Recommended)

### Option A: Deploy to Railway (Recommended)

#### Step 1: Prepare Backend Repository

```powershell
# From project root
cd f:\insta-downloader-gui

# Create a new branch for production
git checkout -b production

# Ensure all changes are committed
git add .
git commit -m "Prepare for production deployment"
git push origin production
```

#### Step 2: Create Railway Project

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your `insta-downloader-gui` repository
4. Railway will auto-detect Python and use `requirements.txt`

#### Step 3: Configure Environment Variables

In Railway project settings, add these environment variables:

| Variable Name | Value |
|--------------|-------|
| `GROQ_API_KEY` | Your Groq API key from https://console.groq.com |
| `GROQ_WHISPER_MODEL` | `whisper-large-v3-turbo` |
| `GROQ_PRIMARY_LLM` | `llama-3.3-70b-versatile` |
| `PORT` | `8000` (Railway auto-assigns this) |
| `PYTHON_VERSION` | `3.11.0` |

#### Step 4: Configure Start Command

In Railway project settings → **Settings** → **Start Command**:

```bash
uvicorn api_server:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 300
```

#### Step 5: Deploy

1. Railway will automatically deploy when you push to your branch
2. Wait for deployment to complete (check Logs tab)
3. Copy the generated URL (e.g., `https://your-app.railway.app`)
4. Test health endpoint: `https://your-app.railway.app/health`

---

### Option B: Deploy to Render (Alternative)

#### Step 1: Create render.yaml Configuration

Create `render.yaml` in project root:

```yaml
services:
  - type: web
    name: insta-downloader-api
    env: python
    buildCommand: pip install -r requirements-production.txt
    startCommand: uvicorn api_server:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 300
    envVars:
      - key: GROQ_API_KEY
        sync: false
      - key: GROQ_WHISPER_MODEL
        value: whisper-large-v3-turbo
      - key: GROQ_PRIMARY_LLM
        value: llama-3.3-70b-versatile
      - key: PYTHON_VERSION
        value: 3.11.0
```

#### Step 2: Deploy to Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub repository
4. Select `production` branch
5. Render will auto-detect `render.yaml`
6. Add `GROQ_API_KEY` in environment variables (marked as secret)
7. Click **"Create Web Service"**
8. Copy the generated URL (e.g., `https://your-app.onrender.com`)

---

## Part 2: Frontend Deployment (Vercel)

### Step 1: Update API URL for Production

Update `frontend/.env` or create `frontend/.env.production`:

```env
# Replace with your Railway/Render backend URL
VITE_API_URL=https://your-app.railway.app
```

### Step 2: Update CORS in Backend

Update `api_server.py` to allow your Vercel domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://your-frontend-name.vercel.app",  # Add your specific domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Commit and push this change to trigger a Railway/Render redeploy.

### Step 3: Deploy Frontend to Vercel

#### Option 1: Using Vercel CLI (Recommended)

```powershell
# Install Vercel CLI globally (if not installed)
npm install -g vercel

# Navigate to frontend directory
cd f:\insta-downloader-gui\frontend

# Login to Vercel
vercel login

# Deploy (first time will prompt for configuration)
vercel --prod

# Follow prompts:
# - Set up and deploy? Yes
# - Scope: Your account
# - Link to existing project? No
# - Project name: instagram-downloader
# - Directory: ./ (current directory)
# - Override build settings? No
```

#### Option 2: Using Vercel Dashboard (GUI)

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Configure project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add environment variable:
   - `VITE_API_URL` = `https://your-app.railway.app`
6. Click **"Deploy"**

### Step 4: Verify Deployment

1. Visit your Vercel URL (e.g., `https://instagram-downloader.vercel.app`)
2. Open browser DevTools → Network tab
3. Test download with a sample Instagram URL
4. Verify API calls go to your Railway/Render backend
5. Test Hinglish transcription with enable_hinglish checkbox

---

## Part 3: Post-Deployment Configuration

### Update Backend CORS (Final Step)

Once you have your Vercel URL, update `api_server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://instagram-downloader.vercel.app",  # Your actual Vercel URL
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Commit, push, and let Railway/Render redeploy automatically.

---

## Part 4: Monitoring & Maintenance

### Backend Monitoring (Railway)

1. **Logs**: Railway Dashboard → Your Project → Logs tab
2. **Metrics**: Check CPU, Memory, Network usage
3. **Health Check**: Set up uptime monitoring with UptimeRobot or similar

### Frontend Monitoring (Vercel)

1. **Analytics**: Vercel Dashboard → Your Project → Analytics
2. **Logs**: Runtime Logs tab shows server-side errors
3. **Speed Insights**: Enable in project settings

### Cost Management

| Service | Free Tier | Pricing Beyond Free |
|---------|-----------|---------------------|
| Railway | $5 free credit/month (~500 hours) | $0.000231/GB-hour for RAM |
| Render | 750 hours/month (sleeps after 15 min idle) | $7/month for always-on |
| Vercel | 100GB bandwidth, unlimited builds | $20/month Pro plan |
| Groq | Limited free credits | Pay-as-you-go API pricing |

---

## Part 5: Troubleshooting Common Issues

### Issue 1: CORS Errors in Browser

**Symptoms**: Console shows "CORS policy blocked" errors

**Solution**:
1. Verify backend CORS allows your Vercel domain
2. Check `api_server.py` line 55-64
3. Redeploy backend after updating CORS

### Issue 2: API Timeout Errors

**Symptoms**: Frontend shows "Request timeout" after 5 minutes

**Solution**:
1. Large files or long transcriptions may exceed timeout
2. Railway/Render have 30-second default request timeout
3. Increase in deployment settings or use background jobs

### Issue 3: Groq API Errors

**Symptoms**: Transcription fails with 401/403 errors

**Solution**:
1. Verify `GROQ_API_KEY` is set correctly in Railway/Render
2. Check API key hasn't expired at https://console.groq.com
3. Verify Groq account has available credits

### Issue 4: Download Files Corrupted

**Symptoms**: Downloaded files won't open or wrong size

**Solution**:
1. This was fixed in frontend/src/App.tsx (base64 → Uint8Array)
2. Verify you're running latest code
3. Clear browser cache and retry

### Issue 5: Railway Deployment Fails

**Symptoms**: Build fails with dependency errors

**Solution**:
1. Check `requirements.txt` has all dependencies
2. Verify Python version matches `runtime.txt` (3.11.0)
3. Check Railway logs for specific error messages
4. Try using `requirements-production.txt` (lighter dependencies)

---

## Part 6: Rollback Procedures

### Rollback Backend (Railway)

1. Railway Dashboard → Your Project → Deployments tab
2. Find the last working deployment
3. Click **"..."** → **"Redeploy"**

### Rollback Frontend (Vercel)

1. Vercel Dashboard → Your Project → Deployments tab
2. Find the last working deployment
3. Click **"..."** → **"Promote to Production"**

---

## Part 7: Environment Variables Checklist

### Backend (.env or Railway/Render settings)

```env
✓ GROQ_API_KEY=gsk_xxx...
✓ GROQ_WHISPER_MODEL=whisper-large-v3-turbo
✓ GROQ_PRIMARY_LLM=llama-3.3-70b-versatile
✓ PORT=8000 (auto-set by platform)
```

### Frontend (.env.production or Vercel settings)

```env
✓ VITE_API_URL=https://your-backend.railway.app
```

---

## Success Criteria

After completing all steps, you should have:

✅ Backend API running on Railway/Render with health endpoint accessible  
✅ Frontend running on Vercel with React UI  
✅ CORS properly configured between frontend and backend  
✅ Instagram downloads working (video, audio, thumbnail, caption)  
✅ Hinglish transcription working with Groq AI  
✅ Files downloading correctly without corruption  
✅ Transcripts in Roman script (not Devanagari)  

---

## Quick Reference: Essential URLs

| Resource | URL |
|----------|-----|
| Railway Dashboard | https://railway.app/dashboard |
| Render Dashboard | https://dashboard.render.com |
| Vercel Dashboard | https://vercel.com/dashboard |
| Groq Console | https://console.groq.com |
| Frontend Repo | https://github.com/yourusername/insta-downloader-gui |
| Production Frontend | https://your-app.vercel.app |
| Production Backend | https://your-app.railway.app |
| Backend Health Check | https://your-app.railway.app/health |
| API Docs | https://your-app.railway.app/api/docs |

---

## Support

If you encounter issues not covered in this guide:

1. Check GitHub Issues: https://github.com/dhruvagrawal27/insta-downloader-gui/issues
2. Review Railway/Render/Vercel documentation
3. Check Groq API status: https://status.groq.com
4. Review browser console and network tab for errors

---

**Last Updated**: 2024-01-20  
**Version**: 2.0.0  
**Author**: Dhruv Agrawal
