#!/usr/bin/env python3
"""
Simple Reservation Handler for Step-by-Step Conversation Flow
"""

import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
from database import ReservationDatabase

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
            extracted_name = self._parse_name(customer_response)
            session_data["name"] = extracted_name
            session_data["step"] = 2
            logger.info(f"Collected name: {session_data['name']}")
            return "What date would you like to make your reservation?", False, session_data
            
        elif current_step == 2:  # Collecting date
            # Simple date parsing (in a real system, you'd use NLP)
            parsed_date = self._parse_date(customer_response)
            session_data["date"] = parsed_date
            session_data["step"] = 3
            logger.info(f"Collected date: {session_data['date']}")
            return "What time would you prefer for your reservation?", False, session_data
            
        elif current_step == 3:  # Collecting time
            # Simple time parsing (in a real system, you'd use NLP)
            parsed_time = self._parse_time(customer_response)
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
    
    def _parse_name(self, name_text: str) -> str:
        """
        Parse name from customer text (extract actual name from phrases like "my name is John")
        
        Args:
            name_text (str): Customer's name text
            
        Returns:
            str: Extracted name
        """
        text = name_text.strip()
        text_lower = text.lower()
        
        # Handle common name introduction patterns
        if "my name is" in text_lower:
            # Extract everything after "my name is"
            parts = text_lower.split("my name is", 1)
            if len(parts) > 1:
                name = parts[1].strip()
                # Remove punctuation from the end
                name = name.rstrip('.,!?;:')
                # Take only the first word(s) as the name (remove extra words)
                name_words = name.split()
                if name_words:
                    # Take first 2 words maximum (first name + last name)
                    return " ".join(name_words[:2]).title()
        
        elif "i'm" in text_lower or "i am" in text_lower:
            # Handle "I'm John" or "I am John"
            for phrase in ["i'm", "i am"]:
                if phrase in text_lower:
                    parts = text_lower.split(phrase, 1)
                    if len(parts) > 1:
                        name = parts[1].strip()
                        # Remove punctuation from the end
                        name = name.rstrip('.,!?;:')
                        name_words = name.split()
                        if name_words:
                            return " ".join(name_words[:2]).title()
        
        elif "name is" in text_lower:
            # Handle "name is John"
            parts = text_lower.split("name is", 1)
            if len(parts) > 1:
                name = parts[1].strip()
                # Remove punctuation from the end
                name = name.rstrip('.,!?;:')
                name_words = name.split()
                if name_words:
                    return " ".join(name_words[:2]).title()
        
        elif "call me" in text_lower:
            # Handle "call me John"
            parts = text_lower.split("call me", 1)
            if len(parts) > 1:
                name = parts[1].strip()
                # Remove punctuation from the end
                name = name.rstrip('.,!?;:')
                name_words = name.split()
                if name_words:
                    return " ".join(name_words[:2]).title()
        
        else:
            # If no pattern matches, assume the entire text is the name
            # But clean it up (remove common words)
            words = text.split()
            # Filter out common words that aren't names
            filtered_words = []
            skip_words = ["is", "am", "the", "a", "an", "and", "or", "but", "please", "thank", "you"]
            
            for word in words:
                if word.lower() not in skip_words and word.isalpha():
                    filtered_words.append(word)
            
            if filtered_words:
                # Take first 2 words maximum
                return " ".join(filtered_words[:2]).title()
        
        # Fallback: return the original text cleaned up
        cleaned_text = text.strip().rstrip('.,!?;:')
        return cleaned_text.title()
    
    def _parse_date(self, date_text: str) -> str:
        """
        Parse date from customer text (simplified)
        
        Args:
            date_text (str): Customer's date text
            
        Returns:
            str: Parsed date in YYYY-MM-DD format
        """
        text = date_text.lower()
        today = datetime.now()
        
        if "today" in text:
            return today.strftime("%Y-%m-%d")
        elif "tomorrow" in text:
            from datetime import timedelta
            tomorrow = today + timedelta(days=1)
            return tomorrow.strftime("%Y-%m-%d")
        elif "september" in text or "sep" in text:
            # Extract day from text
            import re
            match = re.search(r'(\d{1,2})', date_text)
            if match:
                day = int(match.group(1))
                return f"2025-09-{day:02d}"
        
        # Default to today if parsing fails
        return today.strftime("%Y-%m-%d")
    
    def _parse_time(self, time_text: str) -> str:
        """
        Parse time from customer text (simplified)
        
        Args:
            time_text (str): Customer's time text
            
        Returns:
            str: Parsed time in HH:MM format
        """
        text = time_text.lower()
        
        # Handle AM/PM times with regex
        import re
        
        # Pattern for times like "11:00 a.m.", "11am", "11 am"
        am_pattern = r"(\d{1,2})(?:\s*:\s*\d{2})?\s*(?:a\.m\.|am|a m)"
        pm_pattern = r"(\d{1,2})(?:\s*:\s*\d{2})?\s*(?:p\.m\.|pm|p m)"
        
        # Check for AM times
        am_match = re.search(am_pattern, text)
        if am_match:
            hour = int(am_match.group(1))
            if 1 <= hour <= 12:
                # Convert to 24-hour format
                if hour == 12:
                    return "00:00"  # 12 AM is 00:00
                else:
                    return f"{hour:02d}:00"
        
        # Check for PM times
        pm_match = re.search(pm_pattern, text)
        if pm_match:
            hour = int(pm_match.group(1))
            if 1 <= hour <= 12:
                # Convert to 24-hour format
                if hour == 12:
                    return "12:00"  # 12 PM is 12:00
                else:
                    return f"{hour + 12:02d}:00"
        
        # Handle specific times (fallback for existing functionality)
        if "3:00" in text or "3pm" in text or "3 pm" in text:
            return "15:00"
        elif "6:00" in text or "6pm" in text or "6 pm" in text:
            return "18:00"
        elif "7:00" in text or "7pm" in text or "7 pm" in text:
            return "19:00"
        elif "7:30" in text or "7:30pm" in text:
            return "19:30"
        
        # Default to 7:00 PM if parsing fails
        return "19:00"
    
    def _save_reservation(self, session_data: Dict) -> bool:
        """
        Save completed reservation to database
        
        Args:
            session_data (dict): Completed session data
            
        Returns:
            bool: True if saved successfully
        """
        try:
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

