# 🚀 Quick Start Guide: Groq Hinglish Transcription

## 🎯 In 3 Simple Steps

### Step 1: Get Your Free Groq API Key (2 minutes)

1. Visit **https://console.groq.com**
2. Click **"Sign Up"** (free account)
3. Go to **"API Keys"** section
4. Click **"Create API Key"**
5. Copy your key (starts with `gsk_...`)

### Step 2: Set Up Your API Key (30 seconds)

Choose ONE of these methods:

#### Method A: Using Streamlit (Easiest)
- Just enter your API key in the sidebar when you run the app
- No configuration needed!

#### Method B: Environment Variable (Recommended for CLI)
```bash
# Windows PowerShell
$env:GROQ_API_KEY = "gsk_your_actual_key_here"

# Linux/Mac Terminal
export GROQ_API_KEY="gsk_your_actual_key_here"
```

#### Method C: .env File (Best for Development)
1. Copy `.env.example` to `.env`
2. Open `.env` file
3. Replace `gsk_your_api_key_here` with your actual key
4. Save the file

### Step 3: Run the App (10 seconds)

```bash
streamlit run streamlit_preview_app.py
```

Then in the web interface:
1. ✅ Check **"Transcribe Audio"** in sidebar
2. 📱 Select **"Groq (Hinglish Support)"**
3. 🔑 Enter your API key (if not using env variable)
4. ✅ Enable **"Hinglish Processing"** for Roman script output
5. 🔗 Paste Instagram URL
6. 🚀 Click **"Preview Content"**

## ✨ What You Get

### Before (Without Groq):
```
Raw Whisper: aaj mai gym ja raha hu
```

### After (With Groq Hinglish Processing):
```
Clean Hinglish: Aaj main gym ja raha hun.
```

## 🎨 Example Outputs

### Example 1: Pure Hinglish
**Instagram Audio**: Gym tips for beginners

**Result**:
```
Agar aapka pehli baar gym jaana hai to simple routine se start karo.
Heavy weights mat uthao, proper form sabse important hai.
Warm-up exercises skip mat karo aur consistency maintain karo.
```

### Example 2: Mixed English-Hinglish
**Instagram Audio**: Fitness motivation

**Result**:
```
Bhai, consistency is the key! Har din thoda-thoda karo but regularly karo.
Trainer ki guidance important hai initially. Stay motivated aur apna best do!
```

### Example 3: Pure English
**Instagram Audio**: Professional content

**Result**:
```
Today we're discussing the five essential gym tips for beginners.
First, start with a simple routine and avoid heavy weights initially.
```

## 🔥 Pro Tips

1. **Always enable Hinglish Processing** - Converts everything to Roman script
2. **Use yt-dlp downloader** - More reliable for Instagram
3. **Free tier is generous** - 30 requests/minute is plenty
4. **Transcription takes ~30 seconds** - Includes post-processing
5. **Works offline after download** - Audio is processed locally first

## ❓ Common Questions

### Q: Do I need a credit card?
**A:** No! Groq's free tier requires no payment method.

### Q: How many transcriptions can I do?
**A:** 30 per minute on free tier - more than enough for personal use.

### Q: Will it work for Instagram Reels in Hindi?
**A:** Yes! It automatically detects Hindi and converts to Roman script.

### Q: What if I don't want Hinglish processing?
**A:** Just uncheck "Enable Hinglish Processing" - you'll get raw Whisper output.

### Q: Can I use this without Streamlit?
**A:** Yes! See `test_groq_transcription.py` for CLI usage.

## 🆘 Quick Troubleshooting

### "API key not found"
→ Enter key in Streamlit sidebar OR set environment variable

### "Rate limit exceeded"
→ Wait 60 seconds (free tier: 30 requests/minute)

### "Audio file not found"
→ Make sure to check "Audio" option in sidebar

### "Still getting Devanagari script"
→ Enable "Hinglish Processing" option

## 📚 More Information

- **Full Documentation**: `GROQ_TRANSCRIPTION_README.md`
- **Test Script**: `python test_groq_transcription.py`
- **Code Examples**: See documentation for Python usage

## 🎉 That's It!

You're now ready to transcribe Instagram Reels with perfect Hinglish support!

**Questions?** Check the full documentation or open an issue on GitHub.

---

**Made with ❤️ for the Hinglish community**