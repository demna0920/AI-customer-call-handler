"""
Twilio Handler for Real-time Voice Reservation System

This module handles incoming calls from Twilio, manages call state,
and integrates with the TTS functionality.
"""

from twilio.twiml.voice_response import VoiceResponse
from flask import Flask, request, Response
import logging
from call_state import CallStateManager
from tts_handler import TTSHandler
from audio_stream_processor import AudioStreamProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwilioHandler:
    def __init__(self):
        self.call_state_manager = CallStateManager()
        self.tts_handler = TTSHandler()
        self.audio_processor = AudioStreamProcessor()
    
    def handle_incoming_call(self):
        """
        Handle incoming calls from Twilio
        
        Returns:
            Response: TwiML response with initial greeting
        """
        call_sid = request.values.get('CallSid')
        from_number = request.values.get('From')
        
        logger.info(f"Incoming call from {from_number} with CallSid {call_sid}")
        
        # Initialize call state
        self.call_state_manager.initialize_call(call_sid, from_number)
        
        # Generate greeting response
        response_text = "안녕하세요! 예약 시스템입니다. 성함과 예약 희망일, 시간을 말씀해주세요."
        twiml_response = self.tts_handler.create_response(response_text)
        
        logger.info(f"Sending greeting response for call {call_sid}")
        return Response(twiml_response, mimetype='text/xml')
    
    def handle_audio_stream(self):
        """
        Handle audio streaming from Twilio
        
        Returns:
            Response: TwiML response with AI response (if needed)
        """
        call_sid = request.values.get('CallSid')
        
        # Get audio data
        audio_data = request.data
        
        logger.info(f"Received audio stream for call {call_sid}")
        
        # Process audio and potentially generate response
        response = self.audio_processor.process_audio_stream(call_sid, audio_data)
        
        return Response(response, mimetype='text/xml')
    
    def handle_confirmation(self):
        """
        Handle user confirmation responses
        
        Returns:
            Response: TwiML response based on confirmation
        """
        call_sid = request.values.get('CallSid')
        digit = request.values.get('Digits', '')
        
        logger.info(f"Received confirmation {digit} for call {call_sid}")
        
        # Process confirmation
        response = self.call_state_manager.process_confirmation(call_sid, digit)
        
        return Response(response, mimetype='text/xml')
    
    def handle_call_status(self):
        """
        Handle call status updates from Twilio
        
        Returns:
            Response: Empty response
        """
        call_sid = request.values.get('CallSid')
        call_status = request.values.get('CallStatus', '')
        call_duration = request.values.get('CallDuration', '')
        
        logger.info(f"Call {call_sid} status: {call_status}, duration: {call_duration}")
        
        # Update call state with status
        self.call_state_manager.update_call_status(call_sid, call_status, call_duration)
        
        # Return empty response
        return Response('', mimetype='text/xml')

# Create Flask app instance
app = Flask(__name__)
twilio_handler = TwilioHandler()

@app.route("/voice/incoming", methods=["POST"])
def incoming_call():
    """Handle incoming calls"""
    return twilio_handler.handle_incoming_call()

@app.route("/voice/stream", methods=["POST"])
def stream_audio():
    """Handle audio streaming"""
    return twilio_handler.handle_audio_stream()

@app.route("/voice/confirm", methods=["POST"])
def confirm_reservation():
    """Handle user confirmation"""
    return twilio_handler.handle_confirmation()

@app.route("/voice/status", methods=["POST"])
def call_status():
    """Handle call status updates"""
    return twilio_handler.handle_call_status()

if __name__ == "__main__":
    app.run(debug=True, port=5000)