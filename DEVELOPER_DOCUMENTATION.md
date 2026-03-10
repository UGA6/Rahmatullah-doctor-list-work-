# ADMA Healthcare Chatbot - Developer Documentation

## Project Overview

This is an AI-powered healthcare chatbot system built with Python, FastAPI, and SQLite. It allows patients to describe symptoms, find doctors, get medicine information, and book appointments.

---

## Architecture Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CLIENT (Browser/Mobile)                            │
│                                                                            │
│   ┌─────────────────┐           ┌──────────────────────────┐              │
│   │  User Interface │           │   API Documentation      │              │
│   │  (index.html)   │           │   (Swagger UI)          │              │
│   └────────┬────────┘           └────────────┬─────────────┘              │
│            │                                 │                              │
│            └──────────────┬──────────────────┘                              │
│                           │                                                 │
│                           ▼                                                 │
│                    ┌─────────────┐                                          │
│                    │  FastAPI    │                                          │
│                    │  Server     │                                          │
│                    └──────┬──────┘                                          │
└───────────────────────────┼────────────────────────────────────────────────┘
                            │
            ┌───────────────┼────────────────┐
            │               │                │
            ▼               ▼                ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │  Chatbot    │ │  Database   │ │  i18n       │
    │  Logic      │ │  (SQLite)   │ │  Module     │
    └──────┬──────┘ └──────┬──────┘ └─────────────┘
           │
           └───────────────┬────────────────────┐
                           ▼                    ▼
                    ┌─────────────┐      ┌─────────────┐
                    │  Doctors    │      │  Medicines  │
                    │  Labs       │      │  Appointmnts│
                    └─────────────┘      └─────────────┘
```

---

## File Structure & Purpose

### 1. `chatbot/config.py` - Configuration
```python
# Key settings:
DATABASE_URL = "sqlite:///./adma_healthcare.db"  # Database connection
API_VERSION = "1.0.0"                            # API version
DEFAULT_LANGUAGE = "en"                          # Default language
```
- Stores all configuration variables
- Easy to change database URL for production

### 2. `chatbot/models.py` - Database Schema
Defines 7 SQLAlchemy models:

```python
# 1. Conversation - Chat session
class Conversation(Base):
    conversation_id: str      # Unique ID (e.g., "CONV-ABC123")
    user_id: str            # User identifier
    language: str           # en, ur, ps
    location: str           # City/area
    latitude, longitude     # GPS coordinates (optional)

# 2. Message - Individual chat messages
class Message(Base):
    conversation_id: FK      # Link to conversation
    role: str              # "user" or "bot"
    message_text: str      # Message content
    extracted_symptoms: str # JSON of symptoms
    extracted_duration: str # e.g., "2 days"
    detected_intent: str   # doctor, medicine, lab

# 3. Doctor - Doctor information
# 4. Medicine - Medicine database
# 5. Laboratory - Lab information
# 6. Appointment - Booking records
# 7. SymptomMapping - Symptom to specialty mapping
```

### 3. `chatbot/database.py` - Database Operations

**Functions:**
- `Database()` - Creates database engine and session
- `create_tables()` - Creates all tables
- `initialize_database()` - Adds sample data

**Sample Data Added:**
- 12 doctors with different specializations
- 20 medicines with full details
- 6 laboratories
- 15 symptom-to-specialty mappings

### 4. `chatbot/chatbot_logic.py` - Core AI Logic

This is the brain of the chatbot. Key functions:

#### a) Intent Detection
```python
def detect_intent(message: str) -> str:
    # Detects what user wants:
    # - "doctor" - Finding a doctor
    # - "medicine" - Medicine information
    # - "lab" - Laboratory tests
    # - "greeting" - Hello/hi
    # - "emergency" - Urgent help
    # - "language" - Change language
```

#### b) Symptom Extraction
```python
def extract_symptoms(message: str) -> List[str]:
    # Extracts symptoms from message:
    # "I have fever and headache" 
    # → ["fever", "headache"]
    #
    # Supports: fever, cough, headache, stomach pain,
    # chest pain, skin rash, etc.
```

#### c) Duration Parsing
```python
def extract_duration(message: str) -> Optional[str]:
    # Extracts how long symptoms last:
    # "for 3 days" → "3 days"
    # "since last week" → "last week"
```

#### d) Specialty Mapping
```python
def map_symptoms_to_specialization(symptoms: List) -> str:
    # Maps symptoms to medical specialty:
    # fever → "General Physician"
    # headache → "Neurologist"
    # chest pain → "Cardiologist"
    # cough → "Pulmonologist"
