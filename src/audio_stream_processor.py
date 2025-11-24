"""
Audio Stream Processor for Real-time Voice Reservation System

This module processes incoming audio streams from Twilio, buffers audio chunks,
interfaces with Whisper for transcription, and triggers response generation.
"""

import logging
import numpy as np
import io
import time
from pydub import AudioSegment
import whisper
from call_state import CallStateManager
from ai_response_generator import AIResponseGenerator
from tts_handler import TTSHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioStreamProcessor:
    def __init__(self):
        self.call_state_manager = CallStateManager()
        self.response_generator = AIResponseGenerator()
        self.tts_handler = TTSHandler()
        
        # Load Whisper model
        logger.info("Loading Whisper model...")
        self.whisper_model = whisper.load_model("base")
        logger.info("Whisper model loaded successfully!")
        
        # Audio processing parameters
        self.chunk_size = 16000 * 5  # 5 seconds of audio at 16kHz
        self.sample_rate = 16000
        self.channels = 1
    
    def process_audio_stream(self, call_id, audio_data):
        """
        Process audio stream from Twilio and generate response if needed
        
        Args:
            call_id (str): Twilio Call SID
            audio_data (bytes): Audio data from Twilio
            
        Returns:
            str: TwiML response (empty if no response needed)
        """
        try:
            # Convert audio data to proper format
            audio_segment = self._convert_audio_data(audio_data)
            
            if audio_segment is None:
                logger.warning(f"Failed to convert audio data for call {call_id}")
                return self._create_empty_response()
            
            # Transcribe audio
            transcription = self._transcribe_audio(audio_segment)
            
            if not transcription:
                logger.info(f"No transcription for call {call_id}")
                return self._create_empty_response()
            
            logger.info(f"Transcription for call {call_id}: {transcription}")
            
            # Update call state with transcription
            call_state = self.call_state_manager.update_call_with_transcription(
                call_id, transcription
            )
            
            # Check if we should generate a response
            if self._should_generate_response(call_id, call_state):
                # Generate AI response
                response_text = self.response_generator.generate_next_response(call_state)
                
                # Create TTS response
                twiml_response = self.tts_handler.create_response(response_text)
                
                logger.info(f"Generated response for call {call_id}: {response_text}")
                return twiml_response
            
            return self._create_empty_response()
            
        except Exception as e:
            logger.error(f"Error processing audio stream for call {call_id}: {e}")
            return self._create_empty_response()
    
    def _convert_audio_data(self, audio_data):
        """
        Convert audio data from Twilio to format suitable for Whisper
        
        Args:
            audio_data (bytes): Raw audio data from Twilio
            
        Returns:
            AudioSegment: Processed audio segment or None if conversion fails
        """
        try:
            # Create AudioSegment from raw data
            # Twilio sends audio as 8kHz or 16kHz linear PCM
            audio_segment = AudioSegment(
                data=audio_data,
                sample_width=2,  # 16-bit
                frame_rate=self.sample_rate,
                channels=self.channels
            )
            
            # Convert to mono if needed
            if audio_segment.channels > 1:
                audio_segment = audio_segment.set_channels(1)
            
            # Set frame rate to 16kHz if needed
            if audio_segment.frame_rate != self.sample_rate:
                audio_segment = audio_segment.set_frame_rate(self.sample_rate)
            
            return audio_segment
            
        except Exception as e:
            logger.error(f"Error converting audio data: {e}")
            return None
    
    def _transcribe_audio(self, audio_segment):
        """
        Transcribe audio using Whisper
        
        Args:
            audio_segment (AudioSegment): Audio to transcribe
            
        Returns:
            str: Transcribed text or empty string if transcription fails
        """
        try:
            # Convert AudioSegment to numpy array
            samples = np.array(audio_segment.get_array_of_samples())
            
            # Normalize to float32
            samples = samples.astype(np.float32) / 32768.0
            
            # Transcribe with Whisper
            result = self.whisper_model.transcribe(
                samples, 
                language="ko",
                fp16=False  # Use float32 instead of float16
            )
            
            text = result["text"].strip()
            return text
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return ""
    
    def _should_generate_response(self, call_id, call_state):
        """
        Determine if we should generate a response now
        
        Args:
            call_id (str): Call identifier
            call_state (dict): Current call state
            
        Returns:
            bool: True if response should be generated
        """
        # For now, always generate a response when we have transcription
        # In a more sophisticated implementation, we would check:
        # - Time since last response
        # - Whether new information was extracted
        # - Call phase (greeting, gathering, confirming, etc.)
        return True
    
    def _create_empty_response(self):
        """Create an empty TwiML response"""
        return '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'