"""
Groq-based Audio Transcriber with Hinglish Support

This module provides audio transcription using Groq's Whisper API
and post-processes the transcription using Groq's LLM for proper
Hinglish handling in Roman script.
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from groq import Groq


class GroqTranscriber:
    """
    Handles audio transcription using Groq's Whisper API and LLM for Hinglish support.
    
    This transcriber:
    1. Uses Groq Whisper API for initial transcription
    2. Post-processes with Groq LLM for proper Hinglish in Roman script
    3. Corrects spelling and maintains natural flow
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the GroqTranscriber.
        
        Args:
            api_key: Groq API key. If not provided, will try to get from environment.
        """
        # Try multiple sources for API key
        self.api_key = (
            api_key 
            or os.getenv("GROQ_API_KEY") 
            or os.getenv("GROQ_API_TOKEN")
            or self._load_from_env_file()
        )
        
        if not self.api_key:
            raise ValueError(
                "Groq API key not found. Please provide api_key parameter, "
                "set GROQ_API_KEY environment variable, or create a .env file. "
                "Get your free API key at: https://console.groq.com"
            )
        
        self.client = Groq(api_key=self.api_key)
        self.whisper_model = os.getenv("GROQ_WHISPER_MODEL", "whisper-large-v3")
        self.llm_models = [
            os.getenv("GROQ_PRIMARY_LLM", "meta-llama/llama-4-scout-17b-16e-instruct"),  # Primary model (30k TPM)
            os.getenv("GROQ_FALLBACK_LLM_1", "llama-3.3-70b-versatile"),   # Fallback 1
            os.getenv("GROQ_FALLBACK_LLM_2", "llama-3.1-8b-instant"),        # Fallback 2
        ]
    
    def _load_from_env_file(self) -> Optional[str]:
        """Try to load API key from .env file."""
        try:
            env_file = Path(__file__).parent.parent.parent / ".env"
            if env_file.exists():
                with open(env_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GROQ_API_KEY="):
                            key = line.split("=", 1)[1].strip()
                            # Remove quotes if present
                            key = key.strip('"').strip("'")
                            if key and not key.startswith("gsk_your"):
                                return key
        except Exception:
            pass
        return None

    def _compress_audio_if_needed(
        self,
        audio_path: str,
        max_size_mb: float = 24.5,  # Leave some margin below 25MB limit
        progress_callback=None
    ) -> str:
        """
        Compress audio file if it exceeds Groq's size limit (25MB).
        Uses bitrate reduction to compress without trimming.
        
        Args:
            audio_path: Path to the original audio file
            max_size_mb: Maximum file size in MB
            progress_callback: Optional callback for progress updates
        
        Returns:
            Path to compressed audio (or original if compression not needed)
        """
        import os
        from pathlib import Path
        
        # Check file size
        file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
        
        if file_size_mb <= max_size_mb:
            # No compression needed
            return audio_path
        
        if progress_callback:
            progress_callback("", 5, f"Compressing audio ({file_size_mb:.1f} MB → ~{max_size_mb:.1f} MB)...")
        
        try:
            from pydub import AudioSegment
            
            # Load audio
            audio = AudioSegment.from_file(audio_path)
            
            # Calculate target bitrate to reach desired size
            # Formula: bitrate (kbps) = (target_size_mb * 8192) / duration_seconds
            duration_seconds = len(audio) / 1000.0
            target_bitrate_kbps = int((max_size_mb * 8192) / duration_seconds)
            
            # Ensure bitrate is reasonable (minimum 32 kbps for intelligibility)
            target_bitrate_kbps = max(32, min(target_bitrate_kbps, 128))
            
            # Create compressed file path
            compressed_path = str(Path(audio_path).parent / f"compressed_{Path(audio_path).name}")
            if compressed_path.endswith('.m4a'):
                compressed_path = compressed_path.replace('.m4a', '.mp3')
            
            # Export with reduced bitrate
            audio.export(
                compressed_path,
                format="mp3",
                bitrate=f"{target_bitrate_kbps}k",
                parameters=["-ac", "1"]  # Convert to mono to save space
            )
            
            # Verify compression worked
            compressed_size_mb = os.path.getsize(compressed_path) / (1024 * 1024)
            
            if progress_callback:
                progress_callback("", 10, f"Compressed: {file_size_mb:.1f} MB → {compressed_size_mb:.1f} MB")
            
            return compressed_path
            
        except ImportError:
            # pydub not available, try ffmpeg directly
            if progress_callback:
                progress_callback("", 5, "Compressing with ffmpeg...")
            
            import subprocess
            
            compressed_path = str(Path(audio_path).parent / f"compressed_{Path(audio_path).stem}.mp3")
            
            # Calculate target bitrate
            duration_seconds = self._get_audio_duration(audio_path)
            if duration_seconds:
                target_bitrate_kbps = int((max_size_mb * 8192) / duration_seconds)
                target_bitrate_kbps = max(32, min(target_bitrate_kbps, 128))
            else:
                target_bitrate_kbps = 64  # Default fallback
            
            # Use ffmpeg for compression
            cmd = [
                'ffmpeg', '-i', audio_path,
                '-vn',  # No video
                '-ac', '1',  # Mono
                '-b:a', f'{target_bitrate_kbps}k',
                '-y',  # Overwrite
                compressed_path
            ]
            
            subprocess.run(cmd, capture_output=True, check=True)
            
            compressed_size_mb = os.path.getsize(compressed_path) / (1024 * 1024)
            
            if progress_callback:
                progress_callback("", 10, f"Compressed: {file_size_mb:.1f} MB → {compressed_size_mb:.1f} MB")
            
            return compressed_path
            
        except Exception as e:
            # Compression failed, return original and hope it works
            if progress_callback:
                progress_callback("", 10, f"Compression failed, trying original file...")
            return audio_path
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get audio duration in seconds."""
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(audio_path)
            return len(audio) / 1000.0
        except:
            try:
                import subprocess
                result = subprocess.run(
                    ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                     '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
                    capture_output=True,
                    text=True
                )
                return float(result.stdout.strip())
            except:
                return None

    def transcribe_audio(
        self, 
        audio_path: str, 
        progress_callback=None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Transcribe audio file using Groq Whisper API.
        
        Args:
            audio_path: Path to the audio file
            progress_callback: Optional callback for progress updates
        
        Returns:
            Tuple of (transcription_text, full_response_dict)
        """
        # Compress audio if needed (Groq has 25MB limit)
        compressed_audio_path = self._compress_audio_if_needed(
            audio_path, 
            max_size_mb=24.5,
            progress_callback=progress_callback
        )
        
        if progress_callback:
            progress_callback("", 10, "Uploading audio to Groq Whisper...")

        try:
            with open(compressed_audio_path, "rb") as audio_file:
                # Use Groq's Whisper API for transcription
                transcription = self.client.audio.transcriptions.create(
                    file=(Path(compressed_audio_path).name, audio_file.read()),
                    model=self.whisper_model,
                    response_format="verbose_json",
                    temperature=0.8,
                )
            
            if progress_callback:
                progress_callback("", 50, "Audio transcription completed")
            
            # Extract text from response
            transcription_dict = transcription.model_dump() if hasattr(transcription, 'model_dump') else transcription
            transcription_text = transcription_dict.get("text", "")
            
            # Clean up compressed file if it was created
            if compressed_audio_path != audio_path:
                try:
                    os.remove(compressed_audio_path)
                except:
                    pass
            
            return transcription_text, transcription_dict
            
        except Exception as e:
            # Clean up compressed file on error too
            if compressed_audio_path != audio_path:
                try:
                    os.remove(compressed_audio_path)
                except:
                    pass
            
            error_msg = f"Groq Whisper transcription failed: {str(e)}"
            if progress_callback:
                progress_callback("", 0, error_msg)
            raise Exception(error_msg)

    def post_process_with_llm(
        self, 
        transcription_text: str, 
        progress_callback=None
    ) -> str:
        """
        Post-process transcription using Groq LLM for Hinglish handling.
        
        Args:
            transcription_text: Raw transcription text from Whisper
            progress_callback: Optional callback for progress updates
        
        Returns:
            Cleaned and corrected transcription in proper format
        """
        if progress_callback:
            progress_callback("", 60, "Processing transcription with LLM...")
        
        system_prompt = """You are an expert transcription assistant specialized in handling both English and Hinglish content.
Your tasks are:

1. Language Detection: First determine if the content is primarily English, primarily Hindi, or mixed Hinglish.
2. English Content: For pure English content, provide clean English transcription with corrected spelling and grammar while maintaining the original tone and meaning.
3. Hindi/Hinglish Content: For ANY Hindi or mixed Hinglish content, provide accurate transcription in Roman script ONLY - NEVER use Devanagari (Hindi) script.
4. Contextual Correction: When words are unclear, check 2–3 words before and after to infer the correct meaning.
5. Spelling Correction: Fix misspellings while preserving the intended language of each word.
6. Readable Formatting: Use proper punctuation, sentence breaks, and paragraphing.
7. Preserve Intent: Maintain the original speaker's tone, style, and natural flow.

CRITICAL OUTPUT RULES:
- For English content: Output in clean, corrected English only
- For Hindi/Hinglish content: Output in Roman script Hinglish ONLY (e.g., "tu kaisa hai?" not "तू कैसा है?")
- NEVER use Devanagari script - All Hindi words must be written in Roman letters
- Do not convert English to Hindi or Hindi to English - preserve the original language choice of each word/phrase
- Convert Devanagari to Roman: If input contains Devanagari script, convert it to Roman script equivalent

Example:
Input: "आज मैं gym जा रहा हूँ"
Output: "Aaj main gym ja raha hun"
NOT: "आज मैं gym जा रहा हूँ"
"""

        user_prompt = f"""Please transcribe the following audio content with appropriate language handling and correct any spelling errors while maintaining natural flow.

Requirements:
1. Language Detection: Identify if content is English, Hinglish, or Hindi
2. English Content: For pure English, provide clean English transcription with corrected spelling/grammar
3. Hindi/Hinglish Content: For ANY Hindi or mixed content, provide transcription in Roman script Hinglish ONLY - NEVER use Devanagari script
4. Contextual Correction: If a word is garbled, infer the right word from nearby context
5. Spelling Correction: Fix misspellings while preserving intended language
6. Sense Check: Replace nonsensical words with logical alternatives
7. Proper Nouns: Correct names, brands, and cultural references
8. Formatting: Add punctuation and paragraph breaks for readability

Input:
{transcription_text}

Output:
Provide the transcription maintaining the original language choice - English content in English, Hindi/Hinglish content in Roman script Hinglish ONLY like देख would be written as Dekh.

Return ONLY the cleaned transcription text without any additional commentary or formatting markers."""

        # Try models in order with fallback
        for model_name in self.llm_models:
            try:
                if progress_callback:
                    progress_callback("", 70, f"Using {model_name} for post-processing...")
                
                print(f"[DEBUG] Attempting LLM post-processing with model: {model_name}")
                
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ],
                    model=model_name,
                    temperature=0.8,
                    max_tokens=4000,  # Reduced to avoid exceeding 30k TPM limit
                )
                
                cleaned_text = chat_completion.choices[0].message.content.strip()
                
                print(f"[DEBUG] LLM post-processing successful with {model_name}")
                print(f"[DEBUG] Input length: {len(transcription_text)} chars")
                print(f"[DEBUG] Output length: {len(cleaned_text)} chars")
                
                if progress_callback:
                    progress_callback("", 90, "Post-processing completed")
                
                return cleaned_text
                
            except Exception as e:
                error_msg = f"LLM post-processing with {model_name} failed: {str(e)}"
                print(f"[ERROR] {error_msg}")
                if model_name == self.llm_models[-1]:  # Last model
                    # If all models fail, return original transcription
                    print(f"[WARNING] All LLM models failed, returning raw transcription")
                    if progress_callback:
                        progress_callback("", 90, "Using raw transcription (post-processing failed)")
                    return transcription_text
                continue
        
        return transcription_text

    def transcribe_and_process(
        self, 
        audio_path: str, 
        enable_post_processing: bool = True,
        progress_callback=None
    ) -> Dict[str, Any]:
        """
        Complete transcription pipeline: Whisper transcription + LLM post-processing.
        
        Args:
            audio_path: Path to the audio file
            enable_post_processing: Whether to use LLM for post-processing
            progress_callback: Optional callback for progress updates
        
        Returns:
            Dictionary containing:
                - raw_transcription: Original Whisper output
                - cleaned_transcription: LLM-processed output (if enabled)
                - final_transcription: The final text to use
                - metadata: Additional transcription metadata
        """
        try:
            # Step 1: Transcribe with Whisper
            raw_text, metadata = self.transcribe_audio(audio_path, progress_callback)
            
            result = {
                "raw_transcription": raw_text,
                "metadata": metadata,
            }
            
            # Step 2: Post-process with LLM (if enabled)
            if enable_post_processing and raw_text:
                cleaned_text = self.post_process_with_llm(raw_text, progress_callback)
                result["cleaned_transcription"] = cleaned_text
                result["final_transcription"] = cleaned_text
            else:
                result["cleaned_transcription"] = raw_text
                result["final_transcription"] = raw_text
            
            if progress_callback:
                progress_callback("", 100, "Transcription completed successfully")
            
            return result
            
        except Exception as e:
            error_msg = f"Transcription pipeline failed: {str(e)}"
            if progress_callback:
                progress_callback("", 0, error_msg)
            raise Exception(error_msg)

    def transcribe_audio_from_reel(
        self,
        reel_folder: Path,
        reel_number: int,
        result: Dict[str, Any],
        progress_callback=None,
        enable_post_processing: bool = True,
    ):
        """
        Transcribe audio from a reel and save results.
        
        This method is compatible with the existing AudioTranscriber interface.
        
        Args:
            reel_folder: Folder containing the reel files
            reel_number: Sequential number of the reel
            result: Dictionary to update with transcription results
            progress_callback: Optional callback for progress updates
            enable_post_processing: Whether to use LLM for post-processing
        """
        if progress_callback:
            progress_callback("", 85, "Starting transcription...")
        
        # Get audio path from result
        audio_path = result.get("audio_path")
        
        if not audio_path or not os.path.exists(audio_path):
            error_msg = "Transcription skipped: No audio file found"
            result["transcript"] = error_msg
            result["transcript_error"] = error_msg
            if progress_callback:
                progress_callback("", 0, error_msg)
            return

        
        try:
            # Run transcription pipeline
            transcription_result = self.transcribe_and_process(
                audio_path,
                enable_post_processing=enable_post_processing,
                progress_callback=progress_callback
            )
            
            # Use the final transcription
            transcript_text = transcription_result["final_transcription"]
            result["transcript"] = transcript_text
            result["raw_transcript"] = transcription_result["raw_transcription"]
            
            # Save transcript to file
            transcript_path = reel_folder / f"transcript{reel_number}.txt"
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(f"=== FINAL TRANSCRIPTION ===\n\n")
                f.write(transcript_text)
                f.write(f"\n\n=== RAW WHISPER OUTPUT ===\n\n")
                f.write(transcription_result["raw_transcription"])
            
            result["transcript_path"] = str(transcript_path)
            
            if progress_callback:
                progress_callback("", 100, "Transcription saved successfully")
            
        except Exception as e:
            error_msg = f"Transcription failed: {str(e)}"
            result["transcript"] = error_msg
            result["transcript_error"] = error_msg
            print(error_msg)
            if progress_callback:
                progress_callback("", 0, error_msg)


# Convenience function for direct usage
def transcribe_with_groq(
    audio_path: str,
    api_key: Optional[str] = None,
    enable_post_processing: bool = True,
) -> Dict[str, Any]:
    """
    Convenience function to transcribe audio using Groq.
    
    Args:
        audio_path: Path to the audio file
        api_key: Groq API key (optional, will try environment variable)
        enable_post_processing: Whether to use LLM for Hinglish post-processing
    
    Returns:
        Dictionary with transcription results
    """
    transcriber = GroqTranscriber(api_key=api_key)
    return transcriber.transcribe_and_process(
        audio_path,
        enable_post_processing=enable_post_processing
    )
