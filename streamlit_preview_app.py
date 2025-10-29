"""
Instagram Media Downloader - Preview Mode Streamlit Application

This version focuses on previewing content without saving to local storage.
Users can preview media and download individual files as needed.
"""

import streamlit as st
import os
import io
import base64
import tempfile
import zipfile
from pathlib import Path
from typing import List, Dict, Any
import threading
import time
from datetime import datetime
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file."""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and value and not value.startswith("gsk_your"):
                        os.environ[key] = value

# Load .env on startup
load_env_file()

# Import your existing core functionality
from src.core.data_models import ReelItem
from src.core.session_manager import SessionManager
from src.utils.url_validator import is_valid_instagram_url
from src.agents import instaloader as instaloader_agent
from src.agents import yt_dlp as yt_dlp_agent
from src.core.transcriber import AudioTranscriber
from src.core.groq_transcriber import GroqTranscriber
from src.utils.lazy_imports import lazy_import_instaloader


class PreviewDownloader:
    """Streamlit-compatible downloader with preview functionality."""
    
    def __init__(self, groq_api_key: str = None, use_groq: bool = True):
        self.session_manager = SessionManager()
        self.use_groq = use_groq
        
        # Initialize appropriate transcriber
        if use_groq and groq_api_key:
            try:
                self.audio_transcriber = GroqTranscriber(api_key=groq_api_key)
                self.transcriber_type = "groq"
            except Exception as e:
                st.warning(f"Failed to initialize Groq transcriber: {e}. Falling back to Whisper.")
                self.audio_transcriber = AudioTranscriber()
                self.transcriber_type = "whisper"
        else:
            self.audio_transcriber = AudioTranscriber()
            self.transcriber_type = "whisper"
        
        self.loader = None
        
    def setup_instaloader(self):
        """Initialize Instaloader instance with better error handling."""
        if self.loader is None:
            try:
                instaloader_module = lazy_import_instaloader()
                # Use a temporary directory that gets cleaned up
                temp_dir = tempfile.mkdtemp()
                self.loader = instaloader_module.Instaloader(
                    download_video_thumbnails=True,
                    download_comments=False,
                    save_metadata=False,
                    compress_json=False,
                    dirname_pattern=temp_dir,
                    # Add more robust settings
                    request_timeout=30,
                    max_connection_attempts=3,
                    sleep=True,
                )
            except Exception as e:
                st.error(f"Failed to setup Instaloader: {str(e)}")
                return False
        return True
    
    def download_for_preview(self, url: str, options: Dict[str, Any], progress_callback=None) -> Dict[str, Any]:
        """Download content and return file data for preview."""
        
        # Create temporary session for this download
        temp_session = tempfile.mkdtemp()
        self.session_manager.session_folder = Path(temp_session)
        
        if progress_callback:
            progress_callback("Initializing download...")
        
        # Setup downloader based on preference
        if options.get("downloader", "yt-dlp") == "Instaloader":
            if not self.setup_instaloader():
                options["downloader"] = "yt-dlp"  # Fallback to yt-dlp
        
        reel_item = ReelItem(url=url)
        
        try:
            # Try primary downloader
            if options.get("downloader", "yt-dlp") == "yt-dlp":
                if progress_callback:
                    progress_callback("Downloading with yt-dlp...")
                result = yt_dlp_agent.download_reel(
                    reel_item, 1, self.session_manager.session_folder,
                    options, lambda url, progress, status: progress_callback(status) if progress_callback else None
                )
            else:
                if progress_callback:
                    progress_callback("Downloading with Instaloader...")
                result = instaloader_agent.download_reel(
                    reel_item, 1, self.session_manager.session_folder,
                    self.loader, options, 
                    lambda url, progress, status: progress_callback(status) if progress_callback else None
                )
        except Exception as e:
            # Try fallback downloader
            try:
                if progress_callback:
                    progress_callback("Primary downloader failed, trying fallback...")
                
                if options.get("downloader", "yt-dlp") == "yt-dlp":
                    if not self.setup_instaloader():
                        raise Exception("Both downloaders failed")
                    result = instaloader_agent.download_reel(
                        reel_item, 1, self.session_manager.session_folder,
                        self.loader, options, 
                        lambda url, progress, status: progress_callback(status) if progress_callback else None
                    )
                else:
                    result = yt_dlp_agent.download_reel(
                        reel_item, 1, self.session_manager.session_folder,
                        options, lambda url, progress, status: progress_callback(status) if progress_callback else None
                    )
            except Exception as e2:
                raise Exception(f"Both downloaders failed: {str(e)} | {str(e2)}")
        
        # Handle transcription if enabled
        if options.get("transcribe", False):
            if progress_callback:
                progress_callback("Transcribing audio...")
            try:
                reel_folder = Path(result["folder_path"])
                
                # Use Groq transcriber if available, otherwise fallback to Whisper
                if self.transcriber_type == "groq":
                    if progress_callback:
                        progress_callback("Using Groq for Hinglish transcription...")
                    self.audio_transcriber.transcribe_audio_from_reel(
                        reel_folder, 1, result, 
                        lambda url, progress, status: progress_callback(status) if progress_callback else None,
                        enable_post_processing=options.get("enable_hinglish_processing", True)
                    )
                else:
                    if progress_callback:
                        progress_callback("Using local Whisper model...")
                    self.audio_transcriber.load_whisper_model()
                    self.audio_transcriber.transcribe_audio_from_reel(
                        reel_folder, 1, result, 
                        lambda url, progress, status: progress_callback(status) if progress_callback else None
                    )
            except Exception as e:
                result["transcript_error"] = str(e)
        
        # Load file contents for preview
        if progress_callback:
            progress_callback("Loading files for preview...")
        
        result["file_contents"] = self._load_file_contents(result)
        return result
    
    def _load_file_contents(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Load file contents into memory for preview."""
        contents = {}
        
        # Load video
        if result.get('video_path') and Path(result['video_path']).exists():
            with open(result['video_path'], 'rb') as f:
                contents['video'] = f.read()
        
        # Load thumbnail
        if result.get('thumbnail_path') and Path(result['thumbnail_path']).exists():
            with open(result['thumbnail_path'], 'rb') as f:
                contents['thumbnail'] = f.read()
        
        # Load audio
        if result.get('audio_path') and Path(result['audio_path']).exists():
            with open(result['audio_path'], 'rb') as f:
                contents['audio'] = f.read()
        
        # Load caption (text)
        if result.get('caption_path') and Path(result['caption_path']).exists():
            with open(result['caption_path'], 'r', encoding='utf-8') as f:
                contents['caption_text'] = f.read()
        
        # Load transcript (text)
        if result.get('transcript_path') and Path(result['transcript_path']).exists():
            with open(result['transcript_path'], 'r', encoding='utf-8') as f:
                contents['transcript_text'] = f.read()
        
        return contents


