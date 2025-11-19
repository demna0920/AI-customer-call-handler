from flask import Flask, request, jsonify, render_template, send_from_directory
import os
from dotenv import load_dotenv
import whisper
import tempfile
from pydub import AudioSegment
import google.generativeai as genai
import json
import logging
from datetime import datetime
import sqlite3

# Twilio imports for real-time processing
from twilio.twiml.voice_response import VoiceResponse

# Import new modules for real-time processing
from call_state import CallStateManager
from audio_stream_processor import AudioStreamProcessor
from ai_response_generator import AIResponseGenerator
from tts_handler import TTSHandler
from simple_reservation_handler import SimpleReservationHandler
from utils.fallback_extraction import extract_reservation_info_fallback

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# .env 파일 로드
load_dotenv()

# Flask 앱 생성
app = Flask(__name__)

# Google Gemini API 키 설정
try:
    import google.generativeai as genai
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if GOOGLE_API_KEY:
        genai.configure(api_key=GOOGLE_API_KEY)
    else:
        GOOGLE_API_KEY = None
except ImportError:
    genai = None
    GOOGLE_API_KEY = None
    logger.warning("Google Generative AI not available. Using fallback text extraction.")

# Initialize components for real-time processing
call_state_manager = CallStateManager()
audio_processor = AudioStreamProcessor()
response_generator = AIResponseGenerator()
tts_handler = TTSHandler()
simple_reservation_handler = SimpleReservationHandler()

# Whisper 모델 로드
print("Loading Whisper model...")
model = whisper.load_model("base")
print("Whisper model loaded successfully!")

# 오디오 파일 변환
def convert_audio(file_path):
    try:
        temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_wav.close()
        
        sound = AudioSegment.from_file(file_path)
        sound = sound.set_frame_rate(16000).set_channels(1)
        sound.export(temp_wav.name, format="wav")
        
        return temp_wav.name
    except Exception as e:
        logger.error(f"Audio conversion error: {e}")
        return None

# 오디오 스트림 변환
def convert_audio_stream(audio_data, format="mulaw"):
    try:
        # Create temporary file for incoming audio data
        temp_audio = tempfile.NamedTemporaryFile(suffix='.raw', delete=False)
        temp_audio.write(audio_data)
        temp_audio.close()
        
        # Convert to WAV format
        temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_wav.close()
        
        # Handle different audio formats from Twilio
        if format == "mulaw":
            sound = AudioSegment.from_file(temp_audio.name, format="raw", frame_rate=8000, channels=1, sample_width=1)
            sound = sound.set_frame_rate(16000).set_channels(1)
        else:
            sound = AudioSegment.from_file(temp_audio.name)
            sound = sound.set_frame_rate(16000).set_channels(1)
        
        sound.export(temp_wav.name, format="wav")
        
        # Clean up temporary raw audio file
        os.unlink(temp_audio.name)
        
        return temp_wav.name
    except Exception as e:
        logger.error(f"Audio stream conversion error: {e}")
        return None

# Whisper로 실시간 음성 인식
def transcribe_audio_stream(file_path, previous_context=""):
    try:
        logger.info("📝 Transcribing audio stream with Whisper...")
        result = model.transcribe(file_path, language="en")
        text = result["text"].strip()
        
        # Combine with previous context for better accuracy
        full_text = previous_context + " " + text if previous_context else text
        logger.info(f"🗣️ Transcribed text: {text}")
        return full_text
    except Exception as e:
        logger.error(f"Whisper transcription error: {e}")
        return ""

# Whisper로 음성 인식
def transcribe_audio(file_path):
    try:
        logger.info("📝 Transcribing audio with Whisper...")
        result = model.transcribe(file_path, language="en")
        text = result["text"].strip()
        logger.info(f"🗣️ Transcribed text: {text}")
        return text
    except Exception as e:
        logger.error(f"Whisper transcription error: {e}")
        return ""

