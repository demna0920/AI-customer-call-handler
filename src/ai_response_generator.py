"""
AI Response Generator for Real-time Voice Reservation System

This module generates appropriate responses based on call state and manages response templates.
"""

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIResponseGenerator:
    """Generates AI responses based on call state"""
    
    def __init__(self):
        # Restaurant information
        self.restaurant_info = {
            "name": "Korean BBQ House London",
            "location": "Central London",
            "operating_hours": "11:00 AM to 9:00 PM daily",
            "parking": "No parking available. Please use public transport.",
            "halal_options": "Yes, we have halal certified chicken galbi and beef dishes.",
            "vegan_options": "Yes, we have mushroom grill dishes and vegetable sides.",
            "specialties": "Authentic Korean BBQ with premium meats, fresh vegetables, and traditional banchan.",
            "price_range": "£25-£45 per person",
            "reservations": "Reservations recommended, especially for weekends.",
            "phone": "02-1234-5678"
        }

        # Response templates in English with natural, conversational language
        self.templates = {
            "greeting": "Hello! Welcome to Korean BBQ House London. How can I help you today?",
            "info_request_name": "May I have your name for the reservation?",
            "info_request_date": "What date would you like to make your reservation for?",
            "info_request_time": "What time would you prefer?",
            "info_request_party_size": "How many people will be in your party?",
            "info_request_phone": "May I have your phone number for confirmation?",
            "info_request_email": "May I have your email address for confirmation?",
            "info_request_all": "To make a reservation, may I have your name, date, and time all at once? For example, you can say 'I'm James and I'd like to book for September 20th at 7 p.m.'",
            "confirmation": "Let me confirm your reservation. {name}, you'd like to book for {date} at {time}. Is that correct? Press 1 for yes or 2 for no.",
            "clarification": "I'm sorry, I didn't catch that clearly. Could you please repeat that for me?",
            "completion": "Excellent! Your reservation has been confirmed. We look forward to serving you authentic Korean BBQ at Korean BBQ House London!",
            "correction": "Let's start over. Could you please provide your information once more?",
            "gathering_complete": "Thank you for that information. Let me confirm the details with you.",
            "reservation_confirmed": "Perfect! Your reservation is all set for {date} at {time}, {name}. We'll see you at Korean BBQ House London!",
            "reservation_cancelled": "I've cancelled that reservation for you. Is there anything else I can help you with?",
            "goodbye": "Thank you for calling Korean BBQ House London. Have a wonderful day!",
            "processing": "Just a moment while I process that information for you.",
            "repeat_info": "Let me repeat that back to you to make sure I have it right.",
            "ask_for_more_info": "Could you provide a bit more information about what you're looking for?",
            "unable_to_help": "I'm sorry, but I'm unable to help with that specific request. Would you like to speak with a human representative?",
            "thank_you": "Thank you for that information.",
            "please_hold": "Please hold on for just a moment.",
            "connecting": "I'm connecting you with a representative now.",
            "apology": "I apologize for any confusion. Let me try to help you better.",
            "offer_assistance": "Is there anything else I can assist you with today?",

            # Restaurant-specific responses
            "operating_hours": f"We're open from {self.restaurant_info['operating_hours']}.",
            "parking": self.restaurant_info['parking'],
            "halal_menu": self.restaurant_info['halal_options'],
            "vegan_menu": self.restaurant_info['vegan_options'],
            "menu_info": f"We specialize in {self.restaurant_info['specialties']} Our prices range from {self.restaurant_info['price_range']} per person.",
            "location": f"We're located in {self.restaurant_info['location']}.",
            "reservations_info": self.restaurant_info['reservations'],
            "contact": f"You can reach us at {self.restaurant_info['phone']}.",

            # General inquiry responses
            "general_help": "I can help you with reservations, menu information, operating hours, or any other questions about Korean BBQ House London.",
            "transfer_to_human": "For more complex inquiries, let me connect you with one of our staff members.",
            "welcome_back": "Welcome back to Korean BBQ House London! How can I assist you today?",

            # Confirmation and follow-up
            "confirm_reservation_details": "To confirm your reservation details: {name}, booking for {date} at {time}. Does that sound right?",
            "reservation_reminder": "Please arrive 10 minutes before your reservation time. We look forward to serving you!",
            "party_size": "How many people will be in your party?",
            "special_requests": "Do you have any special requests or dietary requirements?"
        }
    
    def generate_next_response(self, call_state):
        """
        Generate the next appropriate response based on call state
        
        Args:
            call_state (CallState): Current call state
            
        Returns:
            str: Generated response text
        """
        try:
            if not call_state:
                return self.templates["clarification"]
            
            # Determine response based on call phase
            if call_state.call_phase == "greeting":
                call_state.call_phase = "gathering"
                return self.templates["greeting"]
            
            elif call_state.call_phase == "gathering":
                if call_state.has_missing_info():
                    # Request missing information
                    missing_fields = call_state.get_missing_fields()
                    if missing_fields:
                        first_missing = missing_fields[0]
                        return self.templates[f"info_request_{first_missing}"]
                else:
                    # All information gathered, move to confirmation
                    call_state.call_phase = "confirming"
                    call_state.set_confirmation_pending(True)
                    return self.templates["gathering_complete"]
            
            elif call_state.call_phase == "confirming":
                if call_state.has_complete_info():
                    # Generate confirmation message
                    info = call_state.extracted_info
                    return self.templates["confirmation"].format(
                        name=info["name"] or "customer",
                        date=info["date"] or "the date",
                        time=info["time"] or "the time"
                    )
                else:
                    # Should not happen, but handle gracefully
                    return self.templates["clarification"]
            
            elif call_state.call_phase == "completed":
                return self.templates["completion"]
            
            else:
                # Default response
                return self.templates["clarification"]
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self.templates["clarification"]
    
    def generate_greeting(self):
        """Generate initial greeting"""
        return self.templates["greeting"]
    
    def generate_info_request(self, missing_field):
        """
        Generate request for specific missing information
        
        Args:
            missing_field (str): Field that is missing (name, date, time)
            
        Returns:
            str: Request for missing information
        """
        template_key = f"info_request_{missing_field}"
        return self.templates.get(template_key, self.templates["clarification"])
    
    def generate_confirmation(self, name, date, time):
        """
        Generate confirmation message
        
        Args:
            name (str): Customer name
            date (str): Reservation date
            time (str): Reservation time
            
        Returns:
            str: Confirmation message
        """
        return self.templates["confirmation"].format(
            name=name or "customer",
            date=date or "the date",
            time=time or "the time"
        )
    
    def generate_clarification(self):
        """Generate clarification request"""
        return self.templates["clarification"]
    
    def generate_completion(self):
        """Generate completion message"""
        return self.templates["completion"]
    
    def generate_correction(self):
        """Generate correction request"""
        return self.templates["correction"]
    
    def generate_reservation_confirmed(self, name, date, time):
        """
        Generate reservation confirmed message
        
        Args:
            name (str): Customer name
            date (str): Reservation date
            time (str): Reservation time
            
        Returns:
            str: Reservation confirmed message
        """
        return self.templates["reservation_confirmed"].format(
            name=name or "customer",
            date=date or "the date",
            time=time or "the time"
        )
    
    def generate_goodbye(self):
        """Generate goodbye message"""
        return self.templates["goodbye"]
    
    def generate_processing(self):
        """Generate processing message"""
        return self.templates["processing"]
    
    def generate_repeat_info(self, name, date, time):
        """
        Generate repeat information message

        Args:
            name (str): Customer name
            date (str): Reservation date
            time (str): Reservation time

        Returns:
            str: Repeat information message
        """
        return self.templates["repeat_info"] + " " + self.templates["confirm_reservation_details"].format(
            name=name or "customer",
            date=date or "the date",
            time=time or "the time"
        )

    def detect_intent(self, text, call_state=None):
        """
        Detect the user's intent from their speech

        Args:
            text (str): User's speech text
            call_state (CallState): Current call state for context

        Returns:
            str: Detected intent (reservation, hours, menu, parking, etc.)
        """
        text_lower = text.lower()

        # Check for conversation-ending phrases first
        if any(phrase in text_lower for phrase in [
            "that's all", "no more", "nothing else", "that's it", "no thanks",
            "i'm good", "that's fine", "no more questions", "that's everything"
        ]):
            return "end_conversation"

        # If we're in a reservation conversation, check for information provision
        if call_state and call_state.intent == "reservation":
            # Check if user is providing name
            if any(phrase in text_lower for phrase in ["my name is", "i'm", "name is", "call me", "i am"]):
                return "providing_name"
            # Check if user is providing date
            if any(word in text_lower for word in ["tomorrow", "today", "next", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]) or any(char in text_lower for char in ["-", "/"]):
                return "providing_date"
            # Check if user is providing time
            time_indicators = ["at", "o'clock", "pm", "am", "evening", "afternoon", "morning", "night"]
            if any(word in text_lower for word in time_indicators):
                # But not if they're asking about hours
                if not any(word in text_lower for word in ["what", "your", "opening", "closing", "hours", "time"]):
                    return "providing_time"
            # Check if user is providing party size
            if any(word in text_lower for word in ["people", "person", "party", "group"]) or any(char.isdigit() for char in text_lower):
                # But not if they're asking a question
                if not any(word in text_lower for word in ["how many", "what", "question"]):
                    return "providing_party_size"
            # Check if user is providing phone number
            if any(char.isdigit() for char in text_lower) and ("phone" in text_lower or "number" in text_lower or "call" in text_lower):
                return "providing_phone"
            # Check if user is providing email
            if "@" in text_lower and "." in text_lower:
                return "providing_email"
            # If we're in reservation mode and the user just says a single word that could be a name
            if call_state.call_phase == "gathering" and call_state.get_missing_fields() and call_state.get_missing_fields()[0] == "name":
                # If the user just says a single word after we asked for their name, treat it as providing_name
                words = text_lower.strip().split()
                if len(words) == 1 and words[0].isalpha():
                    return "providing_name"
            # Special handling for time expressions that might not have clear time indicators
            if call_state.call_phase == "gathering" and call_state.get_missing_fields() and call_state.get_missing_fields()[0] == "time":
                # If we're asking for time and the user provides something that could be a time
                time_words = ["p.m.", "a.m.", "evening", "afternoon", "morning", "night"]
                if any(word in text_lower for word in time_words) or any(char.isdigit() for char in text_lower):
                    return "providing_time"
            # Special handling for party size
            if call_state.call_phase == "gathering" and call_state.get_missing_fields() and call_state.get_missing_fields()[0] == "party_size":
                # If we're asking for party size and the user provides a number
                if any(char.isdigit() for char in text_lower):
                    return "providing_party_size"
            # Special handling for phone number
            if call_state.call_phase == "gathering" and call_state.get_missing_fields() and call_state.get_missing_fields()[0] == "phone":
                # If we're asking for phone and the user provides numbers
                if any(char.isdigit() for char in text_lower):
                    return "providing_phone"
            # Special handling for email
            if call_state.call_phase == "gathering" and call_state.get_missing_fields() and call_state.get_missing_fields()[0] == "email":
                # If we're asking for email and the user provides an email format
                if "@" in text_lower and "." in text_lower:
                    return "providing_email"

        # Reservation intents
        if any(word in text_lower for word in ["book", "reserve", "reservation", "table", "booking", "make a reservation"]):
            return "reservation"

        # Operating hours
        if any(word in text_lower for word in ["hours", "open", "close", "time", "operating", "when"]):
            return "hours"

        # Menu inquiries
        if any(word in text_lower for word in ["menu", "food", "dish", "eat", "special", "recommend", "what do you have"]):
            return "menu"

        # Halal inquiries
        if "halal" in text_lower:
            return "halal"

        # Vegan inquiries
        if any(word in text_lower for word in ["vegan", "vegetarian", "plant-based"]):
            return "vegan"

        # Parking inquiries
        if any(word in text_lower for word in ["parking", "car", "drive", "park"]):
            return "parking"

        # Location inquiries
        if any(word in text_lower for word in ["location", "address", "where", "find", "directions"]):
            return "location"

        # Contact inquiries
        if any(word in text_lower for word in ["phone", "call", "contact", "number", "reach you"]):
            return "contact"

        # Price inquiries
        if any(word in text_lower for word in ["price", "cost", "expensive", "cheap", "how much"]):
            return "price"

        return "general"

    def generate_response_for_intent(self, intent, context="", call_state=None):
        """
        Generate appropriate response based on detected intent

        Args:
            intent (str): Detected intent
            context (str): Additional context if needed
            call_state (CallState): Current call state for context

        Returns:
            str: Response text
        """
        intent_responses = {
            "reservation": "I'd be happy to help you make a reservation. May I have your name please?",
            "providing_name": "Thank you! What date would you like to make your reservation for?",
            "providing_date": "Great! What time would you prefer?",
            "providing_time": "Perfect! How many people will be in your party?",
            "providing_party_size": "Got it! May I have your phone number for confirmation?",
            "providing_phone": "Thank you! May I have your email address for confirmation?",
            "providing_email": "Perfect! Let me confirm your reservation details.",
            "end_conversation": "Thank you for calling Korean BBQ House London. Have a wonderful day!",
            "hours": self.templates["operating_hours"],
            "menu": self.templates["menu_info"],
            "halal": self.templates["halal_menu"],
            "vegan": self.templates["vegan_menu"],
            "parking": self.templates["parking"],
            "location": self.templates["location"],
            "contact": self.templates["contact"],
            "price": f"Our prices range from {self.restaurant_info['price_range']} per person.",
            "general": self.templates["general_help"]
        }

        response = intent_responses.get(intent, self.templates["general_help"])

        # Add follow-up question for most intents (except reservation and ending)
        if intent not in ["reservation", "providing_name", "providing_date", "providing_time", "end_conversation"]:
            response += " Is there anything else I can help you with?"

        return response

    def generate_party_size_request(self):
        """Generate request for party size"""
        return self.templates["party_size"]

    def generate_special_requests(self):
        """Generate special requests question"""
        return self.templates["special_requests"]

    def generate_reservation_reminder(self):
        """Generate reservation reminder"""
        return self.templates["reservation_reminder"]

# Example usage
if __name__ == "__main__":
    # This is just for testing purposes
    generator = AIResponseGenerator()
    print("AI Response Generator initialized")
    
    # Test generating a greeting
    greeting = generator.generate_greeting()
    print(f"Greeting: {greeting}")