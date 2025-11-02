"""
FastAPI Backend for Instagram Media Downloader

This is a REST API server that works alongside the Streamlit apps.
It provides API endpoints for the React frontend while keeping all existing functionality.

Author: Dhruv Agrawal
Version: 2.0.0
License: MIT
Repository: https://github.com/dhruvagrawal27/insta-downloader-gui
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import base64
import tempfile
from pathlib import Path
import mimetypes
import os
import warnings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Suppress warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Import existing core functionality
from src.core.data_models import ReelItem
from src.core.session_manager import SessionManager
from src.utils.url_validator import is_valid_instagram_url
from src.agents import instaloader as instaloader_agent
from src.agents import yt_dlp as yt_dlp_agent
from src.core.transcriber import AudioTranscriber
from src.core.groq_transcriber import GroqTranscriber
from src.utils.lazy_imports import lazy_import_instaloader

# Initialize FastAPI app
app = FastAPI(
    title="Instagram Media Downloader API",
    description="REST API for downloading Instagram media with AI transcription",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "https://*.vercel.app",   # All Vercel deployments
        "https://instagram-downloader.vercel.app",  # Your production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Pydantic Models for Request/Response
# ============================================================================

class DownloadRequest(BaseModel):
    """Request model for download endpoint."""
    url: str = Field(..., description="Instagram post/reel URL")
    video: bool = Field(True, description="Download video file")
    thumbnail: bool = Field(True, description="Download thumbnail image")
    audio: bool = Field(True, description="Extract audio from video")
    caption: bool = Field(True, description="Save post caption")
    transcribe: bool = Field(False, description="Transcribe audio using Whisper AI")
    enable_hinglish: bool = Field(False, description="Enable Hinglish translation")
    downloader: str = Field("yt-dlp", description="Preferred downloader: 'yt-dlp' or 'Instaloader'")


class MediaFile(BaseModel):
    """Model for media file in response."""
    type: str = Field(..., description="File type: video, thumbnail, audio, caption, transcript")
    data: str = Field(..., description="Base64 encoded file data")
    filename: str = Field(..., description="Original filename")
    size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type of the file")


class DownloadResponse(BaseModel):
    """Response model for download endpoint."""
    success: bool
    files: List[MediaFile] = []
    caption: Optional[str] = None
    transcript: Optional[str] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    message: str


# ============================================================================
# Downloader Class
# ============================================================================

class APIDownloader:
    """API-compatible downloader class."""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.audio_transcriber = AudioTranscriber()
        self.groq_transcriber = None  # Initialize only when needed
        self.loader = None
        
    def setup_instaloader(self):
        """Initialize Instaloader instance."""
        if self.loader is None:
            instaloader_module = lazy_import_instaloader()
            self.loader = instaloader_module.Instaloader(
                download_video_thumbnails=True,
                download_comments=False,
                save_metadata=False,
                compress_json=False,
                dirname_pattern=str(self.session_manager.get_session_folder()),
            )
    
    def file_to_base64(self, file_path: Path) -> str:
        """Convert file to base64 string."""
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    def get_mime_type(self, file_path: Path) -> str:
        """Get MIME type for file."""
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type or "application/octet-stream"
    
    def create_media_file(self, file_path: Path, file_type: str) -> MediaFile:
        """Create MediaFile object from file path."""
        if not file_path or not Path(file_path).exists():
            return None
        
        file_path = Path(file_path)
        return MediaFile(
            type=file_type,
            data=self.file_to_base64(file_path),
            filename=file_path.name,
            size=file_path.stat().st_size,
            mime_type=self.get_mime_type(file_path)
        )
    
    def download_reel(self, url: str, options: Dict[str, Any]) -> DownloadResponse:
        """Download a reel with the given options."""
        try:
            # Setup session folder
            self.session_manager.setup_session_folder()
            
            if options.get("downloader", "yt-dlp") == "Instaloader":
                self.setup_instaloader()
            
            reel_item = ReelItem(url=url)
            
            # Attempt download with primary downloader
            try:
                if options.get("downloader", "yt-dlp") == "Instaloader":
                    result = instaloader_agent.download_reel(
                        reel_item, 1, self.session_manager.get_session_folder(),
                        self.loader, options, lambda url, progress, status: None
                    )
                else:
                    result = yt_dlp_agent.download_reel(
                        reel_item, 1, self.session_manager.get_session_folder(),
                        options, lambda url, progress, status: None
                    )
            except Exception as e:
                # Try fallback downloader
                if options.get("downloader", "yt-dlp") == "Instaloader":
                    result = yt_dlp_agent.download_reel(
                        reel_item, 1, self.session_manager.get_session_folder(),
                        options, lambda url, progress, status: None
                    )
                else:
                    self.setup_instaloader()
                    result = instaloader_agent.download_reel(
                        reel_item, 1, self.session_manager.get_session_folder(),
                        self.loader, options, lambda url, progress, status: None
                    )
            
            # Handle transcription if enabled
            if options.get("transcribe", False):
                try:
                    reel_folder = Path(result["folder_path"])
                    
                    # Use Groq transcriber if Hinglish is enabled
                    if options.get("enable_hinglish", False):
                        # Initialize Groq transcriber if not already done
                        if not self.groq_transcriber:
                            self.groq_transcriber = GroqTranscriber()
                        
                        # Transcribe with Groq (includes Hinglish post-processing)
                        self.groq_transcriber.transcribe_audio_from_reel(
                            reel_folder, 1, result, 
                            lambda url, progress, status: None,
                            enable_post_processing=True
                        )
                    else:
                        # Use basic Whisper transcription (no Hinglish processing)
                        self.audio_transcriber.load_whisper_model()
                        self.audio_transcriber.transcribe_audio_from_reel(
                            reel_folder, 1, result, lambda url, progress, status: None
                        )
                except Exception as e:
                    error_msg = f"Transcription failed: {str(e)}"
                    result["transcript_error"] = error_msg
                    result["transcript"] = error_msg
                    print(f"[ERROR] {error_msg}")
                    import traceback
                    traceback.print_exc()
            
            # Convert files to base64 for API response
            files = []
            
            if result.get('video_path') and options.get('video', True):
                media_file = self.create_media_file(Path(result['video_path']), "video")
                if media_file:
                    files.append(media_file)
            
            if result.get('thumbnail_path') and options.get('thumbnail', True):
                media_file = self.create_media_file(Path(result['thumbnail_path']), "thumbnail")
                if media_file:
                    files.append(media_file)
            
            if result.get('audio_path') and options.get('audio', True):
                media_file = self.create_media_file(Path(result['audio_path']), "audio")
                if media_file:
                    files.append(media_file)
            
            if result.get('caption_path') and options.get('caption', True):
                media_file = self.create_media_file(Path(result['caption_path']), "caption")
                if media_file:
                    files.append(media_file)
            
            if result.get('transcript_path') and options.get('transcribe', False):
                media_file = self.create_media_file(Path(result['transcript_path']), "transcript")
                if media_file:
                    files.append(media_file)
            
            # Extract caption and transcript text
            caption_text = result.get('caption', None)
            transcript_text = result.get('transcript', None)
            
            # Note: Session folder cleanup handled by OS temp cleanup
            # Files are already converted to base64 for API response
            
            return DownloadResponse(
                success=True,
                files=files,
                caption=caption_text,
                transcript=transcript_text
            )
            
        except Exception as e:
            return DownloadResponse(
                success=False,
                error=str(e)
            )


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - API info."""
    return HealthResponse(
        status="online",
        version="2.0.0",
        message="Instagram Media Downloader API is running. Visit /api/docs for documentation."
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        message="API is operational"
    )