# Google Gemini로 정보 추출 (with fallback)
def extract_reservation_info(text):
    if not GOOGLE_API_KEY or genai is None:
        # API 키가 없을 때 간단한 텍스트 분석으로 대체
        logger.info("🔄 Using fallback text extraction (no Google API key)")
        return extract_reservation_info_fallback(text)

    try:
        prompt = f"""
        Please extract the name, date, and time from the customer's message.
        For the name: Extract the customer's actual name, ignoring filler words like "uh", "um", "like", "well", etc. The name should be the person's proper name (e.g., if they say "Uh, my name is John", extract "John").
        For relative dates like "tomorrow", "next week", "this weekend", etc., convert them to specific dates.
        For times mentioned in natural language like "3 o'clock", "in the afternoon", "evening", etc., convert them to 24-hour format.
        Today's date is {datetime.now().strftime("%Y-%m-%d")}. Use this as a reference for relative dates.
        Return the result in the following JSON format only. Do not include any other text.

        Example:
        {{
          "name": "John Doe",
          "date": "2024-03-15",
          "time": "15:00"
        }}

        Customer message:
        "{text}"
        """
        logger.info("🧠 Extracting information with Google Gemini...")
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        result = response.text.strip()
        logger.info(f"📋 Extracted information: {result}")

        # Remove markdown code block formatting if present
        if result.startswith("```json"):
            result = result[7:]  # Remove ```json
        if result.startswith("```"):
            result = result[3:]  # Remove ```
        if result.endswith("```"):
            result = result[:-3]  # Remove ```

        # Clean up any extra whitespace
        result = result.strip()

        return json.loads(result)
    except Exception as e:
        logger.error(f"Gemini extraction error: {e}")
        # 오류 시 기본값 반환
        return extract_reservation_info_fallback(text)

# Google Gemini로 정보 증분 추출 (with fallback)
def extract_reservation_info_incremental(text_segment, accumulated_text=""):
    """
    Extract reservation info from text segment, with option to accumulate context
    """
    full_text = accumulated_text + " " + text_segment if accumulated_text else text_segment

    if not GOOGLE_API_KEY or genai is None:
        # API 키가 없을 때 간단한 텍스트 분석으로 대체
        logger.info("🔄 Using fallback incremental extraction (no Google API key)")
        return extract_reservation_info_fallback(full_text)

    try:
        prompt = f"""
        Please extract the name, date, and time from the customer's message.
        For the name: Extract the customer's actual name, ignoring filler words like "uh", "um", "like", "well", etc. The name should be the person's proper name (e.g., if they say "Uh, my name is John", extract "John").
        For relative dates like "tomorrow", "next week", "this weekend", etc., convert them to specific dates.
        For times mentioned in natural language like "3 o'clock", "in the afternoon", "evening", etc., convert them to 24-hour format.
        Today's date is {datetime.now().strftime("%Y-%m-%d")}. Use this as a reference for relative dates.
        Conversation so far: "{full_text}"

        Return the result in the following JSON format only. Do not include any other text.

        {{
          "name": "John Doe",
          "date": "2024-03-15",
          "time": "15:00"
        }}
        """

        logger.info("🧠 Extracting incremental information with Google Gemini...")
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        result = response.text.strip()
        logger.info(f"📋 Extracted information: {result}")

        # Remove markdown code block formatting if present
        if result.startswith("```json"):
            result = result[7:]  # Remove ```json
        if result.startswith("```"):
            result = result[3:]  # Remove ```
        if result.endswith("```"):
            result = result[:-3]  # Remove ```

        # Clean up any extra whitespace
        result = result.strip()

        return json.loads(result)
    except Exception as e:
        logger.error(f"Gemini incremental extraction error: {e}")
        # 오류 시 기본값 반환
        return extract_reservation_info_fallback(full_text)