def main():
    """Test the simple reservation handler"""
    print("🍽️ Korean BBQ House London - Simple Reservation Handler Test")
    print("=" * 60)
    
    try:
        # Initialize handler
        handler = SimpleReservationHandler("test_simple_reservations.db")
        print("✅ Simple reservation handler initialized")
        
        # Test complete flow
        session_data = {}
        
        # Start reservation flow
        response = handler.start_reservation_flow()
        print(f"🤖 AI: '{response}'")
        
        # Customer provides name
        print(f"🗣️  Customer: 'My name is Kim Cheolsu.'")
        response, is_complete, session_data = handler.process_customer_response(session_data, "My name is Kim Cheolsu.")
        print(f"🤖 AI: '{response}'")
        
        # Customer provides date
        print(f"🗣️  Customer: 'September 10th, please.'")
        response, is_complete, session_data = handler.process_customer_response(session_data, "September 10th, please.")
        print(f"🤖 AI: '{response}'")
        
        # Customer provides time
        print(f"🗣️  Customer: '3:00 PM, please.'")
        response, is_complete, session_data = handler.process_customer_response(session_data, "3:00 PM, please.")
        
        if is_complete:
            print(f"🤖 AI: '{response}'")
            print(f"✅ Reservation completed successfully!")
        else:
            print(f"❌ Reservation failed: {response}")
        
        print("\n🎉 Simple reservation handler test completed!")
        
    except Exception as e:
        print(f"❌ Simple reservation handler test failed: {e}")

if __name__ == "__main__":
    main()