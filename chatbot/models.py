"""
Database Models for ADMA Healthcare Chatbot
This file defines all database tables using SQLAlchemy ORM

Tables:
1. Conversations - Stores chat sessions
2. Messages - Stores individual messages in conversations
3. Doctors - Stores doctor information
4. Medicines - Stores medicine information
5. Laboratories - Stores lab information
6. Appointments - Stores booking information
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship, declarative_base

# Create base class for all models
Base = declarative_base()


class Conversation(Base):
    """
    Represents a chat session between a patient and the chatbot
    """
    __tablename__ = "conversations"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Unique conversation identifier
    conversation_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # User identification
    user_id = Column(String(50), nullable=False, index=True)
    
    # User's preferred language (en, ur, ps)
    language = Column(String(10), default="en")
    
    # User's location (city/area)
    location = Column(String(100), nullable=True)
    
    # GPS coordinates (optional)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Conversation metadata
    started_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(20), default="active")  # active, completed
    
    # Relationship to messages
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    # Relationship to appointments
    appointments = relationship("Appointment", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation {self.conversation_id} - User: {self.user_id}>"


class Message(Base):
    """
    Represents a single message in a conversation
    Can be from user or chatbot
    """
    __tablename__ = "messages"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to conversation
    conversation_id = Column(String(50), ForeignKey("conversations.conversation_id"), nullable=False)
    
    # Message content
    role = Column(String(10), nullable=False)  # 'user' or 'bot'
    message_text = Column(Text, nullable=False)
    
    # Extracted data from user messages (for AI processing)
    extracted_symptoms = Column(Text, nullable=True)  # JSON string of symptoms
    extracted_duration = Column(String(50), nullable=True)  # e.g., "2 days", "1 week"
    detected_intent = Column(String(50), nullable=True)  # doctor, medicine, lab, general
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship to conversation
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message {self.role}: {self.message_text[:30]}...>"


class Doctor(Base):
    """
    Stores information about doctors/specialists
    """
    __tablename__ = "doctors"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Doctor information
    doctor_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    specialization = Column(String(100), nullable=False)
    qualification = Column(String(200), nullable=True)
    
    # Contact information
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    
    # Location
    city = Column(String(50), nullable=False, index=True)
    area = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Practice details
    hospital_clinic = Column(String(200), nullable=True)
    experience_years = Column(Integer, nullable=True)
    consultation_fee = Column(Integer, nullable=True)
    
    # Availability
    is_available = Column(Boolean, default=True)
    available_days = Column(String(50), nullable=True)  # e.g., "Mon-Sat"
    available_hours = Column(String(50), nullable=True)  # e.g., "9AM-5PM"
    
    # Languages spoken
    languages = Column(String(100), nullable=True)  # e.g., "English,Urdu,Pashto"
    
    # Rating (out of 5)
    rating = Column(Float, default=4.0)
    
    # Relationship to appointments
    appointments = relationship("Appointment", back_populates="doctor")
    
    def __repr__(self):
        return f"<Doctor: {self.name} - {self.specialization}>"


class Medicine(Base):
    """
    Stores information about medicines/drugs
    """
    __tablename__ = "medicines"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Medicine information
    medicine_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    
    # Medical details
    generic_name = Column(String(100), nullable=True)
    used_for = Column(Text, nullable=False)  # Conditions this medicine treats
    category = Column(String(50), nullable=True)  # e.g., "Pain Relief", "Antibiotic"
    
    # Dosage information
    common_dose = Column(String(200), nullable=True)
    dose_timing = Column(String(100), nullable=True)  # e.g., "After meal"
    
    # Safety information
    side_effects = Column(Text, nullable=True)
    precautions = Column(Text, nullable=True)
    interactions = Column(Text, nullable=True)
    
    # Availability
    requires_prescription = Column(Boolean, default=False)
    
    # Price range (optional)
    price_range = Column(String(50), nullable=True)
    
    def __repr__(self):
        return f"<Medicine: {self.name}>"


class Laboratory(Base):
    """
    Stores information about diagnostic laboratories
    """
    __tablename__ = "laboratories"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Lab information
    lab_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    
    # Contact information
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    
    # Location
    city = Column(String(50), nullable=False, index=True)
    area = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Services
    tests_available = Column(Text, nullable=True)  # List of tests offered
    home_sample = Column(Boolean, default=False)  # Home sample collection
    
    # Operating hours
    operating_hours = Column(String(100), nullable=True)
    
    # Accreditation/certifications
    certifications = Column(String(200), nullable=True)
    
    # Rating
    rating = Column(Float, default=4.0)
    
    def __repr__(self):
        return f"<Laboratory: {self.name}>"


class Appointment(Base):
    """
    Stores appointment booking information
    """
    __tablename__ = "appointments"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Unique appointment ID
    appointment_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Foreign keys
    conversation_id = Column(String(50), ForeignKey("conversations.conversation_id"), nullable=False)
    doctor_id = Column(String(50), ForeignKey("doctors.doctor_id"), nullable=False)
    
    # Appointment details
    patient_name = Column(String(100), nullable=True)
    patient_phone = Column(String(20), nullable=True)
    patient_age = Column(Integer, nullable=True)
    patient_gender = Column(String(10), nullable=True)
    
    # Appointment scheduling
    appointment_date = Column(String(20), nullable=True)  # e.g., "2024-01-20"
    appointment_time = Column(String(20), nullable=True)  # e.g., "10:00 AM"
    
    # Status
    status = Column(String(20), default="pending")  # pending, confirmed, cancelled, completed
    
    # Notes
    symptoms_summary = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    
    def __repr__(self):
        return f"<Appointment: {self.appointment_id} - Doctor: {self.doctor_id}>"


class SymptomMapping(Base):
    """
    Maps symptoms to medical specialties (for AI logic)
    """
    __tablename__ = "symptom_mappings"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Symptom keywords (comma-separated)
    symptom_keywords = Column(String(200), nullable=False, index=True)
    
    # Related medical specialty
    specialization = Column(String(100), nullable=False)
    
    # Severity level (1-3)
    severity = Column(Integer, default=1)
    
    # Additional notes
    description = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<SymptomMapping: {self.symptom_keywords} -> {self.specialization}>"