# 예약 정보 저장
def save_reservation(data):
    try:
        from database import db
        
        # Extract reservation data
        name = data.get("name", "")
        date = data.get("date", "")
        time = data.get("time", "")
        party_size = data.get("party_size", 2)
        special_requests = data.get("special_requests", "")
        
        if not name or not date or not time:
            logger.error("Missing required reservation data")
            return False
        
        # Check if customer already exists
        customer = db.get_customer_by_name(name)
        if customer:
            customer_id = customer['id']
            logger.info(f"Using existing customer ID {customer_id} for {name}")
        else:
            # Create new customer
            customer_id = db.create_customer(name)
            logger.info(f"Created new customer ID {customer_id} for {name}")
        
        # Create reservation
        reservation_id = db.create_reservation(
            customer_id,
            date,
            time,
            party_size,
            special_requests
        )
        
        logger.info(f"💾 Reservation saved successfully with ID {reservation_id}!")
        return True
    except Exception as e:
        logger.error(f"Reservation save error: {e}")
        return False

# 예약 정보 업데이트 (CSV에서는 사용하지 않음)
def update_reservation(sheet, row_index, data):
    # CSV에서는 별도의 업데이트 기능이 필요하지 않음
    return True

# 예약 정보 저장 또는 업데이트
def save_or_update_reservation(data, call_sid=None):
    # CSV 저장 방식으로 변경
    return save_reservation(data)

# 🎯 메인 테스트 엔드포인트
@app.route("/test-reservation", methods=["POST"])
def test_reservation():
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "Audio file is required"}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({"error": "Please select a file"}), 400

        temp_audio = tempfile.NamedTemporaryFile(delete=False)
        audio_file.save(temp_audio.name)
        temp_audio.close()

        logger.info("🔊 Converting audio file...")
        wav_path = convert_audio(temp_audio.name)
        if not wav_path:
            return jsonify({"error": "Audio conversion failed"}), 500

        text = transcribe_audio(wav_path)
        if not text:
            return jsonify({"error": "Audio transcription failed"}), 400

        reservation = extract_reservation_info(text)
        success = save_reservation(reservation)
        
        os.unlink(temp_audio.name)
        os.unlink(wav_path)

        if success:
            return jsonify({
                "status": "success",
                "message": "Reservation completed successfully!",
                "transcribed_text": text,
                "reservation_info": reservation
            })
        else:
            return jsonify({"error": "Reservation save failed"}), 500
            
    except Exception as e:
        logger.error(f"Server error: {e}")
        return jsonify({"error": "Server error occurred"}), 500

# 📞 Twilio incoming call endpoint
@app.route("/voice/incoming", methods=["POST"])
def incoming_call():
    """Handle incoming calls from Twilio"""
    call_sid = request.values.get('CallSid')
    from_number = request.values.get('From')
    
    logger.info(f"Incoming call from {from_number} with CallSid {call_sid}")
    
    # Initialize call state
    call_state = call_state_manager.initialize_call(call_sid, from_number)

    # Mark that greeting is about to be played
    call_state.set_greeting_played(True)

    # Generate greeting response using Eleven Labs TTS
    response_text = response_generator.generate_greeting()

    # Create TwiML response that continues the call using Eleven Labs and gathers speech input
    return tts_handler.create_gather_response(
        response_text,
        '/voice/gather',
        num_digits=0,  # Gather speech input, not digits
        speech_timeout='auto'
    )

