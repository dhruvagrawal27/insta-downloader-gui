# Usage Guide - Instagram Downloader Web App# Usage Guide



A comprehensive guide for using the Instagram Downloader web application with Groq AI transcription.A comprehensive guide on how to use the insta-downloader-gui - a PyQt6-based desktop app to download Instagram Reels, posts, and stories quickly and reliably.



**See Also**: ## Table of Contents

- [Main README](README.md) - Overview and features

- [Preview Mode Guide](../PREVIEW_MODE_README.md) - Zero local storage mode- [Overview](#overview)

- [Groq Transcription](../GROQ_TRANSCRIPTION_README.md) - AI transcription details- [Quick Start](#quick-start)

- [Quick Start Groq](../QUICK_START_GROQ.md) - 5-minute setup- [Installation](#installation)

- [Running the Application](#running-the-application)

## Table of Contents- [User Interface Guide](#user-interface-guide)

- [Supported URL Types](#supported-url-types)

- [Overview](#overview)- [Download Options](#download-options)

- [Quick Start](#quick-start)- [Troubleshooting](#troubleshooting)

- [Running the Application](#running-the-application)- [Best Practices](#best-practices)

- [User Interface Guide](#user-interface-guide)- [FAQ](#faq)

- [Supported URLs](#supported-urls)

- [Download Options](#download-options)## Overview

- [Groq Transcription Setup](#groq-transcription-setup)

- [Troubleshooting](#troubleshooting)The insta-downloader-gui is a professional-grade tool designed to download media content from Instagram efficiently. Built with PyQt6, it provides an intuitive desktop interface for:

- [Best Practices](#best-practices)

- [FAQ](#faq)- **Media Extraction**: Download videos, thumbnails, and captions from Instagram.

- **Batch Processing**: Download multiple files simultaneously with progress tracking.

## Overview- **Audio Extraction**: Extract and save audio from videos.

- **Transcription**: Transcribe audio to text using OpenAI's Whisper model.

The Instagram Downloader is a **web-based application** built with Streamlit for downloading Instagram media with AI-powered transcription.- **Flexible Output**: Save files in organized, timestamped folders.

- **Dual Download Engines**: Uses both `instaloader` and `yt-dlp` for maximum reliability.

### Key Capabilities

- **Web Interface**: Browser-based, no desktop app needed## Quick Start

- **Preview Mode**: Zero local storage option

- **Groq AI**: Fast Hinglish transcription### Prerequisites

- **Batch Processing**: Multiple URLs at once

- **Cloud Deployment**: Deploy anywhere- Python 3.7 or higher

- Internet connection

## Quick Start

### Installation

```bash

# 1. Install```bash

pip install -r requirements_streamlit.txt# Clone the repository

git clone https://github.com/dhruvagrawal27/insta-downloader-gui.git

# 2. Run

streamlit run streamlit_preview_app.py# Navigate to the project directory

cd insta-downloader-gui

# 3. Use

# - Open browser (auto-opens)# Install required dependencies

# - Paste Instagram URLpip install -r requirements.txt

# - Click Preview/Download```

```

## Running the Application

## Running the Application

```bash

### Three Modes Availablepython src/main.py

```

#### 1. Preview Mode (Recommended)

```bashThe application will launch, and you can start downloading media.

streamlit run streamlit_preview_app.py

```## User Interface Guide

- ✅ No local storage

- ✅ Preview before download### Main Interface Components

- ✅ Individual file downloads

#### 1. URL Input Section

#### 2. Single URL Mode- **URL Input Field**: Enter any valid Instagram URL.

```bash- **Add to Queue Button**: Add the URL to the download queue.

streamlit run streamlit_app.py

```#### 2. Download Options

- ✅ One URL at a time- **Downloader Selection**: Choose between `instaloader` and `yt-dlp`.

- ✅ Auto ZIP package- **Content Selection**: Checkboxes to select what to download (video, thumbnail, audio, caption, transcribe).



#### 3. Batch Mode#### 3. Queue and Progress

```bash- **Queue List**: Shows the list of URLs to be downloaded.

streamlit run streamlit_batch_app.py- **Progress Bar**: Displays the overall download progress.

```- **Progress Label**: Shows the status of the current download.

- ✅ Multiple URLs

- ✅ Progress tracking#### 4. Action Buttons

- **Start Download**: Begins the download process for all items in the queue.

See **[STREAMLIT_README.md](../STREAMLIT_README.md)** for mode comparison.- **Clear Queue**: Clears the download queue.

- **Open Folder**: Opens the folder where downloaded files are saved.

## User Interface Guide

#### 5. Results and Logs

### Sidebar Configuration- **Results Tab**: Displays the details of completed downloads.

- **Downloader**: yt-dlp (recommended) or Instaloader- **Log Tab**: Shows detailed logs of the download process.

- **Content**: Video, Thumbnail, Audio, Caption, Transcribe

- **Groq Settings**: API key, Hinglish processing## Supported URL Types



### Main Area### Instagram Post URLs

- **URL Input**: Paste Instagram URL```

- **Actions**: Preview or Downloadhttps://www.instagram.com/p/Cxyz123.../

- **Results**: Preview/download area```



### Preview Section (Preview Mode)### Instagram Reel URLs

- Thumbnail preview```

- Video playerhttps://www.instagram.com/reel/Cxyz123.../

- Audio player```

- Caption display

- Transcript display### Instagram Story URLs

- Individual download buttons(Requires login, not yet supported in the GUI)



## Supported URLs## Download Options



### ✅ Works### Content Selection

```- **Video**: Download the video file (.mp4).

https://www.instagram.com/reel/ABC123/- **Thumbnail**: Download the post/reel thumbnail (.jpg).

https://www.instagram.com/p/ABC123/- **Audio**: Extract and save the audio from the video (.mp3).

https://instagr.am/p/ABC123/- **Caption**: Save the post/reel caption as a text file (.txt).

```- **Transcribe**: Transcribe the audio to text using the Whisper model.



### ❌ Doesn't Work### Downloader Engine

- Stories (24-hour expiration)- **Instaloader**: A popular and powerful Instagram scraping library.

- Private accounts- **yt-dlp**: A versatile video downloader that also supports Instagram.

- IGTV (deprecated)The application will automatically fall back to the other downloader if the selected one fails.



## Download Options## Troubleshooting



### Content Types### Common Issues and Solutions

- **Video** (MP4): Main content

- **Thumbnail** (JPG): Cover image#### "Invalid URL"

- **Audio** (MP3): Extracted audio**Possible Causes:**

- **Caption** (TXT): Post description- The URL is not a valid Instagram URL.

- **Transcription** (TXT): AI-generated text- The URL is for a private account or post.



### Downloaders**Solutions:**

- **yt-dlp**: More reliable (recommended)1. Verify the URL is a public Instagram post or reel.

- **Instaloader**: Instagram-specific features2. Copy the URL directly from Instagram.



## Groq Transcription Setup#### Download Failures

**Possible Causes:**

### 1. Get API Key- Network interruption.

- Visit [console.groq.com](https://console.groq.com)- Instagram's anti-scraping measures.

- Sign up (free)- The post has been deleted.

- Create API key

**Solutions:**

### 2. Configure1. Check your internet connection.

```bash2. Try the other downloader engine.

# Create .env file3. Wait a few minutes and try again.

GROQ_API_KEY=gsk_your_key_here

```## Best Practices



### 3. Use### Ethical Usage

- Enable "Transcribe" in sidebar- Respect Instagram's Terms of Service.

- Toggle "Hinglish Processing" (recommended)- Only download content you have permission to use.

- Download as usual- Consider copyright and intellectual property rights.

- Don't overload Instagram's servers with excessive requests.

See **[GROQ_TRANSCRIPTION_README.md](../GROQ_TRANSCRIPTION_README.md)** for details.

### Performance Optimization

## Troubleshooting- Start with a small batch of URLs to test.

- If one downloader fails, try the other.

### Invalid URL

- Check URL format## FAQ

- Ensure public post

- Remove tracking parameters### General Questions



### Download Fails**Q: Is this application free to use?**

- Switch downloaderA: Yes, this is an open-source project under the MIT license.

- Wait and retry

- Check internet**Q: Do I need an Instagram account?**

A: For public posts, no. For private posts or stories, you would need to be logged in, which is not yet supported by the GUI.

### 403 Forbidden

- Use **yt-dlp** downloader**Q: Can I download from private Instagram accounts?**

- Clear cacheA: No, only publicly accessible content can be downloaded.

- Try different network

### Technical Questions

### Transcription Error

- Verify API key**Q: Why is my download slow?**

- Check rate limits (30/min)A: Download speed depends on your internet connection and the size of the media files.

- Ensure video has audio

**Q: Where are downloaded files saved?**

### Memory Issues (Batch)A: Files are saved in a `downloads` folder within the application's directory, organized into timestamped session folders.

- Reduce concurrent downloads
- Use single URL mode
- Process smaller batches

## Best Practices

### Ethical Usage
- ✅ Respect Terms of Service
- ✅ Only public content
- ✅ Get permission
- ✅ Credit creators

### Performance
- Disable transcription for speed
- Use yt-dlp downloader
- Limit batch size (10-20 URLs)
- Preview mode for testing

### Storage
- Preview mode: Download before closing
- Other modes: Files in `downloads/`
- Clean up old sessions
- Monitor disk space

## FAQ

**Q: Is it free?**
A: Yes, MIT license.

**Q: Need Instagram account?**
A: No for public content.

**Q: Works on mobile?**
A: Yes, but desktop recommended.

**Q: Download private posts?**
A: No, only public content.

**Q: Where are files saved?**
A: Preview = memory, Others = `downloads/` folder.

**Q: Transcription cost?**
A: Free tier: 30 requests/minute.

**Q: Hinglish accuracy?**
A: Very accurate with LLM post-processing.

**Q: Deploy online?**
A: Yes, Streamlit Cloud/Heroku/Docker supported.

---

**More Help**: [GitHub Issues](https://github.com/dhruvagrawal27/insta-downloader-gui/issues)

**Related Guides**:
- [Main README](README.md)
- [Preview Mode](../PREVIEW_MODE_README.md)
- [Streamlit Apps](../STREAMLIT_README.md)
- [Groq Setup](../QUICK_START_GROQ.md)
- [Technical Docs](../IMPLEMENTATION_SUMMARY.md)