@app.post("/api/download", response_model=DownloadResponse)
async def download_media(request: DownloadRequest):
    """
    Download Instagram media endpoint.
    
    Args:
        request: DownloadRequest with URL and options
        
    Returns:
        DownloadResponse with files as base64 or error message
    """
    # Validate URL
    if not request.url or not request.url.strip():
        raise HTTPException(status_code=400, detail="URL is required")
    
    if not is_valid_instagram_url(request.url.strip()):
        raise HTTPException(status_code=400, detail="Invalid Instagram URL")
    
    # Validate transcription requirements (Groq API key from .env)
    if request.transcribe and request.enable_hinglish:
        if not os.getenv("GROQ_API_KEY"):
            raise HTTPException(
                status_code=400, 
                detail="Groq API key not found in environment. Please set GROQ_API_KEY in .env file"
            )
    
    # Prepare options
    options = {
        "video": request.video,
        "thumbnail": request.thumbnail,
        "audio": request.audio,
        "caption": request.caption,
        "transcribe": request.transcribe,
        "enable_hinglish": request.enable_hinglish,
        "downloader": request.downloader
    }
    
    # Initialize downloader and process
    downloader = APIDownloader()
    response = downloader.download_reel(request.url.strip(), options)
    
    if not response.success:
        raise HTTPException(status_code=500, detail=response.error)
    
    return response


@app.get("/api/validate-url")
async def validate_url(url: str):
    """
    Validate Instagram URL endpoint.
    
    Args:
        url: Instagram URL to validate
        
    Returns:
        JSON with validation result
    """
    if not url or not url.strip():
        return JSONResponse(
            status_code=400,
            content={"valid": False, "message": "URL is required"}
        )
    
    is_valid = is_valid_instagram_url(url.strip())
    
    return {
        "valid": is_valid,
        "message": "Valid Instagram URL" if is_valid else "Invalid Instagram URL"
    }


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 80)
    print("🚀 Starting Instagram Media Downloader API Server")
    print("=" * 80)
    print("📡 API Documentation: http://localhost:8000/api/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    print("🎯 Endpoint: POST http://localhost:8000/api/download")
    print("=" * 80)
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        timeout_keep_alive=300,  # 5 minutes for long transcriptions
    )
