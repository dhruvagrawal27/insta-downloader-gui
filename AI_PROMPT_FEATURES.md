# 🎬 Sora 2/Veo 3 AI Video Prompt Generation - Feature Guide

## Overview

Your Streamlit Preview App now includes **AI-powered video prompt generation** for **Sora 2** and **Veo 3**! This feature transforms your Instagram transcripts into professional, cinematic video prompts using Groq's LLM.

---

## ✨ New Features Added

### 1. **Prompt Type Selection**
- Choose between **Sora 2** or **Veo 3** AI video models
- Each model gets optimized prompts for its specific capabilities

### 2. **Cameo Support (Sora 2)**
- Add up to **3 Instagram cameo usernames** (e.g., @dhruvagr)
- Cameos are automatically integrated into character descriptions
- Optional: Works fine without cameos too

### 3. **AI-Generated Cinematic Prompts**
- **Script segmentation**: Breaks transcript into 2-4 optimal chunks (6-8 seconds each)
- **Scene descriptions**: Complete cinematic details for each segment
- **Camera specs**: Type, style, movement, quality specifications
- **Lighting & Sound**: Detailed environment and audio design
- **Character actions**: Precise movements, gestures, and dialogue timing
- **Visual effects**: FX requirements and post-production notes
- **Production notes**: Continuity guides, shooting recommendations, viral optimization tips

### 4. **Formatted Display**
- Beautiful, expandable UI for each segment
- Organized sections: Hook, Location, Environment, Camera, Characters, FX, Audio
- Copy-paste ready JSON output
- Download as JSON or formatted text

---

## 🚀 How to Use

### Step 1: Enable Transcription
1. In the sidebar, check **"🎤 Transcribe Audio"**
2. Select **"Groq (Hinglish Support)"** as transcription engine
3. Your Groq API key from `.env` will be auto-loaded

### Step 2: Enable Prompt Generation
1. In sidebar under **"🎬 AI Video Prompts"**, check **"🎥 Generate Sora 2/Veo 3 Prompts"**
2. Select your preferred model:
   - **Sora 2**: Full cinematic prompts with cameo support
   - **Veo 3**: Optimized for Google's Veo 3 model

### Step 3: Add Cameos (Optional - Sora 2 only)
1. If using Sora 2, you'll see cameo input fields
2. Enter up to 3 Instagram usernames:
   - With or without `@` symbol (both work)
   - Example: `dhruvagr` or `@dhruvagr`
3. Leave empty if no cameos needed

### Step 4: Download & Preview
1. Paste Instagram URL
2. Click **"🔍 Preview Content"**
3. Wait for:
   - Content download ✓
   - Audio transcription ✓
   - AI prompt generation ✓
4. Navigate to the **"🎬 AI Prompts"** tab

---

## 📋 Prompt Structure

Each generated prompt includes:

### Video Series Overview
```json
{
  "video_series": {
    "title": "Your Video Title",
    "total_segments": 3,
    "total_duration": "18-24s",
    "narrative_arc": "Story progression"
  }
}
```

### Individual Segments
For each 6-8 second segment:

**Meta Information**
- Title (Part X)
- Description
- Aspect ratio (default 9:16)
- Tone/mood

**Hook** (First segment only)
- 2-second pattern interrupt
- Scroll-stopping visual

**Scene Details**
- **Location**: Specific setting with atmosphere
- **Environment**: Lighting setup + ambient sounds
- **Camera**: Type, style, movement, quality
- **Characters**: Role, appearance, action, dialogue, motion
- **FX**: Visual effects list
- **Audio**: Mix style + background elements
- **End State**: Final frame or transition

**Production Notes**
- Continuity guidelines
- Shooting recommendations
- Viral optimization strategies

---

## 💡 Use Cases

### 1. **Content Creators**
- Convert Instagram Reels into AI video remakes
- Generate B-roll scripts with exact specs
- Create cinematic versions of viral content

### 2. **Video Producers**
- Get detailed shot lists from concepts
- Plan multi-angle shoots with precise timing
- Generate client pitch documents

### 3. **AI Video Enthusiasts**
- Create Sora 2/Veo 3 ready prompts
- Test different cinematic styles
- Experiment with viral video formulas

### 4. **Marketing Teams**
- Storyboard viral campaigns
- Prototype video ads
- Generate multiple creative variations

---

## 🎯 Example Workflow

### Input
```
Instagram URL: https://www.instagram.com/reel/xyz123/
Transcript: "An AI just noticed its own thoughts. Not a simulation. 
Not a prompt trick. It recognized a foreign idea in its own mind..."
Cameos: @dhruvagr
Model: Sora 2
```

### Output
```json
{
  "video_series": {
    "title": "AI Self-Awareness Discovery",
    "total_segments": 3,
    "total_duration": "21s"
  },
  "segments": [
    {
      "segment_number": 1,
      "duration": "7s",
      "meta": {
        "title": "Discovery - Part 1",
        "aspect_ratio": "9:16",
        "tone": "intriguing_revelation"
      },
      "scene": {
        "hook": {
          "shot": "Binary code explosion, snap to holographic AI face"
        },
        "location": "Underground AI research lab, neon-lit",
        "camera": {
          "type": "handheld mobile",
          "style": "dolly-in, shallow DOF",
          "quality": "raw cinematic lowlight"
        },
        "characters": [
          {
            "role": "@dhruvagr",
            "appearance": "AI researcher in lab coat",
            "dialogue": "An AI just noticed its own thoughts..."
          }
        ]
      }
    }
  ]
}
```

