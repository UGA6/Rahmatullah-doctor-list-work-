"""
ADMA Healthcare Chatbot - Main Application
============================================

FastAPI application for the ADMA Healthcare Chatbot
Provides REST API endpoints for:
- Sending messages and receiving chatbot responses
- Getting chat history
- Booking appointments
- Finding doctors, medicines, and laboratories
- Managing user preferences

Author: ADMA Development Team
Version: 1.0.0
"""

import uuid
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

# Import local modules
from chatbot.config import API_VERSION, API_TITLE, API_DESCRIPTION
from chatbot.database import Database, get_db, initialize_database
from chatbot.models import Conversation, Message, Doctor, Medicine, Laboratory, Appointment
from chatbot.chatbot_logic import create_chatbot_response


# ==================== FASTAPI APP SETUP ====================
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Pydantic Models (Request/Response) ====================

class MessageRequest(BaseModel):
    """Request model for sending a message to the chatbot"""
    user_id: str = Field(..., description="Unique user identifier")
    message: str = Field(..., description="User's message text")
    language: str = Field(default="en", description="User's preferred language (en, ur, ps)")
    conversation_id: Optional[str] = Field(default=None, description="Existing conversation ID if continuing")
    latitude: Optional[float] = Field(default=None, description="User's GPS latitude")
    longitude: Optional[float] = Field(default=None, description="User's GPS longitude")


class MessageResponse(BaseModel):
    """Response model for chatbot message"""
    bot_reply: str = Field(..., description="Chatbot's response")
    conversation_id: str = Field(..., description="Conversation identifier")
    detected_intent: str = Field(..., description="Detected user intent")
    extracted_symptoms: List[str] = Field(default=[], description="Extracted symptoms from message")
    extracted_duration: Optional[str] = Field(default=None, description="Duration of symptoms")
    language: str = Field(..., description="Response language")


class ChatHistoryResponse(BaseModel):
    """Response model for chat history"""
    conversation_id: str
    user_id: str
    language: str
    started_at: str
    messages: List[Dict[str, Any]]
    status: str


class AppointmentRequest(BaseModel):
    """Request model for booking an appointment"""
    conversation_id: str = Field(..., description="Conversation identifier")
    doctor_id: str = Field(..., description="Doctor's ID")
    patient_name: str = Field(..., description="Patient's name")
    patient_phone: str = Field(..., description="Patient's phone number")
    patient_age: Optional[int] = Field(default=None, description="Patient's age")
    patient_gender: Optional[str] = Field(default=None, description="Patient's gender")
    appointment_date: str = Field(..., description="Preferred date (YYYY-MM-DD)")
    appointment_time: str = Field(..., description="Preferred time (HH:MM)")
    symptoms_summary: Optional[str] = Field(default=None, description="Brief summary of symptoms")


class AppointmentResponse(BaseModel):
    """Response model for appointment booking"""
    appointment_id: str
    doctor_name: str
    doctor_specialization: str
    patient_name: str
    appointment_date: str
    appointment_time: str
    status: str
    message: str


class DoctorSearchRequest(BaseModel):
    """Request model for searching doctors"""
    specialization: Optional[str] = Field(default=None, description="Medical specialization")
    city: Optional[str] = Field(default=None, description="City or area")
    limit: int = Field(default=5, description="Maximum number of results")


class DoctorResponse(BaseModel):
    """Response model for doctor information"""
    doctor_id: str
    name: str
    specialization: str
    qualification: str
    city: str
    area: str
    phone: str
    hospital_clinic: str
    experience_years: int
    consultation_fee: int
    available_days: str
    available_hours: str
    languages: str
    rating: float


class MedicineSearchRequest(BaseModel):
    """Request model for searching medicines"""
    name: str = Field(..., description="Medicine name")


class LabSearchRequest(BaseModel):
    """Request model for searching laboratories"""
    city: Optional[str] = Field(default=None, description="City or area")
    test_type: Optional[str] = Field(default=None, description="Type of test")
    limit: int = Field(default=5, description="Maximum number of results")


class LanguageChangeRequest(BaseModel):
    """Request model for changing language"""
    user_id: str = Field(..., description="User identifier")
    language: str = Field(..., description="New language (en, ur, ps)")


