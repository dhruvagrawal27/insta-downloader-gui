"""
Multi-URL Instagram Downloader - Streamlit Web Application

Enhanced version that supports batch downloading multiple URLs.
"""

import streamlit as st
import os
import tempfile
import zipfile
import io
from pathlib import Path
from typing import List, Dict, Any
import threading
import time
from datetime import datetime
import queue
import uuid
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


class BatchDownloader:
    """Streamlit-compatible batch downloader class."""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.audio_transcriber = AudioTranscriber()
        self.loader = None
        self.progress_queue = queue.Queue()
        self.results = []
        
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
    
    def download_batch(self, urls: List[str], options: Dict[str, Any]):
        """Download multiple URLs in batch."""
        self.session_manager.setup_session_folder()
        
        if options.get("downloader", "Instaloader") == "Instaloader":
            self.setup_instaloader()
        
        # Load transcription model if needed
        if options.get("transcribe", False):
            self.progress_queue.put(("", 0, "Loading transcription model..."))
            self.audio_transcriber.load_whisper_model()
        
        total_urls = len(urls)
        
        for i, url in enumerate(urls, 1):
            try:
                self.progress_queue.put((url, 0, f"Processing {i}/{total_urls}: Starting download..."))
                
                reel_item = ReelItem(url=url)
                
                # Try primary downloader
                try:
                    if options.get("downloader", "Instaloader") == "Instaloader":
                        result = instaloader_agent.download_reel(
                            reel_item, i, self.session_manager.get_session_folder(),
                            self.loader, options, 
                            lambda url, progress, status: self.progress_queue.put((url, progress, status))
                        )
                    else:
                        result = yt_dlp_agent.download_reel(
                            reel_item, i, self.session_manager.get_session_folder(),
                            options, 
                            lambda url, progress, status: self.progress_queue.put((url, progress, status))
                        )
                except Exception as e:
                    # Try fallback downloader
                    self.progress_queue.put((url, 0, f"Primary downloader failed, trying fallback..."))
                    
                    if options.get("downloader", "Instaloader") == "Instaloader":
                        result = yt_dlp_agent.download_reel(
                            reel_item, i, self.session_manager.get_session_folder(),
                            options, 
                            lambda url, progress, status: self.progress_queue.put((url, progress, status))
                        )
                    else:
                        self.setup_instaloader()
                        result = instaloader_agent.download_reel(
                            reel_item, i, self.session_manager.get_session_folder(),
                            self.loader, options, 
                            lambda url, progress, status: self.progress_queue.put((url, progress, status))
                        )
                
                # Handle transcription
                if options.get("transcribe", False):
                    self.progress_queue.put((url, 90, "Transcribing audio..."))
                    try:
                        reel_folder = Path(result["folder_path"])
                        self.audio_transcriber.transcribe_audio_from_reel(
                            reel_folder, i, result, 
                            lambda url, progress, status: self.progress_queue.put((url, progress, status))
                        )
                    except Exception as e:
                        result["transcript_error"] = str(e)
                
                result["url"] = url
                result["status"] = "completed"
                self.results.append(result)
                self.progress_queue.put((url, 100, "Completed"))
                
            except Exception as e:
                error_result = {
                    "url": url,
                    "status": "error",
                    "error": str(e)
                }
                self.results.append(error_result)
                self.progress_queue.put((url, 0, f"Error: {str(e)}"))
        
        self.progress_queue.put(("", 100, "Batch download completed!"))


