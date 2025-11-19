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
        Parse time from customer text (enhanced)

        Args:
            time_text (str): Customer's time text

        Returns:
            str: Parsed time in HH:MM format
        """
        import re
        text = time_text.lower().strip()

        # Handle common time expressions first
        if "morning" in text and not any(word in text for word in ["evening", "afternoon", "night"]):
            return "11:00"
        elif "afternoon" in text:
            return "15:00"
        elif "evening" in text or "night" in text:
            return "19:00"
        elif "lunch" in text:
            return "13:00"
        elif "dinner" in text:
            return "19:00"
        elif "breakfast" in text:
            return "09:00"

        # Handle specific time formats with regex
        # Pattern for HH:MM AM/PM or H AM/PM
        time_pattern = r'(\d{1,2})(?::(\d{2}))?\s*(a\.?m\.?|p\.?m\.?|am|pm)?'
        match = re.search(time_pattern, text)

        if match:
            hour = int(match.group(1))
            minute = match.group(2) if match.group(2) else "00"
            am_pm = match.group(3).lower() if match.group(3) else None

            if hour < 1 or hour > 12:
                pass  # Continue to other patterns
            else:
                # Convert to 24-hour format
                if am_pm:
                    if am_pm in ['a.m.', 'am', 'a m']:
                        if hour == 12:
                            hour = 0
                    elif am_pm in ['p.m.', 'pm', 'p m']:
                        if hour != 12:
                            hour += 12
                else:
                    # No AM/PM specified, assume afternoon for hours 1-6, morning for 7-12
                    if 1 <= hour <= 6:
                        hour += 12
                    elif hour == 12:
                        hour = 12  # Noon

                return f"{hour:02d}:{minute}"

        # Handle "o'clock" expressions
        oclock_match = re.search(r"(\d{1,2})\s*o'?clock", text)
        if oclock_match:
            hour = int(oclock_match.group(1))
            if 1 <= hour <= 12:
                # Assume afternoon/evening for hours 1-6, morning for 7-12
                if 1 <= hour <= 6:
                    return f"{hour + 12:02d}:00"
                else:
                    return f"{hour:02d}:00"

        # Handle written numbers (one, two, etc.)
        number_words = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
            'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10, 'eleven': 11, 'twelve': 12,
            '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, '11': 11, '12': 12
        }

        for word, num in number_words.items():
            if word in text:
                # Check for AM/PM context
                if any(pm in text for pm in ['pm', 'p.m.', 'evening', 'night']):
                    if num != 12:
                        hour = num + 12
                    else:
                        hour = 12
                elif any(am in text for am in ['am', 'a.m.', 'morning']):
                    if num == 12:
                        hour = 0
                    else:
                        hour = num
                else:
                    # No AM/PM, use same logic as o'clock
                    if 1 <= num <= 6:
                        hour = num + 12
                    else:
                        hour = num
                return f"{hour:02d}:00"

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