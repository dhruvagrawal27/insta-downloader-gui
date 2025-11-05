"""
yt-dlp Agent for Web (Streamlit): Uses yt-dlp Python package directly.
This module is specifically designed for web deployments where the executable is not available.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Union

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

from src.utils.lazy_imports import lazy_import_requests, lazy_import_moviepy
from src.core.data_models import ReelItem


def download_reel(
    item: ReelItem,
    reel_number: int,
    session_folder: Path,
    download_options: Dict[str, Union[bool, str]],
    progress_callback: Any,
) -> Dict[str, Any]:
    """
    Download individual reel and process it using yt-dlp Python package.

    Args:
        item: ReelItem to download.
        reel_number: Sequential number for file naming.
        session_folder: The root folder for the current download session.
        download_options: A dictionary of download preferences.
        progress_callback: A function to report progress updates.

    Returns:
        A dictionary containing paths to downloaded files.
    """
    if not YT_DLP_AVAILABLE:
        raise ImportError(
            "yt-dlp not found. Please install it: pip install yt-dlp"
        )
    
    result = {}
    assert session_folder is not None, "Session folder not created"
    reel_folder = session_folder / f"reel{reel_number}"
    reel_folder.mkdir(exist_ok=True)
    result["folder_path"] = str(reel_folder)

    progress_callback(item.url, 10, "Downloading with yt-dlp...")

    video_path = reel_folder / f"video{reel_number}.mp4"
    
    # yt-dlp options optimized for Instagram
    ydl_opts = {
        'outtmpl': str(video_path),
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
        # Instagram-specific options to bypass rate limiting
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
        'extractor_args': {
            'instagram': {
                'api_mode': 'embed',  # Use embed API to avoid rate limits
            }
        },
        'socket_timeout': 30,
        'retries': 3,
        'fragment_retries': 3,
    }
    
    # Add cookies if available (helps with private/restricted content)
    cookies_file = Path.home() / '.yt-dlp' / 'cookies.txt'
    if cookies_file.exists():
        ydl_opts['cookiefile'] = str(cookies_file)
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Download the video
            info = ydl.extract_info(item.url, download=True)
            metadata = ydl.sanitize_info(info)
            
            result["video_path"] = str(video_path)
            
            # Handle thumbnail
            if download_options.get("thumbnail"):
                thumb_url = metadata.get("thumbnail")
                if thumb_url:
                    thumb_path = reel_folder / f"thumbnail{reel_number}.jpg"
                    try:
                        requests_module = lazy_import_requests()
                        resp = requests_module.get(thumb_url, timeout=30, headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        })
                        resp.raise_for_status()
                        with open(thumb_path, "wb") as f:
                            f.write(resp.content)
                        result["thumbnail_path"] = str(thumb_path)
                    except Exception as e:
                        print(f"Failed to download thumbnail: {e}")
            
            # Handle caption
            if download_options.get("caption"):
                caption = metadata.get("description", "No caption available")
                caption_path = reel_folder / f"caption{reel_number}.txt"
                with open(caption_path, "w", encoding="utf-8") as f:
                    f.write(caption)
                result["caption_path"] = str(caption_path)
                result["caption"] = caption
            
            # Handle audio extraction
            if download_options.get("audio"):
                _extract_audio(
                    reel_folder, reel_number, result, download_options, progress_callback
                )
            
            result["title"] = metadata.get("title", f"Reel {reel_number}")
            progress_callback(item.url, 100, "Completed")
            
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if "429" in error_msg or "rate limit" in error_msg.lower():
            raise Exception(
                "Instagram rate limit reached. Please try again in a few minutes "
                "or use a different downloader."
            )
        elif "401" in error_msg or "403" in error_msg:
            raise Exception(
                "Access denied by Instagram. The content might be private or "
                "requires authentication. Try logging in with cookies."
            )
        else:
            raise Exception(f"Failed to download: {error_msg}")
    
    return result


def _extract_audio(
    reel_folder: Path,
    reel_number: int,
    result: Dict,
    download_options: Dict,
    progress_callback: Any,
):
    """
    Extracts audio from the downloaded video file if enabled.

    Args:
        reel_folder: The folder where the reel is downloaded.
        reel_number: Sequential number for file naming.
        result: Dictionary to store download results.
        download_options: A dictionary of download preferences.
        progress_callback: A function to report progress updates.
    """
    if not download_options.get("audio", True):
        return

    progress_callback("", 60, "Extracting audio...")
    video_path = result.get("video_path") or str(
        reel_folder / f"video{reel_number}.mp4"
    )
    if not os.path.exists(video_path):
        return
    
    audio_path = reel_folder / f"audio{reel_number}.mp3"
    video_clip = None
    audio_clip = None
    
    try:
        VideoFileClip = lazy_import_moviepy()
        video_clip = VideoFileClip(video_path)
        if video_clip.audio is not None:
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(str(audio_path), verbose=False, logger=None)
            result["audio_path"] = str(audio_path)
    except Exception as e:
        print(f"Failed to extract audio: {e}")
    finally:
        _cleanup_video_resources(audio_clip, video_clip)


def _cleanup_video_resources(audio_clip, video_clip):
    """
    Safely closes and cleans up moviepy video and audio clip resources.

    Args:
        audio_clip: The audio clip object to close.
        video_clip: The video clip object to close.
    """
    if audio_clip:
        try:
            audio_clip.close()
        except Exception:
            pass
    if video_clip:
        try:
            video_clip.close()
        except Exception:
            pass


def check_availability() -> bool:
    """Check if yt-dlp is available."""
    return YT_DLP_AVAILABLE
