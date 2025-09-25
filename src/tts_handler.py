"""
TTS Handler for Real-time Voice Reservation System

This module generates TwiML responses with TTS using Eleven Labs and manages voice and language settings.
"""

import os
import logging
from twilio.twiml.voice_response import VoiceResponse
from elevenlabs import generate, save
import tempfile
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSHandler:
    """Handles Text-to-Speech responses using Eleven Labs"""
    
    def __init__(self):
        # Default voice settings for English
        self.default_voice = 'Brian'  # More natural sounding male voice
        self.default_language = 'en-US'
        # Base URL for serving audio files (you'll need to set this to your actual URL)
        self.audio_base_url = os.getenv('AUDIO_BASE_URL', 'https://your-domain.com/audio')
        # Directory to store generated audio files
        self.audio_dir = os.path.join(os.getcwd(), 'audio_files')
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)
    
    def create_response(self, text, voice=None, language=None):
        """
        Create a TwiML response with TTS using Eleven Labs
        
        Args:
            text (str): Text to convert to speech
            voice (str): Voice to use (optional)
            language (str): Language to use (optional)
            
        Returns:
            str: TwiML response as string
        """
        try:
            # Generate audio file using Eleven Labs
            audio_url = self._generate_audio_file(text)
            
            # Create TwiML response to play the audio
            resp = VoiceResponse()
            resp.play(audio_url)
            return str(resp)
        except Exception as e:
            logger.error(f"Error creating TTS response: {e}")
            return self._create_empty_response()
    
    def create_gather_response(self, text, action_url, num_digits=1, 
                              voice=None, language=None, speech_timeout='auto'):
        """
        Create a response with gather for user input
        
        Args:
            text (str): Text to convert to speech
            action_url (str): URL to send user input
            num_digits (int): Number of digits to gather
            voice (str): Voice to use (optional)
            language (str): Language to use (optional)
            speech_timeout (str): Speech timeout setting (default: 'auto')
            
        Returns:
            str: TwiML response as string
        """
        try:
            # Generate audio file using Eleven Labs
            audio_url = self._generate_audio_file(text)
            
            # Create TwiML response to play the audio and gather input
            resp = VoiceResponse()
            resp.play(audio_url)
            # If num_digits is specified, gather digits; otherwise gather speech
            if num_digits > 0:
                resp.gather(numDigits=num_digits, action=action_url)
            else:
                resp.gather(input='speech', action=action_url, speechTimeout=speech_timeout)
            return str(resp)
        except Exception as e:
            logger.error(f"Error creating gather response: {e}")
            return self._create_empty_response()
    
    def create_hangup_response(self, text, voice=None, language=None):
        """
        Create a response that ends the call
        
        Args:
            text (str): Text to convert to speech before hanging up
            voice (str): Voice to use (optional)
            language (str): Language to use (optional)
            
        Returns:
            str: TwiML response as string
        """
        try:
            # Generate audio file using Eleven Labs
            audio_url = self._generate_audio_file(text)
            
            # Create TwiML response to play the audio and hang up
            resp = VoiceResponse()
            resp.play(audio_url)
            resp.hangup()
            return str(resp)
        except Exception as e:
            logger.error(f"Error creating hangup response: {e}")
            # Fallback to simple hangup
            resp = VoiceResponse()
            resp.hangup()
            return str(resp)
    
    def create_redirect_response(self, text, redirect_url, 
                                voice=None, language=None):
        """
        Create a response that redirects to another URL
        
        Args:
            text (str): Text to convert to speech before redirecting
            redirect_url (str): URL to redirect to
            voice (str): Voice to use (optional)
            language (str): Language to use (optional)
            
        Returns:
            str: TwiML response as string
        """
        try:
            # Generate audio file using Eleven Labs
            audio_url = self._generate_audio_file(text)
            
            # Create TwiML response to play the audio and redirect
            resp = VoiceResponse()
            resp.play(audio_url)
            resp.redirect(redirect_url)
            return str(resp)
        except Exception as e:
            logger.error(f"Error creating redirect response: {e}")
            return self._create_empty_response()
    
    def create_pause_response(self, text, pause_seconds=1,
                             voice=None, language=None):
        """
        Create a response with a pause
        
        Args:
            text (str): Text to convert to speech
            pause_seconds (int): Seconds to pause
            voice (str): Voice to use (optional)
            language (str): Language to use (optional)
            
        Returns:
            str: TwiML response as string
        """
        try:
            # Generate audio file using Eleven Labs
            audio_url = self._generate_audio_file(text)
            
            # Create TwiML response to play the audio and pause
            resp = VoiceResponse()
            resp.play(audio_url)
            resp.pause(length=pause_seconds)
            return str(resp)
        except Exception as e:
            logger.error(f"Error creating pause response: {e}")
            return self._create_empty_response()
    
    def _generate_audio_file(self, text, voice=None):
        """
        Generate audio file using Eleven Labs
        
        Args:
            text (str): Text to convert to speech
            voice (str): Voice to use (optional)
            
        Returns:
            str: URL to the generated audio file
        """
        try:
            # Get Eleven Labs API key from environment
            api_key = os.getenv("ELEVEN_API_KEY")
            
            # Generate audio using Eleven Labs with API key
            audio = generate(
                text=text,
                api_key=api_key,
                voice=voice or self.default_voice,
                model="eleven_turbo_v2"
            )
            
            # Save audio to file
            filename = f"{uuid.uuid4().hex}.mp3"
            filepath = os.path.join(self.audio_dir, filename)
            save(audio, filepath)
            
            # Return URL to the audio file
            return f"{self.audio_base_url}/{filename}"
        except Exception as e:
            logger.error(f"Error generating audio file: {e}")
            raise
    
    def _create_empty_response(self):
        """Create an empty TwiML response"""
        return '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'
    
    def set_default_voice(self, voice):
        """
        Set the default voice
        
        Args:
            voice (str): Voice to use as default
        """
        self.default_voice = voice
    
    def set_default_language(self, language):
        """
        Set the default language
        
        Args:
            language (str): Language to use as default
        """
        self.default_language = language

# Example usage
if __name__ == "__main__":
    # This is just for testing purposes
    tts_handler = TTSHandler()
    print("TTS Handler initialized")
    
    # Test creating a simple response
    response = tts_handler.create_response("Hello, welcome to our reservation system.")
    print(f"TTS Response: {response}")