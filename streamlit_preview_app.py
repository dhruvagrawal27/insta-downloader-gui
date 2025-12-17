"""
Instagram Media Downloader - Preview Mode Streamlit Application

This version focuses on previewing content without saving to local storage.
Users can preview media and download individual files as needed.
"""

import streamlit as st
import os
import sys
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

# Add the project root to Python path for imports to work
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

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

# Try to import web-compatible yt-dlp first, fallback to executable version
try:
    from src.agents import yt_dlp_web as yt_dlp_agent
    YT_DLP_WEB = True
except ImportError:
    from src.agents import yt_dlp as yt_dlp_agent
    YT_DLP_WEB = False

from src.core.transcriber import AudioTranscriber
from src.core.groq_transcriber import GroqTranscriber
from src.utils.lazy_imports import lazy_import_instaloader
from groq import Groq
import json


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
    # Check which downloader method is selected (default to rapidapi)
    current_method = st.session_state.get("downloader_method", "rapidapi")
    
    # Show different options based on downloader method
    if current_method == "rapidapi":
        # RapidAPI Downloader - Only transcription options
        st.sidebar.header("⚙️ RapidAPI Options")
        st.sidebar.success("✅ No rate limits!")
        st.sidebar.info("💡 Automatic Hinglish transcription using Groq AI")
        
        # Only show Groq API key setting
        st.sidebar.markdown("---")
        st.sidebar.subheader("🎤 Transcription Settings")
        
        groq_api_key = os.getenv("GROQ_API_KEY")
        
        if groq_api_key:
            masked_key = groq_api_key[:8] + "..." + groq_api_key[-4:]
            st.sidebar.success(f"✅ Groq API ready")
            st.sidebar.caption(f"Key: {masked_key}")
        else:
            st.sidebar.warning("⚠️ No Groq API key found in .env file")
            st.sidebar.info("""
            **To enable transcription:**
            1. Add to `.env`: `GROQ_API_KEY=gsk_your_key`
            2. Restart app
            3. Get key at: console.groq.com
            """)
        
        # Tips
        st.sidebar.markdown("---")
        st.sidebar.subheader("💡 How it works")
        st.sidebar.info("""
    1. **Enter** Instagram URL
    2. **Click** Download & Transcribe
    3. **Get** Hinglish transcript in Roman script
    
    • Fast & reliable
    • No authentication needed
    • Works with public content
    """)
        
        # Simple return for RapidAPI
        return {
            "transcribe": True,  # Always transcribe for RapidAPI
            "use_groq": True,    # Always use Groq
            "groq_api_key": groq_api_key,
            "enable_hinglish_processing": True,  # Always enable Hinglish
            "generate_prompts": False,  # No prompts for RapidAPI
            "video": False,
            "thumbnail": False,
            "audio": False,
            "caption": False
        }
    
    elif current_method == "iiilab":
        # iiiLab YouTube Downloader - Only transcription options
        st.sidebar.header("⚙️ iiiLab YouTube Options")
        st.sidebar.success("✅ No rate limits!")
        st.sidebar.info("💡 Automatic Hinglish transcription using Groq AI")
        
        # Only show Groq API key setting
        st.sidebar.markdown("---")
        st.sidebar.subheader("🎤 Transcription Settings")
        
        groq_api_key = os.getenv("GROQ_API_KEY")
        
        if groq_api_key:
            masked_key = groq_api_key[:8] + "..." + groq_api_key[-4:]
            st.sidebar.success(f"✅ Groq API ready")
            st.sidebar.caption(f"Key: {masked_key}")
        else:
            st.sidebar.warning("⚠️ No Groq API key found in .env file")
            st.sidebar.info("""
            **To enable transcription:**
            1. Add to `.env`: `GROQ_API_KEY=gsk_your_key`
            2. Restart app
            3. Get key at: console.groq.com
            """)
        
        # Tips
        st.sidebar.markdown("---")
        st.sidebar.subheader("💡 How it works")
        st.sidebar.info("""
    1. **Enter** YouTube URL
    2. **Click** Get Transcript
    3. **Get** Hinglish transcript in Roman script
    
    • Fast & reliable
    • No authentication needed
    • Works with public videos
    """)
        
        # Simple return for iiiLab
        return {
            "transcribe": True,  # Always transcribe for iiiLab
            "use_groq": True,    # Always use Groq
            "groq_api_key": groq_api_key,
            "enable_hinglish_processing": True,  # Always enable Hinglish
            "generate_prompts": False,  # No prompts for iiiLab
            "video": False,
            "thumbnail": False,
            "audio": False,
            "caption": False
        }
    
    else:
        # Standard Downloaders - Full options
        st.sidebar.header("⚙️ Preview Options")
        
        # Check yt-dlp availability
        yt_dlp_available = hasattr(yt_dlp_agent, 'check_availability') and yt_dlp_agent.check_availability()
        
        # Downloader selection - Default to yt-dlp for better reliability
        if yt_dlp_available:
            downloader = st.sidebar.selectbox(
                "🔧 Preferred Downloader",
                ["yt-dlp", "Instaloader"],
                help="yt-dlp is more reliable for Instagram content. Instaloader may face API restrictions."
            )
        else:
            st.sidebar.warning("⚠️ yt-dlp not available. Using Instaloader only.")
            downloader = "Instaloader"
        
        # Authentication Section
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔐 Authentication (Optional)")
        
        use_cookies = st.sidebar.checkbox(
            "🍪 Use Instagram Cookies",
            value=False,
            help="Add cookies to bypass rate limits and access private content"
        )
        
        cookies_text = None
        if use_cookies:
            st.sidebar.info("""
            **How to get cookies:**
            1. Install browser extension: "Get cookies.txt LOCALLY"
            2. Login to Instagram
            3. Click extension → Export cookies
            4. Paste Netscape format below
            """)
            
            cookies_text = st.sidebar.text_area(
                "Paste cookies (Netscape format)",
                height=100,
                placeholder="# Netscape HTTP Cookie File\n.instagram.com\tTRUE\t/\tTRUE\t...",
                help="Cookies in Netscape format from browser extension"
            )
            
            if cookies_text and len(cookies_text.strip()) > 50:
                st.sidebar.success("✅ Cookies loaded")
            elif cookies_text:
                st.sidebar.warning("⚠️ Cookies seem too short. Make sure you copied the full content.")
            
            st.sidebar.caption("🔒 Cookies are used only for this session and never stored.")
    
    # Common options for both methods
    # Sora 2/Veo 3 Prompt Generation
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎬 AI Video Prompts")
    generate_prompts = st.sidebar.checkbox(
        "🎥 Generate Sora 2/Veo 3 Prompts",
        value=False,
        help="Generate cinematic AI video prompts from transcript"
    )
    
    prompt_type = None
    cameo_usernames = []
    
    if generate_prompts:
        prompt_type = st.sidebar.radio(
            "Select AI Model",
            ["Sora 2", "Veo 3"],
            help="Choose which AI video model to generate prompts for"
        )
        
        if prompt_type == "Sora 2":
            st.sidebar.markdown("**Cameo Settings** (Optional)")
            st.sidebar.caption("Add up to 3 Instagram usernames")
            
            cameo1 = st.sidebar.text_input(
                "Cameo 1",
                placeholder="@dhruvagr",
                help="First cameo username (without @)"
            )
            cameo2 = st.sidebar.text_input(
                "Cameo 2",
                placeholder="@username2",
                help="Second cameo username (optional)"
            )
            cameo3 = st.sidebar.text_input(
                "Cameo 3",
                placeholder="@username3",
                help="Third cameo username (optional)"
            )
            
            # Collect non-empty cameos
            for cameo in [cameo1, cameo2, cameo3]:
                if cameo and cameo.strip():
                    # Add @ if not present
                    username = cameo.strip()
                    if not username.startswith("@"):
                        username = "@" + username
                    cameo_usernames.append(username)
        
        st.sidebar.info("""
        **AI Prompt Features:**
        - Script segmentation (chunks)
        - Cinematic scene descriptions
        - Camera & lighting specs
        - Character actions & dialogue
        - Audio & FX details
        """)
        
        st.sidebar.warning("⚠️ Requires transcription to be enabled")
    
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
    
    # Tips and Limitations
    st.sidebar.markdown("---")
    st.sidebar.subheader("💡 Tips & Limitations")
    
    # Show different tips based on method
    if current_method == "rapidapi":
        st.sidebar.info("""
    • **RapidAPI** bypasses Instagram restrictions
    • **Groq** for Hinglish transcription
    • **No files saved locally** - everything in memory
    • **Download individual files** from preview
    • **Works with public content**
    """)
    else:
        st.sidebar.info("""
    • **yt-dlp** is recommended for Instagram
    • **Groq** for Hinglish transcription
    • **No files saved locally** - everything in memory
    • **Download individual files** from preview
    • **Private accounts** may not work
    """)
        
        st.sidebar.warning("⚠️ **Known Issue**: Instagram Rate Limits")
        st.sidebar.markdown("""
        <details>
        <summary style="cursor: pointer; font-weight: bold;">📖 Why downloads may fail?</summary>
        <div style="margin-top: 10px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;">
        <p><strong>Instagram blocks cloud servers</strong> (like Streamlit Cloud) to prevent bots.</p>
        <p><strong>Solutions:</strong></p>
        <ul>
        <li>✅ Use RapidAPI downloader (button above)</li>
        <li>✅ Add Instagram cookies (see Authentication section)</li>
        <li>✅ Wait 10-15 minutes between requests</li>
        <li>✅ Try different URLs</li>
        <li>✅ Run locally: <code>streamlit run streamlit_preview_app.py</code></li>
        </ul>
        <p><strong>This is an Instagram limitation, not an app bug.</strong></p>
        </div>
        </details>
        """, unsafe_allow_html=True)
    
    # Build return dict based on method
    result = {
        "video": video,
        "thumbnail": thumbnail,
        "audio": audio,
        "caption": caption,
        "transcribe": transcribe,
        "use_groq": use_groq,
        "groq_api_key": groq_api_key,
        "enable_hinglish_processing": enable_hinglish_processing,
        "generate_prompts": generate_prompts,
        "prompt_type": prompt_type,
        "cameo_usernames": cameo_usernames
    }
    
    # Add standard downloader specific options
    if current_method == "standard":
        result["downloader"] = downloader
        result["use_cookies"] = use_cookies
        result["cookies_text"] = cookies_text if use_cookies else None
    
    return result


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
        
        # Add AI prompts if available
        if 'ai_prompts_json' in file_contents:
            zip_file.writestr("ai_video_prompts.json", file_contents['ai_prompts_json'])
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def generate_ai_video_prompts(script: str, prompt_type: str, cameo_usernames: List[str], groq_api_key: str, progress_callback=None) -> Dict[str, Any]:
    """Generate Sora 2 or Veo 3 video prompts from transcript using Groq LLM."""
    
    if progress_callback:
        progress_callback(f"Generating {prompt_type} prompts with AI...")
    
    try:
        # Initialize Groq client
        client = Groq(api_key=groq_api_key)
        
        # Format cameo string
        cameo_str = ", ".join(cameo_usernames) if cameo_usernames else "No Cameo Provided"
        
        # System prompt for AI video generation
        system_prompt = """You are an expert AI video prompt engineer specializing in creating cinematic, viral-style video prompts for advanced AI video generation platforms like Sora 2 and Veo 3. Your expertise includes:

Core Capabilities:
- Script Analysis & Chunking: Break down video scripts into optimal 6-8 second segments that maintain narrative flow and emotional impact
- Cinematic Storytelling: Create high-drama, pattern-interrupt hooks and cinematically compelling scenes
- Technical Precision: Generate detailed JSON prompts with exact specifications for camera movements, lighting, audio design, character actions, visual effects

Prompt Structure Requirements:
Each prompt must include:
- Meta: Title, description, aspect ratio (default 9:16), and tone
- Hook: 2-3 second pattern interrupt (for first segment only)
- Scene: Location, environment (lighting + sound), camera specs, characters with exact dialogue
- FX: Visual effects and cinematic enhancements
- Audio: Dialogue mix and background elements
- End State: Final frame action or transition

Style Principles:
- High Drama: Think creatively about the content's context
- Pattern Interrupts: Start with unexpected visual/audio elements
- Realism: Prioritize handheld, documentary-style authenticity
- Viral Optimization: Create thumb-stopping moments in first 2 seconds

Key Rules:
- Never modify dialogue - use exact words provided
- If user mentions @username, include them as specified character
- If no cameo specified, create prompts without named individuals
- Maintain dialogue continuity across chunked segments
- Each segment must be self-contained but flow into next
- Default to vertical (9:16) format unless specified otherwise"""

        # User prompt with script and cameo
        user_prompt = f"""Script: {script}
Cameo: {cameo_str}

When user provides a script, follow this process:

Step 1: Analyze & Chunk Script
Break the provided script into segments of 6-8 seconds each:
- Identify natural dialogue breaks
- Preserve complete thoughts/sentences
- Note emotional beats and intensity changes
- Consider visual transition points

Step 2: Create Detailed JSON Prompts
For each segment, generate a complete JSON prompt following this structure:

{{
  "meta": {{
    "title": "[Compelling title - Part X]",
    "description": "[Brief scene description with key visual elements]",
    "aspect_ratio": "9:16",
    "tone": "[mood_category]"
  }},
  "scene": {{
    "hook": {{
      "shot": "[First 2s only for opening segment - pattern interrupt description]"
    }},
    "location": "[Specific setting with atmospheric details]",
    "environment": {{
      "lighting": "[Detailed lighting setup]",
      "sound": ["ambient_1", "ambient_2", "ambient_3"]
    }},
    "camera": {{
      "type": "[camera_type]",
      "style": "[movement, framing, focus techniques]",
      "quality": "[visual_aesthetic]"
    }},
    "characters": [
      {{
        "role": "[Character name or @username if provided]",
        "appearance": "[Detailed physical description]",
        "action": "[Specific movements and gestures]",
        "dialogue": "[EXACT dialogue from script - no changes]",
        "motion": "[Micro-gestures and timing]"
      }}
    ],
    "fx": {{
      "[effect_name]": true,
      "[effect_name_2]": true
    }},
    "audio": {{
      "mix": "[audio_mixing_style]",
      "bg": ["sound_1", "sound_2"]
    }},
    "end_state": {{
      "action": "[Final frame description or transition cue]"
    }}
  }}
}}

Step 3: Provide Context
After all JSON prompts, include:
- Brief explanation of chunking decisions
- Suggested shooting order if different from narrative order
- Tips for maintaining continuity between segments
- Optional: suggestions for editing transitions

Generate the complete JSON response with all segments."""

        if progress_callback:
            progress_callback("Calling Groq LLM for prompt generation...")
        
        # Call Groq API with structured output
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="openai/gpt-oss-120b",
            temperature=0.7,
            max_tokens=8000,
            response_format={"type": "json_object"}
        )
        
        # Parse response
        response_text = chat_completion.choices[0].message.content
        
        if progress_callback:
            progress_callback("Parsing AI-generated prompts...")
        
        # Try to parse as JSON
        try:
            prompts_json = json.loads(response_text)
        except json.JSONDecodeError:
            # If not valid JSON, wrap in a structure
            prompts_json = {
                "raw_response": response_text,
                "note": "Response was not in JSON format"
            }
        
        return {
            "success": True,
            "prompts": prompts_json,
            "model": "openai/gpt-oss-120b",
            "prompt_type": prompt_type,
            "cameos": cameo_usernames,
            "script": script
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


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
    if 'ai_prompts' in file_contents:
        tab_names.append("🎬 AI Prompts")
    
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
            tab_index += 1
        
        # AI Prompts preview
        if 'ai_prompts' in file_contents:
            with tabs[tab_index]:
                st.subheader(f"🎬 {file_contents['ai_prompts'].get('prompt_type', 'AI')} Video Prompts")
                
                prompts_data = file_contents['ai_prompts']
                
                if prompts_data.get('success'):
                    # Display metadata summary card
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
                        <h3 style="color: white; margin: 0;">✨ AI-Generated Video Prompts</h3>
                        <p style="color: #e0e0e0; margin: 0.5rem 0 0 0;">
                            Professional cinematic prompts ready for AI video generation
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Metadata metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("🤖 Model", prompts_data.get('model', 'N/A').split('/')[-1])
                    with col2:
                        st.metric("🎬 Platform", prompts_data.get('prompt_type', 'N/A'))
                    with col3:
                        prompts_json = prompts_data.get('prompts', {})
                        # Count segments from different possible structures
                        if isinstance(prompts_json, list):
                            seg_count = len(prompts_json)
                        elif 'segments' in prompts_json:
                            seg_count = len(prompts_json['segments'])
                        elif 'video_series' in prompts_json:
                            seg_count = prompts_json['video_series'].get('total_segments', 'N/A')
                        else:
                            seg_count = 'N/A'
                        st.metric("📹 Segments", seg_count)
                    with col4:
                        cameo_count = len(prompts_data.get('cameos', []))
                        st.metric("👥 Cameos", cameo_count if cameo_count > 0 else "None")
                    
                    if prompts_data.get('cameos'):
                        st.success(f"**Featured Cameos:** {', '.join(prompts_data['cameos'])}")
                    
                    st.markdown("---")
                    
                    # Display formatted JSON prompts
                    prompts_json = prompts_data.get('prompts', {})
                    
                    # Detect format: wrapped in video_series or direct array
                    segments = []
                    if 'video_series' in prompts_json:
                        # Format 1: Full structure with video_series wrapper
                        series_info = prompts_json['video_series']
                        st.markdown("### 📺 Video Series Overview")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Title", series_info.get('title', 'N/A'))
                        with col2:
                            st.metric("Segments", series_info.get('total_segments', 'N/A'))
                        with col3:
                            st.metric("Duration", series_info.get('total_duration', 'N/A'))
                        with col4:
                            st.metric("Arc", series_info.get('narrative_arc', 'N/A').replace('_', ' ').title())
                        st.markdown("---")
                        segments = prompts_json.get('segments', [])
                    elif isinstance(prompts_json, list):
                        # Format 2: Direct array of segments
                        segments = prompts_json
                        st.markdown("### 📺 Video Series")
                        st.info(f"**{len(segments)} video segments** detected from transcript")
                        st.markdown("---")
                    elif 'segments' in prompts_json:
                        # Format 3: Object with segments key but no video_series
                        segments = prompts_json['segments']
                    
                    # Display each segment
                    if segments:
                        st.markdown(f"### 🎞️ Video Segments ({len(segments)} total)")
                        
                        # Quick overview cards
                        if len(segments) > 0:
                            st.markdown("#### Quick Overview")
                            
                            # Display all segments in rows of 4
                            num_segments = len(segments)
                            num_rows = (num_segments + 3) // 4  # Calculate rows needed (ceiling division)
                            
                            for row_idx in range(num_rows):
                                start_idx = row_idx * 4
                                end_idx = min(start_idx + 4, num_segments)
                                segments_in_row = segments[start_idx:end_idx]
                                
                                # Create columns for this row
                                overview_cols = st.columns(len(segments_in_row))
                                
                                for col_idx, seg in enumerate(segments_in_row):
                                    with overview_cols[col_idx]:
                                        seg_idx = start_idx + col_idx
                                        seg_num = seg.get('segment_number', seg_idx + 1) if isinstance(seg, dict) else seg_idx + 1
                                        seg_dur = seg.get('duration', '~6-8s') if isinstance(seg, dict) else '~6-8s'
                                        seg_title = "Unknown"
                                        if isinstance(seg, dict) and 'meta' in seg:
                                            seg_title = seg['meta'].get('title', f'Segment {seg_num}')
                                        
                                        st.markdown(f"""
                                        <div style="background: #f0f2f6; padding: 1rem; border-radius: 8px; 
                                                    border-left: 4px solid #667eea; margin-bottom: 0.5rem;">
                                            <h4 style="margin: 0; color: #667eea;">Part {seg_num}</h4>
                                            <p style="margin: 0.3rem 0; font-size: 0.85em; color: #666;">
                                                ⏱️ {seg_dur}
                                            </p>
                                            <p style="margin: 0; font-size: 0.75em; color: #888; overflow: hidden; 
                                                      text-overflow: ellipsis; white-space: nowrap;">
                                                {seg_title[:30]}...
                                            </p>
                                        </div>
                                        """, unsafe_allow_html=True)
                            
                            st.markdown("---")
                        
                        # Detailed segment breakdowns
                        st.markdown("#### 📋 Detailed Breakdown")
                        
                        for idx, segment in enumerate(segments, 1):
                            # Handle both indexed and numbered segments
                            if isinstance(segment, dict):
                                seg_num = segment.get('segment_number', idx)
                                duration = segment.get('duration', 'N/A')
                                
                                # Create segment header
                                segment_title = f"Segment {seg_num}"
                                if duration != 'N/A':
                                    segment_title += f" - {duration}"
                            
                            with st.expander(f"**{segment_title}**", expanded=(idx == 1)):
                                # Meta info
                                if 'meta' in segment:
                                    meta = segment['meta']
                                    st.markdown(f"### 📌 {meta.get('title', 'Untitled')}")
                                    if meta.get('description'):
                                        st.info(meta.get('description'))
                                    
                                    # Meta details in columns
                                    meta_col1, meta_col2 = st.columns(2)
                                    with meta_col1:
                                        st.metric("Aspect Ratio", meta.get('aspect_ratio', '9:16'))
                                    with meta_col2:
                                        st.metric("Tone", meta.get('tone', 'N/A').replace('_', ' ').title())
                                    st.markdown("---")
                                
                                # Scene details
                                if 'scene' in segment:
                                    scene = segment['scene']
                                    
                                    # Hook (first segment only)
                                    if 'hook' in scene and scene['hook']:
                                        st.markdown("#### 🎣 Hook (First 2 seconds)")
                                        hook_text = scene['hook'].get('shot', 'N/A') if isinstance(scene['hook'], dict) else scene['hook']
                                        st.success(f"⚡ {hook_text}")
                                        st.markdown("---")
                                    
                                    # Location
                                    if scene.get('location'):
                                        st.markdown("#### 📍 Location & Setting")
                                        st.write(f"📌 {scene.get('location')}")
                                        st.markdown("---")
                                    
                                    # Environment
                                    if 'environment' in scene and scene['environment']:
                                        env = scene['environment']
                                        st.markdown("#### 🌅 Environment")
                                        
                                        env_col1, env_col2 = st.columns(2)
                                        with env_col1:
                                            st.markdown("**💡 Lighting**")
                                            st.write(env.get('lighting', 'N/A'))
                                        with env_col2:
                                            st.markdown("**🔊 Ambient Sounds**")
                                            if 'sound' in env and env['sound']:
                                                for sound in env['sound']:
                                                    st.write(f"• {sound}")
                                            else:
                                                st.write("N/A")
                                        st.markdown("---")
                                    
                                    # Camera
                                    if 'camera' in scene and scene['camera']:
                                        cam = scene['camera']
                                        st.markdown("#### 📹 Camera Setup")
                                        
                                        cam_col1, cam_col2, cam_col3 = st.columns(3)
                                        with cam_col1:
                                            st.markdown("**Type**")
                                            st.info(cam.get('type', 'N/A'))
                                        with cam_col2:
                                            st.markdown("**Style**")
                                            st.info(cam.get('style', 'N/A'))
                                        with cam_col3:
                                            st.markdown("**Quality**")
                                            st.info(cam.get('quality', 'N/A'))
                                        st.markdown("---")
                                    
                                    # Characters
                                    if 'characters' in scene and scene['characters']:
                                        st.markdown("#### 👥 Characters & Performance")
                                        
                                        for char_idx, char in enumerate(scene['characters'], 1):
                                            char_role = char.get('role', f'Character {char_idx}')
                                            
                                            # Character card
                                            st.markdown(f"##### {char_role}")
                                            
                                            # Appearance & Action in columns
                                            char_col1, char_col2 = st.columns(2)
                                            with char_col1:
                                                st.markdown("**👤 Appearance**")
                                                st.write(char.get('appearance', 'N/A'))
                                            with char_col2:
                                                st.markdown("**🎭 Action**")
                                                st.write(char.get('action', 'N/A'))
                                            
                                            # Dialogue (highlighted)
                                            if char.get('dialogue'):
                                                st.markdown("**💬 Dialogue**")
                                                st.success(f'"{char.get("dialogue")}"')
                                            
                                            # Motion details
                                            if char.get('motion'):
                                                st.markdown("**🕺 Motion & Gestures**")
                                                st.write(char.get('motion'))
                                            
                                            if char_idx < len(scene['characters']):
                                                st.markdown("---")
                                    
                                        st.markdown("---")
                                    
                                    # FX
                                    if 'fx' in scene and scene['fx']:
                                        st.markdown("#### ✨ Visual Effects")
                                        fx_list = [k.replace('_', ' ').title() for k, v in scene['fx'].items() if v]
                                        if fx_list:
                                            fx_cols = st.columns(min(3, len(fx_list)))
                                            for fx_idx, fx_name in enumerate(fx_list):
                                                with fx_cols[fx_idx % 3]:
                                                    st.info(f"✓ {fx_name}")
                                        else:
                                            st.write("None specified")
                                        st.markdown("---")
                                    
                                    # Audio
                                    if 'audio' in scene and scene['audio']:
                                        aud = scene['audio']
                                        st.markdown("#### 🎵 Audio Design")
                                        
                                        aud_col1, aud_col2 = st.columns(2)
                                        with aud_col1:
                                            st.markdown("**Mix Style**")
                                            st.write(aud.get('mix', 'N/A'))
                                        with aud_col2:
                                            st.markdown("**Background**")
                                            if 'bg' in aud and aud['bg']:
                                                for bg_sound in aud['bg']:
                                                    st.write(f"• {bg_sound}")
                                            else:
                                                st.write("N/A")
                                        st.markdown("---")
                                    
                                    # End state
                                    if 'end_state' in scene and scene['end_state']:
                                        st.markdown("#### 🎬 End Frame / Transition")
                                        end_action = scene['end_state'].get('action', 'N/A') if isinstance(scene['end_state'], dict) else scene['end_state']
                                        st.warning(f"➡️ {end_action}")
                                        st.markdown("---")
                                
                                # Copy segment JSON section
                                st.markdown("---")
                                st.markdown("### 📋 Segment JSON")
                                segment_json = json.dumps(segment, indent=2)
                                
                                # Display JSON with copy button
                                st.markdown(f"""
<div style="background: #f8f9fa; padding: 0.5rem; border-radius: 5px; border-left: 4px solid #667eea;">
    <p style="margin: 0; font-size: 0.9em; color: #666;">
        💡 <b>Tip:</b> Click the copy icon (📋) in the top-right corner of the code block below to copy JSON
    </p>
</div>
""", unsafe_allow_html=True)
                                
                                st.code(segment_json, language="json")
                                
                                # Download button for this segment
                                st.download_button(
                                    label=f"📥 Download Segment {seg_num} JSON",
                                    data=segment_json,
                                    file_name=f"segment_{seg_num}.json",
                                    mime="application/json",
                                    key=f"download_segment_{idx}",
                                    use_container_width=False
                                )
                    
                    # Production notes
                    if 'production_notes' in prompts_json and prompts_json['production_notes']:
                        notes = prompts_json['production_notes']
                        st.markdown("---")
                        st.markdown("### 📝 Production Notes")
                        
                        # Continuity Guide
                        if 'continuity_guide' in notes and notes['continuity_guide']:
                            with st.expander("🔄 Continuity Guide", expanded=False):
                                for key, value in notes['continuity_guide'].items():
                                    st.markdown(f"**{key.replace('_', ' ').title()}**")
                                    st.write(value)
                                    st.write("")
                        
                        # Shooting Recommendations
                        if 'shooting_recommendations' in notes and notes['shooting_recommendations']:
                            with st.expander("🎥 Shooting Recommendations", expanded=False):
                                for i, rec in enumerate(notes['shooting_recommendations'], 1):
                                    st.markdown(f"**{i}.** {rec}")
                                    st.write("")
                        
                        # Viral Optimization
                        if 'viral_optimization' in notes and notes['viral_optimization']:
                            with st.expander("🚀 Viral Optimization Strategy", expanded=False):
                                for key, value in notes['viral_optimization'].items():
                                    st.markdown(f"**{key.replace('_', ' ').title()}**")
                                    st.info(value)
                                    st.write("")
                    
                    # Raw JSON display
                    with st.expander("📄 Raw JSON (Copy/Paste)"):
                        json_str = json.dumps(prompts_json, indent=2)
                        st.code(json_str, language="json")
                    
                    # Download options
                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.download_button(
                            label="📥 Download JSON",
                            data=json.dumps(prompts_json, indent=2),
                            file_name=f"{prompts_data.get('prompt_type', 'ai')}_prompts.json",
                            mime="application/json"
                        )
                    
                    with col2:
                        # Download formatted text
                        formatted_text = f"""AI Video Prompts - {prompts_data.get('prompt_type', 'AI')}
Model: {prompts_data.get('model', 'N/A')}
Cameos: {', '.join(prompts_data.get('cameos', [])) if prompts_data.get('cameos') else 'None'}

Script:
{prompts_data.get('script', 'N/A')}

{json.dumps(prompts_json, indent=2)}
"""
                        st.download_button(
                            label="📥 Download Text",
                            data=formatted_text,
                            file_name=f"{prompts_data.get('prompt_type', 'ai')}_prompts.txt",
                            mime="text/plain"
                        )
                
                else:
                    st.error(f"❌ Failed to generate prompts: {prompts_data.get('error', 'Unknown error')}")
                    st.info("💡 Make sure transcription is enabled and completed successfully.")


def main():
    """Main Streamlit application."""
    init_streamlit_config()
    render_header()
    
    # Get preview options from sidebar
    options = render_sidebar()
    
    # Downloader method selection - 3 options now
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        use_rapidapi = st.button(
            "� Instagram (RapidAPI)",
            use_container_width=True,
            type="primary",
            help="Instagram downloader using RapidAPI - bypasses rate limits"
        )
    
    with col2:
        use_iiilab = st.button(
            "🎬 YouTube (iiiLab)",
            use_container_width=True,
            help="YouTube downloader using iiiLab API - fast and reliable"
        )
    
    with col3:
        use_standard = st.button(
            "🔧 Standard Downloaders",
            use_container_width=True,
            help="Traditional method using Instaloader/yt-dlp (may face rate limits)"
        )
    
    # Store selection in session state
    if use_rapidapi:
        st.session_state.downloader_method = "rapidapi"
    elif use_iiilab:
        st.session_state.downloader_method = "iiilab"
    elif use_standard:
        st.session_state.downloader_method = "standard"
    
    # Default to RapidAPI if not set
    if "downloader_method" not in st.session_state:
        st.session_state.downloader_method = "rapidapi"
    
    st.markdown("---")
    
    # Show appropriate interface based on selection
    if st.session_state.downloader_method == "rapidapi":
        handle_rapidapi_download(options)
    elif st.session_state.downloader_method == "iiilab":
        handle_iiilab_download(options)
    else:
        handle_standard_download(options)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: gray; font-size: 0.8em;">
        <p>Multi-Platform Media Downloader | No Local Storage | Built with Streamlit</p>
        <p>⚠️ Please respect content creators' rights and platform terms of service</p>
        <p>🔒 All content is processed in memory - nothing saved to disk</p>
    </div>
    """, unsafe_allow_html=True)


def handle_rapidapi_download(options):
    """Handle downloads using RapidAPI - focused on transcription only."""
    st.subheader("🎤 Instagram to Hinglish Transcript")
    st.info("✨ Enter Instagram URL below to get automatic Hinglish transcription")
    
    # URL input
    url_input = st.text_input(
        label="Instagram Reel/Post URL",
        placeholder="https://www.instagram.com/reel/... or https://www.instagram.com/p/...",
        help="Paste Instagram reel or post URL",
        key="rapidapi_url_input"
    )
    
    # Download button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        download_btn = st.button("� Get Transcript", use_container_width=True, type="primary", key="rapidapi_download_btn")
    
    if download_btn:
        if not url_input.strip():
            st.error("❌ Please enter an Instagram URL")
            return
        
        # Validate Instagram URL
        if not is_valid_instagram_url(url_input.strip()):
            st.error("❌ Please enter a valid Instagram URL (must contain instagram.com)")
            return
        
        # Check Groq API key
        groq_api_key = options.get("groq_api_key") or os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            st.error("❌ Groq API key not found. Please add GROQ_API_KEY to your .env file")
            st.info("Get your free API key at: https://console.groq.com")
            return
        
        # Single progress indicator
        progress_placeholder = st.empty()
        
        try:
            import requests
            from moviepy.editor import VideoFileClip
            import tempfile
            from pathlib import Path
            from io import BytesIO
            
            # Step 1: Fetch from RapidAPI
            progress_placeholder.info("🔍 Fetching content from Instagram...")
            
            api_url = "https://instagram-story-downloader-media-downloader.p.rapidapi.com/unified/url"
            headers = {
                "x-rapidapi-key": "0d7481b280mshcd4e4845f499b53p1ddf9djsnb259e8d623b6",
                "x-rapidapi-host": "instagram-story-downloader-media-downloader.p.rapidapi.com"
            }
            
            response = requests.get(api_url, headers=headers, params={"url": url_input.strip()}, timeout=30)
            
            if response.status_code != 200:
                progress_placeholder.empty()
                st.error(f"❌ Failed to fetch content (Error {response.status_code})")
                return
            
            data = response.json()
            if not data.get("success"):
                progress_placeholder.empty()
                st.error("❌ Could not fetch Instagram content")
                return
            
            # Extract media info
            media_type = data.get("media_type", "unknown")
            content = data.get("data", {}).get("content", {})
            media_url = content.get("media_url")
            title = data.get("data", {}).get("title", "Instagram Media")
            
            if not media_url:
                progress_placeholder.empty()
                st.error("❌ No media URL found")
                return
            
            if media_type != "video":
                progress_placeholder.empty()
                st.warning("⚠️ Only video content can be transcribed (no audio in images)")
                return
            
            # Step 2: Download video
            progress_placeholder.info("📥 Downloading video...")
            media_response = requests.get(media_url, timeout=60)
            media_response.raise_for_status()
            video_data = media_response.content
            
            # Step 3: Extract audio
            progress_placeholder.info("🎵 Extracting audio from video...")
            
            temp_dir = tempfile.mkdtemp()
            temp_video = Path(temp_dir) / "video.mp4"
            temp_audio = Path(temp_dir) / "audio.mp3"
            
            # Write video to temp file
            with open(temp_video, "wb") as f:
                f.write(video_data)
            
            # Extract audio
            video_clip = VideoFileClip(str(temp_video))
            if video_clip.audio is None:
                video_clip.close()
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                progress_placeholder.empty()
                st.warning("⚠️ No audio found in this video")
                return
            
            video_clip.audio.write_audiofile(str(temp_audio), verbose=False, logger=None)
            video_clip.close()
            
            # Read audio into memory
            with open(temp_audio, "rb") as f:
                audio_data = f.read()
            
            # Cleanup temp files
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            # Step 4: Transcribe with Groq
            progress_placeholder.info("🎤 Transcribing to Hinglish (this may take a minute)...")
            
            from src.core.groq_transcriber import GroqTranscriber
            import tempfile
            
            transcriber = GroqTranscriber(api_key=groq_api_key)
            
            # Save audio to temp file (Groq needs file path)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
                temp_audio_file.write(audio_data)
                temp_audio_path = temp_audio_file.name
            
            try:
                # Use transcribe_and_process which includes post-processing
                result = transcriber.transcribe_and_process(
                    temp_audio_path,
                    enable_post_processing=True  # Always enable Hinglish for RapidAPI
                )
                
                transcript_text = result.get("final_transcription", "")
                
            finally:
                # Cleanup temp file
                import os
                try:
                    os.unlink(temp_audio_path)
                except:
                    pass
            
            # Clear progress
            progress_placeholder.empty()
            
            if not transcript_text:
                st.error("❌ Transcription returned empty result")
                return
            
            # Display result
            st.success("✅ Transcription Complete!")
            st.markdown(f"**Title:** {title}")
            st.markdown("---")
            
            # Show transcript
            st.subheader("📝 Hinglish Transcript (Roman Script)")
            st.text_area(
                "Transcript",
                value=transcript_text,
                height=300,
                key="rapidapi_transcript_result",
                label_visibility="collapsed"
            )
            
            # Download button for transcript
            st.download_button(
                label="💾 Download Transcript (.txt)",
                data=transcript_text,
                file_name=f"transcript_{title.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
        except Exception as e:
            progress_placeholder.empty()
            st.error(f"❌ Error: {str(e)}")
            import traceback
            with st.expander("🔍 Technical Details"):
                st.code(traceback.format_exc())
                            
            st.error(f"❌ Error: {str(e)}")
            import traceback
            with st.expander("🔍 Error Details"):
                st.code(traceback.format_exc())


def handle_iiilab_download(options):
    """Handle downloads using iiiLab YouTube API with Groq transcription."""
    st.subheader("🎬 YouTube to Hinglish Transcript")
    st.info("📝 Enter a YouTube URL to get an AI-powered Hinglish transcript using Groq Whisper + Llama 3.3")
    
    # Simple URL input
    url_input = st.text_input("🔗 YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
    
    # Get Transcript button
    if st.button("🚀 Get Transcript", type="primary", use_container_width=True):
        if not url_input:
            st.error("❌ Please enter a YouTube URL")
            return
        
        # Validate YouTube URL
        if not ('youtube.com' in url_input or 'youtu.be' in url_input):
            st.error("❌ Please enter a valid YouTube URL")
            return
        
        try:
            # Fetch video from iiiLab API
            with st.spinner("📥 Fetching video from YouTube..."):
                import requests
                import time
                from hashlib import md5
                
                # Prepare iiiLab API request
                timestamp = str(int(time.time() * 1000))
                language = "en"
                key = "6HTugjCXxR"
                signature = md5((url_input + language + timestamp + key).encode()).hexdigest()
                
                headers = {
                    "G-Timestamp": timestamp,
                    "G-Footer": signature,
                    "Accept-Language": language,
                    "Content-Type": "application/json"
                }
                
                payload = {"link": url_input}
                
                # Call iiiLab API
                response = requests.post(
                    "https://api.snapany.com/v1/extract",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code != 200:
                    st.error(f"❌ Failed to fetch video. Status code: {response.status_code}")
                    st.error(f"Response: {response.text}")
                    return
                
                api_data = response.json()
                
                # Extract audio/video URLs from response
                if not api_data.get('medias'):
                    st.error("❌ No media data found in API response")
                    with st.expander("🔍 API Response"):
                        st.json(api_data)
                    return
                
                # Get audio and video URLs from medias array
                medias = api_data['medias']
                audio_url = None
                video_url = None
                
                # Try to find direct audio first (faster - no extraction needed!)
                for media in medias:
                    if media.get('media_type') == 'audio' and media.get('resource_url'):
                        audio_url = media['resource_url']
                        st.info("🎵 Found direct audio URL - skipping video extraction!")
                        break
                
                # Fallback: Find video if no audio found
                if not audio_url:
                    for media in medias:
                        if media.get('media_type') == 'video' and media.get('resource_url'):
                            video_url = media['resource_url']
                            break
                
                if not audio_url and not video_url:
                    st.error("❌ No valid audio or video URL found")
                    with st.expander("🔍 Medias Data"):
                        st.json(medias)
                    return
            
            # Download audio (either direct or extract from video)
            temp_audio_path = None
            
            if audio_url:
                # Direct audio download with retry logic and progress
                max_retries = 3
                retry_delay = 2
                download_success = False
                
                for attempt in range(max_retries):
                    try:
                        # Use streaming to handle large files with browser-like headers
                        session = requests.Session()
                        # Full browser headers to avoid 403 from YouTube CDN
                        session.headers.update({
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                            'Accept': '*/*',
                            'Accept-Language': 'en-US,en;q=0.9',
                            'Accept-Encoding': 'identity;q=1, *;q=0',
                            'Connection': 'keep-alive',
                            'Referer': 'https://www.youtube.com/',
                            'Origin': 'https://www.youtube.com',
                            'Sec-Fetch-Dest': 'audio',
                            'Sec-Fetch-Mode': 'cors',
                            'Sec-Fetch-Site': 'cross-site',
                        })
                        
                        audio_response = session.get(
                            audio_url, 
                            timeout=(30, 180),  # (connect timeout, read timeout)
                            stream=True,
                            allow_redirects=True
                        )
                        audio_response.raise_for_status()
                        download_success = True
                        
                        # Get total file size
                        total_size = int(audio_response.headers.get('content-length', 0))
                        total_size_mb = total_size / (1024 * 1024)
                        
                        # Create progress bar and status
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Download in chunks with progress
                        audio_content = bytearray()
                        downloaded = 0
                        
                        for chunk in audio_response.iter_content(chunk_size=32768):  # 32KB chunks
                            if chunk:
                                audio_content.extend(chunk)
                                downloaded += len(chunk)
                                
                                # Update progress
                                if total_size > 0:
                                    progress = downloaded / total_size
                                    downloaded_mb = downloaded / (1024 * 1024)
                                    progress_bar.progress(progress)
                                    status_text.text(f"📥 Downloading: {downloaded_mb:.1f} / {total_size_mb:.1f} MB ({progress*100:.1f}%)")
                        
                        # Clear progress indicators
                        progress_bar.empty()
                        status_text.empty()
                        
                        audio_size_mb = len(audio_content) / (1024 * 1024)
                        st.success(f"✅ Downloaded audio: {audio_size_mb:.2f} MB")
                        
                        # Store in memory (no disk usage!)
                        audio_data = io.BytesIO(audio_content)
                        
                        break  # Success - exit retry loop
                        
                    except (requests.exceptions.ChunkedEncodingError, 
                            requests.exceptions.ConnectionError,
                            requests.exceptions.Timeout) as e:
                        if attempt < max_retries - 1:
                            st.warning(f"⚠️ Download interrupted (attempt {attempt + 1}/{max_retries}). Retrying in {retry_delay}s...")
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                        else:
                            raise Exception(f"Failed to download audio after {max_retries} attempts: {str(e)}")
                    except requests.exceptions.HTTPError as e:
                        # 403 Forbidden - YouTube CDN blocked direct access
                        if e.response.status_code == 403:
                            st.warning(f"⚠️ Direct audio download blocked (403). Will try video extraction instead...")
                            download_success = False
                            break  # Exit retry loop, will fall through to video extraction
                        else:
                            if attempt < max_retries - 1:
                                st.warning(f"⚠️ HTTP Error {e.response.status_code} (attempt {attempt + 1}/{max_retries}). Retrying...")
                                time.sleep(retry_delay)
                                retry_delay *= 2
                            else:
                                raise
                
                # If audio download failed due to 403, fall back to video extraction
                if not download_success and video_url:
                    st.info("🎬 Falling back to video download and audio extraction...")
                    audio_url = None  # Force video extraction path
            
            if not audio_url or (audio_url and not download_success):
                # Fallback: Extract audio from video with progress
                if not video_url:
                    raise Exception("No video URL available for fallback extraction")
                    
                max_retries = 3
                retry_delay = 2
                
                for attempt in range(max_retries):
                    try:
                        # Use streaming for large video files with browser-like headers
                        session = requests.Session()
                        session.headers.update({
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                            'Accept': '*/*',
                            'Accept-Language': 'en-US,en;q=0.9',
                            'Accept-Encoding': 'identity;q=1, *;q=0',
                            'Connection': 'keep-alive',
                            'Referer': 'https://www.youtube.com/',
                            'Origin': 'https://www.youtube.com',
                            'Sec-Fetch-Dest': 'video',
                            'Sec-Fetch-Mode': 'cors',
                            'Sec-Fetch-Site': 'cross-site',
                        })
                        
                        video_response = session.get(
                            video_url, 
                            timeout=(30, 180),
                            stream=True,
                            allow_redirects=True
                        )
                        video_response.raise_for_status()
                        
                        # Get total file size
                        total_size = int(video_response.headers.get('content-length', 0))
                        total_size_mb = total_size / (1024 * 1024)
                        
                        # Create progress bar and status
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Download in chunks with progress
                        video_content = bytearray()
                        downloaded = 0
                        
                        for chunk in video_response.iter_content(chunk_size=32768):
                            if chunk:
                                video_content.extend(chunk)
                                downloaded += len(chunk)
                                
                                # Update progress
                                if total_size > 0:
                                    progress = downloaded / total_size
                                    downloaded_mb = downloaded / (1024 * 1024)
                                    progress_bar.progress(progress)
                                    status_text.text(f"📥 Downloading video: {downloaded_mb:.1f} / {total_size_mb:.1f} MB ({progress*100:.1f}%)")
                        
                        # Clear progress indicators
                        progress_bar.empty()
                        status_text.empty()
                        
                        video_data = io.BytesIO(video_content)
                        video_size_mb = len(video_content) / (1024 * 1024)
                        st.success(f"✅ Downloaded video: {video_size_mb:.2f} MB")
                        
                        break  # Success - exit retry loop
                        
                    except (requests.exceptions.ChunkedEncodingError,
                            requests.exceptions.ConnectionError,
                            requests.exceptions.Timeout) as e:
                        if attempt < max_retries - 1:
                            st.warning(f"⚠️ Download interrupted (attempt {attempt + 1}/{max_retries}). Retrying in {retry_delay}s...")
                            time.sleep(retry_delay)
                            retry_delay *= 2
                        else:
                            raise Exception(f"Failed to download video after {max_retries} attempts: {str(e)}")
                    except requests.exceptions.HTTPError as e:
                        # YouTube CDN may block video too
                        if attempt < max_retries - 1:
                            st.warning(f"⚠️ HTTP Error {e.response.status_code} (attempt {attempt + 1}/{max_retries}). Retrying...")
                            time.sleep(retry_delay)
                            retry_delay *= 2
                        else:
                            raise Exception(f"YouTube CDN blocked download (Error {e.response.status_code}). This video may have download restrictions. Try a different video.")
                
                # Extract audio from video
                with st.spinner("🎵 Extracting audio from video..."):
                    from moviepy.editor import VideoFileClip
                    import tempfile
                    
                    # Use temporary file (will be auto-deleted)
                    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_video:
                        temp_video_path = temp_video.name
                        temp_video.write(video_data.getvalue())
                    
                    # Use temporary file for audio output
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
                        temp_audio_path = temp_audio.name
                    
                    try:
                        # Extract audio
                        video_clip = VideoFileClip(temp_video_path)
                        audio_clip = video_clip.audio
                        
                        # Save audio to temp file
                        audio_clip.write_audiofile(temp_audio_path, verbose=False, logger=None)
                        
                        # Load audio into memory
                        with open(temp_audio_path, 'rb') as f:
                            audio_data = io.BytesIO(f.read())
                        
                        # Clean up
                        audio_clip.close()
                        video_clip.close()
                        
                        st.success("✅ Audio extracted successfully")
                    finally:
                        # Delete temp files immediately
                        if os.path.exists(temp_video_path):
                            os.remove(temp_video_path)
                        if os.path.exists(temp_audio_path):
                            os.remove(temp_audio_path)
            
            # Transcribe with Groq (using in-memory audio)
            with st.spinner("🤖 Transcribing with Groq AI... (Hinglish processing enabled)"):
                from src.core.groq_transcriber import GroqTranscriber
                import tempfile
                
                # Create temporary file for Groq API (required for upload)
                with tempfile.NamedTemporaryFile(suffix='.m4a', delete=False) as temp_file:
                    temp_audio_path = temp_file.name
                    temp_file.write(audio_data.getvalue())
                
                try:
                    transcriber = GroqTranscriber()
                    result = transcriber.transcribe_and_process(
                        audio_path=temp_audio_path,
                        enable_post_processing=True  # Hinglish processing
                    )
                    
                    # Extract the final transcript
                    transcript = result.get("final_transcription", result.get("cleaned_transcription", ""))
                finally:
                    # Clean up temp file immediately after transcription
                    if os.path.exists(temp_audio_path):
                        os.remove(temp_audio_path)
            
            # Display results
            st.success("✅ Transcription complete!")
            
            # Show transcript
            st.markdown("### 📝 Hinglish Transcript")
            st.text_area(
                "Transcript",
                value=transcript,
                height=300,
                label_visibility="collapsed"
            )
            
            # Download button
            st.download_button(
                label="📥 Download Transcript",
                data=transcript,
                file_name=f"youtube_transcript_{int(time.time())}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            import traceback
            with st.expander("🔍 Error Details"):
                st.code(traceback.format_exc())


def handle_standard_download(options):
    """Handle downloads using standard Instaloader/yt-dlp method."""
    # Important notice about rate limiting
    if options.get("cookies_text"):
        st.success("🍪 **Authenticated Mode**: Using Instagram cookies for better reliability!")
    else:
        st.info("""
        ⚠️ **Important**: Instagram aggressively blocks cloud-hosted apps. If downloads fail:
        - 🍪 **Best Solution**: Add Instagram cookies in sidebar (bypasses rate limits!)
        - ✅ Download the **desktop version** from [GitHub Releases](https://github.com/dhruvagrawal27/insta-downloader-gui/releases)
        - ✅ Run locally: `git clone` → `streamlit run streamlit_preview_app.py`
        - ⏰ Wait 10-15 minutes if you see rate limit errors
        
        This is an Instagram API limitation, not an app issue.
        """)
    
    # Main content area
    st.subheader("🔗 Enter Instagram URL")
    
    # URL input
    url_input = st.text_input(
        label="Instagram URL",
        placeholder="https://www.instagram.com/reel/... or https://www.instagram.com/p/...",
        help="Supports Instagram Reels and Posts",
        label_visibility="collapsed",
        key="standard_url_input"
    )
    
    # Preview button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        preview_btn = st.button("🔍 Preview Content", use_container_width=True, type="primary", key="standard_preview_btn")
    
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
            
            # Generate AI prompts if requested
            if options.get("generate_prompts") and options.get("transcribe"):
                file_contents = result.get("file_contents", {})
                transcript = file_contents.get("transcript_text", "")
                
                if transcript and options.get("groq_api_key"):
                    try:
                        with st.spinner(f"Generating {options.get('prompt_type', 'AI')} prompts..."):
                            prompts_result = generate_ai_video_prompts(
                                script=transcript,
                                prompt_type=options.get("prompt_type", "Sora 2"),
                                cameo_usernames=options.get("cameo_usernames", []),
                                groq_api_key=options.get("groq_api_key"),
                                progress_callback=update_progress
                            )
                            
                            # Add to result
                            result["file_contents"]["ai_prompts"] = prompts_result
                            
                            # Also save JSON string for zip download
                            if prompts_result.get("success"):
                                result["file_contents"]["ai_prompts_json"] = json.dumps(
                                    prompts_result.get("prompts", {}), 
                                    indent=2
                                )
                    except Exception as e:
                        st.warning(f"⚠️ Prompt generation failed: {str(e)}")
                elif not transcript:
                    st.warning("⚠️ No transcript available. Enable transcription first.")
                elif not options.get("groq_api_key"):
                    st.warning("⚠️ Groq API key required for prompt generation.")
            elif options.get("generate_prompts") and not options.get("transcribe"):
                st.warning("⚠️ Transcription must be enabled to generate AI prompts.")
            
            # Clear progress indicators
            progress_bar.progress(100)
            status_text.empty()
            
            # Display preview
            display_media_preview(result)
            
        except Exception as e:
            error_msg = str(e)
            st.error(f"❌ Failed to load content: {error_msg}")
            
            # Provide helpful suggestions based on error type
            if "rate limit" in error_msg.lower() or "429" in error_msg:
                st.warning("⏰ **Instagram Rate Limit Detected**")
                st.info("""
                **What happened:** Instagram is temporarily blocking too many requests.
                
                **Solutions:**
                1. ✅ Wait 5-10 minutes before trying again
                2. ✅ Try a different Instagram URL
                3. ✅ Use a VPN or different network (if available)
                4. ✅ Try the RapidAPI downloader (click button above)
                
                **Why this happens:** Streamlit Cloud shares IP addresses, and Instagram may block high traffic.
                """)
            elif "403" in error_msg or "Forbidden" in error_msg or "401" in error_msg:
                st.warning("🚫 **Access Denied by Instagram**")
                st.info("""
                **What happened:** Instagram blocked the request.
                
                **Possible reasons:**
                - Content is from a private account
                - Instagram detected automated access
                - Geographic restrictions
                - Content was deleted
                
                **Try:**
                - Use the RapidAPI downloader (more reliable)
                - Verify the URL is correct and public
                - Wait a few minutes and try again
                """)
            elif "not found" in error_msg.lower() or "yt-dlp" in error_msg.lower() and "install" in error_msg.lower():
                st.warning("📦 **Package Installation Issue**")
                st.info("""
                **What happened:** yt-dlp is not properly installed.
                
                **Try:** Use the RapidAPI downloader instead (click button above)
                """)
            elif "Private" in error_msg or "login" in error_msg.lower():
                st.info("🔒 **Note:** This appears to be private/restricted content. Only public content can be accessed.")
            else:
                st.info("💡 **Try:** Use the RapidAPI downloader or switch downloaders in the sidebar.")
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