def init_streamlit_config():
    """Initialize Streamlit page configuration."""
    st.set_page_config(
        page_title="Instagram Batch Downloader",
        page_icon="📱",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def render_header():
    """Render the application header."""
    st.title("📱 Instagram Batch Media Downloader")
    st.markdown("""
    <div style="background: linear-gradient(90deg, #833ab4, #fd1d1d, #fcb045); 
                padding: 1rem; border-radius: 10px; margin-bottom: 2rem;">
        <h3 style="color: white; text-align: center; margin: 0;">
            Download Multiple Instagram Reels and Posts at Once!
        </h3>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with download options."""
    st.sidebar.header("⚙️ Download Options")
    
    # Downloader selection
    downloader = st.sidebar.selectbox(
        "🔧 Preferred Downloader",
        ["Instaloader", "yt-dlp"],
        help="Choose your preferred download engine. The app will fallback to the other if the first fails."
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
    
    # Batch options
    st.sidebar.subheader("📦 Batch Options")
    max_concurrent = st.sidebar.slider("Max Concurrent Downloads", 1, 5, 2)
    
    return {
        "downloader": downloader,
        "video": video,
        "thumbnail": thumbnail,
        "audio": audio,
        "caption": caption,
        "transcribe": transcribe,
        "max_concurrent": max_concurrent
    }


def parse_urls(text: str) -> List[str]:
    """Parse URLs from text input."""
    lines = text.strip().split('\n')
    urls = []
    
    for line in lines:
        line = line.strip()
        if line and is_valid_instagram_url(line):
            urls.append(line)
    
    return urls


def create_batch_download_package(results: List[Dict[str, Any]]) -> bytes:
    """Create a zip file containing all downloaded files from batch."""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for result in results:
            if result.get("status") == "completed":
                folder_path = Path(result.get("folder_path", ""))
                
                if folder_path.exists():
                    for file_path in folder_path.rglob("*"):
                        if file_path.is_file():
                            # Create a unique path within the zip
                            url_hash = str(hash(result["url"]))[-8:]
                            arcname = f"{url_hash}_{folder_path.name}/{file_path.relative_to(folder_path)}"
                            zip_file.write(file_path, arcname)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def display_batch_results(results: List[Dict[str, Any]]):
    """Display batch download results."""
    completed = sum(1 for r in results if r.get("status") == "completed")
    total = len(results)
    errors = sum(1 for r in results if r.get("status") == "error")
    
    # Summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("✅ Completed", completed)
    with col2:
        st.metric("❌ Errors", errors)
    with col3:
        st.metric("📊 Total", total)
    
    # Detailed results
    if completed > 0:
        st.subheader("✅ Completed Downloads")
        for result in results:
            if result.get("status") == "completed":
                with st.expander(f"📹 {result.get('title', 'Unknown Title')} - {result['url'][:50]}..."):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Files:**")
                        if result.get('video_path'):
                            st.write("📹 Video")
                        if result.get('thumbnail_path'):
                            st.write("🖼️ Thumbnail")
                        if result.get('audio_path'):
                            st.write("🎵 Audio")
                        if result.get('caption_path'):
                            st.write("📝 Caption")
                        if result.get('transcript_path'):
                            st.write("🎤 Transcript")
                    
                    with col2:
                        st.write("**Details:**")
                        st.write(f"Folder: {result.get('folder_path', 'N/A')}")
                        if result.get('caption'):
                            st.text_area("Caption:", value=result['caption'][:200] + "...", height=100, key=f"caption_{hash(result['url'])}")
    
    if errors > 0:
        st.subheader("❌ Failed Downloads")
        for result in results:
            if result.get("status") == "error":
                st.error(f"**{result['url'][:50]}...** - {result.get('error', 'Unknown error')}")
    
    # Download all files
    if completed > 0:
        try:
            zip_data = create_batch_download_package(results)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"instagram_batch_download_{timestamp}.zip"
            
            st.download_button(
                label=f"📦 Download All Files ({completed} items)",
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
    
    # Mode selection
    mode = st.radio("📋 Download Mode", ["Single URL", "Batch URLs"], horizontal=True)
    
    if mode == "Single URL":
        # Single URL mode
        st.subheader("🔗 Enter Instagram URL")
        url_input = st.text_input(
            "Paste your Instagram Reel or Post URL here:",
            placeholder="https://www.instagram.com/reel/...",
            help="Supports Instagram Reels and Posts"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            download_btn = st.button("🚀 Download", use_container_width=True, type="primary")
        
        if download_btn:
            if not url_input.strip():
                st.error("❌ Please enter an Instagram URL")
                return
            
            if not is_valid_instagram_url(url_input.strip()):
                st.error("❌ Please enter a valid Instagram URL")
                return
            
            urls = [url_input.strip()]
    
    else:
        # Batch URL mode
        st.subheader("📝 Enter Multiple Instagram URLs")
        url_text = st.text_area(
            "Paste Instagram URLs (one per line):",
            placeholder="https://www.instagram.com/reel/...\nhttps://www.instagram.com/p/...\nhttps://www.instagram.com/reel/...",
            height=200,
            help="Enter each URL on a new line. Invalid URLs will be ignored."
        )
        
        # Parse and validate URLs
        if url_text.strip():
            urls = parse_urls(url_text)
            if urls:
                st.success(f"✅ Found {len(urls)} valid Instagram URLs")
                with st.expander("📋 View URLs"):
                    for i, url in enumerate(urls, 1):
                        st.write(f"{i}. {url}")
            else:
                st.warning("⚠️ No valid Instagram URLs found")
                urls = []
        else:
            urls = []
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            download_btn = st.button(
                f"🚀 Download {len(urls)} URLs" if urls else "🚀 Download",
                use_container_width=True,
                type="primary",
                disabled=len(urls) == 0
            )
    
    # Handle download
    if 'download_btn' in locals() and download_btn and urls:
        # Initialize session state for progress tracking
        if 'download_progress' not in st.session_state:
            st.session_state.download_progress = {}
        
        # Progress containers
        progress_container = st.container()
        with progress_container:
            st.subheader("📊 Download Progress")
            
            # Overall progress
            overall_progress = st.progress(0)
            overall_status = st.empty()
            
            # Individual URL progress
            url_progress_container = st.container()
        
        # Initialize downloader
        downloader = BatchDownloader()
        
        # Start download in a separate thread
        def download_worker():
            downloader.download_batch(urls, options)
        
        download_thread = threading.Thread(target=download_worker)
        download_thread.start()
        
        # Progress tracking
        url_progress_bars = {}
        url_status_texts = {}
        completed_count = 0
        
        # Create progress bars for each URL
        with url_progress_container:
            for i, url in enumerate(urls):
                col1, col2 = st.columns([3, 1])
                with col1:
                    url_status_texts[url] = st.empty()
                    url_status_texts[url].text(f"🔗 {url[:60]}... - Waiting")
                with col2:
                    url_progress_bars[url] = st.progress(0)
        
        # Monitor progress
        while download_thread.is_alive() or not downloader.progress_queue.empty():
            try:
                # Get progress updates
                while not downloader.progress_queue.empty():
                    url, progress, status = downloader.progress_queue.get_nowait()
                    
                    if url:  # URL-specific progress
                        if url in url_progress_bars:
                            url_progress_bars[url].progress(progress)
                            url_status_texts[url].text(f"🔗 {url[:60]}... - {status}")
                            
                            if progress == 100:
                                completed_count += 1
                    else:  # Overall status
                        overall_status.text(f"⏳ {status}")
                
                # Update overall progress
                if urls:
                    overall_progress_value = completed_count / len(urls)
                    overall_progress.progress(overall_progress_value)
                
                time.sleep(0.1)
                
            except queue.Empty:
                time.sleep(0.1)
                continue
        
        # Wait for thread to complete
        download_thread.join()
        
        # Final progress update
        overall_progress.progress(1.0)
        overall_status.text("✅ All downloads completed!")
        
        # Display results
        if downloader.results:
            st.success("🎉 Batch download completed!")
            display_batch_results(downloader.results)
        else:
            st.error("❌ No results available")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: gray; font-size: 0.8em;">
        <p>Instagram Batch Media Downloader | Web Version | Built with Streamlit</p>
        <p>⚠️ Please respect content creators' rights and Instagram's terms of service</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
