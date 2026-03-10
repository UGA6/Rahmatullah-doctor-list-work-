# ADMA Healthcare Chatbot

An AI-powered healthcare chatbot for patients to describe symptoms, find doctors, get medicine information, and book appointments.

## Features

### Core Features
- **Symptom Description**: Patients can describe symptoms in their own words
- **Symptom Extraction**: Automatically extracts key symptoms and duration from patient input
- **Specialty Mapping**: Maps symptoms to relevant medical specialties automatically
- **Location Services**: Uses patient's location or GPS to find nearby doctors
- **Doctor Listings**: Provides list of specialist doctors with contact and booking options
- **Appointment Booking**: Patients can book appointments directly through the chatbot
- **Directions**: Get directions to doctor locations

### Multilingual Support
- English (en)
- Urdu (اردو)
- Pashto (پښتو)

### Future Upgrades
- AI-powered summaries of doctor-patient consultations
- Auto-generated visit notes with key complaints and diagnoses
- Voice input for medication prescriptions
- Lab report scanning and automatic upload
- Integration with lab machines for real-time test results
- Alerts for abnormal lab values
- Clinical decision support based on symptoms, history, and labs
- Medication reminders
- Insurance query support

## Project Structure

```
AiChatbot/
├── chatbot/
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection and initialization
│   ├── models.py            # SQLAlchemy database models
│   ├── chatbot_logic.py     # Core chatbot logic
│   ├── i18n.py              # Internationalization
│   └── main.py              # FastAPI application
├── requirements.txt         # Python dependencies
├── README.md                # This file
└── ADMA_Healthcare.db      # SQLite database (auto-created)
```

## Installation

1. **Install Python Dependencies**

```bash
pip install -r requirements.txt
```

2. **Run the Application**

```bash
cd AiChatbot
python -m chatbot.main
```

Or using uvicorn directly:

```bash
uvicorn chatbot.main:app --reload
```

3. **Access the API**

- API Documentation: http://localhost:8000/docs
- ReDoc Documentation: http://localhost:8000/redoc

## API Endpoints

### 1. Send Message to Chatbot
```
POST /api/chat/send
```

**Request:**
```json
{
  "user_id": "user123",
  "message": "I have fever and headache",
  "language": "en",
  "conversation_id": null
}
```

**Response:**
```json
{
  "bot_reply": "I understand you have fever and headache. What is your location?",
  "conversation_id": "CONV-ABC123",
  "detected_intent": "doctor",
  "extracted_symptoms": ["fever", "headache"],
  "extracted_duration": null,
  "language": "en"
}
```

### 2. Get Chat History
```
GET /api/chat/history/{conversation_id}
```

**Response:**
```json
{
  "conversation_id": "CONV-ABC123",
  "user_id": "user123",
  "language": "en",
  "started_at": "2024-01-15T10:30:00",
  "messages": [
    {
      "role": "user",
      "text": "I have fever and headache",
      "timestamp": "2024-01-15T10:30:00"
    }
  ],
  "status": "active"
}
```

### 3. Search Doctors
```
POST /api/doctors/search
```

**Request:**
```json
{
  "specialization": "Cardiologist",
  "city": "Karachi",
  "limit": 5
}
```

### 4. Search Medicines
```
POST /api/medicines/search
```

**Request:**
```json
{
  "name": "Paracetamol"
}
```

### 5. Search Laboratories
```
POST /api/labs/search
```

**Request:**
```json
{
  "city": "Karachi",
  "test_type": "blood",
  "limit": 5
}
```

### 6. Book Appointment
```
POST /api/appointments/book
```

**Request:**
```json
{
  "conversation_id": "CONV-ABC123",
  "doctor_id": "DR001",
  "patient_name": "John Doe",
  "patient_phone": "+92-300-1234567",
  "patient_age": 30,
  "patient_gender": "male",
  "appointment_date": "2024-01-20",
  "appointment_time": "10:00",
  "symptoms_summary": "Fever and headache for 2 days"
}
```

### 7. Change Language
```
POST /api/language/change
```

**Request:**
```json
{
  "user_id": "user123",
  "language": "ur"
}
```

## Conversation Flow Examples

### Example 1: Finding a Doctor
```
User: I need a doctor
Bot: What symptoms are you experiencing? Please describe in your own words.

User: I have fever and headache
Bot: How long have you had these symptoms? (e.g., 2 days, 1 week)

User: 2 days
Bot: What is your location or city?

User: Karachi
Bot: Let me find doctors for your symptoms near Karachi...
[Lists doctors with details]
```

### Example 2: Medicine Information
```
User: What medicine for fever?
Bot: For fever, common medicines include Paracetamol or Ibuprofen.
    However, please consult a doctor before taking any medicine.
    ⚠️ Please note: This is only informational. Always consult a doctor.
```

### Example 3: Laboratory Tests
```
User: I need a blood test
Bot: What is your location or city?

User: Lahore
Bot: Here are laboratories in Lahore for blood tests...
[Lists laboratories with details]
```

## Database

The application uses SQLite by default with the following tables:

- **conversations**: Stores chat sessions
- **messages**: Stores individual messages
- **doctors**: Doctor information (12 sample doctors)
- **medicines**: Medicine database (20 sample medicines)
- **laboratories**: Lab information (6 sample labs)
- **appointments**: Booking records
- **symptom_mappings**: Maps symptoms to specialties

## Supported Symptoms

The chatbot can detect and extract the following symptoms:
- Fever, Headache, Cough, Cold
- Body pain, Stomach pain
- Chest pain, Breathing difficulty
- Skin rash, Eye problems, Ear problems
- Throat problems, Dizziness, Fatigue
- Nausea, Vomiting, Diarrhea
- Back pain, Toothache
- Pregnancy-related issues
- Mental health (depression, anxiety)
- Chronic conditions (diabetes, blood pressure)

## Configuration

Edit `chatbot/config.py` to change:
- Database URL
- API settings
- Default language
- Session timeout

## Running in Production

For production deployment:

1. Use a production database (PostgreSQL recommended)
2. Set environment variables
3. Configure CORS properly
4. Use a WSGI server (Gunicorn)
5. Set up HTTPS/SSL

Example with Gunicorn:
```bash
gunicorn chatbot.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## License

This project is developed for ADMA Healthcare System.

## Support

For questions or issues, please contact the development team.
