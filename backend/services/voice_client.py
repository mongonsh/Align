"""
ElevenLabs Voice Client for speech synthesis and recognition
"""

import os
import asyncio
from typing import Optional
import tempfile
from elevenlabs.client import ElevenLabs


class VoiceClient:
    """
    Wrapper for ElevenLabs API.
    Handles voice output (text-to-speech) and basic voice input processing.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment")

        self.client = ElevenLabs(api_key=self.api_key)
        
        # Use the provided voice ID
        self.voice_id = "Fahco4VZzobUeiPqni1S"  # Your custom voice

    async def text_to_speech(self, text: str, voice_id: Optional[str] = None) -> bytes:
        """
        Convert text to speech using ElevenLabs.

        Args:
            text: Text to convert to speech
            voice_id: Optional voice ID (uses default if not provided)

        Returns:
            Audio bytes (MP3 format)
        """
        def _generate_sync():
            audio = self.client.generate(
                text=text,
                voice=voice_id or self.voice_id,
                model="eleven_multilingual_v2"
            )
            
            # Convert generator to bytes
            audio_bytes = b""
            for chunk in audio:
                audio_bytes += chunk
                
            return audio_bytes

        # Run in thread pool since ElevenLabs API is synchronous
        return await asyncio.get_event_loop().run_in_executor(None, _generate_sync)

    async def speech_to_text(self, audio_bytes: bytes, audio_format: str = "webm") -> str:
        """
        Convert speech to text using browser-based Web Speech API.
        This is a placeholder that returns instructions for the frontend.

        Args:
            audio_bytes: Audio data
            audio_format: Format of the audio (webm, mp3, wav, etc.)

        Returns:
            Transcribed text or instructions
        """
        # For now, we'll rely on the browser's Web Speech API
        # The frontend should handle speech recognition directly
        return "Please use the browser's built-in speech recognition. Click and hold the microphone button to speak."

    async def get_available_voices(self) -> list[dict]:
        """
        Get list of available voices from ElevenLabs.

        Returns:
            List of voice information dictionaries
        """
        def _get_voices_sync():
            voices = self.client.voices.get_all()
            return [
                {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": getattr(voice, 'category', 'unknown'),
                    "description": getattr(voice, 'description', ''),
                }
                for voice in voices.voices
            ]

        return await asyncio.get_event_loop().run_in_executor(None, _get_voices_sync)

    def validate_api_key(self) -> bool:
        """Validate that the API key is configured and working."""
        try:
            # Simple test request
            voices = self.client.voices.get_all()
            return len(voices.voices) > 0
        except Exception:
            return False

    async def generate_voice_summary(self, mockup_description: str, changes_made: str) -> bytes:
        """
        Generate a voice summary of the mockup generation process.

        Args:
            mockup_description: Original user description
            changes_made: Summary of changes made

        Returns:
            Audio bytes of the summary
        """
        summary_text = f"""
        Your mockup has been generated successfully! 

        You requested: {mockup_description}

        Here's what I created for you: {changes_made}

        You can now review the mockup and export it when you're ready.
        """

        return await self.text_to_speech(summary_text.strip())