# 📞 Twilio gather speech input endpoint
@app.route("/voice/gather", methods=["POST"])
def gather_input():
    """Handle gathered user input with simple step-by-step flow"""
    call_sid = request.values.get('CallSid')
    speech_result = request.values.get('SpeechResult', '')

    logger.info(f"Gathered speech for call {call_sid}: {speech_result}")

    # Process the speech result
    if speech_result:
        # Get or create call state
        call_state = call_state_manager.get_call_state(call_sid)
        if not call_state:
            call_state = call_state_manager.initialize_call(call_sid)
        
        # Check if this is a reservation request
        speech_lower = speech_result.lower()
        if "reservation" in speech_lower or "book" in speech_lower or "reserve" in speech_lower:
            # Start reservation flow
            call_state.intent = "reservation"
            call_state.call_phase = "gathering"
            
            # Initialize simple reservation session data
            if not hasattr(call_state, 'reservation_session'):
                call_state.reservation_session = {
                    "step": 1,  # 1=name, 2=date, 3=time
                    "name": None,
                    "date": None,
                    "time": None
                }
            
            # Check if we already have the customer's name from a previous interaction
            # This prevents asking for the name twice in the same call
            if (hasattr(call_state, 'reservation_session') and
                call_state.reservation_session.get("name") and
                call_state.reservation_session["step"] >= 1):
                # Skip asking for name again, move to date collection if we're at name step
                if call_state.reservation_session["step"] == 1:
                    # We have a name but are still at name step, move to date step
                    call_state.reservation_session["step"] = 2
                    response_text = "What date would you like to make your reservation?"
                elif call_state.reservation_session["step"] == 2:
                    # We already have name and are at date step
                    response_text = "What date would you like to make your reservation?"
                elif call_state.reservation_session["step"] == 3:
                    # We already have name and date, asking for time
                    response_text = "What time would you prefer for your reservation?"
                else:
                    # Reservation already completed
                    # Create confirmation message manually since we can't access the private method
                    session_data = call_state.reservation_session
                    name = session_data["name"]
                    date = session_data["date"]
                    time = session_data["time"]
                    from datetime import datetime
                    date_obj = datetime.strptime(date, "%Y-%m-%d")
                    formatted_date = date_obj.strftime("%B %dth")
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
                    response_text = f"Mr. {name}, your reservation for {formatted_date} at {formatted_time} has been confirmed."
                    return tts_handler.create_hangup_response(response_text)
            else:
                # Start the simple reservation flow
                response_text = simple_reservation_handler.start_reservation_flow()
                # Initialize session if not already done
                if not hasattr(call_state, 'reservation_session'):
                    call_state.reservation_session = {
                        "step": 1,  # 1=name, 2=date, 3=time
                        "name": None,
                        "date": None,
                        "time": None
                    }
            return tts_handler.create_gather_response(
                response_text,
                '/voice/gather',
                num_digits=0,
                speech_timeout='auto'
            )
        
        # Handle ongoing reservation flow
        if call_state.intent == "reservation" and hasattr(call_state, 'reservation_session'):
            # Process customer response using simple handler
            response_text, is_complete, updated_session = simple_reservation_handler.process_customer_response(
                call_state.reservation_session,
                speech_result
            )
            
            # Update session data
            call_state.reservation_session = updated_session
            
            if is_complete:
                # Reservation completed, hang up
                return tts_handler.create_hangup_response(response_text)
            else:
                # Continue gathering information
                return tts_handler.create_gather_response(
                    response_text,
                    '/voice/gather',
                    num_digits=0,
                    speech_timeout='auto'
                )
        
        # Handle general inquiries using existing logic
        intent = response_generator.detect_intent(speech_result, call_state)
        response_text = response_generator.generate_response_for_intent(intent, speech_result, call_state)
        
        # Update call state to track conversation
        if call_state:
            call_state.last_intent = intent
            call_state.conversation_history.append({
                "user_input": speech_result,
                "intent": intent,
                "response": response_text
            })
        
        return tts_handler.create_gather_response(
            response_text,
            '/voice/gather',
            num_digits=0,
            speech_timeout='auto'
        )

    # If no speech was detected, ask again and gather more input
    response_text = response_generator.generate_clarification()
    return tts_handler.create_gather_response(
        response_text,
        '/voice/gather',
        speech_timeout='auto'
    )

# 📞 Twilio audio stream endpoint
@app.route("/voice/stream", methods=["POST"])
def stream_audio():
    """Handle audio streaming from Twilio"""
    call_sid = request.values.get('CallSid')
    
    # Get audio data
    audio_data = request.data
    
    logger.info(f"Received audio stream for call {call_sid}")
    
    # Process audio and potentially generate response
    response = audio_processor.process_audio_stream(call_sid, audio_data)
    
    return response

