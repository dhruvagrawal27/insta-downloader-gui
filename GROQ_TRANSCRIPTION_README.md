# 🎤 Groq Hinglish Transcription Integration

## Overview

This Instagram downloader now includes **Groq-powered transcription** with native **Hinglish support**. The system uses:

1. **Groq Whisper API** (`whisper-large-v3-turbo`) - Fast, accurate transcription
2. **Groq LLM** (`llama-3.3-70b-versatile`) - Post-processing for Hinglish in Roman script

## ✨ Key Features

### 🌍 Language Support
- ✅ **English**: Clean, corrected English transcription
- ✅ **Hinglish**: Proper Roman script (e.g., "aaj main gym ja raha hun")
- ✅ **Hindi**: Converts Devanagari to Roman script
- ✅ **Context-aware**: Fixes garbled words using surrounding context
- ✅ **Spelling correction**: Maintains natural flow while fixing errors

### 🚀 Performance
- **Fast**: Groq's optimized inference (~10x faster than local Whisper)
- **Accurate**: Whisper-large-v3-turbo model
- **Reliable**: Automatic fallback between multiple LLM models
- **Cloud-based**: No local GPU required

### 💰 Cost
- **FREE Tier**: 30 requests/minute, 6000 tokens/minute
- **Perfect for**: Personal use and testing
- **Get API Key**: https://console.groq.com

## 📦 Installation

### 1. Install Dependencies

```bash
pip install groq>=0.9.0
```

Or install all requirements:

```bash
pip install -r requirements_streamlit.txt
```

### 2. Get Groq API Key

1. Visit https://console.groq.com
2. Sign up (free)
3. Create an API key
4. Copy your key (starts with `gsk_`)

### 3. Set API Key

#### Option A: Environment Variable
```bash
# Windows PowerShell
$env:GROQ_API_KEY = "gsk_your_api_key_here"

# Linux/Mac
export GROQ_API_KEY="gsk_your_api_key_here"
```

#### Option B: Direct in Code
```python
from src.core.groq_transcriber import GroqTranscriber

transcriber = GroqTranscriber(api_key="gsk_your_api_key_here")
```

#### Option C: In Streamlit App
Enter your API key in the sidebar when transcription is enabled.

## 🎯 Usage Examples

### Example 1: Streamlit Web App

1. **Run the app**:
```bash
streamlit run streamlit_preview_app.py
```

2. **Enable transcription** in sidebar
3. **Select "Groq (Hinglish Support)"**
4. **Enter your API key**
5. **Enable Hinglish Processing** (recommended)
6. **Paste Instagram URL** and preview

### Example 2: Direct Python Usage

```python
from src.core.groq_transcriber import GroqTranscriber

# Initialize
transcriber = GroqTranscriber(api_key="gsk_your_key")

# Transcribe with Hinglish support
result = transcriber.transcribe_and_process(
    audio_path="audio.mp3",
    enable_post_processing=True  # Enable Hinglish processing
)

# Get results
print("Raw Whisper:", result["raw_transcription"])
print("Cleaned Hinglish:", result["cleaned_transcription"])
print("Final Output:", result["final_transcription"])
```

### Example 3: Integration with Existing Code

```python
from src.core.groq_transcriber import GroqTranscriber
from pathlib import Path

# Initialize transcriber
transcriber = GroqTranscriber(api_key="gsk_your_key")

# Use with existing reel download
reel_folder = Path("downloads/reel1")
result = {
    "audio_path": "downloads/reel1/audio1.mp3"
}

# Transcribe
transcriber.transcribe_audio_from_reel(
    reel_folder=reel_folder,
    reel_number=1,
    result=result,
    enable_post_processing=True
)

# Results are in the dict
print("Transcript:", result["transcript"])
print("Saved to:", result["transcript_path"])
```

### Example 4: Convenience Function

```python
from src.core.groq_transcriber import transcribe_with_groq

# Simple one-liner
result = transcribe_with_groq(
    audio_path="audio.mp3",
    api_key="gsk_your_key",
    enable_post_processing=True
)

print(result["final_transcription"])
```

## 🧪 Testing

### Test Script

```bash
python test_groq_transcription.py
```

This interactive script lets you:
1. Test with any audio file
2. See raw vs. cleaned output
3. View example code
4. Validate your setup

### Manual Testing

```python
# Test with existing Instagram download
from src.core.groq_transcriber import GroqTranscriber

transcriber = GroqTranscriber(api_key="gsk_your_key")

# If you have downloaded audio
result = transcriber.transcribe_and_process(
    "downloads/session_20251023_180815/reel1/audio1.mp3",
    enable_post_processing=True
)

print(result["final_transcription"])
```

## 📊 Transcription Pipeline

```
Audio File (MP3/WAV/etc.)
    ↓
[1] Groq Whisper API
    - Model: whisper-large-v3-turbo
    - Output: Raw transcription
    ↓
[2] Groq LLM Post-Processing (Optional)
    - Model: llama-3.3-70b-versatile
    - Tasks:
      * Language detection
      * Hinglish → Roman script
      * Spelling correction
      * Context-aware fixes
      * Proper formatting
    ↓
Final Transcription
    - English: Clean English
    - Hinglish: Roman script only
    - Saved to: transcript.txt
```

