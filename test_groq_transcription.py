"""
Test script for Groq Hinglish Transcription

This script demonstrates how to use the GroqTranscriber for audio transcription
with Hinglish support.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.groq_transcriber import GroqTranscriber, transcribe_with_groq


def load_env_file():
    """Load environment variables from .env file."""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and value and not value.startswith("gsk_your"):
                        os.environ[key] = value


def test_groq_transcription():
    """Test Groq transcription with a sample audio file."""
    
    # Load .env file first
    load_env_file()
    
    # Get API key from environment
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("❌ Error: Groq API key not found")
        print("💡 Please add GROQ_API_KEY to your .env file")
        print("   Example: GROQ_API_KEY=gsk_your_actual_key_here")
        return
    
    # Show masked key
    masked_key = api_key[:8] + "..." + api_key[-4:]
    print(f"✅ Using API key from .env: {masked_key}")
    
    # Get audio file path
    audio_file = input("Enter path to audio file (MP3, WAV, MP4, etc.): ").strip()
    
    if not os.path.exists(audio_file):
        print(f"❌ Error: Audio file not found: {audio_file}")
        return
    
    print(f"\n🎤 Starting transcription for: {audio_file}")
    print("=" * 80)
    
    try:
        # Initialize transcriber
        transcriber = GroqTranscriber(api_key=api_key)
        
        # Progress callback
        def progress_callback(url, progress, message):
            print(f"[{progress}%] {message}")
        
        # Transcribe with post-processing
        print("\n📝 Transcribing with Hinglish post-processing...")
        result = transcriber.transcribe_and_process(
            audio_file,
            enable_post_processing=True,
            progress_callback=progress_callback
        )
        
        print("\n" + "=" * 80)
        print("✅ TRANSCRIPTION COMPLETED")
        print("=" * 80)
        
        print("\n📄 RAW WHISPER OUTPUT:")
        print("-" * 80)
        print(result["raw_transcription"])
        
        print("\n\n✨ CLEANED HINGLISH OUTPUT:")
        print("-" * 80)
        print(result["cleaned_transcription"])
        
        # Save to file
        output_file = Path(audio_file).with_suffix(".txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("=== FINAL TRANSCRIPTION (Hinglish in Roman Script) ===\n\n")
            f.write(result["cleaned_transcription"])
            f.write("\n\n=== RAW WHISPER OUTPUT ===\n\n")
            f.write(result["raw_transcription"])
        
        print(f"\n💾 Transcription saved to: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


def test_direct_api():
    """Test direct API calls without the class wrapper."""
    
    # Load .env file first
    load_env_file()
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ Error: Groq API key not found in .env file")
        return
    
    # Show masked key
    masked_key = api_key[:8] + "..." + api_key[-4:]
    print(f"✅ Using API key from .env: {masked_key}")
    
    audio_file = input("Enter path to audio file: ").strip()
    
    if not os.path.exists(audio_file):
        print(f"❌ Error: File not found: {audio_file}")
        return
    
    print("\n🚀 Using convenience function...")
    
    try:
        result = transcribe_with_groq(
            audio_file,
            api_key=api_key,
            enable_post_processing=True
        )
        
        print("\n✅ SUCCESS!")
        print("\n📄 Final Transcription:")
        print("-" * 80)
        print(result["final_transcription"])
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def show_example():
    """Show example usage."""
    
    example_code = """
# Example 1: Using GroqTranscriber class
from src.core.groq_transcriber import GroqTranscriber

transcriber = GroqTranscriber(api_key="your_groq_api_key")
result = transcriber.transcribe_and_process(
    "audio.mp3",
    enable_post_processing=True
)
print(result["final_transcription"])

# Example 2: Using convenience function
from src.core.groq_transcriber import transcribe_with_groq

result = transcribe_with_groq(
    "audio.mp3",
    api_key="your_groq_api_key",
    enable_post_processing=True
)
print(result["final_transcription"])

# Example 3: Integration with existing code
from src.core.groq_transcriber import GroqTranscriber
from pathlib import Path

transcriber = GroqTranscriber(api_key="your_groq_api_key")
reel_folder = Path("downloads/reel1")
result = {}

transcriber.transcribe_audio_from_reel(
    reel_folder=reel_folder,
    reel_number=1,
    result=result,
    enable_post_processing=True
)

print("Transcript:", result["transcript"])
print("Saved to:", result["transcript_path"])
"""
    
    print("\n📚 EXAMPLE USAGE:")
    print("=" * 80)
    print(example_code)


def main():
    """Main test menu."""
    
    print("\n" + "=" * 80)
    print("🎤 GROQ HINGLISH TRANSCRIPTION - TEST SCRIPT")
    print("=" * 80)
    
    print("\nSelect an option:")
    print("1. Test with audio file (full workflow)")
    print("2. Test with convenience function")
    print("3. Show example code")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        test_groq_transcription()
    elif choice == "2":
        test_direct_api()
    elif choice == "3":
        show_example()
    elif choice == "4":
        print("👋 Goodbye!")
        return
    else:
        print("❌ Invalid choice")
    
    # Ask to continue
    if input("\n\nRun another test? (y/n): ").lower() == 'y':
        main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