# 📞 Twilio confirmation endpoint
@app.route("/voice/confirm", methods=["POST"])
def confirm_reservation():
    """Handle user confirmation responses"""
    call_sid = request.values.get('CallSid')
    digit = request.values.get('Digits', '')
    speech_result = request.values.get('SpeechResult', '')
    
    logger.info(f"Received confirmation digit: '{digit}', speech: '{speech_result}' for call {call_sid}")
    
    # Check if user said "yes" or "no" (speech input)
    if speech_result:
        # Normalize speech input
        speech_normalized = speech_result.lower().strip()
        if 'yes' in speech_normalized or 'yeah' in speech_normalized or 'yep' in speech_normalized:
            digit = "1"
        elif 'no' in speech_normalized or 'nope' in speech_normalized:
            digit = "2"
    
    if digit == "1":
        # Get the call state and extracted information
        call_state = call_state_manager.get_call_state(call_sid)
        if call_state:
            # Save reservation using the extracted information from call state
            success = save_reservation(call_state.extracted_info)
            
            if success:
                response_text = response_generator.generate_completion()
            else:
                response_text = "There was an error saving your reservation. Please try again."
        else:
            response_text = "Reservation information is not correct. Please start over."
        
        return tts_handler.create_hangup_response(response_text)
    elif digit == "2":
        # If not confirmed, ask for correction and gather more input
        response_text = response_generator.generate_correction()
        return tts_handler.create_gather_response(
            response_text,
            '/voice/gather',
            num_digits=0,  # Gather speech input, not digits
            speech_timeout='auto'
        )
    else:
        # If no valid input, ask for confirmation again
        call_state = call_state_manager.get_call_state(call_sid)
        if call_state and call_state.has_complete_info():
            # Generate confirmation message again
            info = call_state.extracted_info
            response_text = response_generator.generate_confirmation(
                info['name'],
                info['date'],
                info['time']
            )
            return tts_handler.create_gather_response(
                response_text,
                '/voice/confirm',
                num_digits=1
            )
        else:
            # Fallback to clarification
            response_text = response_generator.generate_clarification()
            return tts_handler.create_gather_response(
                response_text,
                '/voice/gather',
                num_digits=0,  # Gather speech input, not digits
                speech_timeout='auto'
            )

# 📞 Twilio call status endpoint
@app.route("/voice/status", methods=["POST"])
def call_status():
    """Handle call status updates from Twilio"""
    call_sid = request.values.get('CallSid')
    call_status = request.values.get('CallStatus', '')
    call_duration = request.values.get('CallDuration', '')

    logger.info(f"Call {call_sid} status: {call_status}, duration: {call_duration}")

    # Update call state with status
    call_state_manager.update_call_status(call_sid, call_status, call_duration)

    # Return empty response
    return '', 200

# 🎵 Serve audio files
@app.route("/audio/<filename>")
def serve_audio(filename):
    """Serve generated audio files"""
    try:
        return send_from_directory('audio_files', filename)
    except FileNotFoundError:
        return "Audio file not found", 404

# 📊 Early Disconnection Statistics
@app.route("/stats/early-disconnections")
def early_disconnection_stats():
    """Get statistics about early disconnections"""
    try:
        stats = call_state_manager.get_early_disconnection_stats()
        return jsonify({
            "status": "success",
            "data": stats
        })
    except Exception as e:
        logger.error(f"Error getting early disconnection stats: {e}")
        return jsonify({"error": "Failed to get statistics"}), 500