def init_streamlit_config():
    """Initialize Streamlit page configuration."""
    st.set_page_config(
        page_title="Instagram Media Previewer",
        page_icon="📱",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def render_header():
    """Render the application header."""
    st.title("📱 Instagram Media Previewer")
    st.markdown("""
    <div style="background: linear-gradient(90deg, #833ab4, #fd1d1d, #fcb045); 
                padding: 1rem; border-radius: 10px; margin-bottom: 2rem;">
        <h3 style="color: white; text-align: center; margin: 0;">
            Preview Instagram Content - No Local Storage Required!
        </h3>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with download options."""
    st.sidebar.header("⚙️ Preview Options")
    
    # Downloader selection - Default to yt-dlp for better reliability
    downloader = st.sidebar.selectbox(
        "🔧 Preferred Downloader",
        ["yt-dlp", "Instaloader"],
        help="yt-dlp is more reliable for Instagram content. Instaloader may face API restrictions."
    )
    
    st.sidebar.subheader("📥 What to Preview")
    
    # Download options
    video = st.sidebar.checkbox("📹 Video", value=True, help="Preview the video file")
    thumbnail = st.sidebar.checkbox("🖼️ Thumbnail", value=True, help="Preview the thumbnail image")
    audio = st.sidebar.checkbox("🎵 Audio", value=True, help="Preview extracted audio")
    caption = st.sidebar.checkbox("📝 Caption", value=True, help="Show post caption/description")
    transcribe = st.sidebar.checkbox("🎤 Transcribe Audio", value=False, 
                                   help="Generate transcript using AI (takes longer)")
    
    # Transcription settings
    use_groq = False
    groq_api_key = os.getenv("GROQ_API_KEY")  # Load from .env automatically
    enable_hinglish_processing = True
    
    if transcribe:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🎤 Transcription Settings")
        
        # Check if API key is available
        if groq_api_key:
            transcription_engine = st.sidebar.radio(
                "Transcription Engine",
                ["Groq (Hinglish Support)", "Local Whisper"],
                help="Groq provides better Hinglish support with Roman script output"
            )
            
            use_groq = transcription_engine == "Groq (Hinglish Support)"
            
            if use_groq:
                # Show API key status (masked)
                masked_key = groq_api_key[:8] + "..." + groq_api_key[-4:]
                st.sidebar.success(f"✅ Using Groq API key from .env")
                st.sidebar.caption(f"Key: {masked_key}")
                
                enable_hinglish_processing = st.sidebar.checkbox(
                    "📝 Enable Hinglish Processing",
                    value=True,
                    help="Post-process transcription with LLM for proper Hinglish in Roman script"
                )
                
                if enable_hinglish_processing:
                    st.sidebar.info("""
                    **Hinglish Mode:**
                    - Hindi/Hinglish → Roman script
                    - English → Clean English
                    - Spelling correction
                    - Context-aware fixes
                    """)
            else:
                st.sidebar.info("Using local Whisper model (no Hinglish post-processing)")
        else:
            st.sidebar.warning("⚠️ No Groq API key found in .env file")
            st.sidebar.info("""
            **To enable Groq transcription:**
            1. Add to `.env` file:
               `GROQ_API_KEY=gsk_your_key`
            2. Restart the app
            3. Get free key at: console.groq.com
            """)
            # Force local Whisper if no API key
            use_groq = False
        
        st.sidebar.warning("⚠️ Transcription requires additional processing time.")
    
    # Tips
    st.sidebar.markdown("---")
    st.sidebar.subheader("💡 Tips")
    st.sidebar.info("""
    • **yt-dlp** is recommended for Instagram
    • **Groq** for Hinglish transcription
    • **No files saved locally** - everything in memory
    • **Download individual files** from preview
    • **Private accounts** may not work
    """)
    
    return {
        "downloader": downloader,
        "video": video,
        "thumbnail": thumbnail,
        "audio": audio,
        "caption": caption,
        "transcribe": transcribe,
        "use_groq": use_groq,
        "groq_api_key": groq_api_key,
        "enable_hinglish_processing": enable_hinglish_processing
    }


def create_download_zip(result: Dict[str, Any]) -> bytes:
    """Create a zip file from the downloaded content."""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        file_contents = result.get("file_contents", {})
        
        # Add video
        if 'video' in file_contents:
            zip_file.writestr("video.mp4", file_contents['video'])
        
        # Add thumbnail
        if 'thumbnail' in file_contents:
            zip_file.writestr("thumbnail.jpg", file_contents['thumbnail'])
        
        # Add audio
        if 'audio' in file_contents:
            zip_file.writestr("audio.mp3", file_contents['audio'])
        
        # Add caption
        if 'caption_text' in file_contents:
            zip_file.writestr("caption.txt", file_contents['caption_text'])
        
        # Add transcript
        if 'transcript_text' in file_contents:
            zip_file.writestr("transcript.txt", file_contents['transcript_text'])
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def display_media_preview(result: Dict[str, Any]):
    """Display media preview with download options."""
    st.success("✅ Content loaded successfully!")
    
    file_contents = result.get("file_contents", {})
    
    # Basic info
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Content Summary")
        st.write(f"**Title:** {result.get('title', 'Instagram Content')}")
        
        # Show what was loaded
        loaded_items = []
        if 'video' in file_contents:
            loaded_items.append("📹 Video")
        if 'thumbnail' in file_contents:
            loaded_items.append("🖼️ Thumbnail")
        if 'audio' in file_contents:
            loaded_items.append("🎵 Audio")
        if 'caption_text' in file_contents:
            loaded_items.append("📝 Caption")
        if 'transcript_text' in file_contents:
            loaded_items.append("🎤 Transcript")
        
        st.write("**Available Content:**")
        for item in loaded_items:
            st.write(f"- {item}")
    
    with col2:
        st.subheader("📦 Download All")
        try:
            zip_data = create_download_zip(result)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"instagram_content_{timestamp}.zip"
            
            st.download_button(
                label="📦 Download ZIP Package",
                data=zip_data,
                file_name=filename,
                mime="application/zip",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error creating package: {str(e)}")
    
    # Media previews in tabs
    tabs = []
    tab_names = []
    
    if 'thumbnail' in file_contents:
        tab_names.append("🖼️ Thumbnail")
    if 'video' in file_contents:
        tab_names.append("📹 Video")
    if 'audio' in file_contents:
        tab_names.append("🎵 Audio")
    if 'caption_text' in file_contents:
        tab_names.append("📝 Caption")
    if 'transcript_text' in file_contents:
        tab_names.append("🎤 Transcript")
    
    if tab_names:
        tabs = st.tabs(tab_names)
        
        tab_index = 0
        
        # Thumbnail preview
        if 'thumbnail' in file_contents:
            with tabs[tab_index]:
                st.subheader("🖼️ Thumbnail Preview")
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.image(io.BytesIO(file_contents['thumbnail']), caption="Thumbnail", use_column_width=True)
                
                st.download_button(
                    label="📥 Download Thumbnail",
                    data=file_contents['thumbnail'],
                    file_name="thumbnail.jpg",
                    mime="image/jpeg"
                )
            tab_index += 1
        
        # Video preview
        if 'video' in file_contents:
            with tabs[tab_index]:
                st.subheader("📹 Video Preview")
                st.video(io.BytesIO(file_contents['video']))
                
                st.download_button(
                    label="📥 Download Video",
                    data=file_contents['video'],
                    file_name="video.mp4",
                    mime="video/mp4"
                )
            tab_index += 1
        
        # Audio preview
        if 'audio' in file_contents:
            with tabs[tab_index]:
                st.subheader("🎵 Audio Preview")
                st.audio(io.BytesIO(file_contents['audio']))
                
                st.download_button(
                    label="📥 Download Audio",
                    data=file_contents['audio'],
                    file_name="audio.mp3",
                    mime="audio/mpeg"
                )
            tab_index += 1
        
        # Caption preview
        if 'caption_text' in file_contents:
            with tabs[tab_index]:
                st.subheader("📝 Caption")
                st.text_area(
                    label="Caption Content",
                    value=file_contents['caption_text'], 
                    height=200, 
                    disabled=True,
                    label_visibility="collapsed"
                )
                
                st.download_button(
                    label="📥 Download Caption",
                    data=file_contents['caption_text'].encode('utf-8'),
                    file_name="caption.txt",
                    mime="text/plain"
                )
            tab_index += 1
        
        # Transcript preview
        if 'transcript_text' in file_contents:
            with tabs[tab_index]:
                st.subheader("🎤 Transcript")
                st.text_area(
                    label="Transcript Content",
                    value=file_contents['transcript_text'], 
                    height=200, 
                    disabled=True,
                    label_visibility="collapsed"
                )
                
                st.download_button(
                    label="📥 Download Transcript",
                    data=file_contents['transcript_text'].encode('utf-8'),
                    file_name="transcript.txt",
                    mime="text/plain"
                )


def main():
    """Main Streamlit application."""
    init_streamlit_config()
    render_header()
    
    # Get preview options from sidebar
    options = render_sidebar()
    
    # Main content area
    st.subheader("🔗 Enter Instagram URL")
    
    # URL input
    url_input = st.text_input(
        label="Instagram URL",
        placeholder="https://www.instagram.com/reel/... or https://www.instagram.com/p/...",
        help="Supports Instagram Reels and Posts",
        label_visibility="collapsed"
    )
    
    # Preview button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        preview_btn = st.button("🔍 Preview Content", use_container_width=True, type="primary")
    
    # Handle preview
    if preview_btn:
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
            # Initialize downloader with Groq support if enabled and API key available
            if options.get("transcribe") and options.get("use_groq") and options.get("groq_api_key"):
                downloader = PreviewDownloader(
                    groq_api_key=options.get("groq_api_key"),
                    use_groq=True
                )
            else:
                downloader = PreviewDownloader(use_groq=False)
            
            # Progress callback
            def update_progress(message):
                status_text.text(f"⏳ {message}")
            
            # Start preview
            with st.spinner("Loading content..."):
                result = downloader.download_for_preview(
                    url_input.strip(), 
                    options, 
                    progress_callback=update_progress
                )
            
            # Clear progress indicators
            progress_bar.progress(100)
            status_text.empty()
            
            # Display preview
            display_media_preview(result)
            
        except Exception as e:
            error_msg = str(e)
            st.error(f"❌ Failed to load content: {error_msg}")
            
            # Provide helpful suggestions
            if "403" in error_msg or "Forbidden" in error_msg:
                st.info("💡 **Suggestion:** Instagram may be blocking requests. Try:")
                st.write("- Using yt-dlp instead of Instaloader")
                st.write("- Waiting a few minutes before trying again")
                st.write("- Using a different Instagram URL")
            elif "Private" in error_msg:
                st.info("💡 **Note:** This appears to be a private account. Only public content can be accessed.")
            else:
                st.info("💡 **Try:** Switch to a different downloader in the sidebar options.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: gray; font-size: 0.8em;">
        <p>Instagram Media Previewer | No Local Storage | Built with Streamlit</p>
        <p>⚠️ Please respect content creators' rights and Instagram's terms of service</p>
        <p>🔒 All content is processed in memory - nothing saved to disk</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