## 🎨 Output Examples

### Example 1: Hinglish Content

**Input Audio**: "आज मैं gym जा रहा हूँ और वहाँ workout करूँगा"

**Raw Whisper Output**:
```
aaj mai gym ja raha hu aur waha workout karunga
```

**Cleaned Groq Output**:
```
Aaj main gym ja raha hun aur wahan workout karunga.
```

### Example 2: English Content

**Input Audio**: "Today I'm going to the gym for a workout"

**Raw Whisper Output**:
```
today im going to the gym for a workout
```

**Cleaned Groq Output**:
```
Today I'm going to the gym for a workout.
```

### Example 3: Mixed Hinglish

**Input Audio**: "Bhai gym tips बताओ यार for beginners"

**Raw Whisper Output**:
```
bhai gym tips batao yaar for beginners
```

**Cleaned Groq Output**:
```
Bhai, gym tips batao yaar for beginners.
```

## ⚙️ Configuration Options

### Transcriber Settings

```python
transcriber = GroqTranscriber(
    api_key="gsk_your_key"  # Required
)

# Whisper model (default: whisper-large-v3-turbo)
transcriber.whisper_model = "whisper-large-v3-turbo"

# LLM models with fallback
transcriber.llm_models = [
    "llama-3.3-70b-versatile",   # Primary
    "llama-3.1-70b-versatile",   # Fallback 1
    "mixtral-8x7b-32768",        # Fallback 2
]
```

### Post-Processing Control

```python
# Full post-processing (recommended)
result = transcriber.transcribe_and_process(
    audio_path="audio.mp3",
    enable_post_processing=True
)

# Skip post-processing (faster, but no Hinglish fixing)
result = transcriber.transcribe_and_process(
    audio_path="audio.mp3",
    enable_post_processing=False
)
```

## 🔧 Troubleshooting

### Issue: "Groq API key not found"

**Solution**:
```python
# Option 1: Pass directly
transcriber = GroqTranscriber(api_key="gsk_your_key")

# Option 2: Set environment variable
import os
os.environ["GROQ_API_KEY"] = "gsk_your_key"
```

### Issue: "Rate limit exceeded"

**Solution**:
- Free tier: 30 requests/minute
- Wait a minute or upgrade plan
- Or use `enable_post_processing=False` to skip LLM

### Issue: "Audio file not found"

**Solution**:
```python
# Ensure audio was downloaded
result = {
    "audio_path": "path/to/audio.mp3"  # Must exist
}

# Check file exists
import os
if os.path.exists(result["audio_path"]):
    transcriber.transcribe_audio_from_reel(...)
```

### Issue: "Devanagari in output"

**Solution**:
- Ensure `enable_post_processing=True`
- LLM will convert to Roman script
- Check API key is valid

## 📈 Performance Comparison

| Feature | Local Whisper | Groq Whisper + LLM |
|---------|--------------|-------------------|
| Speed | ~30s/min | ~3s/min (10x faster) |
| Hinglish Support | ❌ Poor | ✅ Excellent |
| Roman Script | ❌ No | ✅ Yes |
| GPU Required | ✅ Yes | ❌ No |
| Internet Required | ❌ No | ✅ Yes |
| Cost | Free | Free (with limits) |
| Spelling Correction | ❌ No | ✅ Yes |
| Context-aware | ❌ No | ✅ Yes |

## 🌟 Best Practices

1. **Always use post-processing** for Hinglish content
2. **Set API key via environment variable** for security
3. **Monitor rate limits** on free tier
4. **Save raw transcription** for debugging
5. **Test with sample audio** before bulk processing

## 🔐 Security Notes

- **Never commit API keys** to git
- **Use environment variables** in production
- **Rotate keys** periodically
- **Monitor usage** in Groq console

## 📚 API Reference

### GroqTranscriber Class

```python
class GroqTranscriber:
    def __init__(self, api_key: Optional[str] = None)
    
    def transcribe_audio(self, audio_path: str, progress_callback=None) -> Tuple[str, Dict]
    
    def post_process_with_llm(self, transcription_text: str, progress_callback=None) -> str
    
    def transcribe_and_process(self, audio_path: str, enable_post_processing: bool = True, progress_callback=None) -> Dict
    
    def transcribe_audio_from_reel(self, reel_folder: Path, reel_number: int, result: Dict, progress_callback=None, enable_post_processing: bool = True)
```

### Convenience Function

```python
def transcribe_with_groq(audio_path: str, api_key: Optional[str] = None, enable_post_processing: bool = True) -> Dict
```

## 🎓 Learn More

- **Groq Documentation**: https://console.groq.com/docs
- **Whisper Models**: https://platform.openai.com/docs/models/whisper
- **LLama Models**: https://www.llama.com

## 🤝 Contributing

Improvements to the Hinglish processing logic are welcome! The prompts are in `src/core/groq_transcriber.py`.

## 📄 License

MIT License - Same as the main project

---

**Happy Transcribing! 🎤✨**

For support, please check the troubleshooting section or open an issue on GitHub.