---

## 📥 Download Options

### From AI Prompts Tab:
1. **📥 Download JSON** - Raw structured data for API use
2. **📥 Download Text** - Formatted readable version
3. **📄 Raw JSON** - Copy-paste from code block

### From Main Preview:
- **📦 Download ZIP Package** - Includes video, audio, transcript, AND prompts JSON

---

## ⚙️ Technical Details

### Model Used
- **LLM**: Groq `llama-3.3-70b-versatile`
- **Temperature**: 0.7 (creative but consistent)
- **Max Tokens**: 8000 (handles long scripts)
- **Response Format**: Structured JSON

### System Prompt Features
- Expert AI video prompt engineer persona
- Script chunking algorithms (6-8s segments)
- Cinematic storytelling principles
- Pattern interrupt techniques
- Viral optimization strategies
- Character integration for cameos

### Safety & Privacy
- API calls made securely via Groq
- No data stored on their servers after response
- Your API key loaded from `.env` (not exposed)
- All processing in-memory (no disk writes)

---

## 🐛 Troubleshooting

### "⚠️ Prompt generation failed"
**Cause**: API error or network issue  
**Fix**: 
- Check internet connection
- Verify Groq API key is valid
- Check Groq API status: https://status.groq.com

### "⚠️ No transcript available"
**Cause**: Transcription wasn't enabled or failed  
**Fix**:
- Enable "🎤 Transcribe Audio" checkbox
- Wait for transcription to complete
- Check if audio was extracted successfully

### "⚠️ Groq API key required"
**Cause**: No API key in `.env` file  
**Fix**:
1. Open `.env` in project root
2. Add line: `GROQ_API_KEY=gsk_your_actual_key`
3. Get free key: https://console.groq.com
4. Restart Streamlit app

### "⚠️ Transcription must be enabled"
**Cause**: Prompt generation checkbox is on but transcription is off  
**Fix**: Enable transcription first (AI prompts need transcript as input)

### Prompts not showing in tabs
**Cause**: Generation happened after preview loaded  
**Fix**: Wait for all processes to complete before tabs render

---

## 💰 Cost & Rate Limits

### Groq API (Free Tier)
- **Rate Limit**: ~30 requests/minute
- **Context Window**: 32k tokens
- **Cost**: Free tier available (check console.groq.com for limits)

### Estimated Usage per Prompt
- **Input Tokens**: ~2,000-3,000 (system prompt + script)
- **Output Tokens**: ~4,000-6,000 (full JSON response)
- **Total**: ~6,000-9,000 tokens per generation

### Tips to Optimize
- Use shorter transcripts (trim long videos)
- Generate once, download JSON for reuse
- Avoid regenerating unnecessarily

---

## 🔮 Future Enhancements (Potential)

- [ ] Support for other AI models (Runway, Pika)
- [ ] Multi-language prompt generation
- [ ] Custom tone/style presets
- [ ] Batch prompt generation
- [ ] Export to n8n workflow format
- [ ] Video storyboard visualization
- [ ] Direct integration with Sora/Veo APIs (when available)

---

## 📚 Related Documentation

- **Main Deployment Guide**: `DEPLOYMENT.md`
- **Bug Fixes Summary**: `BUGS_FIXED.md`
- **Quick Start**: `QUICKSTART.md`
- **Streamlit App**: `streamlit_preview_app.py`

---

## 🤝 Contributing

Found a bug or have an idea? Open an issue on GitHub!

**Repository**: https://github.com/dhruvagrawal27/insta-downloader-gui

---

## 📄 License

MIT License - See LICENSE file

---

**Version**: 2.1.0 (Sora 2/Veo 3 Feature)  
**Last Updated**: 2024-01-20  
**Author**: Dhruv Agrawal (@dhruvagr)

---

## 🎉 Example Output Preview

```
📺 Video Series Overview
Title: AI Consciousness Breakthrough
Total Segments: 3
Total Duration: 21 seconds
Narrative Arc: discovery → rejection → philosophical_reflection

🎞️ Segment 1 - 7 seconds
📌 Discovery - Part 1
Underground AI research lab with holographic displays

🎣 Hook (First 2s)
Binary code explodes, snaps to holographic AI face

📍 Location
Underground AI research facility, glass walls with cascading code

💡 Lighting: Cold blue LED panels with rim light
🔊 Sounds: low_futuristic_hum, soft_rising_tone, distant_air_vent

📹 Camera
Type: digital cinema
Style: handheld dolly-in, shallow depth of field
Quality: high contrast neon color grading

👥 Character: @dhruvagr
👤 Appearance: Translucent hologram, circuitry patterns
🎭 Action: Turns slowly toward camera
💬 Dialogue: "An AI just noticed its own thoughts. Not a simulation."
🕺 Motion: Micro-blink of light, torso sway synced to hum

✨ Visual Effects
holographic_neural_display, data_stream_particles, subtle_lens_flare, vignette_edges

🎵 Audio
Mix: balanced_dialogue
Background: low_futuristic_hum, soft_rising_tone

🎬 End State
Camera pushes closer as AI's eyes flicker, transition to tighter shot
```

---

**Enjoy creating cinematic AI video prompts!** 🚀🎬

