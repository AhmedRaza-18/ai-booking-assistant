# 🤖 AI Medical Booking Assistant

An intelligent, AI-powered appointment booking system that handles patient calls and messages 24/7, automates scheduling, and integrates with Google Sheets for real-time tracking.

## ✨ Features

- **🤖 Natural Language AI** - Understands patient requests in conversational language
- **📞 Voice Calls** - Handles phone calls via Twilio integration
- **💬 Text Chat** - Supports text-based booking conversations
- **📊 Google Sheets Logging** - Real-time booking data logging
- **💾 Database Storage** - Persistent conversation history
- **📱 SMS Confirmations** - Automatic appointment confirmation messages
- **🚨 Emergency Detection** - Identifies urgent cases automatically
- **👥 Multi-channel Support** - Works via phone, web chat, and API
- **📈 Admin Dashboard** - View stats and manage conversations

## 🏗️ Architecture

```
Patient → Twilio (Voice/SMS) → FastAPI Backend → AI (Groq) → Google Sheets
                                       ↓
                                   Database
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Twilio account (for voice/SMS)
- Google Cloud account (for Sheets API)
- Groq API key (for AI)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/AhmedRaza-18/ai-booking-assistant.git
cd ai-booking-assistant
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the root directory:

```env
# AI Provider
AI_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
AI_MODEL=llama-3.3-70b-versatile

# Twilio
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Google Sheets
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEET_ID=your_google_sheet_id

# Database
DATABASE_URL=sqlite:///./data/bookings.db
```

5. **Set up Google Sheets**
- Create a Google Cloud project
- Enable Google Sheets API
- Create service account and download credentials
- Save as `google-credentials.json` in project root
- Share your Google Sheet with the service account email

6. **Run the application**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## 📖 API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

#### Chat API
- `POST /chat/message` - Send a message and get AI response
- `GET /chat/session/{session_id}` - Get conversation details
- `DELETE /chat/session/{session_id}` - Delete a session

#### Voice API
- `POST /voice/incoming` - Twilio webhook for incoming calls
- `POST /voice/process` - Process speech input
- `GET /voice/test` - Test voice service status

#### Admin API
- `GET /admin/stats` - Get system statistics
- `GET /admin/conversations/recent` - Get recent conversations
- `GET /admin/conversation/{session_id}` - Get specific conversation
- `GET /admin/bookings/date/{date}` - Get bookings for a date

## 🧪 Testing

### Run Tests
```bash
# Test the complete booking flow
python test_complete_system.py

# Test AI service
python test_ai_only.py

# Test data extraction
python test_debug_booking.py
```

### Manual Testing
```bash
# Test chat endpoint
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test123", "message": "Hi, I need an appointment"}'

# Test health check
curl http://localhost:8000/
```

## 🌐 Deployment

### Deploy to Render

1. **Create `render.yaml`** (already included)

2. **Push to GitHub**
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

3. **Deploy on Render**
- Go to [render.com](https://render.com)
- Create new Web Service
- Connect your GitHub repository
- Add environment variables
- Deploy!

4. **Update Twilio Webhook**
- Get your Render URL: `https://your-app.onrender.com`
- Update Twilio voice webhook: `https://your-app.onrender.com/voice/incoming`

## 📊 Google Sheets Structure

Your Google Sheet should have these columns:

| Timestamp | Caller Name | Phone Number | Symptoms | Preferred Date | Preferred Time | Doctor | Status | Session ID |
|-----------|-------------|--------------|----------|----------------|----------------|--------|--------|------------|

Data is automatically logged when bookings are completed.

## 🔧 Configuration

### AI Models

The system uses Groq's LLaMA model by default. You can switch providers:

```env
# Use Groq (recommended - fast and free)
AI_PROVIDER=groq
GROQ_API_KEY=your_key

# Or use OpenRouter
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key

# Or use OpenAI
AI_PROVIDER=openai
OPENAI_API_KEY=your_key
```

### Conversation States

The system uses a state machine with these states:
- GREETING → IDENTIFY_PATIENT → GET_SERVICE → CHECK_URGENCY
- COLLECT_NAME → COLLECT_PHONE → COLLECT_DOB → COLLECT_INSURANCE
- VERIFY_INFO → CHECK_AVAILABILITY → BOOK_APPOINTMENT
- CONFIRM_BOOKING → COMPLETED

## 🛠️ Project Structure

```
ai-booking-assistant/
├── app/
│   ├── config/
│   │   └── settings.py          # Configuration management
│   ├── models/
│   │   └── database.py          # SQLAlchemy models
│   ├── routes/
│   │   ├── chat.py              # Chat API endpoints
│   │   ├── voice.py             # Voice API endpoints
│   │   └── admin.py             # Admin API endpoints
│   ├── services/
│   │   ├── ai_service.py        # AI integration
│   │   ├── conversation_service.py  # State machine
│   │   ├── qualification.py     # Lead qualification
│   │   ├── voice_service.py     # Twilio voice
│   │   ├── sms_service.py       # SMS notifications
│   │   ├── sheets_service.py    # Google Sheets logging
│   │   └── database_service.py  # Database operations
│   └── main.py                  # FastAPI application
├── tests/
│   ├── test_complete_system.py
│   └── test_ai_only.py
├── .env                         # Environment variables
├── requirements.txt             # Python dependencies
├── render.yaml                  # Render deployment config
└── README.md                    # This file
```

## 💰 Pricing (for Client Demos)

### Suggested Pricing Model

**Setup Fee**: $500 - $1,500 (one-time)
- Custom installation and configuration
- Google Sheets setup
- Staff training
- Testing and go-live support

**Monthly Subscription**: $150 - $300/month
- Server hosting
- AI API costs
- Twilio calls and SMS
- Maintenance and updates
- Email/phone support

### Value Proposition
- Replaces $2,500/month receptionist
- Works 24/7 without breaks
- Never misses a call
- 95% cost savings

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

**Ahmed Raza**
- GitHub: [@AhmedRaza-18](https://github.com/AhmedRaza-18)

## 🙏 Acknowledgments

- Built with FastAPI
- AI powered by Groq
- Voice/SMS via Twilio
- Data logging via Google Sheets

## 📞 Support

For issues or questions:
- Create an issue on GitHub
- Contact: [Your Email]

## 🔐 Security Notes

- Never commit `.env` files
- Keep Google credentials secure
- Use environment variables for all secrets
- Regenerate API keys if exposed

## 📈 Future Enhancements

- [ ] Google Calendar integration
- [ ] Email notifications
- [ ] Web dashboard UI
- [ ] Multi-language support
- [ ] Payment integration
- [ ] Analytics dashboard
- [ ] Appointment reminders
- [ ] Cancel/reschedule via SMS

---

**Built with ❤️ for modern healthcare facilities**