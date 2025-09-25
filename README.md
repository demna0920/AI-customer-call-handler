# 🍖 Korean BBQ House London Reservation System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Twilio](https://img.shields.io/badge/Twilio-API-red.svg)](https://www.twilio.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An AI-powered voice reservation system for Korean BBQ House London that handles customer calls, extracts reservation information using Google Gemini AI, and stores it in a SQLite database. Built with Flask, Twilio, and Whisper for real-time voice processing.

## ✨ Features

- 🎤 **Real-time Voice Processing**: Uses OpenAI Whisper for speech-to-text transcription
- 🤖 **AI-Powered Information Extraction**: Leverages Google Gemini AI to extract reservation details
- 📞 **Twilio Integration**: Handles incoming calls and voice responses
- 🎵 **Text-to-Speech**: ElevenLabs integration for natural voice responses
- 💾 **SQLite Database**: Stores customer and reservation data
- 🌐 **Web Dashboard**: Built-in database visualization interface
- 🔄 **Fallback Processing**: Works without Google API keys using rule-based extraction

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Git

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/korean-bbq-reservation-system.git
   cd korean-bbq-reservation-system
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

The application will start on `http://localhost:5001`

## 🔧 Configuration

### Required API Keys

- **Google Gemini API**: For AI-powered information extraction
- **Twilio**: For phone call handling
- **ElevenLabs**: For text-to-speech voice responses

Copy `.env.example` to `.env` and fill in your credentials:

```env
GOOGLE_API_KEY=your_google_api_key_here
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=your_twilio_phone_number_here
ELEVEN_API_KEY=your_elevenlabs_api_key_here
AUDIO_BASE_URL=your_audio_base_url_here
```

## Database Structure

The system uses SQLite to store customer and reservation information in two tables:

### Customers Table
- `id`: Unique customer identifier
- `name`: Customer's name
- `phone`: Customer's phone number (optional)
- `email`: Customer's email address (optional)
- `created_at`: Timestamp when the customer record was created

### Reservations Table
- `id`: Unique reservation identifier
- `customer_id`: Foreign key referencing the customer
- `reservation_date`: Date of the reservation (YYYY-MM-DD)
- `reservation_time`: Time of the reservation (HH:MM)
- `party_size`: Number of people in the party (default: 2)
- `special_requests`: Any special requests from the customer
- `created_at`: Timestamp when the reservation was created

## Viewing Database Contents

### Web-based Visualization (Recommended)

To view the database contents through a web interface:

1. Make sure you're in the project directory:
   ```bash
   cd /path/to/reservation-system
   ```

2. Activate the virtual environment:
   ```bash
   source reservation_env/bin/activate
   ```

3. Run the database visualization app:
   ```bash
   python database_visualization_app.py
   ```

4. Open your web browser and navigate to:
   ```
   http://localhost:5001/database
   ```

This will display a comprehensive visualization of:
- Total customers and reservations statistics
- All customers in the database
- Today's reservations
- All reservations in the database

### Command-line Script

To view the contents of the database using the command-line script:

```bash
python view_database.py
```

This script will display:
1. All customers in the database
2. All reservations in the database
3. Today's reservations

For detailed instructions on using the database visualization feature, see [DATABASE_VISUALIZATION.md](DATABASE_VISUALIZATION.md).

## Reservation Flow

The system uses a step-by-step conversation flow to collect reservation information:
1. Customer name
2. Reservation date
3. Reservation time

The system is designed to prevent asking for the same information twice within a single call. If a customer mentions making a reservation multiple times during the same call, the system will remember previously provided information.

## Common Issues and Solutions

### Why is the customer's name asked twice?

This can happen when a customer says something like "Can I make a reservation?" followed by "Uh, can I make a reservation tomorrow?" The system interprets the second statement as a new reservation request.

The fix implemented in `app.py` checks if the customer's name has already been collected during the current call and skips asking for it again.

## 📖 Usage

### Web Interface

1. Start the application: `python app.py`
2. Open your browser to `http://localhost:5001`
3. Upload a WAV audio file to test reservation processing
4. View the database at `http://localhost:5001/database`

### Phone Integration

Configure Twilio to forward calls to your application endpoint. The system will:
- Answer incoming calls
- Process voice input in real-time
- Extract reservation information
- Store data in the database
- Provide voice confirmations

### Database Management

- **Web Dashboard**: Visit `/database` for a visual interface
- **Command Line**: Run `python view_database.py` for terminal output

## 🧪 Testing

### Audio File Testing

1. Prepare a WAV audio file with a reservation request (e.g., "I'd like to make a reservation for tomorrow at 7 PM")
2. Upload it through the web interface at `http://localhost:5001`
3. Check the transcription and extracted information

### Voice Call Testing

1. Configure Twilio with your application URL
2. Call the Twilio number
3. Test the conversation flow:
   - Greeting response
   - Reservation request processing
   - Information collection (name, date, time)
   - Confirmation

### Example Test Phrases

- "Hi, I'd like to make a reservation for tonight"
- "Can I book a table for tomorrow at 8 PM for 4 people?"
- "My name is John Smith, I'd like to reserve for Friday evening"

## 📦 Dependencies

### Core Dependencies

- **Python 3.8+**
- **Flask** - Web framework
- **Twilio** - Voice communication
- **OpenAI Whisper** - Speech recognition
- **Google Generative AI** - Information extraction
- **ElevenLabs** - Text-to-speech
- **SQLite3** - Database storage

### Additional Libraries

- **pydub** - Audio processing
- **python-dotenv** - Environment management
- **torch & torchaudio** - ML model support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for Whisper speech recognition
- Google for Gemini AI
- Twilio for communication APIs
- ElevenLabs for text-to-speech

## Running the Application

```bash
python app.py
```

The application will start on port 5001.