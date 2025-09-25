"""
Call State Manager for Real-time Voice Reservation System

This module tracks state for each active call, manages transcription history,
and tracks extracted information.
"""

import logging
import time
from threading import Lock

# Import TTS handler and response generator for process_confirmation method
from tts_handler import TTSHandler
from ai_response_generator import AIResponseGenerator

# Initialize global instances
tts_handler = TTSHandler()
response_generator = AIResponseGenerator()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CallState:
    """Represents the state of a single call"""
    
    def __init__(self, call_id, from_number=None):
        self.call_id = call_id
        self.from_number = from_number
        self.start_time = time.time()
        self.last_update = time.time()
        self.audio_buffer = []
        self.transcription_history = []
        self.extracted_info = {
            "name": None,
            "date": None,
            "time": None,
            "party_size": None,
            "phone": None,
            "email": None
        }
        self.last_response = None
        self.response_timestamp = None
        self.confirmation_pending = False
        self.call_phase = "greeting"  # greeting, gathering, confirming, completed, early_disconnected
        self.status = "active"  # active, completed, failed, early_disconnected
        self.call_duration = 0
        self.greeting_played = False  # Track if greeting has been played
        self.intent = None  # Track user's intent (reservation, hours, menu, etc.)
        self.last_intent = None  # Track the last detected intent
        self.conversation_history = []  # Track conversation flow
        self.customer_id = None  # Track customer ID in database
    
    def update_transcription(self, transcription):
        """Add new transcription to history"""
        if transcription:
            self.transcription_history.append(transcription)
            self.last_update = time.time()
    
    def update_extracted_info(self, new_info):
        """Update extracted information"""
        if new_info:
            for key, value in new_info.items():
                if value is not None and value != "":
                    self.extracted_info[key] = value
            self.last_update = time.time()
    
    def has_missing_info(self):
        """Check if any required information is missing"""
        return any(value is None for value in self.extracted_info.values())
    
    def has_complete_info(self):
        """Check if all required information is present"""
        return all(value is not None for value in self.extracted_info.values())
    
    def get_missing_fields(self):
        """Get list of missing fields"""
        return [key for key, value in self.extracted_info.items() if value is None]
    
    def set_confirmation_pending(self, pending=True):
        """Set confirmation pending state"""
        self.confirmation_pending = pending
        self.call_phase = "confirming" if pending else "gathering"
        self.last_update = time.time()
    
    def complete_call(self):
        """Mark call as completed"""
        self.call_phase = "completed"
        self.status = "completed"
        self.call_duration = time.time() - self.start_time
        self.last_update = time.time()
    
    def fail_call(self):
        """Mark call as failed"""
        self.status = "failed"
        self.call_duration = time.time() - self.start_time
        self.last_update = time.time()

    def mark_early_disconnected(self):
        """Mark call as early disconnected (after greeting but before completion)"""
        self.call_phase = "early_disconnected"
        self.status = "early_disconnected"
        self.call_duration = time.time() - self.start_time
        self.last_update = time.time()
        logger.warning(f"Call {self.call_id} marked as early disconnected. Phase: {self.call_phase}, Greeting played: {self.greeting_played}")

    def set_greeting_played(self, played=True):
        """Mark that the greeting has been played"""
        self.greeting_played = played
        self.call_phase = "gathering"  # Move to gathering phase after greeting
        self.last_update = time.time()