# 📊 Database Visualization Endpoint
@app.route("/database")
def database_view():
    """Display database contents in a web interface"""
    try:
        from database import ReservationDatabase
        db = ReservationDatabase()
        
        # Get all customers
        with sqlite3.connect("reservations.db") as conn:
            cursor = conn.cursor()
            
            # Get customers
            cursor.execute('''
                SELECT id, name, phone, email, created_at
                FROM customers
                ORDER BY created_at DESC
            ''')
            customers = cursor.fetchall()
            
            # Get reservations
            cursor.execute('''
                SELECT r.id, c.name, r.reservation_date, r.reservation_time,
                       r.party_size, r.special_requests, r.created_at
                FROM reservations r
                JOIN customers c ON r.customer_id = c.id
                ORDER BY r.reservation_date DESC, r.reservation_time DESC
            ''')
            reservations = cursor.fetchall()
            
            # Get today's reservations using the database method
            todays_reservations = db.get_todays_reservations()
        
        return render_template('database.html', 
                             customers=customers, 
                             reservations=reservations, 
                             todays_reservations=todays_reservations)
    except Exception as e:
        logger.error(f"Error displaying database: {e}")
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>❌ Database Error</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
                .error {{ color: red; }}
                .back-link {{ display: inline-block; margin: 20px 0; color: #d32f2f; text-decoration: none; }}
            </style>
        </head>
        <body>
            <h1>❌ Database Visualization Error</h1>
            <p class="error">Error: {str(e)}</p>
            <a href="/" class="back-link">← Back to Main Page</a>
        </body>
        </html>
        """, 500

# 🏠 메인 페이지
@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>📞 AI Reservation System</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
            .container { text-align: center; }
            .upload-box { border: 2px dashed #ccc; padding: 40px; margin: 20px 0; }
            button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .result { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; }
            .info-box { background: #e9f7fe; padding: 15px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🍖 Korean BBQ House London</h1>
            <p class="subtitle">Authentic Korean BBQ Restaurant in Central London</p>

            <div class="info-box">
                <h3>📞 Call Our ARS System</h3>
                <p>Call us at: <strong>+441135198981</strong></p>
                <p>Our AI assistant can help you with:</p>
                <ul>
                    <li>📅 Make reservations</li>
                    <li>🕐 Check operating hours (11 AM - 9 PM)</li>
                    <li>🍽️ Menu information & recommendations</li>
                    <li>🅿️ Parking & location details</li>
                    <li>🙋 General inquiries</li>
                </ul>
            </div>

            <div class="info-box">
                <h3>📊 Database Visualization</h3>
                <p>View all reservations and customer data:</p>
                <a href="/database" style="display: inline-block; background: #d32f2f; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 10px;">View Database</a>
            </div>

            <h3>📁 Test Audio File</h3>
            <p>Please upload a WAV audio file to test our system</p>
            <p>Examples:</p>
            <ul>
                <li>"I'd like to make a reservation for tonight"</li>
                <li>"What are your operating hours?"</li>
                <li>"Do you have halal options?"</li>
                <li>"Is there parking available?"</li>
            </ul>
            
            <form id="uploadForm" enctype="multipart/form-data">
                <div class="upload-box">
                    <input type="file" id="audioFile" name="audio" accept=".wav" required>
                </div>
                <button type="submit">Test Audio File</button>
            </form>
            
            <div id="result" class="result" style="display:none;"></div>
        </div>

        <script>
            document.getElementById('uploadForm').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const formData = new FormData();
                const fileInput = document.getElementById('audioFile');
                const resultDiv = document.getElementById('result');
                
                if (!fileInput.files[0]) {
                    alert('Please select a file!');
                    return;
                }
                
                formData.append('audio', fileInput.files[0]);
                
                resultDiv.innerHTML = '<p>Processing...</p>';
                resultDiv.style.display = 'block';
                
                fetch('/test-reservation', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        resultDiv.innerHTML = `
                            <h3>✅ Reservation Completed!</h3>
                            <p><strong>Transcribed text:</strong> ${data.transcribed_text}</p>
                            <p><strong>Name:</strong> ${data.reservation_info.name}</p>
                            <p><strong>Date:</strong> ${data.reservation_info.date}</p>
                            <p><strong>Time:</strong> ${data.reservation_info.time}</p>
                        `;
                    } else {
                        resultDiv.innerHTML = `<p style="color:red;">❌ Error: ${data.error}</p>`;
                    }
                })
                .catch(error => {
                    resultDiv.innerHTML = `<p style="color:red;">❌ Error: ${error}</p>`;
                });
            </script>
        </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True, port=5001)