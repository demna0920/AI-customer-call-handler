import logging
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

def clean_name(name_text):
    """
    Clean filler words and extract name from text.
    Combines logic from simple_reservation_handler and previous clean_name.
    """
    if not name_text:
        return ""

    text = name_text.strip()
    
    # Remove common filler words
    filler_words = ["uh", "um", "ah", "er", "like", "so", "actually", "basically"]
    for filler in filler_words:
        # Remove filler words at start
        if text.lower().startswith(f"{filler} "):
            text = text[len(filler)+1:]
        # Remove filler words in middle (simplified)
        text = text.replace(f" {filler} ", " ")
        
    text_lower = text.lower()
    
    # Handle common name introduction patterns
    if "my name is" in text_lower:
        parts = text_lower.split("my name is", 1)
        if len(parts) > 1:
            name = parts[1].strip()
            name = name.rstrip('.,!?;:')
            name_words = name.split()
            if name_words:
                return " ".join(name_words[:2]).title()
    
    elif "i'm" in text_lower or "i am" in text_lower:
        for phrase in ["i'm", "i am"]:
            if phrase in text_lower:
                parts = text_lower.split(phrase, 1)
                if len(parts) > 1:
                    name = parts[1].strip()
                    name = name.rstrip('.,!?;:')
                    name_words = name.split()
                    if name_words:
                        return " ".join(name_words[:2]).title()
    
    elif "name is" in text_lower:
        parts = text_lower.split("name is", 1)
        if len(parts) > 1:
            name = parts[1].strip()
            name = name.rstrip('.,!?;:')
            name_words = name.split()
            if name_words:
                return " ".join(name_words[:2]).title()
    
    elif "call me" in text_lower:
        parts = text_lower.split("call me", 1)
        if len(parts) > 1:
            name = parts[1].strip()
            name = name.rstrip('.,!?;:')
            name_words = name.split()
            if name_words:
                return " ".join(name_words[:2]).title()
    
    # If no pattern matches, try to clean up the text
    words = text.split()
    filtered_words = []
    skip_words = ["is", "am", "the", "a", "an", "and", "or", "but", "please", "thank", "you"]
    
    for word in words:
        if word.lower() not in skip_words and word.isalpha():
            filtered_words.append(word)
    
    if filtered_words:
        return " ".join(filtered_words[:2]).title()

    # Fallback
    return text.strip().rstrip('.,!?;:').title()

def parse_date(date_text):
    """
    Parse date from text, handling relative dates and days of the week.
    """
    if not date_text:
        return datetime.now().strftime("%Y-%m-%d")
        
    text = date_text.lower()
    today = datetime.now()
    
    if "today" in text:
        return today.strftime("%Y-%m-%d")
    elif "tomorrow" in text:
        tomorrow = today + timedelta(days=1)
        return tomorrow.strftime("%Y-%m-%d")
    
    # Handle days of the week
    weekdays = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, 
        "friday": 4, "saturday": 5, "sunday": 6
    }
    
    for day_name, day_num in weekdays.items():
        if day_name in text:
            current_day_num = today.weekday()
            days_ahead = day_num - current_day_num
            
            if days_ahead <= 0: # Target day already happened this week
                days_ahead += 7
                
            if "next " + day_name in text:
                days_ahead += 7
            
            target_date = today + timedelta(days=days_ahead)
            return target_date.strftime("%Y-%m-%d")

    # Simple month parsing (example)
    months = {
        "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }
    
    for month_name, month_num in months.items():
        if month_name in text:
            # Extract day
            match = re.search(r'(\d{1,2})', text)
            if match:
                day = int(match.group(1))
                # Assume current year or next year if date has passed
                try:
                    date_obj = datetime(today.year, month_num, day)
                    if date_obj < today:
                        date_obj = datetime(today.year + 1, month_num, day)
                    return date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    pass
                    
    return today.strftime("%Y-%m-%d")

def parse_time(time_str):
    """
    Convert natural language time to 24-hour format.
    """
    if not time_str:
        return None

    text = time_str.lower().strip()

    # Handle common time expressions
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
    # Added support for "100 pm" -> 1:00 PM
    time_pattern = r'(\d{1,4})(?::(\d{2}))?\s*(a\.?m\.?|p\.?m\.?|am|pm)?'
    match = re.search(time_pattern, text)

    if match:
        raw_hour = match.group(1)
        minute = match.group(2) if match.group(2) else "00"
        am_pm = match.group(3).lower() if match.group(3) else None

        # Handle "100" as "1:00"
        if len(raw_hour) >= 3 and not minute:
             if len(raw_hour) == 3:
                 hour = int(raw_hour[0])
                 minute = raw_hour[1:]
             else: # 4 digits
                 hour = int(raw_hour[:2])
                 minute = raw_hour[2:]
        else:
             hour = int(raw_hour)

        if 1 <= hour <= 12:
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

    # Handle written numbers
    number_words = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
        'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10, 'eleven': 11, 'twelve': 12
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

    return "19:00"  # Default fallback

def extract_reservation_info_fallback(text):
    """Simple text-based extraction as fallback"""
    text_lower = text.lower()

    # Default values
    name = ""
    date = ""
    time = ""

    # Try to extract name
    name = clean_name(text)

    # Try to extract date
    date = parse_date(text)

    # Try to extract time
    time = parse_time(text)

    logger.info(f"📋 Fallback extraction - Name: {name}, Date: {date}, Time: {time}")
    return {
        "name": name if name else "Customer",
        "date": date,
        "time": time if time else "19:00"
    }