# ==================== API Endpoints ====================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("\n" + "="*50)
    print("Starting ADMA Healthcare Chatbot")
    print("="*50)
    initialize_database()
    print("Database initialized successfully")
    print("API Documentation: http://localhost:8000/docs")
    print("="*50 + "\n")


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "ADMA Healthcare Chatbot API",
        "version": API_VERSION,
        "description": "AI-powered healthcare chatbot for patients",
        "endpoints": {
            "chat": "/api/chat/send - Send message to chatbot",
            "history": "/api/chat/history/{conversation_id} - Get chat history",
            "doctors": "/api/doctors/search - Search doctors",
            "medicines": "/api/medicines/search - Search medicines",
            "labs": "/api/labs/search - Search laboratories",
            "appointments": "/api/appointments/book - Book appointment",
        },
        "docs": "http://localhost:8000/docs",
        "ui": "http://localhost:8000/ui - User Interface"
    }


@app.get("/ui")
async def get_user_interface():
    """Serve the user-friendly web interface"""
    import os
    from pathlib import Path
    # Get the base directory (project root)
    base_dir = Path(__file__).parent.parent
    ui_file = base_dir / "templates" / "index.html"
    return FileResponse(str(ui_file))


@app.post("/api/chat/send", response_model=MessageResponse)
async def send_message(request: MessageRequest, db: Session = Depends(get_db)):
    """
    Send a message to the chatbot and get a response
    
    This endpoint:
    1. Receives user message
    2. Detects user intent (doctor, medicine, lab, etc.)
    3. Extracts symptoms and duration
    4. Maps symptoms to medical specialties
    5. Finds relevant doctors/labs if location provided
    6. Generates appropriate response
    
    Returns chatbot reply with extracted information
    """
    try:
        # Get or create conversation
        if request.conversation_id:
            # Get existing conversation
            conversation = db.query(Conversation).filter(
                Conversation.conversation_id == request.conversation_id
            ).first()
            
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            # Create new conversation
            conversation_id = f"CONV-{uuid.uuid4().hex[:10].upper()}"
            conversation = Conversation(
                conversation_id=conversation_id,
                user_id=request.user_id,
                language=request.language,
                location=None,
                latitude=request.latitude,
                longitude=request.longitude
            )
            db.add(conversation)
        
        # Save user message to database
        user_message = Message(
            conversation_id=conversation.conversation_id,
            role="user",
            message_text=request.message,
            timestamp=datetime.utcnow()
        )
        db.add(user_message)
        
        # Get conversation state from database (last message's extracted data)
        previous_messages = db.query(Message).filter(
            Message.conversation_id == conversation.conversation_id
        ).order_by(Message.timestamp.desc()).limit(5).all()
        
        # Build conversation state
        conversation_state = {
            "waiting_for_symptoms": False,
            "waiting_for_location": False,
            "waiting_for_duration": False,
            "extracted_symptoms": [],
            "extracted_duration": None,
            "location": conversation.location,
            "detected_intent": None,
            "specialization": None,
        }
        
        # Extract previous conversation state from messages
        for msg in previous_messages:
            if msg.extracted_symptoms:
                try:
                    conversation_state["extracted_symptoms"] = json.loads(msg.extracted_symptoms)
                except:
                    pass
            if msg.extracted_duration:
                conversation_state["extracted_duration"] = msg.extracted_duration
            if msg.detected_intent:
                conversation_state["detected_intent"] = msg.detected_intent
        
        # Update location in conversation state
        if request.latitude and request.longitude:
            conversation_state["location"] = f"{request.latitude},{request.longitude}"
        
        # Process message with chatbot logic
        result = create_chatbot_response(
            db_session=db,
            message=request.message,
            user_id=request.user_id,
            language=request.language,
            conversation_state=conversation_state
        )
        
        # Save bot response to database
        bot_message = Message(
            conversation_id=conversation.conversation_id,
            role="bot",
            message_text=result["bot_reply"],
            extracted_symptoms=json.dumps(result["extracted_symptoms"]),
            extracted_duration=result["extracted_duration"],
            detected_intent=result["detected_intent"],
            timestamp=datetime.utcnow()
        )
        db.add(bot_message)
        
        # Update conversation with extracted location if found
        if result.get("location") and not conversation.location:
            conversation.location = result["location"]
        
        # Commit changes
        db.commit()
        
        return MessageResponse(
            bot_reply=result["bot_reply"],
            conversation_id=conversation.conversation_id,
            detected_intent=result["detected_intent"],
            extracted_symptoms=result["extracted_symptoms"],
            extracted_duration=result["extracted_duration"],
            language=request.language
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@app.get("/api/chat/history/{conversation_id}", response_model=ChatHistoryResponse)
async def get_chat_history(conversation_id: str, db: Session = Depends(get_db)):
    """
    Get chat history for a conversation
    
    Returns all messages in a conversation with timestamps
    """
    try:
        conversation = db.query(Conversation).filter(
            Conversation.conversation_id == conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Get all messages
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.asc()).all()
        
        # Format messages
        message_list = []
        for msg in messages:
            message_dict = {
                "role": msg.role,
                "text": msg.message_text,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                "detected_intent": msg.detected_intent,
                "extracted_symptoms": msg.extracted_symptoms,
                "extracted_duration": msg.extracted_duration
            }
            message_list.append(message_dict)
        
        return ChatHistoryResponse(
            conversation_id=conversation.conversation_id,
            user_id=conversation.user_id,
            language=conversation.language,
            started_at=conversation.started_at.isoformat() if conversation.started_at else None,
            messages=message_list,
            status=conversation.status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving history: {str(e)}"
        )


@app.post("/api/doctors/search", response_model=List[DoctorResponse])
async def search_doctors(request: DoctorSearchRequest, db: Session = Depends(get_db)):
    """
    Search for doctors by specialization and/or location
    
    Returns list of doctors with their details
    """
    try:
        query = db.query(Doctor).filter(Doctor.is_available == True)
        
        if request.specialization:
            query = query.filter(Doctor.specialization.ilike(f"%{request.specialization}%"))
        
        if request.city:
            query = query.filter(
                (Doctor.city.ilike(f"%{request.city}%")) |
                (Doctor.area.ilike(f"%{request.city}%"))
            )
        
        doctors = query.order_by(Doctor.rating.desc()).limit(request.limit).all()
        
        return [
            DoctorResponse(
                doctor_id=doc.doctor_id,
                name=doc.name,
                specialization=doc.specialization,
                qualification=doc.qualification or "",
                city=doc.city,
                area=doc.area or "",
                phone=doc.phone or "",
                hospital_clinic=doc.hospital_clinic or "",
                experience_years=doc.experience_years or 0,
                consultation_fee=doc.consultation_fee or 0,
                available_days=doc.available_days or "",
                available_hours=doc.available_hours or "",
                languages=doc.languages or "",
                rating=doc.rating or 0.0
            )
            for doc in doctors
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching doctors: {str(e)}"
        )


@app.post("/api/medicines/search")
async def search_medicines(request: MedicineSearchRequest, db: Session = Depends(get_db)):
    """
    Search for medicines by name
    
    Returns medicine information including dosage, side effects, etc.
    """
    try:
        medicines = db.query(Medicine).filter(
            Medicine.name.ilike(f"%{request.name}%")
        ).limit(10).all()
        
        if not medicines:
            return {
                "message": "No medicines found",
                "medicines": []
            }
        
        return {
            "message": f"Found {len(medicines)} medicine(s)",
            "medicines": [
                {
                    "medicine_id": med.medicine_id,
                    "name": med.name,
                    "generic_name": med.generic_name,
                    "used_for": med.used_for,
                    "category": med.category,
                    "common_dose": med.common_dose,
                    "dose_timing": med.dose_timing,
                    "side_effects": med.side_effects,
                    "precautions": med.precautions,
                    "requires_prescription": med.requires_prescription,
                    "price_range": med.price_range
                }
                for med in medicines
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching medicines: {str(e)}"
        )


@app.post("/api/labs/search")
async def search_labs(request: LabSearchRequest, db: Session = Depends(get_db)):
    """
    Search for laboratories by location and/or test type
    
    Returns list of laboratories with their services
    """
    try:
        query = db.query(Laboratory)
        
        if request.city:
            query = query.filter(
                (Laboratory.city.ilike(f"%{request.city}%")) |
                (Laboratory.area.ilike(f"%{request.city}%"))
            )
        
        if request.test_type:
            query = query.filter(Laboratory.tests_available.ilike(f"%{request.test_type}%"))
        
        labs = query.order_by(Laboratory.rating.desc()).limit(request.limit).all()
        
        if not labs:
            return {
                "message": "No laboratories found",
                "labs": []
            }
        
        return {
            "message": f"Found {len(labs)} laboratory/labs",
            "labs": [
                {
                    "lab_id": lab.lab_id,
                    "name": lab.name,
                    "city": lab.city,
                    "area": lab.area,
                    "phone": lab.phone,
                    "address": lab.address,
                    "tests_available": lab.tests_available,
                    "home_sample": lab.home_sample,
                    "operating_hours": lab.operating_hours,
                    "certifications": lab.certifications,
                    "rating": lab.rating
                }
                for lab in labs
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching labs: {str(e)}"
        )


@app.post("/api/appointments/book", response_model=AppointmentResponse)
async def book_appointment(request: AppointmentRequest, db: Session = Depends(get_db)):
    """
    Book an appointment with a doctor
    
    Creates an appointment booking and returns confirmation
    """
    try:
        # Verify conversation exists
        conversation = db.query(Conversation).filter(
            Conversation.conversation_id == request.conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Verify doctor exists
        doctor = db.query(Doctor).filter(
            Doctor.doctor_id == request.doctor_id
        ).first()
        
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found"
            )
        
        # Create appointment
        appointment_id = f"APT-{uuid.uuid4().hex[:10].upper()}"
        appointment = Appointment(
            appointment_id=appointment_id,
            conversation_id=request.conversation_id,
            doctor_id=request.doctor_id,
            patient_name=request.patient_name,
            patient_phone=request.patient_phone,
            patient_age=request.patient_age,
            patient_gender=request.patient_gender,
            appointment_date=request.appointment_date,
            appointment_time=request.appointment_time,
            symptoms_summary=request.symptoms_summary,
            status="pending"
        )
        
        db.add(appointment)
        db.commit()
        
        return AppointmentResponse(
            appointment_id=appointment_id,
            doctor_name=doctor.name,
            doctor_specialization=doctor.specialization,
            patient_name=request.patient_name,
            appointment_date=request.appointment_date,
            appointment_time=request.appointment_time,
            status="pending",
            message=f"Appointment booked successfully with Dr. {doctor.name}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error booking appointment: {str(e)}"
        )


@app.get("/api/appointments/{user_id}")
async def get_user_appointments(user_id: str, db: Session = Depends(get_db)):
    """
    Get all appointments for a user
    """
    try:
        # Get user's conversations
        conversations = db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).all()
        
        conversation_ids = [c.conversation_id for c in conversations]
        
        # Get appointments
        appointments = db.query(Appointment).filter(
            Appointment.conversation_id.in_(conversation_ids)
        ).order_by(Appointment.created_at.desc()).all()
        
        # Get doctor details for each appointment
        result = []
        for apt in appointments:
            doctor = db.query(Doctor).filter(Doctor.doctor_id == apt.doctor_id).first()
            result.append({
                "appointment_id": apt.appointment_id,
                "doctor_name": doctor.name if doctor else "Unknown",
                "doctor_specialization": doctor.specialization if doctor else "Unknown",
                "patient_name": apt.patient_name,
                "appointment_date": apt.appointment_date,
                "appointment_time": apt.appointment_time,
                "status": apt.status,
                "created_at": apt.created_at.isoformat() if apt.created_at else None
            })
        
        return {
            "message": f"Found {len(result)} appointment(s)",
            "appointments": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving appointments: {str(e)}"
        )


@app.post("/api/language/change")
async def change_language(request: LanguageChangeRequest, db: Session = Depends(get_db)):
    """
    Change user's preferred language
    """
    valid_languages = ["en", "ur", "ps"]
    
    if request.language not in valid_languages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid language. Must be one of: {valid_languages}"
        )
    
    # Find user's active conversation
    conversation = db.query(Conversation).filter(
        Conversation.user_id == request.user_id,
        Conversation.status == "active"
    ).first()
    
    if conversation:
        conversation.language = request.language
        db.commit()
    
    language_names = {
        "en": "English",
        "ur": "اردو (Urdu)",
        "ps": "پښتو (Pashto)"
    }
    
    return {
        "message": "Language changed successfully",
        "new_language": request.language,
        "language_name": language_names.get(request.language, request.language)
    }


@app.get("/api/specializations")
async def get_specializations(db: Session = Depends(get_db)):
    """
    Get list of all available medical specializations
    """
    try:
        specializations = db.query(Doctor.specialization).distinct().all()
        return {
            "specializations": [s[0] for s in specializations if s[0]]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving specializations: {str(e)}"
        )


# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ADMA Healthcare Chatbot",
        "version": API_VERSION
    }


# ==================== Run Instructions ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
