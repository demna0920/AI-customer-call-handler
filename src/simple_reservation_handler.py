#!/usr/bin/env python3
"""
Simple Reservation Handler for Step-by-Step Conversation Flow
"""

import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
from database import ReservationDatabase
from utils.fallback_extraction import clean_name, parse_date, parse_time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleReservationHandler:
    """Handles simple step-by-step reservation conversation flow"""
    
    def __init__(self, db_path: str = "reservations.db"):
        """
        Initialize reservation handler
        
        Args:
            db_path (str): Path to database file
        """
        self.db = ReservationDatabase(db_path)
        logger.info("Simple reservation handler initialized")
    
    def start_reservation_flow(self) -> str:
        """
        Start the reservation flow
        
        Returns:
            str: First question to ask the customer
        """
        logger.info("Starting reservation flow")
        return "Great. May I have your name, please?"
    
    def process_customer_response(self, session_data: Dict, customer_response: str) -> Tuple[str, bool, Dict]:
        """
        Process customer response and return next question or confirmation
        
        Args:
            session_data (dict): Current session data with step and collected info
            customer_response (str): Customer's response
            
        Returns:
            tuple: (response_text, is_complete, updated_session_data)
        """
        # Initialize session data if not present
        if not session_data:
            session_data = {
                "step": 1,  # 1=name, 2=date, 3=time
                "name": None,
                "date": None,
                "time": None
            }
        
        current_step = session_data["step"]
        
        # Process based on current step
        if current_step == 1:  # Collecting name
            # Extract just the name from the customer response
            extracted_name = clean_name(customer_response)
            session_data["name"] = extracted_name
            session_data["step"] = 2
            logger.info(f"Collected name: {session_data['name']}")
            return "What date would you like to make your reservation?", False, session_data
            
        elif current_step == 2:  # Collecting date
            # Simple date parsing (in a real system, you'd use NLP)
            parsed_date = parse_date(customer_response)
            session_data["date"] = parsed_date
            session_data["step"] = 3
            logger.info(f"Collected date: {session_data['date']}")
            return "What time would you prefer for your reservation?", False, session_data
            
        elif current_step == 3:  # Collecting time
            # Simple time parsing (in a real system, you'd use NLP)
            parsed_time = parse_time(customer_response)
            session_data["time"] = parsed_time
            session_data["step"] = 4  # Completed
            logger.info(f"Collected time: {session_data['time']}")
            
            # Save reservation to database
            success = self._save_reservation(session_data)
            if success:
                # Create confirmation message
                confirmation = self._create_confirmation_message(session_data)
                return confirmation, True, session_data
            else:
                return "Sorry, there was an error saving your reservation. Please try again.", False, session_data
        
        else:
            return "Sorry, I didn't understand that. May I have your name, please?", False, session_data
    
    def _save_reservation(self, session_data: Dict) -> bool:
        """
        Save completed reservation to database
        
        Args:
            session_data (dict): Completed session data
            
        Returns:
            bool: True if saved successfully
        """
        try:
            # Check for duplicates first
            if self.db.check_duplicate_reservation(
                session_data["name"],
                session_data["date"],
                session_data["time"]
            ):
                logger.info(f"Duplicate reservation detected for {session_data['name']} on {session_data['date']} at {session_data['time']}")
                return True  # Return success to be idempotent
                
            # Create customer record
            customer_id = self.db.create_customer(session_data["name"])
            
            # Create reservation record
            reservation_id = self.db.create_reservation(
                customer_id,
                session_data["date"],
                session_data["time"],
                2  # Default party size
            )
            
            logger.info(f"Saved reservation ID {reservation_id} for customer ID {customer_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving reservation: {e}")
            return False
    
    def _create_confirmation_message(self, session_data: Dict) -> str:
        """
        Create confirmation message
        
        Args:
            session_data (dict): Completed session data
            
        Returns:
            str: Confirmation message
        """
        name = session_data["name"]
        date = session_data["date"]
        time = session_data["time"]
        
        # Format date for confirmation message
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%B %dth")
        
        # Format time for confirmation message
        hour, minute = time.split(":")
        hour_int = int(hour)
        if hour_int > 12:
            formatted_time = f"{hour_int - 12}:{minute} PM"
        elif hour_int == 12:
            formatted_time = f"12:{minute} PM"
        elif hour_int == 0:
            formatted_time = f"12:{minute} AM"
        else:
            formatted_time = f"{hour_int}:{minute} AM"
        
        return f"Mr. {name}, your reservation for {formatted_date} at {formatted_time} has been confirmed."