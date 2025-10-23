# Instagram Downloader - Streamlit Web Application

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_streamlit.txt
```

### 2. Run the Web Application

#### Single URL Mode
```bash
streamlit run streamlit_app.py
```

#### Batch Download Mode (Multiple URLs)
```bash
streamlit run streamlit_batch_app.py
```

## Features

### 🌐 Web Interface
- Clean, modern web interface built with Streamlit
- No need to install desktop application
- Works on any device with a web browser
- Real-time progress tracking

### 📱 Download Options
- **Video**: Download the original video file
- **Thumbnail**: Download post thumbnail/cover image
- **Audio**: Extract audio from video
- **Caption**: Save post description/caption
- **Transcription**: AI-powered audio transcription using Whisper

### 🔧 Dual Download Engines
- **Instaloader**: Primary downloader with robust Instagram support
- **yt-dlp**: Fallback downloader with broad platform support
- Automatic fallback if primary downloader fails

### 📦 Batch Processing
- Download multiple URLs at once
- Progress tracking for each URL
- Bulk download as ZIP file
- Error handling for individual URLs

## Usage

### Single URL Download

1. Open the web application
2. Configure download options in the sidebar
3. Paste an Instagram URL
4. Click "Start Download"
5. Download the ZIP file with all media

### Batch URL Download

1. Run the batch version: `streamlit run streamlit_batch_app.py`
2. Select "Batch URLs" mode
3. Paste multiple URLs (one per line)
4. Configure download options
5. Click "Download X URLs"
6. Monitor progress for each URL
7. Download the combined ZIP file

## Configuration

### Download Options

- **Preferred Downloader**: Choose between Instaloader and yt-dlp
- **Video**: Download MP4 video files
- **Thumbnail**: Download JPG thumbnail images
- **Audio**: Extract MP3/WAV audio files
- **Caption**: Save TXT caption files
- **Transcribe**: Generate AI transcripts (requires additional processing time)

### Batch Options

- **Max Concurrent Downloads**: Control how many downloads run simultaneously (1-5)

## File Organization

Downloaded files are organized in timestamped session folders:
```
downloads/
├── session_20241023_143022/
│   ├── reel_1_shortcode/
│   │   ├── video.mp4
│   │   ├── thumbnail.jpg
│   │   ├── audio.mp3
│   │   ├── caption.txt
│   │   └── transcript.txt
│   └── reel_2_shortcode/
│       └── ...
```

## Supported URLs

- Instagram Reels: `https://www.instagram.com/reel/...`
- Instagram Posts: `https://www.instagram.com/p/...`
- Short URLs: `https://instagr.am/...`

## Requirements

- Python 3.8+
- Internet connection
- FFmpeg (for audio extraction)
- Sufficient disk space for downloads

## Deployment Options

### Local Development
```bash
streamlit run streamlit_app.py
```

### Production Deployment

#### Streamlit Cloud
1. Push code to GitHub repository
2. Connect to Streamlit Cloud
3. Deploy with `requirements_streamlit.txt`

#### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements_streamlit.txt .
RUN pip install -r requirements_streamlit.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Heroku Deployment
1. Add `Procfile`:
```
web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```
2. Deploy to Heroku

## Performance Tips

1. **Transcription**: Disable transcription for faster downloads
2. **Batch Size**: Limit concurrent downloads for better stability
3. **Network**: Use stable internet connection for large files
4. **Storage**: Ensure sufficient disk space for downloads

## Troubleshooting

### Common Issues

1. **"Invalid URL" Error**
   - Ensure URL is a valid Instagram Reel or Post
   - Check for typos in the URL

2. **Download Fails**
   - Try switching to the other downloader in sidebar
   - Check internet connection
   - Some private accounts may not be accessible

3. **Transcription Errors**
   - Transcription requires audio content
   - Large files may take longer to process

4. **Permission Errors**
   - Ensure write permissions to downloads folder
   - Check available disk space

### Error Recovery

- The app automatically tries fallback downloader if primary fails
- Individual URL failures in batch mode don't stop other downloads
- Progress is preserved if connection is temporarily lost

## License

MIT License - see LICENSE file for details

## Disclaimer

This tool is for educational purposes. Please respect:
- Instagram's Terms of Service
- Content creators' rights
- Copyright laws
- Privacy settings

Always obtain permission before downloading someone else's content.
