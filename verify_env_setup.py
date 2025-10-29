"""
Quick verification script to test .env loading
"""

import os
from pathlib import Path

def load_env_file():
    """Load environment variables from .env file."""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print(f"✅ Found .env file at: {env_file}")
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and value and not value.startswith("gsk_your"):
                        os.environ[key] = value
                        if key == "GROQ_API_KEY":
                            masked = value[:8] + "..." + value[-4:]
                            print(f"✅ Loaded {key}: {masked}")
    else:
        print(f"❌ No .env file found at: {env_file}")

# Test loading
print("\n" + "="*60)
print("Testing .env Loading")
print("="*60 + "\n")

load_env_file()

# Verify
api_key = os.getenv("GROQ_API_KEY")
if api_key:
    masked = api_key[:8] + "..." + api_key[-4:]
    print(f"\n✅ SUCCESS! GROQ_API_KEY is available: {masked}")
    print(f"   Length: {len(api_key)} characters")
    print(f"   Starts with: {api_key[:4]}")
    
    # Test import
    try:
        from src.core.groq_transcriber import GroqTranscriber
        print("\n✅ GroqTranscriber module imported successfully")
        
        # Test initialization (without making API calls)
        print("\n🧪 Testing GroqTranscriber initialization...")
        transcriber = GroqTranscriber(api_key=api_key)
        print("✅ GroqTranscriber initialized successfully!")
        print(f"   Whisper Model: {transcriber.whisper_model}")
        print(f"   Primary LLM: {transcriber.llm_models[0]}")
        
    except Exception as e:
        print(f"\n⚠️ Import test: {str(e)}")
else:
    print("\n❌ GROQ_API_KEY not found!")
    print("   Make sure your .env file has: GROQ_API_KEY=gsk_...")

print("\n" + "="*60)
print("Verification Complete")
print("="*60 + "\n")