```

#### e) Database Queries
```python
def find_doctors(specialization, location, limit) -> List[Doctor]
def find_medicine(medicine_name) -> Optional[Medicine]
def find_labs(location, test_type, limit) -> List[Laboratory]
```

### 5. `chatbot/i18n.py` - Multilingual Support

Translates all responses to:
- English (en)
- Urdu (ur) - اردو
- Pashto (ps) - پښتو

```python
# Example translations:
"greeting": {
    "en": "Hi! I'm your ADMA healthcare assistant.",
    "ur": "السلام علیکم! میں آپ کا ADMA صحت معاون ہوں۔",
    "ps": "سلام! زه ستاسو د ADMA روغني مرستیال یم."
}
```

### 6. `chatbot/main.py` - FastAPI Endpoints

**API Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/ui` | GET | User-friendly web interface |
| `/api/chat/send` | POST | Send message, get response |
| `/api/chat/history/{id}` | GET | Get chat history |
| `/api/doctors/search` | POST | Search doctors |
| `/api/medicines/search` | POST | Search medicines |
| `/api/labs/search` | POST | Search laboratories |
| `/api/appointments/book` | POST | Book appointment |
| `/api/language/change` | POST | Change language |

### 7. `templates/index.html` - User Interface

A modern, responsive web interface featuring:
- Chat interface with message bubbles
- Language selector (EN/UR/PS)
- Quick action buttons
- Typing indicators
- Mobile-responsive design

---

## Data Flow Example

### Example: Finding a Doctor

```
User: "I have fever and headache"
         │
         ▼
   API: POST /api/chat/send
         │
         ▼
   Chatbot Logic:
   1. detect_intent() → "doctor"
   2. extract_symptoms() → ["fever", "headache"]
   3. map_symptoms_to_specialization() → "General Physician"
         │
         ▼
   Database: find_doctors("General Physician", location)
         │
         ▼
   Response: List of doctors with details
         │
         ▼
   UI: Display doctor cards
```

---

## API Request/Response Example

### Send Message
```bash
curl -X POST http://localhost:8000/api/chat/send \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "I have fever",
    "language": "en"
  }'
```

**Response:**
```json
{
  "bot_reply": "I understand you have fever. What is your location?",
  "conversation_id": "CONV-ABC123",
  "detected_intent": "doctor",
  "extracted_symptoms": ["fever"],
  "extracted_duration": null,
  "language": "en"
}
```

---

## Running the Project

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Server
```bash
python -m chatbot.main
```

### 3. Access Interfaces
- **Patient UI**: http://localhost:8000/ui
- **API Docs**: http://localhost:8000/docs
- **API Root**: http://localhost:8000/

---

## Database Schema Diagram

```
┌──────────────────┐       ┌──────────────────┐
│  conversations   │       │     messages     │
├──────────────────┤       ├──────────────────┤
│ id (PK)          │◄──────│ conversation_id │
│ conversation_id  │  1:N  │ (FK)            │
│ user_id          │       │ id (PK)         │
│ language         │       │ role            │
│ location         │       │ message_text    │
│ latitude         │       │ extracted_...   │
│ longitude        │       │ detected_intent │
│ started_at       │       │ timestamp      │
└──────────────────┘       └──────────────────┘

┌──────────────────┐
│    doctors      │
├──────────────────┤
│ doctor_id (PK)  │
│ name            │
│ specialization  │
│ qualification   │
│ city           │
│ area           │
│ phone          │
│ fee            │
│ rating         │
└──────────────────┘
```

---

## Future Enhancements

1. **AI Integration**: Connect to OpenAI for smarter responses
2. **Voice Input**: Add speech-to-text
3. **Video Consultation**: WebRTC integration
4. **Payment Gateway**: For appointment fees
5. **Push Notifications**: For appointment reminders
6. **Analytics Dashboard**: For admin panel
7. **Multi-tenancy**: For multiple hospitals

---

## Configuration for Production

1. Change database to PostgreSQL:
```python
# .env file
DATABASE_URL=postgresql://user:pass@localhost/adma_healthcare
```

2. Set CORS origins:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    # ...
)
```

3. Use environment variables for secrets:
```python
import os
SECRET_KEY = os.getenv("SECRET_KEY")
```

---

## Contact & Support

For questions or issues, please refer to the README.md or contact the development team.
