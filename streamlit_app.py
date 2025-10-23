"""
Instagram Media Downloader - Streamlit Web Application

A web-based version of the Instagram media downloader using Streamlit.
This application allows users to download Instagram Reels, posts, and associated media
through a user-friendly web interface.

Author: ukr
Version: 1.0.0
License: MIT
"""

import streamlit as st
import os
import tempfile
import zipfile
import io
from pathlib import Path
from typing import List, Dict, Any
import asyncio
import threading
import time
from datetime import datetime
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Import your existing core functionality
from src.core.data_models import ReelItem
from src.core.session_manager import SessionManager
from src.utils.url_validator import is_valid_instagram_url
from src.agents import instaloader as instaloader_agent
from src.agents import yt_dlp as yt_dlp_agent
from src.core.transcriber import AudioTranscriber
from src.utils.lazy_imports import lazy_import_instaloader


class StreamlitDownloader:
    """Streamlit-compatible downloader class."""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.audio_transcriber = AudioTranscriber()
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
    
    def download_single_reel(self, url: str, options: Dict[str, Any], progress_callback=None) -> Dict[str, Any]:
        """Download a single reel with the given options."""
        self.session_manager.setup_session_folder()
        
        if options.get("downloader", "Instaloader") == "Instaloader":
            self.setup_instaloader()
        
        reel_item = ReelItem(url=url)
        
        # Attempt download with primary downloader
        try:
            if options.get("downloader", "Instaloader") == "Instaloader":
                if progress_callback:
                    progress_callback("Starting download with Instaloader...")
                result = instaloader_agent.download_reel(
                    reel_item, 1, self.session_manager.get_session_folder(),
                    self.loader, options, lambda url, progress, status: progress_callback(status)
                )
            else:
                if progress_callback:
                    progress_callback("Starting download with yt-dlp...")
                result = yt_dlp_agent.download_reel(
                    reel_item, 1, self.session_manager.get_session_folder(),
                    options, lambda url, progress, status: progress_callback(status)
                )
            
            # Handle transcription if enabled
            if options.get("transcribe", False):
                if progress_callback:
                    progress_callback("Transcribing audio...")
                try:
                    self.audio_transcriber.load_whisper_model()
                    reel_folder = Path(result["folder_path"])
                    self.audio_transcriber.transcribe_audio_from_reel(
                        reel_folder, 1, result, lambda url, progress, status: progress_callback(status)
                    )
                except Exception as e:
                    result["transcript_error"] = str(e)
            
            return result
            
        except Exception as e:
            # Try fallback downloader
            try:
                if options.get("downloader", "Instaloader") == "Instaloader":
                    if progress_callback:
                        progress_callback("Instaloader failed, trying yt-dlp...")
                    result = yt_dlp_agent.download_reel(
                        reel_item, 1, self.session_manager.get_session_folder(),
                        options, lambda url, progress, status: progress_callback(status)
                    )
                else:
                    if progress_callback:
                        progress_callback("yt-dlp failed, trying Instaloader...")
                    self.setup_instaloader()
                    result = instaloader_agent.download_reel(
                        reel_item, 1, self.session_manager.get_session_folder(),
                        self.loader, options, lambda url, progress, status: progress_callback(status)
                    )
                
                return result
                
            except Exception as e2:
                raise Exception(f"Both downloaders failed: {str(e)} | {str(e2)}")


