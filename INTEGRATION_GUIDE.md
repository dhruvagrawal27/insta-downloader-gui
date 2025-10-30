# 🔗 Frontend-Backend Integration Guide

Complete guide for connecting the React frontend to your Streamlit backend.

## 📋 Overview

**Architecture:**
```
React Frontend (Vercel) → API Calls → Streamlit Backend (Streamlit Cloud)
     Port: 3000                             Port: 8502
     (or Vercel URL)                        (or deployed URL)
```

## 🎯 Backend API Requirements

Your Streamlit backend needs to expose an API endpoint that the React frontend can call. Here's how to set it up:

### Step 1: Install Streamlit API Extension

```bash
pip install streamlit-server-state
```

### Step 2: Create API Endpoint in Your Streamlit App

Add this to your `streamlit_preview_app.py` or create a new `api.py`:

```python
import streamlit as st
from streamlit.web import cli as stcli
import sys
import json
from pathlib import Path

# Enable CORS for API calls
def enable_cors():
    """Enable CORS for API endpoints"""
    st.set_page_config(
        page_title="Instagram Downloader API",
        page_icon="📱",
    )
    # Add CORS headers
    st.markdown("""
        <script>
        // Allow CORS
        </script>
    """, unsafe_allow_html=True)

# API Endpoint Handler
def handle_api_request():
    """Handle API requests from React frontend"""
    
    # Get request data
    query_params = st.query_params
    
    if 'api' in query_params and query_params['api'] == 'download':
        # Get POST data from session state
        if 'api_request' in st.session_state:
            request_data = st.session_state.api_request
            
            # Process download
            result = process_download_request(request_data)
            
            # Return JSON response
            st.json(result)
            return True
    
    return False

def process_download_request(data):
    """Process download request and return media files"""
    try:
        from src.core.downloader import PreviewDownloader
        from src.core.groq_transcriber import GroqTranscriber
        import base64
        
        # Extract parameters
        url = data.get('url')
        downloader_type = data.get('downloader', 'yt-dlp')
        groq_api_key = data.get('groqApiKey')
        
        # Initialize downloader
        downloader = PreviewDownloader(downloader=downloader_type)
        
        # Download media
        result = downloader.download(
            url=url,
            download_video=data.get('downloadVideo', True),
            download_thumbnail=data.get('downloadThumbnail', True),
            download_audio=data.get('downloadAudio', False),
            download_caption=data.get('downloadCaption', True),
        )
        
        if not result['success']:
            return {
                'success': False,
                'error': result.get('error', 'Download failed'),
                'files': []
            }
        
        # Prepare files for response
        files = []
        for file_type, file_path in result['files'].items():
            if file_path and Path(file_path).exists():
                with open(file_path, 'rb') as f:
                    file_data = base64.b64encode(f.read()).decode('utf-8')
                
                file_info = {
                    'type': file_type,
                    'data': file_data,
                    'filename': Path(file_path).name,
                    'size': Path(file_path).stat().st_size,
                    'mimeType': get_mime_type(file_type)
                }
                files.append(file_info)
        
        # Transcription if requested
        transcript = None
        if data.get('transcribe') and groq_api_key and result.get('audio_path'):
            try:
                transcriber = GroqTranscriber(api_key=groq_api_key)
                transcript_result = transcriber.transcribe_and_process(
                    audio_path=result['audio_path'],
                    enable_post_processing=data.get('enableHinglish', True)
                )
                transcript = transcript_result.get('final_transcription')
            except Exception as e:
                print(f"Transcription error: {e}")
        
        return {
            'success': True,
            'files': files,
            'caption': result.get('caption'),
            'transcript': transcript
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'files': []
        }

def get_mime_type(file_type):
    """Get MIME type for file type"""
    mime_types = {
        'video': 'video/mp4',
        'audio': 'audio/mpeg',
        'thumbnail': 'image/jpeg',
        'caption': 'text/plain',
        'transcript': 'text/plain'
    }
    return mime_types.get(file_type, 'application/octet-stream')

# Main app
if __name__ == "__main__":
    enable_cors()
    
    # Check if API request
    if handle_api_request():
        sys.exit(0)
    
    # Otherwise, show normal Streamlit UI
    st.title("Instagram Downloader API")
    st.write("API is running!")
```

### Step 3: Alternative - Use FastAPI Wrapper

For better API support, create a FastAPI wrapper:

```python
# api_server.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
from pathlib import Path
from src.core.downloader import PreviewDownloader
from src.core.groq_transcriber import GroqTranscriber

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DownloadRequest(BaseModel):
    url: str
    downloadVideo: bool = True
    downloadThumbnail: bool = True
    downloadAudio: bool = False
    downloadCaption: bool = True
    transcribe: bool = False
    groqApiKey: str = None
    enableHinglish: bool = True
    downloader: str = "yt-dlp"

@app.post("/download")
async def download_media(request: DownloadRequest):
    try:
        # Initialize downloader
        downloader = PreviewDownloader(downloader=request.downloader)
        
        # Download media
        result = downloader.download(
            url=request.url,
            download_video=request.downloadVideo,
            download_thumbnail=request.downloadThumbnail,
            download_audio=request.downloadAudio,
            download_caption=request.downloadCaption,
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error', 'Download failed'))
        
        # Prepare files
        files = []
        for file_type, file_path in result['files'].items():
            if file_path and Path(file_path).exists():
                with open(file_path, 'rb') as f:
                    file_data = base64.b64encode(f.read()).decode('utf-8')
                
                files.append({
                    'type': file_type,
                    'data': file_data,
                    'filename': Path(file_path).name,
                    'size': Path(file_path).stat().st_size,
                    'mimeType': get_mime_type(file_type)
                })
        
        # Transcription
        transcript = None
        if request.transcribe and request.groqApiKey and result.get('audio_path'):
            transcriber = GroqTranscriber(api_key=request.groqApiKey)
            transcript_result = transcriber.transcribe_and_process(
                audio_path=result['audio_path'],
                enable_post_processing=request.enableHinglish
            )
            transcript = transcript_result.get('final_transcription')
        
        return {
            'success': True,
            'files': files,
            'caption': result.get('caption'),
            'transcript': transcript
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

def get_mime_type(file_type):
    mime_types = {
        'video': 'video/mp4',
        'audio': 'audio/mpeg',
        'thumbnail': 'image/jpeg',
        'caption': 'text/plain',
        'transcript': 'text/plain'
    }
    return mime_types.get(file_type, 'application/octet-stream')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8502)
```

Install FastAPI:
```bash
pip install fastapi uvicorn
```

Run:
```bash
python api_server.py
```

## 🔧 Frontend Configuration

Update `.env.local` in frontend:

### Development
```env
VITE_API_URL=http://localhost:8502
```

### Production
```env
VITE_API_URL=https://your-backend.streamlit.app
```

Or FastAPI:
```env
VITE_API_URL=https://your-api.herokuapp.com
```

## 🚀 Deployment Options

### Option 1: Streamlit + Vercel

1. **Deploy Backend to Streamlit Cloud**:
   - Push code to GitHub
   - Connect to Streamlit Cloud
   - Deploy

2. **Deploy Frontend to Vercel**:
   - `cd frontend && vercel`
   - Set `VITE_API_URL` to Streamlit URL

### Option 2: FastAPI + Vercel

1. **Deploy Backend to Railway/Heroku**:
   ```bash
   # Heroku
   heroku create your-api
   git push heroku main
   ```

2. **Deploy Frontend to Vercel**:
   - Set `VITE_API_URL` to Railway/Heroku URL

### Option 3: All-in-One

Deploy everything on Railway:
- Backend on port 8502
- Frontend on port 3000

## 🧪 Testing Integration

### 1. Test Backend Locally

```bash
# Terminal 1: Start backend
python api_server.py

# Terminal 2: Test API
curl -X POST http://localhost:8502/download \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://instagram.com/reel/...",
    "downloadVideo": true
  }'
```

### 2. Test Frontend Locally

```bash
cd frontend
npm run dev
```

Open http://localhost:3000 and test download.

### 3. Test CORS

Check browser console for CORS errors. If present:
- Add your frontend URL to `allow_origins` in FastAPI
- Or enable CORS in Streamlit

## 🐛 Troubleshooting

### CORS Errors

**FastAPI Solution**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Large File Sizes

Files are base64 encoded, which increases size by ~33%. For large videos:

1. **Option 1**: Return pre-signed URLs instead of base64
2. **Option 2**: Compress before encoding
3. **Option 3**: Stream files directly

### Memory Issues

Vercel has memory limits. For large files:
- Use file streaming
- Implement chunked downloads
- Set size limits

## 📝 API Contract

### Request Format

```typescript
interface DownloadRequest {
  url: string
  downloadVideo: boolean
  downloadThumbnail: boolean
  downloadAudio: boolean
  downloadCaption: boolean
  transcribe: boolean
  groqApiKey?: string
  enableHinglish?: boolean
  downloader: 'yt-dlp' | 'instaloader'
}
```

### Response Format

```typescript
interface DownloadResponse {
  success: boolean
  files: Array<{
    type: 'video' | 'audio' | 'thumbnail' | 'caption' | 'transcript'
    data: string  // base64
    filename: string
    size: number
    mimeType: string
  }>
  caption?: string
  transcript?: string
  error?: string
}
```

## ✅ Production Checklist

- [ ] Backend API deployed and accessible
- [ ] CORS configured correctly
- [ ] Environment variables set in Vercel
- [ ] API endpoints tested
- [ ] Error handling implemented
- [ ] Rate limiting configured
- [ ] Monitoring set up
- [ ] SSL/HTTPS enabled

---

**Need Help?** Open an issue on GitHub!
