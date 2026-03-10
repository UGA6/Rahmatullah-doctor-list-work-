"""
Chatbot Logic Module for ADMA Healthcare Chatbot

This module contains:
1. Intent detection - Understanding what the user wants
2. Symptom extraction - Extracting symptoms from user input
3. Duration parsing - Extracting how long symptoms have been present
4. Specialty mapping - Mapping symptoms to medical specialties
5. Response generation - Generating appropriate chatbot responses
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.orm import Session

# Import models and i18n
from chatbot.models import Doctor, Medicine, Laboratory
from chatbot.i18n import get_translator

# Import OpenAI service
from chatbot.openai_service import OpenAIService, get_openai_service
from chatbot.config import USE_OPENAI


class ChatbotLogic:
    """
    Main chatbot logic class that handles all AI/ML operations
    Uses keyword matching and rule-based logic for simplicity
    """
    
    def __init__(self, db_session: Session, language: str = "en"):
        """
        Initialize chatbot logic
        
        Args:
            db_session: SQLAlchemy database session
            language: User's preferred language (en, ur, ps)
        """
        self.db = db_session
        self.language = language
        self.translator = get_translator(language)
        
        # Initialize OpenAI service
        self.openai_service: OpenAIService = get_openai_service(db_session)
        
        # Conversation state tracking
        self.conversation_state = {
            "waiting_for_symptoms": False,
            "waiting_for_location": False,
            "waiting_for_duration": False,
            "waiting_for_appointment_details": False,
            "waiting_for_medicine_name": False,
            "waiting_for_lab_test": False,
            "detected_intent": None,
            "extracted_symptoms": [],
            "extracted_duration": None,
            "location": None,
            "specialization": None,
        }
    
    def set_language(self, language: str):
        """
        Change the chatbot language
        
        Args:
            language: New language code
        """
        self.language = language
        self.translator = get_translator(language)
    
    def detect_intent(self, message: str) -> str:
        """
        Detect what the user wants based on their message
        
        Args:
            message: User's input message
            
        Returns:
            Intent type: 'doctor', 'medicine', 'lab', 'greeting', 'language', 'general', 'emergency', 'appointment'
        """
        # Try OpenAI first if available
        if self.openai_service.is_enabled():
            try:
                result = self.openai_service.detect_intent(message, self.language)
                if result.get("success"):
                    # Update conversation state with detected intent
                    self.conversation_state["detected_intent"] = result.get("intent")
                    return result.get("intent", "general")
            except Exception as e:
                # Fall back to keyword matching
                pass
        
        # Fallback to keyword matching
        message_lower = message.lower()
        
        # Emergency detection
        emergency_keywords = [
            "emergency", "urgent", "critical", "dying", "heart attack", 
            "bleeding", "accident", "overdose", "suicide", "coma"
        ]
        if any(keyword in message_lower for keyword in emergency_keywords):
            return "emergency"
        
        # Language change detection
        language_keywords = {
            "en": ["english", "angrezi"],
            "ur": ["urdu", "اردو"],
            "ps": ["pashto", "پښتو"]
        }
        for lang_code, keywords in language_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                if any(phrase in message_lower for phrase in ["change language", "switch language", "language"]):
                    return "language"
        
        # Doctor finding intent
        doctor_keywords = [
            "doctor", "physician", "specialist", "consult", "appointment",
            "find doctor", "need doctor", "want doctor", "see a doctor",
            "checkup", "check up", "ڈاکټر", "doctor", "د ډاکټر"
        ]
        if any(keyword in message_lower for keyword in doctor_keywords):
            return "doctor"
        
        # Medicine intent
        medicine_keywords = [
            "medicine", "medication", "drug", "pill", "tablet", "dose",
            "what medicine", "medicine for", "medicine information",
            "دوا", "دری", "medicine", "tablet"
        ]
        if any(keyword in message_lower for keyword in medicine_keywords):
            return "medicine"
        
        # Lab intent
        lab_keywords = [
            "lab", "laboratory", "test", "blood test", "urine test", "x-ray",
            "mri", "scan", "diagnostic", "sample", "report",
            "لیب", "lab", "لیباریٹری", "test", "ازمېښت"
        ]
        if any(keyword in message_lower for keyword in lab_keywords):
            return "lab"
        
        # Appointment specific
        appointment_keywords = [
            "book", "booking", "schedule", "reserve", "appointment",
            "تڼۍ", "اپائنٹمنٹ", "book"
        ]
        if any(keyword in message_lower for keyword in appointment_keywords):
            return "appointment"
        
        # Greeting
        greeting_keywords = [
            "hello", "hi", "hey", "good morning", "good evening", "good night",
            "السلام علیکم", "سلام", "hello", "هیلو", "په خوښې"
        ]
        if any(keyword in message_lower for keyword in greeting_keywords):
            return "greeting"
        
        # Help request
        help_keywords = ["help", "help me", "what can you do", "options", "menu"]
        if any(keyword in message_lower for keyword in help_keywords):
            return "help"
        
        # Thank you / Goodbye
        gratitude_keywords = ["thank", "thanks", "goodbye", "bye", "خوش", "مننه"]
        if any(keyword in message_lower for keyword in gratitude_keywords):
            return "goodbye"
        
        return "general"
    
    def extract_symptoms(self, message: str) -> List[str]:
        """
        Extract medical symptoms from user message
        
        Args:
            message: User's input message
            
        Returns:
            List of extracted symptoms
        """
        # Try OpenAI extraction first if available
        if self.openai_service.is_enabled():
            try:
                result = self.openai_service.extract_entities(message, self.language)
                if result.get("success") and result.get("symptoms"):
                    return result["symptoms"]
            except Exception:
                pass
        
        # Fallback to keyword-based extraction
        message_lower = message.lower()
        symptoms = []
        
        # Common symptom keywords to look for
        symptom_keywords = {
            "fever": ["fever", "temperature", "hot body", "febrile", "بخار", " temperature"],
            "headache": ["headache", "head pain", "migraine", "سر درد", "د سر درد"],
            "cough": ["cough", "coughing", "cold", "flu", "زکام", "کڼchino", "کوفی"],
            "body pain": ["body pain", "body ache", "muscle pain", "joint pain", "بدن درد", "د بدن درد"],
            "stomach pain": ["stomach pain", "abdomen pain", "stomach ache", "پیٹ درد", "د پیٹ درد"],
            "vomiting": ["vomiting", "vomit", "nausea", "throw up", "کرکرا", "ککرا"],
            "diarrhea": ["diarrhea", "loose motion", "watery stool", "اسهال", "د شکم هلک"],
            "chest pain": ["chest pain", "heart pain", "cardiac pain", "سینے درد", "د سینے درد"],
            "breathing difficulty": ["breathing", "shortness of breath", "asthma", "difficulty breathing", "سالنۍ", "د سالنۍ ستونزه"],
            "skin rash": ["rash", "skin problem", "allergy", "itching", "جلد", "د پوستکي ستونزه"],
            "eye problem": ["eye", "vision", "blind", "blindness", "اکه", "د سترګو ستونزه"],
            "ear problem": ["ear", "hearing", "deaf", "کړن", "د کړنو ستونزه"],
            "throat problem": ["throat", "sore throat", "swallow", "گلو", "د گلو ستونزه"],
            "dizziness": ["dizziness", "dizzy", "vertigo", "سر ګیڼه", "د سر ګیڼه"],
            "fatigue": ["tired", "fatigue", "weakness", "exhausted", "ټکان", "د خستګي"],
            "nausea": ["nausea", "sick", "queasy", "رنځورېدل", "د رنځورېدلو"],
            "back pain": ["back pain", "backache", "کمر درد", "د کمر درد"],
            "toothache": ["toothache", "tooth pain", "dental", " dent", "د غاښ درد", "د غاښ درد"],
            "pregnancy": ["pregnant", "pregnancy", "حامله", "ولادت", " pregnancy"],
            "mental health": ["depression", "anxiety", "stress", "mental", "psychological", " depression", "anxiety"],
            "high blood pressure": ["blood pressure", "hypertension", "bp", "فشار خون", "د وینې فشار"],
            "diabetes": ["diabetes", "sugar", "blood sugar", "diabetic", "شکر", "شکرې", " diabetes"],
            "weight loss": ["weight loss", "losing weight", " weight"],
            "insomnia": ["insomnia", "can't sleep", "sleep problem", "بې خوبۍ", "د خوب ستونزه"],
        }
        
        for symptom, keywords in symptom_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                if symptom not in symptoms:
                    symptoms.append(symptom)
        
        return symptoms
    
    def extract_duration(self, message: str) -> Optional[str]:
        """
        Extract duration of symptoms from user message
        
        Args:
            message: User's input message
            
        Returns:
            Duration string like "2 days", "1 week", etc.
        """
        # Try OpenAI extraction first if available
        if self.openai_service.is_enabled():
            try:
                result = self.openai_service.extract_entities(message, self.language)
                if result.get("success") and result.get("durations"):
                    return result["durations"][0]  # Return first duration
            except Exception:
                pass
        
        # Fallback to keyword-based extraction
        message_lower = message.lower()
        
        # Duration patterns
        duration_patterns = [
            # English patterns
            r"(\d+)\s*(day|days|d)",
            r"(\d+)\s*(week|weeks|w)",
            r"(\d+)\s*(month|months|m)",
            r"(\d+)\s*(hour|hours|h)",
            r"(\d+)\s*(year|years|y)",
            # Urdu patterns
            r"(\d+)\s*روز",
            r"(\d+)\s*هفتہ",
            r"(\d+)\s*مہینہ",
            r"(\d+)\s*سال",
            # Common time expressions
            r"since\s+(\w+)",
            r"for\s+(\w+)",
            r"last\s+(\w+)",
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, message_lower)
            if match:
                # Return the matched duration
                duration_text = match.group(0)
                # Clean up and return
                return duration_text.strip()
        
        # Check for relative time expressions
        time_expressions = {
            "today": "today",
            "yesterday": "yesterday",
            "few days": "few days",
            "several days": "several days",
            "a week": "a week",
            "long time": "long time",
            "recently": "recently",
        }
        
        for expr in time_expressions:
            if expr in message_lower:
                return time_expressions[expr]
        
        return None
    
    def map_symptoms_to_specialization(self, symptoms: List[str]) -> Optional[str]:
        """
        Map extracted symptoms to appropriate medical specialization
        
        Args:
            symptoms: List of extracted symptoms
            
        Returns:
            Medical specialization string
        """
        if not symptoms:
            return None
        
        # Map symptoms to specializations
        symptom_to_specialization = {
            "fever": "General Physician",
            "headache": "Neurologist",
            "chest pain": "Cardiologist",
            "breathing difficulty": "Pulmonologist",
            "cough": "Pulmonologist",
            "skin rash": "Dermatologist",
            "stomach pain": "Gastroenterologist",
            "vomiting": "Gastroenterologist",
            "diarrhea": "Gastroenterologist",
            "eye problem": "Ophthalmologist",
            "ear problem": "ENT Specialist",
            "throat problem": "ENT Specialist",
            "dizziness": "Neurologist",
            "fatigue": "General Physician",
            "nausea": "General Physician",
            "back pain": "Orthopedic",
            "toothache": "Dentist",
            "pregnancy": "Gynecologist",
            "mental health": "Psychiatrist",
            "high blood pressure": "Cardiologist",
            "diabetes": "General Physician",
            "weight loss": "General Physician",
            "insomnia": "Psychiatrist",
            "body pain": "General Physician",
        }
        
        # Get specializations for all symptoms
        specializations = []
        for symptom in symptoms:
            if symptom in symptom_to_specialization:
                specializations.append(symptom_to_specialization[symptom])
        
        # Return most relevant (first one or most common)
        if specializations:
            # Prioritize General Physician for general symptoms
            if "General Physician" in specializations and len(specializations) > 1:
                specializations.remove("General Physician")
            return specializations[0] if specializations else "General Physician"
        
        return "General Physician"  # Default
    
    def extract_location(self, message: str) -> Optional[str]:
        """
        Extract location from user message
        
        Args:
            message: User's input message
            
        Returns:
            Location string (city/area)
        """
        # Try OpenAI extraction first if available
        if self.openai_service.is_enabled():
            try:
                result = self.openai_service.extract_entities(message, self.language)
                if result.get("success") and result.get("locations"):
                    return result["locations"][0]  # Return first location
            except Exception:
                pass
        
        # Fallback to keyword-based extraction
        message_lower = message.lower()
        
        # Common cities in Pakistan
        cities = [
            "karachi", "lahore", "islamabad", "rawalpindi", "faisalabad",
            "multan", "peshawar", "quetta", "sialkot", "gujranwala",
            "hyderabad", "sukkur", "lahore", "karachi"
        ]
        
        # Check for cities in message
        for city in cities:
            if city in message_lower:
                return city.title()
        
        # Check for common location phrases
        location_patterns = [
            r"(?:in|at|near|from|around)\s+([a-zA-Z]+)",
            r"i(?:'m| am)\s+(?:in|at|from)\s+([a-zA-Z]+)",
            r"location[:\s]+([a-zA-Z]+)",
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, message_lower)
            if match:
                location = match.group(1).strip()
                if len(location) > 2:  # Avoid single letters
                    return location.title()
        
        return None
    
    def find_doctors(self, specialization: str, location: str = None, limit: int = 5) -> List[Doctor]:
        """
        Find doctors by specialization and location
        
        Args:
            specialization: Medical specialization
            location: City or area (optional)
            limit: Maximum number of results
            
        Returns:
            List of Doctor objects
        """
        query = self.db.query(Doctor).filter(Doctor.is_available == True)
        
        # Filter by specialization (case-insensitive)
        if specialization:
            query = query.filter(Doctor.specialization.ilike(f"%{specialization}%"))
        
        # Filter by location if provided
        if location:
            query = query.filter(
                (Doctor.city.ilike(f"%{location}%")) | 
                (Doctor.area.ilike(f"%{location}%"))
            )
        
        # Order by rating and return limit
        doctors = query.order_by(Doctor.rating.desc()).limit(limit).all()
        return doctors
    
    def find_medicine(self, medicine_name: str) -> Optional[Medicine]:
        """
        Find medicine by name
        
        Args:
            medicine_name: Name of the medicine
            
        Returns:
            Medicine object or None
        """
        # Try exact match first
        medicine = self.db.query(Medicine).filter(
            Medicine.name.ilike(f"%{medicine_name}%")
        ).first()
        
        return medicine
    
    def find_labs(self, location: str = None, test_type: str = None, limit: int = 5) -> List[Laboratory]:
        """
        Find laboratories by location and test type
        
        Args:
            location: City or area
            test_type: Type of test (optional)
            limit: Maximum number of results
            
        Returns:
            List of Laboratory objects
        """
        query = self.db.query(Laboratory)
        
        # Filter by location
        if location:
            query = query.filter(
                (Laboratory.city.ilike(f"%{location}%")) | 
                (Laboratory.area.ilike(f"%{location}%"))
            )
        
        # Filter by test type if provided
        if test_type:
            query = query.filter(Laboratory.tests_available.ilike(f"%{test_type}%"))
        
        # Order by rating and return limit
        labs = query.order_by(Laboratory.rating.desc()).limit(limit).all()
        return labs
    
    def format_doctor_info(self, doctor: Doctor) -> str:
        """
        Format doctor information for display
        
        Args:
            doctor: Doctor object
            
        Returns:
            Formatted string with doctor details
        """
        return self.translator.get("doctor_info").format(
            name=doctor.name,
            specialization=doctor.specialization,
            area=doctor.area or "",
            city=doctor.city,
            experience=doctor.experience_years or "N/A",
            fee=doctor.consultation_fee or "N/A",
            days=doctor.available_days or "N/A",
            hours=doctor.available_hours or "N/A",
            rating=doctor.rating
        )
    
    def format_lab_info(self, lab: Laboratory) -> str:
        """
        Format laboratory information for display
        
        Args:
            lab: Laboratory object
            
        Returns:
            Formatted string with lab details
        """
        home_sample = "Yes" if lab.home_sample else "No"
        
        return self.translator.get("lab_info").format(
            name=lab.name,
            area=lab.area or "",
            city=lab.city,
            tests=lab.tests_available or "N/A",
            home=home_sample,
            hours=lab.operating_hours or "N/A",
            rating=lab.rating
        )
    
    def format_medicine_info(self, medicine: Medicine) -> str:
        """
        Format medicine information for display
        
        Args:
            medicine: Medicine object
            
        Returns:
            Formatted string with medicine details
        """
        prescription = "Yes" if medicine.requires_prescription else "No"
        
        return self.translator.get("medicine_info").format(
            name=medicine.name,
            generic=medicine.generic_name or "N/A",
            used_for=medicine.used_for or "N/A",
            dose=medicine.common_dose or "N/A",
            timing=medicine.dose_timing or "N/A",
            side_effects=medicine.side_effects or "N/A",
            precautions=medicine.precautions or "N/A",
            prescription=prescription
        )
    
    def process_message(self, message: str, conversation_state: Dict = None) -> Tuple[str, Dict]:
        """
        Process user message and generate appropriate response
        
        Args:
            message: User's input message
            conversation_state: Current conversation state (if continuing)
            
        Returns:
            Tuple of (bot_response, new_conversation_state)
        """
        # Update conversation state if provided
        if conversation_state:
            self.conversation_state.update(conversation_state)
        
        # Detect intent
        intent = self.detect_intent(message)
        self.conversation_state["detected_intent"] = intent
        
        # Extract symptoms if in symptom-gathering mode
        symptoms = self.extract_symptoms(message)
        duration = self.extract_duration(message)
        location = self.extract_location(message)
        
        # Update state
        if symptoms:
            self.conversation_state["extracted_symptoms"] = symptoms
            self.conversation_state["waiting_for_symptoms"] = False
            self.conversation_state["detected_intent"] = "doctor"
        
        if duration:
            self.conversation_state["extracted_duration"] = duration
            self.conversation_state["waiting_for_duration"] = False
        
        if location:
            self.conversation_state["location"] = location
            self.conversation_state["waiting_for_location"] = False
        
        # Generate response based on intent and state
        response = self.generate_response(intent, message, symptoms, duration, location)
        
        return response, self.conversation_state.copy()
    
    def generate_response(self, intent: str, message: str, symptoms: List, 
                          duration: Optional[str], location: Optional[str]) -> str:
        """
        Generate appropriate response based on intent and state
        
        Args:
            intent: Detected user intent
            message: Original user message
            symptoms: Extracted symptoms
            duration: Extracted duration
            location: Extracted location
            
        Returns:
            Bot response string
        """
        
        # ============ GREETING ============
        if intent == "greeting":
            return self.translator.get("greeting")
        
        # ============ HELP ============
        if intent == "help":
            return self.translator.get("help_options")
        
        # ============ GOODBYE ============
        if intent == "goodbye":
            return self.translator.get("goodbye")
        
        # ============ EMERGENCY ============
        if intent == "emergency":
            return self.translator.get("emergency_warning") + "\n\n" + self.translator.get("medical_disclaimer")
        
        # ============ LANGUAGE CHANGE ============
        if intent == "language":
            return self.translator.get("select_language")
        
        # ============ DOCTOR ============
        if intent == "doctor":
            # If symptoms already extracted, check for location
            if self.conversation_state.get("extracted_symptoms") or symptoms:
                symptoms_list = symptoms or self.conversation_state.get("extracted_symptoms", [])
                
                # Get specialization
                specialization = self.map_symptoms_to_specialization(symptoms_list)
                self.conversation_state["specialization"] = specialization
                
                # Check for location
                user_location = location or self.conversation_state.get("location")
                
                if user_location:
                    # Find doctors
                    doctors = self.find_doctors(specialization, user_location)
                    
                    if doctors:
                        response = self.translator.get("finding_doctors").format(location=user_location) + "\n\n"
                        response += self.translator.get("doctors_found").format(count=len(doctors)) + "\n\n"
                        
                        for doctor in doctors:
                            response += self.format_doctor_info(doctor) + "\n\n"
                        
                        response += self.translator.get("confirm_more_info")
                        return response
                    else:
                        return self.translator.get("no_doctors_found").format(location=user_location)
                else:
                    # Ask for location
                    self.conversation_state["waiting_for_location"] = True
                    return self.translator.get("ask_location")
            else:
                # Ask for symptoms
                self.conversation_state["waiting_for_symptoms"] = True
                return self.translator.get("ask_symptoms")
        
        # ============ MEDICINE ============
        if intent == "medicine":
            # Try to extract medicine name from message
            medicine_name = message.lower()
            
            # Clean up common prefixes
            for prefix in ["medicine for ", "medicine ", "what medicine ", "drug ", "medication "]:
                if medicine_name.startswith(prefix):
                    medicine_name = medicine_name[len(prefix):].strip()
            
            # Find medicine
            medicine = self.find_medicine(medicine_name)
            
            if medicine:
                response = self.format_medicine_info(medicine) + "\n\n"
                response += self.translator.get("medicine_disclaimer")
                return response
            else:
                return self.translator.get("medicine_not_found") + "\n\n" + \
                       self.translator.get("medicine_disclaimer")
        
        # ============ LAB ============
        if intent == "lab":
            # Check for location
            user_location = location or self.conversation_state.get("location")
            
            if user_location:
                # Find labs
                labs = self.find_labs(user_location)
                
                if labs:
                    response = self.translator.get("finding_labs").format(location=user_location) + "\n\n"
                    response += self.translator.get("labs_found").format(count=len(labs)) + "\n\n"
                    
                    for lab in labs:
                        response += self.format_lab_info(lab) + "\n\n"
                    
                    response += self.translator.get("confirm_more_info")
                    return response
                else:
                    return self.translator.get("no_labs_found").format(location=user_location)
            else:
                # Ask for location
                self.conversation_state["waiting_for_location"] = True
                return self.translator.get("ask_location")
        
        # ============ LOCATION PROVIDED ============
        if location and self.conversation_state.get("waiting_for_location"):
            self.conversation_state["location"] = location
            
            # If we have specialization, find doctors
            specialization = self.conversation_state.get("specialization")
            if specialization:
                doctors = self.find_doctors(specialization, location)
                
                if doctors:
                    response = self.translator.get("finding_doctors").format(location=location) + "\n\n"
                    response += self.translator.get("doctors_found").format(count=len(doctors)) + "\n\n"
                    
                    for doctor in doctors:
                        response += self.format_doctor_info(doctor) + "\n\n"
                    
                    response += self.translator.get("confirm_more_info")
                    return response
                else:
                    return self.translator.get("no_doctors_found").format(location=location)
            
            # If we have symptoms but no specialization
            symptoms_list = self.conversation_state.get("extracted_symptoms", [])
            if symptoms_list:
                specialization = self.map_symptoms_to_specialization(symptoms_list)
                doctors = self.find_doctors(specialization, location)
                
                if doctors:
                    response = self.translator.get("finding_doctors").format(location=location) + "\n\n"
                    response += self.translator.get("doctors_found").format(count=len(doctors)) + "\n\n"
                    
                    for doctor in doctors:
                        response += self.format_doctor_info(doctor) + "\n\n"
                    
                    response += self.translator.get("confirm_more_info")
                    return response
                else:
                    return self.translator.get("no_doctors_found").format(location=location)
            
            # Just find general physicians
            doctors = self.find_doctors("General Physician", location)
            
            if doctors:
                response = self.translator.get("finding_doctors").format(location=location) + "\n\n"
                response += self.translator.get("doctors_found").format(count=len(doctors)) + "\n\n"
                
                for doctor in doctors:
                    response += self.format_doctor_info(doctor) + "\n\n"
                
                response += self.translator.get("confirm_more_info")
                return response
            else:
                return self.translator.get("no_doctors_found").format(location=location)
        
        # ============ SYMPTOMS PROVIDED ============
        if symptoms and self.conversation_state.get("waiting_for_symptoms"):
            self.conversation_state["extracted_symptoms"] = symptoms
            
            # Check for duration
            if duration:
                self.conversation_state["extracted_duration"] = duration
            else:
                # Ask for duration
                self.conversation_state["waiting_for_duration"] = True
                return self.translator.get("ask_duration")
            
            # Ask for location
            self.conversation_state["waiting_for_location"] = True
            return self.translator.get("ask_location")
        
        # ============ DURATION PROVIDED ============
        if duration and self.conversation_state.get("waiting_for_duration"):
            self.conversation_state["extracted_duration"] = duration
            self.conversation_state["waiting_for_location"] = True
            return self.translator.get("ask_location")
        
        # ============ DEFAULT ============
        return self.translator.get("sorry_alt")


def create_chatbot_response(db_session: Session, message: str, user_id: str, 
                            language: str = "en", conversation_state: Dict = None) -> Dict[str, Any]:
    """
    Main function to create chatbot response
    
    Args:
        db_session: Database session
        message: User's message
        user_id: User identifier
        language: User's language preference
        conversation_state: Previous conversation state
        
    Returns:
        Dictionary with response and state
    """
    # Create chatbot instance
    chatbot = ChatbotLogic(db_session, language)
    
    # Check if OpenAI should be used
    if USE_OPENAI and chatbot.openai_service.is_enabled():
        # Try to use OpenAI for response generation
        openai_result = chatbot.openai_service.generate_response(
            message=message,
            conversation_history=None,  # Could pass history here
            language=language,
            context={
                "conversation_state": conversation_state,
                "user_id": user_id
            }
        )
        
        if openai_result.get("success"):
            # OpenAI succeeded - use its response
            response = openai_result["bot_reply"]
            
            # Try to extract structured data from OpenAI response
            parsed_data = openai_result.get("parsed_data", {})
            
            # Add medical disclaimer to response if not already there
            if "disclaimer" not in response.lower():
                if any(keyword in message.lower() for keyword in ["medicine", "drug", "دوا", "دری"]):
                    response += "\n\n" + chatbot.translator.get("medical_disclaimer")
            
            # Update conversation state based on OpenAI extraction
            new_state = conversation_state.copy() if conversation_state else chatbot.conversation_state.copy()
            
            # Extract entities if available
            if parsed_data:
                if "symptoms" in parsed_data:
                    new_state["extracted_symptoms"] = parsed_data["symptoms"]
                if "intent" in parsed_data:
                    new_state["detected_intent"] = parsed_data["intent"]
            
            return {
                "bot_reply": response,
                "conversation_state": new_state,
                "detected_intent": new_state.get("detected_intent", "general"),
                "extracted_symptoms": new_state.get("extracted_symptoms", []),
                "extracted_duration": new_state.get("extracted_duration"),
                "location": new_state.get("location"),
                "ai_generated": True  # Flag to indicate AI response
            }
    
    # Fallback to original keyword-based logic
    # Process message
    response, new_state = chatbot.process_message(message, conversation_state)
    
    # Add medical disclaimer to response if not already there
    if "medical_disclaimer" not in response.lower() and "disclaimer" not in response.lower():
        if any(keyword in message.lower() for keyword in ["medicine", "drug", "دوا", "دری"]):
            response += "\n\n" + chatbot.translator.get("medical_disclaimer")
    
    return {
        "bot_reply": response,
        "conversation_state": new_state,
        "detected_intent": new_state.get("detected_intent", "general"),
        "extracted_symptoms": new_state.get("extracted_symptoms", []),
        "extracted_duration": new_state.get("extracted_duration"),
        "location": new_state.get("location"),
        "ai_generated": False  # Flag to indicate non-AI response
    }
