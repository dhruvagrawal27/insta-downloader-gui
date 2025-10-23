"""
Configuration file for Streamlit deployment
"""

import streamlit as st
import os
from pathlib import Path

# Streamlit configuration
def configure_streamlit():
    """Configure Streamlit settings for the Instagram downloader."""
    
    # Page configuration
    st.set_page_config(
        page_title="Instagram Media Downloader",
        page_icon="📱",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/uikraft-hub/insta-downloader-gui',
            'Report a bug': 'https://github.com/uikraft-hub/insta-downloader-gui/issues',
            'About': """
            # Instagram Media Downloader
            
            A web application for downloading Instagram Reels and Posts.
            
            **Features:**
            - Download videos, thumbnails, audio
            - Extract captions and generate transcripts
            - Batch downloading support
            - Multiple download engines
            
            **Version:** 1.0.0
            **License:** MIT
            """
        }
    )

# Environment configuration
def setup_environment():
    """Set up the environment for the application."""
    
    # Create necessary directories
    directories = [
        "downloads",
        "temp",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    # Set environment variables for better performance
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    os.environ["STREAMLIT_THEME_BASE"] = "dark"

# Cache configuration
@st.cache_data
def load_app_config():
    """Load application configuration."""
    return {
        "app_name": "Instagram Media Downloader",
        "version": "1.0.0",
        "author": "ukr",
        "supported_formats": ["mp4", "jpg", "mp3", "txt"],
        "max_file_size": "500MB",
        "supported_platforms": ["Instagram Reels", "Instagram Posts"]
    }

# Session state initialization
def init_session_state():
    """Initialize Streamlit session state variables."""
    
    if 'download_history' not in st.session_state:
        st.session_state.download_history = []
    
    if 'current_downloads' not in st.session_state:
        st.session_state.current_downloads = {}
    
    if 'app_config' not in st.session_state:
        st.session_state.app_config = load_app_config()
    
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {
            "preferred_downloader": "Instaloader",
            "download_video": True,
            "download_thumbnail": True,
            "download_audio": True,
            "download_caption": True,
            "enable_transcription": False
        }

# CSS styling
def get_custom_css():
    """Return custom CSS for the application."""
    return """
    <style>
    /* Main app styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(90deg, #833ab4, #fd1d1d, #fcb045);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .header-title {
        color: white;
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
    }
    
    .header-subtitle {
        color: white;
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Progress styling */
    .download-progress {
        margin: 1rem 0;
        padding: 1rem;
        background-color: #f0f2f6;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
    }
    
    .progress-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 0.5rem 0;
        padding: 0.5rem;
        background: white;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Success/Error styling */
    .success-item {
        border-left: 4px solid #28a745;
        background-color: #f8fff9;
    }
    
    .error-item {
        border-left: 4px solid #dc3545;
        background-color: #fff8f8;
    }
    
    /* Download button styling */
    .download-button {
        background: linear-gradient(90deg, #28a745, #20c997);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-size: 1.1rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .download-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
    }
    
    /* URL input styling */
    .url-input {
        border: 2px solid #e1e5e9;
        border-radius: 8px;
        padding: 0.75rem;
        font-size: 1rem;
        transition: border-color 0.3s ease;
    }
    
    .url-input:focus {
        border-color: #1f77b4;
        box-shadow: 0 0 0 3px rgba(31, 119, 180, 0.1);
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        color: #6c757d;
        font-size: 0.9rem;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid #e1e5e9;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .header-title {
            font-size: 1.5rem;
        }
        
        .header-subtitle {
            font-size: 1rem;
        }
        
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    
    /* Animation for progress bars */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .pulsing {
        animation: pulse 2s infinite;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    </style>
    """

# JavaScript for enhanced interactivity
def get_custom_js():
    """Return custom JavaScript for the application."""
    return """
    <script>
    // Auto-refresh progress every 2 seconds during downloads
    function autoRefreshProgress() {
        if (window.downloadInProgress) {
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        }
    }
    
    // Copy to clipboard functionality
    function copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            // Show success message
            const toast = document.createElement('div');
            toast.textContent = 'Copied to clipboard!';
            toast.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #28a745;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                z-index: 9999;
                animation: slideIn 0.3s ease;
            `;
            document.body.appendChild(toast);
            
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 3000);
        });
    }
    
    // Add slide-in animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
    
    // Initialize auto-refresh if needed
    document.addEventListener('DOMContentLoaded', autoRefreshProgress);
    </script>
    """

# Utility functions
def format_file_size(size_bytes):
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def get_file_icon(file_extension):
    """Get appropriate icon for file type."""
    icons = {
        '.mp4': '📹',
        '.avi': '📹',
        '.mov': '📹',
        '.jpg': '🖼️',
        '.jpeg': '🖼️',
        '.png': '🖼️',
        '.mp3': '🎵',
        '.wav': '🎵',
        '.txt': '📝',
        '.json': '📄'
    }
    return icons.get(file_extension.lower(), '📄')

def validate_instagram_url(url):
    """Enhanced Instagram URL validation."""
    import re
    
    patterns = [
        r'https?://(?:www\.)?instagram\.com/(?:p|reel)/([A-Za-z0-9_-]+)/?',
        r'https?://(?:www\.)?instagr\.am/p/([A-Za-z0-9_-]+)/?',
        r'https?://ig\.me/([A-Za-z0-9_-]+)/?'
    ]
    
    for pattern in patterns:
        if re.match(pattern, url):
            return True
    
    return False