def init_streamlit_config():
    """Initialize Streamlit page configuration."""
    st.set_page_config(
        page_title="Instagram Media Downloader",
        page_icon="📱",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def render_header():
    """Render the application header."""
    st.title("📱 Instagram Media Downloader")
    st.markdown("""
    <div style="background: linear-gradient(90deg, #833ab4, #fd1d1d, #fcb045); 
                padding: 1rem; border-radius: 10px; margin-bottom: 2rem;">
        <h3 style="color: white; text-align: center; margin: 0;">
            Download Instagram Reels, Videos, Audio, and More!
        </h3>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with download options."""
    st.sidebar.header("⚙️ Download Options")
    
    # Downloader selection - Default to yt-dlp for better reliability with Instagram
    downloader = st.sidebar.selectbox(
        "🔧 Preferred Downloader",
        ["yt-dlp", "Instaloader"],
        help="yt-dlp is more reliable for Instagram. Instaloader may face API restrictions."
    )
    
    st.sidebar.subheader("📥 What to Download")
    
    # Download options
    video = st.sidebar.checkbox("📹 Video", value=True, help="Download the video file")
    thumbnail = st.sidebar.checkbox("🖼️ Thumbnail", value=True, help="Download the thumbnail image")
    audio = st.sidebar.checkbox("🎵 Audio", value=True, help="Extract and save audio from video")
    caption = st.sidebar.checkbox("📝 Caption", value=True, help="Save post caption/description")
    transcribe = st.sidebar.checkbox("🎤 Transcribe Audio", value=False, 
                                   help="Generate transcript using AI (takes longer)")
    
    if transcribe:
        st.sidebar.warning("⚠️ Transcription requires additional processing time and resources.")
    
    return {
        "downloader": downloader,
        "video": video,
        "thumbnail": thumbnail,
        "audio": audio,
        "caption": caption,
        "transcribe": transcribe
    }


def create_download_package(result: Dict[str, Any]) -> bytes:
    """Create a zip file containing all downloaded files."""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        folder_path = Path(result.get("folder_path", ""))
        
        if folder_path.exists():
            for file_path in folder_path.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(folder_path.parent)
                    zip_file.write(file_path, arcname)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def display_download_results(result: Dict[str, Any]):
    """Display the download results in the main area."""
    st.success("✅ Download completed successfully!")
    
    # Display basic info
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Download Summary")
        st.write(f"**Title:** {result.get('title', 'N/A')}")
        st.write(f"**Folder:** {result.get('folder_path', 'N/A')}")
        
        # Show what was downloaded
        downloaded_items = []
        if result.get('video_path'):
            downloaded_items.append("📹 Video")
        if result.get('thumbnail_path'):
            downloaded_items.append("🖼️ Thumbnail")
        if result.get('audio_path'):
            downloaded_items.append("🎵 Audio")
        if result.get('caption_path'):
            downloaded_items.append("📝 Caption")
        if result.get('transcript_path'):
            downloaded_items.append("🎤 Transcript")
        
        st.write("**Downloaded:**")
        for item in downloaded_items:
            st.write(f"- {item}")
    
    with col2:
        st.subheader("📁 Files")
        
        # Display file paths
        if result.get('video_path'):
            st.code(f"Video: {result['video_path']}")
        if result.get('thumbnail_path'):
            st.code(f"Thumbnail: {result['thumbnail_path']}")
        if result.get('audio_path'):
            st.code(f"Audio: {result['audio_path']}")
        if result.get('caption_path'):
            st.code(f"Caption: {result['caption_path']}")
        if result.get('transcript_path'):
            st.code(f"Transcript: {result['transcript_path']}")
    
    # Show content previews
    if result.get('caption'):
        st.subheader("📝 Caption")
        st.text_area(
            label="Caption Content", 
            value=result['caption'], 
            height=100, 
            disabled=True,
            label_visibility="collapsed"
        )
    
    if result.get('transcript'):
        st.subheader("🎤 Transcript")
        st.text_area(
            label="Transcript Content", 
            value=result['transcript'], 
            height=150, 
            disabled=True,
            label_visibility="collapsed"
        )
    
    # Download package button
    try:
        zip_data = create_download_package(result)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"instagram_download_{timestamp}.zip"
        
        st.download_button(
            label="📦 Download All Files (ZIP)",
            data=zip_data,
            file_name=filename,
            mime="application/zip",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error creating download package: {str(e)}")


def main():
    """Main Streamlit application."""
    init_streamlit_config()
    render_header()
    
    # Get download options from sidebar
    options = render_sidebar()
    
    # Main content area
    st.subheader("🔗 Enter Instagram URL")
    
    # URL input
    url_input = st.text_input(
        "Paste your Instagram Reel or Post URL here:",
        placeholder="https://www.instagram.com/reel/...",
        help="Supports Instagram Reels and Posts"
    )
    
    # Download button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        download_btn = st.button("🚀 Start Download", use_container_width=True, type="primary")
    
    # Handle download
    if download_btn:
        if not url_input.strip():
            st.error("❌ Please enter an Instagram URL")
            return
        
        if not is_valid_instagram_url(url_input.strip()):
            st.error("❌ Please enter a valid Instagram URL")
            return
        
        # Initialize progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Initialize downloader
            downloader = StreamlitDownloader()
            
            # Progress callback
            def update_progress(message):
                status_text.text(f"⏳ {message}")
            
            # Start download
            with st.spinner("Initializing download..."):
                result = downloader.download_single_reel(
                    url_input.strip(), 
                    options, 
                    progress_callback=update_progress
                )
            
            # Clear progress indicators
            progress_bar.progress(100)
            status_text.text("✅ Download completed!")
            
            # Display results
            display_download_results(result)
            
        except Exception as e:
            st.error(f"❌ Download failed: {str(e)}")
            st.info("💡 Try switching to a different downloader in the sidebar options.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: gray; font-size: 0.8em;">
        <p>Instagram Media Downloader | Web Version | Built with Streamlit</p>
        <p>⚠️ Please respect content creators' rights and Instagram's terms of service</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
