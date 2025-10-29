# Instagram Media Downloader - Web Application

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)
[![Status: Active](https://img.shields.io/badge/Status-Active-brightgreen.svg)](STATUS.md)
[![Version: 2.0.0](https://img.shields.io/badge/Version-2.0.0-red.svg)](CHANGELOG.md)
![Language: Python](https://img.shields.io/badge/Language-Python-blue)
![Framework: Streamlit](https://img.shields.io/badge/Framework-Streamlit-FF4B4B)

<div align="center">
  <img src="https://readme-typing-svg.demolab.com/?lines=Instagram+Downloader+Web+App;Groq+AI+Transcription;Preview+Mode+%7C+No+Local+Storage;Hinglish+Support+Built-in&font=Fira%20Code&pause=1000&color=F75C7E&center=true&vCenter=true&width=1000&height=30&cursor=true">
</div>

---

## 🎯 What's This?

A **modern web application** for downloading Instagram media with **AI-powered Hinglish transcription**. No desktop installation required - runs in your browser with zero local storage!

### 🌟 Key Features

- 🌐 **Web-Based**: Access from any browser, no .exe installation
- 🎤 **Groq AI Transcription**: Fast, accurate Hinglish transcription with Roman script
- 👁️ **Preview Mode**: See all content before downloading (no local storage)
- 🔄 **Dual Downloaders**: Automatic fallback between Instaloader and yt-dlp
- 📦 **Batch Processing**: Download multiple URLs simultaneously
- 🚀 **Cloud-Ready**: Deploy to Streamlit Cloud, Heroku, Docker, etc.

---

## ✨ What's New in v2.0.0

### 🌐 Complete Web App Transformation
- ✅ **Streamlit Web Interface**: Replaced desktop app with modern web UI
- ✅ **Preview Mode**: View content before downloading (no local storage)
- ✅ **Three App Modes**: Preview, Single URL, and Batch processing
- ✅ **Cloud Deployment Ready**: Deploy to Streamlit Cloud, Heroku, Docker

### 🎤 Groq AI Integration
- ✅ **Groq Whisper API**: 10x faster transcription than local models
- ✅ **Hinglish Support**: Native Roman script transcription
- ✅ **LLM Post-Processing**: AI-powered spelling correction
- ✅ **Multi-Model Fallback**: Automatic model switching

### 🚀 Enhanced Features
- ✅ **Zero Local Storage**: Preview mode keeps everything in memory
- ✅ **Individual File Downloads**: Download each file separately
- ✅ **Better Instagram Compatibility**: yt-dlp default for reliable downloads
- ✅ **Environment Configuration**: Auto-load API keys from .env file

---

## 📚 Documentation Index

### 🚀 Quick Start Guides
- **[Getting Started](#-quick-start)** - Installation and first run
- **[Quick Start: Groq](../QUICK_START_GROQ.md)** - Set up AI transcription in 5 minutes
- **[Usage Guide](USAGE.md)** - Comprehensive usage instructions

### 📖 Feature Documentation
- **[Preview Mode](../PREVIEW_MODE_README.md)** - No local storage mode explained
- **[Streamlit Apps](../STREAMLIT_README.md)** - All three app modes compared
- **[Groq Transcription](../GROQ_TRANSCRIPTION_README.md)** - AI transcription setup
- **[Complete Groq Guide](../GROQ_COMPLETE_GUIDE.md)** - Advanced Groq features

### 🔧 Development Resources
- **[Implementation Summary](../IMPLEMENTATION_SUMMARY.md)** - Technical architecture overview
- **[Demo Script](../DEMO_SCRIPT.md)** - Testing and demonstration guide
- **[Contributing](CONTRIBUTING.md)** - How to contribute to this project
- **[Changelog](CHANGELOG.md)** - Version history and release notes

### 📋 Project Information
- **[Code of Conduct](CODE_OF_CONDUCT.md)** - Community guidelines
- **[Security Policy](SECURITY.md)** - Security and vulnerability reporting
- **[Project Status](STATUS.md)** - Current development status

---

## 🛠️ Core Features

### 🌐 Web Application Modes

#### 1. **Preview Mode** (Recommended)
- 👁️ Preview all content before downloading
- 💾 Zero local storage - everything in memory
- 📥 Download files individually or as ZIP
- 🎨 Modern, clean interface
```bash
streamlit run streamlit_preview_app.py
```

#### 2. **Single URL Mode**
- 🎯 One URL at a time
- 📦 Automatic ZIP package
- 💽 Local file saving
```bash
streamlit run streamlit_app.py
```

#### 3. **Batch Mode**
- 📋 Multiple URLs simultaneously
- 📊 Progress tracking per URL
- 📦 Bulk ZIP download
```bash
streamlit run streamlit_batch_app.py
```

### 🎤 AI Transcription Features

- **Groq Whisper API**: Fast, accurate transcription (whisper-large-v3-turbo)
- **Hinglish Support**: Proper Roman script for Hindi/Hinglish content
- **LLM Post-Processing**: Context-aware spelling correction using Llama models
- **Multi-Language**: English, Hindi, Hinglish, and 90+ languages
- **Cost-Effective**: Free tier with 30 requests/minute

### 📥 Download Options

- 📹 **Video**: High-quality MP4 downloads
- 🖼️ **Thumbnail**: JPG cover images and previews
- 🎵 **Audio**: MP3 extraction from videos
- 📝 **Caption**: Text captions and descriptions
- 🎤 **Transcription**: AI-generated transcripts with Hinglish support

### 🔄 Download Engines

- **yt-dlp**: Default downloader, most reliable for Instagram
- **Instaloader**: Fallback with Instagram-specific features
- **Automatic Switching**: Seamless fallback on failure

---

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.8 or higher
- **Internet**: Active connection
- **Groq API Key**: Free from [console.groq.com](https://console.groq.com) (for transcription)

### Installation

```bash
# Clone the repository
git clone https://github.com/dhruvagrawal27/insta-downloader-gui.git
cd insta-downloader-gui

# Install dependencies
pip install -r requirements_streamlit.txt

# (Optional) Set up Groq API key for transcription
# Create .env file with: GROQ_API_KEY=gsk_your_key_here
```

### Running the App

#### Windows Users (Easy Start)
```bash
# Double-click to run
run_preview.bat
```

#### Manual Start (All Platforms)
```bash
# Preview Mode (Recommended)
streamlit run streamlit_preview_app.py

# Single URL Mode
streamlit run streamlit_app.py

# Batch Mode
streamlit run streamlit_batch_app.py
```

### First Download

1. **Open** the web interface (automatically opens in browser)
2. **Configure** download options in the sidebar
   - Choose downloader (yt-dlp recommended)
   - Select what to download (video, audio, caption, etc.)
   - Enable transcription (optional, requires Groq API key)
3. **Paste** an Instagram URL
4. **Click** "Start Download" or "Preview"
5. **Download** your files!

---

## 🗂️ Folder Structure

```
insta-downloader-gui/
├── .env                          # API keys (create this)
├── .env.example                  # API key template
├── requirements_streamlit.txt    # Web app dependencies
├── streamlit_preview_app.py      # Preview mode (no storage)
├── streamlit_app.py              # Single URL mode
├── streamlit_batch_app.py        # Batch mode
├── streamlit_config.py           # App configuration
├── run_preview.bat               # Windows launcher
│
├── docs/                         # Documentation
│   ├── README.md                 # This file
│   ├── USAGE.md                  # Usage guide
│   ├── CHANGELOG.md              # Version history
│   ├── CONTRIBUTING.md           # Contribution guide
│   ├── SECURITY.md               # Security policy
│   ├── CODE_OF_CONDUCT.md        # Community guidelines
│   └── STATUS.md                 # Project status
│
├── QUICK_START_GROQ.md           # Groq setup guide
├── GROQ_TRANSCRIPTION_README.md  # Transcription details
├── GROQ_COMPLETE_GUIDE.md        # Advanced Groq guide
├── PREVIEW_MODE_README.md        # Preview mode details
├── STREAMLIT_README.md           # Streamlit apps guide
├── IMPLEMENTATION_SUMMARY.md     # Technical overview
├── DEMO_SCRIPT.md                # Demo/testing guide
│
├── src/                          # Source code
│   ├── core/                     # Core functionality
│   │   ├── downloader.py         # Download logic
│   │   ├── groq_transcriber.py   # Groq AI transcription
│   │   ├── transcriber.py        # Local Whisper (legacy)
│   │   └── session_manager.py    # Session handling
│   ├── agents/                   # Download engines
│   │   ├── instaloader.py        # Instaloader agent
│   │   └── yt_dlp.py             # yt-dlp agent
│   └── utils/                    # Utilities
│       ├── url_validator.py      # URL validation
│       └── resource_loader.py    # Resource management
│
└── tests/                        # Test files
    ├── test_groq_transcription.py
    └── verify_env_setup.py
```

---

## 📊 Feature Comparison

| Feature | Preview Mode | Single URL | Batch Mode |
|---------|-------------|------------|------------|
| **Local Storage** | ❌ No | ✅ Yes | ✅ Yes |
| **Content Preview** | ✅ Full | ❌ No | ❌ No |
| **Individual Downloads** | ✅ Yes | ❌ No | ❌ No |
| **Multiple URLs** | ❌ No | ❌ No | ✅ Yes |
| **Memory Usage** | 🟡 Medium | 🟢 Low | 🔴 High |
| **Best For** | Testing | Single use | Bulk downloads |

---

## 🕹 Usage

For detailed usage instructions, see **[USAGE.md](USAGE.md)**

### Basic Workflow

1. **Choose Mode**: Preview (recommended), Single URL, or Batch
2. **Configure Options**: Select downloader and content types
3. **Add URL(s)**: Paste Instagram URL(s)
4. **Process**: Click download or preview button
5. **Download**: Get your files!

### Supported URLs

- ✅ Instagram Reels: `https://www.instagram.com/reel/ABC123/`
- ✅ Instagram Posts: `https://www.instagram.com/p/ABC123/`
- ✅ Short URLs: `https://instagr.am/p/ABC123/`
- ❌ Stories: Not supported (24-hour expiration)
- ❌ Private Accounts: Not accessible

---

## 🤝 Contributing

We welcome contributions! Please see **[CONTRIBUTING.md](CONTRIBUTING.md)** for guidelines.

### Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🔧 Submit pull requests
- ⭐ Star the repository

---

## 📋 Roadmap

- [x] Web-based interface
- [x] Preview mode (no local storage)
- [x] Groq AI transcription
- [x] Hinglish support
- [x] Batch processing
- [ ] User authentication
- [ ] Download history
- [ ] Playlist support
- [ ] Mobile-optimized UI
- [ ] Docker containerization

See **[open issues](https://github.com/dhruvagrawal27/insta-downloader-gui/issues)** for more.

---

## 📝 Changelog

All notable changes are documented in **[CHANGELOG.md](CHANGELOG.md)**.

### Latest (v2.0.0)
- 🌐 Streamlit web interface
- 🎤 Groq AI transcription
- 👁️ Preview mode
- 📦 Batch processing
- 🚀 Cloud deployment ready

---

## 📄 License

This project is licensed under the **MIT License** - see the **[LICENSE](../LICENSE)** file for details.

---

## 🙏 Acknowledgments

* **[Streamlit](https://streamlit.io/)** - Web framework
* **[Groq](https://groq.com/)** - AI transcription infrastructure
* **[Instaloader](https://github.com/instaloader/instaloader)** - Instagram downloading
* **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** - Video downloading
* **[MoviePy](https://github.com/Zulko/moviepy)** - Audio/video processing

---

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/dhruvagrawal27/insta-downloader-gui/issues)
- 🔓 **Security**: [Security Policy](SECURITY.md)
- ⛏ **Pull Requests**: [GitHub PRs](https://github.com/dhruvagrawal27/insta-downloader-gui/pulls)
- 📖 **Docs**: [Documentation](https://github.com/dhruvagrawal27/insta-downloader-gui/tree/main/docs)

---

## 🔗 Connect

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/dhruvagrawal27)

---

<div align="center">
  Made with ❤️ by <a href="https://github.com/dhruvagrawal27">Dhruv Agrawal</a>
</div>

---

## ⚖️ Disclaimer

This tool is for **educational purposes** only. Please respect:
- Instagram's Terms of Service
- Content creators' rights
- Copyright laws
- Privacy settings

Always obtain permission before downloading content that doesn't belong to you.
