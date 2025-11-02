"""
Streamlit with API endpoints (experimental)
WARNING: This is a hacky solution. Streamlit is not designed for REST APIs.
Use FastAPI backend on Render for production API needs.
"""

import streamlit as st
from streamlit.web import cli as stcli
import sys
from pathlib import Path
import json
import base64

# Import your existing downloader
from src.core.downloader import download_media
from src.core.groq_transcriber import GroqTranscriber

# This creates a hidden API endpoint
def api_endpoint():
    """Handle API requests to Streamlit"""
    # Check if this is an API call
    query_params = st.query_params
    
    if "api" in query_params:
        url = query_params.get("url", "")
        transcribe = query_params.get("transcribe", "false") == "true"
        
        try:
            # Download and process
            result = download_media(url, {
                "video": False,
                "audio": True,
                "transcribe": transcribe,
                "enable_hinglish": True,
                "downloader": "yt-dlp"
            })
            
            # Return JSON
            response = {
                "status": "success",
                "audio": result.get("audio_base64", ""),
                "transcript": result.get("transcript", "")
            }
            st.json(response)
            return
            
        except Exception as e:
            st.json({"status": "error", "message": str(e)})
            return

# Regular Streamlit UI
def main():
    api_endpoint()  # Check for API calls first
    
    st.title("Instagram Downloader")
    st.write("For API access, use: https://insta-downloader-gui.onrender.com")
    
    # Your regular Streamlit UI here
    url = st.text_input("Instagram URL")
    if st.button("Download"):
        st.write(f"Downloading: {url}")

if __name__ == "__main__":
    main()