class CallStateManager:
    """Manages state for all active calls"""
    
    def __init__(self):
        self.calls = {}  # call_id -> CallState
        self.lock = Lock()  # Thread safety
    
    def initialize_call(self, call_id, from_number=None):
        """
        Initialize state for a new call
        
        Args:
            call_id (str): Twilio Call SID
            from_number (str): Caller's phone number
            
        Returns:
            CallState: Initialized call state
        """
        with self.lock:
            if call_id not in self.calls:
                self.calls[call_id] = CallState(call_id, from_number)
                logger.info(f"Initialized call state for {call_id}")
            return self.calls[call_id]
    
    def get_call_state(self, call_id):
        """
        Get state for a specific call
        
        Args:
            call_id (str): Twilio Call SID
            
        Returns:
            CallState: Call state or None if not found
        """
        with self.lock:
            return self.calls.get(call_id)
    
    def update_call_with_transcription(self, call_id, transcription):
        """
        Update call state with new transcription
        
        Args:
            call_id (str): Twilio Call SID
            transcription (str): New transcription
            
        Returns:
            CallState: Updated call state
        """
        with self.lock:
            call_state = self.calls.get(call_id)
            if call_state:
                call_state.update_transcription(transcription)
                logger.info(f"Updated transcription for call {call_id}")
            return call_state
    
    def update_call_with_info(self, call_id, extracted_info):
        """
        Update call state with extracted information
        
        Args:
            call_id (str): Twilio Call SID
            extracted_info (dict): Extracted information
            
        Returns:
            CallState: Updated call state
        """
        with self.lock:
            call_state = self.calls.get(call_id)
            if call_state:
                call_state.update_extracted_info(extracted_info)
                logger.info(f"Updated extracted info for call {call_id}: {extracted_info}")
            return call_state
    
    def process_confirmation(self, call_id, digit):
        """
        Process user confirmation response
        
        Args:
            call_id (str): Twilio Call SID
            digit (str): User input digit
            
        Returns:
            str: TwiML response
        """
        with self.lock:
            call_state = self.calls.get(call_id)
            if not call_state:
                return self._create_empty_response()
            
            if digit == "1":  # Yes - confirm reservation
                # In a real implementation, we would save to Google Sheets here
                call_state.complete_call()
                response_text = response_generator.generate_completion()
                response = tts_handler.create_hangup_response(response_text)
                logger.info(f"Call {call_id} completed successfully")
            else:  # No or invalid - ask for correction
                call_state.set_confirmation_pending(False)
                response_text = response_generator.generate_correction()
                response = tts_handler.create_response(response_text)
                logger.info(f"Call {call_id} needs correction")
            
            return response
    
    def update_call_status(self, call_id, status, duration=""):
        """
        Update call status from Twilio

        Args:
            call_id (str): Twilio Call SID
            status (str): Call status (completed, failed, etc.)
            duration (str): Call duration (if completed)
        """
        with self.lock:
            call_state = self.calls.get(call_id)
            if call_state:
                if status == "completed":
                    # Check if this is an early disconnection
                    if (call_state.call_phase in ["greeting", "gathering"] and
                        call_state.has_missing_info() and
                        not call_state.has_complete_info()):
                        call_state.mark_early_disconnected()
                        logger.warning(f"Early disconnection detected for call {call_id}. "
                                     f"Phase: {call_state.call_phase}, "
                                     f"Duration: {duration}s, "
                                     f"Greeting played: {call_state.greeting_played}")
                    else:
                        call_state.complete_call()
                        if duration:
                            call_state.call_duration = int(duration)
                elif status == "failed":
                    call_state.fail_call()

                logger.info(f"Updated call {call_id} status to {status}")
    
    def cleanup_completed_calls(self, max_age=3600):
        """
        Remove completed calls older than max_age seconds

        Args:
            max_age (int): Maximum age in seconds
        """
        current_time = time.time()
        with self.lock:
            completed_calls = [
                call_id for call_id, call_state in self.calls.items()
                if call_state.status in ["completed", "failed", "early_disconnected"] and
                (current_time - call_state.last_update) > max_age
            ]

            for call_id in completed_calls:
                del self.calls[call_id]

            if completed_calls:
                logger.info(f"Cleaned up {len(completed_calls)} completed/failed/early_disconnected calls")

    def get_early_disconnection_stats(self):
        """
        Get statistics about early disconnections

        Returns:
            dict: Statistics about early disconnections
        """
        with self.lock:
            early_disconnected = [
                call_state for call_state in self.calls.values()
                if call_state.status == "early_disconnected"
            ]

            total_early_disconnections = len(early_disconnected)
            avg_duration = sum(call.call_duration for call in early_disconnected) / total_early_disconnections if total_early_disconnections > 0 else 0

            return {
                "total_early_disconnections": total_early_disconnections,
                "average_duration_seconds": round(avg_duration, 2),
                "early_disconnected_calls": [call.call_id for call in early_disconnected]
            }
    
    def _create_empty_response(self):
        """Create an empty TwiML response"""
        return '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'

# Example usage
if __name__ == "__main__":
    # This is just for testing purposes
    manager = CallStateManager()
    print("Call State Manager initialized")