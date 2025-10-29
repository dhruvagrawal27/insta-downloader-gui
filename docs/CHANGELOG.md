# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-10-30

### 🌐 Complete Web App Transformation
- **Streamlit Web Interface**: Replaced PyQt6 desktop app with modern Streamlit web UI
- **Preview Mode**: Zero local storage - view all content in-memory before downloading
- **Three App Modes**: Preview, Single URL, and Batch processing modes
- **Cloud Deployment**: Ready for Streamlit Cloud, Heroku, Docker deployment

### 🎤 Groq AI Integration
- **Groq Whisper API**: Fast, accurate transcription (whisper-large-v3-turbo)
- **Hinglish Support**: Native Roman script transcription for Hindi/Hinglish content
- **LLM Post-Processing**: AI-powered spelling correction using Llama models
- **Multi-Model Fallback**: Automatic switching between Llama 3.3, 3.1, and Mixtral

### 🚀 Enhanced Features
- **Individual File Downloads**: Download each file separately in preview mode
- **Better Instagram Compatibility**: yt-dlp as default downloader
- **Environment Configuration**: Auto-load API keys from .env file
- **Comprehensive Documentation**: 7 new markdown guides added

### Changed
- Replaced desktop PyQt6 GUI with Streamlit web interface
- Changed default transcription from local Whisper to Groq API
- Updated all documentation to reflect web app architecture

### Removed
- PyQt6 desktop application (legacy code preserved in src/)
- Local Whisper transcription as default (still available as fallback)
- Desktop-specific features and launcher scripts

---

## [1.0.0] - 2025-04-11

### Added
- 🎉 **Initial release** with core download and UI functionality  
- **Dual Download Engines**: Powered by both `instaloader` and `yt-dlp`
- **User-Selectable Downloader**: Choose preferred download engine from UI
- **Automatic Fallback**: Auto-switch downloaders on failure
- **Enhanced Reliability**: Improved success rates for Instagram Reels

### Security
- Added SECURITY.md

---

## Guidelines for Contributors

When adding entries to this changelog:

1. **Group changes** by type using the categories above
2. **Write for humans** - use clear, descriptive language
3. **Include issue/PR numbers** when relevant: `Fixed login bug (#123)`
4. **Date format** should be YYYY-MM-DD
5. **Version format** should follow [Semantic Versioning](https://semver.org/)
6. **Keep entries concise** but informative

### Version Number Guidelines
- **Major** (X.y.z) - Breaking changes
- **Minor** (x.Y.z) - New features, backwards compatible
- **Patch** (x.y.Z) - Bug fixes, backwards compatible

### Example Entry Format
```markdown
## [1.2.3] - 2024-01-15

### Added
- New feature description (#PR-number)

### Fixed
- Bug fix description (fixes #issue-number)
```
