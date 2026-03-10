"""
Database Connection and Setup for ADMA Healthcare Chatbot
This file handles database initialization and connection
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from chatbot.models import Base, Doctor, Medicine, Laboratory, SymptomMapping

# Import config
from chatbot.config import DATABASE_URL


class Database:
    """Database connection and session management"""
    
    def __init__(self):
        """Initialize database connection"""
        self.engine = create_engine(
            DATABASE_URL,
            echo=False,  # Set to True for SQL debugging
            connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
        print("Database tables created successfully")
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()
    
    def close_session(self, session: Session):
        """Close database session"""
        session.close()


def get_db():
    """
    Dependency function for FastAPI to get database session
    Usage: def endpoint(db: Session = Depends(get_db))
    """
    db = Database()
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()


def initialize_database():
    """
    Initialize database with tables and sample data
    Call this function once when starting the application
    """
    db = Database()
    db.create_tables()
    session = db.get_session()
    
    try:
        # Check if data already exists
        if session.query(Doctor).count() > 0:
            print("Database already contains data")
            return
        
        # Add sample doctors (at least 10)
        sample_doctors = [
            Doctor(doctor_id="DR001", name="Dr. Ahmad Khan", specialization="General Physician",
                   qualification="MBBS, FCPS", city="Karachi", area="Clifton",
                   phone="+92-21-12345678", hospital_clinic="Adma Hospital",
                   experience_years=15, consultation_fee=1500, languages="English,Urdu",
                   available_days="Mon-Sat", available_hours="9AM-5PM", rating=4.5),
            
            Doctor(doctor_id="DR002", name="Dr. Sara Hassan", specialization="Cardiologist",
                   qualification="MBBS, FCPS (Cardiology)", city="Karachi", area="Gulshan-e-Iqbal",
                   phone="+92-21-23456789", hospital_clinic="National Heart Center",
                   experience_years=12, consultation_fee=2500, languages="English,Urdu",
                   available_days="Mon-Fri", available_hours="10AM-4PM", rating=4.8),
            
            Doctor(doctor_id="DR003", name="Dr. Muhammad Ali", specialization="Dermatologist",
                   qualification="MBBS, FCPS (Dermatology)", city="Lahore", area="Gulberg",
                   phone="+92-42-12345678", hospital_clinic="Skin Care Clinic",
                   experience_years=10, consultation_fee=2000, languages="English,Urdu,Punjabi",
                   available_days="Mon-Sat", available_hours="9AM-6PM", rating=4.6),
            
            Doctor(doctor_id="DR004", name="Dr. Fatima Raza", specialization="Pediatrician",
                   qualification="MBBS, FCPS (Pediatrics)", city="Karachi", area="DHA",
                   phone="+92-21-34567890", hospital_clinic="Children's Hospital",
                   experience_years=8, consultation_fee=1800, languages="English,Urdu",
                   available_days="Mon-Sat", available_hours="10AM-5PM", rating=4.7),
            
            Doctor(doctor_id="DR005", name="Dr. Imran Sheikh", specialization="Orthopedic",
                   qualification="MBBS, FCPS (Ortho)", city="Islamabad", area="F-6",
                   phone="+92-51-2345678", hospital_clinic="Orthopedic Center",
                   experience_years=15, consultation_fee=3000, languages="English,Urdu",
                   available_days="Mon-Fri", available_hours="9AM-4PM", rating=4.9),
            
            Doctor(doctor_id="DR006", name="Dr. Ayesha Malik", specialization="Neurologist",
                   qualification="MBBS, FCPS (Neurology)", city="Karachi", area=" Saddar",
                   phone="+92-21-45678901", hospital_clinic="Brain & Spine Institute",
                   experience_years=11, consultation_fee=3500, languages="English,Urdu",
                   available_days="Mon-Sat", available_hours="9AM-5PM", rating=4.8),
            
            Doctor(doctor_id="DR007", name="Dr. Omar Farooq", specialization="Gastroenterologist",
                   qualification="MBBS, FCPS (GI)", city="Lahore", area="Model Town",
                   phone="+92-42-23456789", hospital_clinic="Digestive Health Center",
                   experience_years=9, consultation_fee=2200, languages="English,Urdu,Punjabi",
                   available_days="Mon-Fri", available_hours="10AM-6PM", rating=4.5),
            
            Doctor(doctor_id="DR008", name="Dr. Zainab Ahmed", specialization="Gynecologist",
                   qualification="MBBS, FCPS (Gynae)", city="Karachi", area="North Nazimabad",
                   phone="+92-21-56789012", hospital_clinic="Women's Health Clinic",
                   experience_years=13, consultation_fee=2000, languages="English,Urdu",
                   available_days="Mon-Sat", available_hours="9AM-5PM", rating=4.7),
            
            Doctor(doctor_id="DR009", name="Dr. Hassan Riaz", specialization="Psychiatrist",
                   qualification="MBBS, FCPS (Psychiatry)", city="Islamabad", area="E-7",
                   phone="+92-51-3456789", hospital_clinic="Mental Wellness Center",
                   experience_years=7, consultation_fee=2500, languages="English,Urdu",
                   available_days="Mon-Fri", available_hours="10AM-5PM", rating=4.6),
            
            Doctor(doctor_id="DR010", name="Dr. Maria Sultana", specialization="ENT Specialist",
                   qualification="MBBS, FCPS (ENT)", city="Karachi", area="Lyari",
                   phone="+92-21-67890123", hospital_clinic="ENT Care Center",
                   experience_years=10, consultation_fee=1800, languages="English,Urdu",
                   available_days="Mon-Sat", available_hours="9AM-4PM", rating=4.4),
            
            Doctor(doctor_id="DR011", name="Dr. Bilal Mahmood", specialization="Pulmonologist",
                   qualification="MBBS, FCPS (Pulmonology)", city="Karachi", area="S.I.T.E",
                   phone="+92-21-78901234", hospital_clinic="Chest & Respiratory Center",
                   experience_years=12, consultation_fee=2800, languages="English,Urdu",
                   available_days="Mon-Fri", available_hours="9AM-5PM", rating=4.5),
            
            Doctor(doctor_id="DR012", name="Dr. Saima Naveed", specialization="Ophthalmologist",
                   qualification="MBBS, FCPS (Eye)", city="Lahore", area="Cantt",
                   phone="+92-42-3456789", hospital_clinic="Vision Care Hospital",
                   experience_years=14, consultation_fee=2000, languages="English,Urdu,Punjabi",
                   available_days="Mon-Sat", available_hours="10AM-6PM", rating=4.8),
        ]
        
        # Add sample medicines (at least 20)
        sample_medicines = [
            Medicine(medicine_id="MED001", name="Paracetamol", generic_name="Acetaminophen",
                    used_for="Fever, Headache, Pain relief", category="Pain Relief",
                    common_dose="500mg-1000mg", dose_timing="Every 4-6 hours as needed",
                    side_effects="Rare: Nausea, liver damage in overdose",
                    precautions="Avoid alcohol, do not exceed 4g daily",
                    requires_prescription=False, price_range="Rs. 10-50"),
            
            Medicine(medicine_id="MED002", name="Ibuprofen", generic_name="Ibuprofen",
                    used_for="Pain, Inflammation, Fever", category="NSAID",
                    common_dose="200mg-400mg", dose_timing="Every 6-8 hours with food",
                    side_effects="Stomach upset, heartburn, kidney issues",
                    precautions="Take with food, avoid if stomach ulcers",
                    requires_prescription=False, price_range="Rs. 20-100"),
            
            Medicine(medicine_id="MED003", name="Amoxicillin", generic_name="Amoxicillin",
                    used_for="Bacterial infections (respiratory, ear, throat)", category="Antibiotic",
                    common_dose="250mg-500mg", dose_timing="Every 8 hours",
                    side_effects="Diarrhea, nausea, allergic reactions",
                    precautions="Complete full course, allergic reactions possible",
                    requires_prescription=True, price_range="Rs. 100-300"),
            
            Medicine(medicine_id="MED004", name="Aspirin", generic_name="Acetylsalicylic Acid",
                    used_for="Pain, Fever, Heart attack prevention", category="NSAID",
                    common_dose="300mg-500mg", dose_timing="Every 4-6 hours",
                    side_effects="Stomach bleeding, ringing in ears",
                    precautions="Not for children, avoid with blood thinners",
                    requires_prescription=False, price_range="Rs. 10-30"),
            
            Medicine(medicine_id="MED005", name="Omeprazole", generic_name="Omeprazole",
                    used_for="Acid reflux, GERD, Stomach ulcers", category="PPI",
                    common_dose="20mg-40mg", dose_timing="Once daily before breakfast",
                    side_effects="Headache, diarrhea, stomach pain",
                    precautions="Take on empty stomach",
                    requires_prescription=True, price_range="Rs. 50-200"),
            
            Medicine(medicine_id="MED006", name="Cetirizine", generic_name="Cetirizine",
                    used_for="Allergies, Hay fever, Itching", category="Antihistamine",
                    common_dose="10mg", dose_timing="Once daily",
                    side_effects="Drowsiness, dry mouth, fatigue",
                    precautions="May cause drowsiness, avoid driving",
                    requires_prescription=False, price_range="Rs. 30-150"),
            
            Medicine(medicine_id="MED007", name="Metformin", generic_name="Metformin",
                    used_for="Type 2 Diabetes", category="Anti-diabetic",
                    common_dose="500mg-1000mg", dose_timing="With meals",
                    side_effects="Nausea, stomach upset, vitamin B12 deficiency",
                    precautions="Monitor kidney function",
                    requires_prescription=True, price_range="Rs. 50-200"),
            
            Medicine(medicine_id="MED008", name="Amlodipine", generic_name="Amlodipine",
                    used_for="High blood pressure, Angina", category="Calcium Channel Blocker",
                    common_dose="5mg-10mg", dose_timing="Once daily",
                    side_effects="Swelling, dizziness, headache",
                    precautions="Monitor blood pressure regularly",
                    requires_prescription=True, price_range="Rs. 100-400"),
            
            Medicine(medicine_id="MED009", name="Salbutamol", generic_name="Albuterol",
                    used_for="Asthma, Bronchospasm", category="Bronchodilator",
                    common_dose="100-200mcg", dose_timing="As needed for breathing",
                    side_effects="Tremor, fast heartbeat, nervousness",
                    precautions="Use rescue inhaler as directed",
                    requires_prescription=True, price_range="Rs. 50-200"),
            
            Medicine(medicine_id="MED010", name="Azithromycin", generic_name="Azithromycin",
                    used_for="Respiratory infections, Ear infections", category="Antibiotic",
                    common_dose="250mg-500mg", dose_timing="Once daily",
                    side_effects="Diarrhea, nausea, abdominal pain",
                    precautions="Complete full course",
                    requires_prescription=True, price_range="Rs. 200-500"),
            
            Medicine(medicine_id="MED011", name="Pantoprazole", generic_name="Pantoprazole",
                    used_for="GERD, Acid reflux, Ulcers", category="PPI",
                    common_dose="40mg", dose_timing="Once daily before breakfast",
                    side_effects="Headache, diarrhea, nausea",
                    precautions="Take on empty stomach",
                    requires_prescription=True, price_range="Rs. 150-400"),
            
            Medicine(medicine_id="MED012", name="Loratadine", generic_name="Loratadine",
                    used_for="Allergies, Hay fever", category="Antihistamine",
                    common_dose="10mg", dose_timing="Once daily",
                    side_effects="Headache, dry mouth, fatigue",
                    precautions="Non-drowsy formula available",
                    requires_prescription=False, price_range="Rs. 30-100"),
            
            Medicine(medicine_id="MED013", name="Glibenclamide", generic_name="Glibenclamide",
                    used_for="Type 2 Diabetes", category="Sulfonylurea",
                    common_dose="5mg", dose_timing="With breakfast",
                    side_effects="Hypoglycemia, weight gain",
                    precautions="Monitor blood sugar",
                    requires_prescription=True, price_range="Rs. 30-100"),
            
            Medicine(medicine_id="MED014", name="Diclofenac", generic_name="Diclofenac Sodium",
                    used_for="Pain, Arthritis, Inflammation", category="NSAID",
                    common_dose="50mg", dose_timing="Every 8-12 hours with food",
                    side_effects="Stomach upset, liver issues",
                    precautions="Take with food",
                    requires_prescription=False, price_range="Rs. 20-80"),
            
            Medicine(medicine_id="MED015", name="Levocetirizine", generic_name="Levocetirizine",
                    used_for="Allergies, Chronic urticaria", category="Antihistamine",
                    common_dose="5mg", dose_timing="Once daily",
                    side_effects="Drowsiness, dry mouth",
                    precautions="May cause drowsiness",
                    requires_prescription=False, price_range="Rs. 100-300"),
            
            Medicine(medicine_id="MED016", name="Atorvastatin", generic_name="Atorvastatin",
                    used_for="High cholesterol", category="Statin",
                    common_dose="10mg-40mg", dose_timing="Once daily at night",
                    side_effects="Muscle pain, liver issues",
                    precautions="Monitor liver function",
                    requires_prescription=True, price_range="Rs. 200-800"),
            
            Medicine(medicine_id="MED017", name="Domperidone", generic_name="Domperidone",
                    used_for="Nausea, Vomiting, Indigestion", category="Anti-emetic",
                    common_dose="10mg", dose_timing="Before meals",
                    side_effects="Dry mouth, headache",
                    precautions="Not for long-term use",
                    requires_prescription=False, price_range="Rs. 20-60"),
            
            Medicine(medicine_id="MED018", name="ORS (Oral Rehydration Salt)", generic_name="ORS",
                    used_for="Diarrhea, Dehydration", category="Electrolyte",
                    common_dose="1 sachet", dose_timing="After each loose stool",
                    side_effects="None",
                    precautions="Use clean water",
                    requires_prescription=False, price_range="Rs. 10-30"),
            
            Medicine(medicine_id="MED019", name="Mebendazole", generic_name="Mebendazole",
                    used_for="Worm infections", category="Anti-parasitic",
                    common_dose="100mg", dose_timing="Twice daily for 3 days",
                    side_effects="Stomach pain, diarrhea",
                    precautions="Hygiene important",
                    requires_prescription=False, price_range="Rs. 20-50"),
            
            Medicine(medicine_id="MED020", name="Multivitamin", generic_name="Multivitamin",
                    used_for="Vitamin deficiency, General health", category="Supplement",
                    common_dose="1 tablet", dose_timing="Once daily after meal",
                    side_effects="Rare: Nausea",
                    precautions="Do not exceed dose",
                    requires_prescription=False, price_range="Rs. 50-500"),
        ]
        
        # Add sample laboratories (at least 5)
        sample_labs = [
            Laboratory(lab_id="LAB001", name="Adma Diagnostic Center", city="Karachi",
                      area="Clifton", phone="+92-21-11111111", address="123 Main Road, Clifton",
                      tests_available="Blood Test, Urine Test, X-Ray, MRI, CT Scan",
                      home_sample=True, operating_hours="24/7", rating=4.5,
                      certifications="ISO 9001, CAP Accredited"),
            
            Laboratory(lab_id="LAB002", name="Chughtai Lab", city="Karachi",
                      area="Gulshan-e-Iqbal", phone="+92-21-22222222", address="456 Market Road",
                      tests_available="Blood Test, Sugar Test, Lipid Profile, Liver Function",
                      home_sample=True, operating_hours="7AM-11PM", rating=4.7,
                      certifications="ISO 9001"),
            
            Laboratory(lab_id="LAB003", name="Agha Khan Laboratory", city="Karachi",
                      area="DHA", phone="+92-21-33333333", address="789 DHA Phase 1",
                      tests_available="All pathology tests, Genetic Testing, Cancer Markers",
                      home_sample=True, operating_hours="6AM-10PM", rating=4.8,
                      certifications="ISO 9001, JCI Accredited"),
            
            Laboratory(lab_id="LAB004", name="Lahore Diagnostic Center", city="Lahore",
                      area="Model Town", phone="+92-42-44444444", address="123 Model Town",
                      tests_available="Blood Test, MRI, CT Scan, Ultrasound",
                      home_sample=False, operating_hours="8AM-8PM", rating=4.4,
                      certifications="ISO 9001"),
            
            Laboratory(lab_id="LAB005", name="Islamabad Pathology Lab", city="Islamabad",
                      area="F-6", phone="+92-51-55555555", address="456 F-6 Markaz",
                      tests_available="Blood Test, Urine Test, Hormone Tests",
                      home_sample=True, operating_hours="7AM-9PM", rating=4.6,
                      certifications="ISO 9001"),
            
            Laboratory(lab_id="LAB006", name="Jinnah Postgraduate Medical Centre Lab", city="Karachi",
                      area="Saddar", phone="+92-21-66666666", address="M.A. Jinnah Road",
                      tests_available="All advanced tests, Biopsy, Cytology",
                      home_sample=False, operating_hours="8AM-4PM", rating=4.7,
                      certifications="ISO 9001, WHO Accredited"),
        ]
        
        # Add symptom mappings
        symptom_mappings = [
            SymptomMapping(symptom_keywords="fever,temperature,hot body", specialization="General Physician", severity=2),
            SymptomMapping(symptom_keywords="headache,head pain,migraine", specialization="Neurologist", severity=1),
            SymptomMapping(symptom_keywords="chest pain,heart pain,palpitation", specialization="Cardiologist", severity=3),
            SymptomMapping(symptom_keywords="cough,cold,breathing,asthma", specialization="Pulmonologist", severity=2),
            SymptomMapping(symptom_keywords="skin,rash,allergy,itching", specialization="Dermatologist", severity=1),
            SymptomMapping(symptom_keywords="stomach pain,abdomen,vomiting,diarrhea", specialization="Gastroenterologist", severity=2),
            SymptomMapping(symptom_keywords="child,kid,baby,infant", specialization="Pediatrician", severity=2),
            SymptomMapping(symptom_keywords="bone,joint,back pain,fracture", specialization="Orthopedic", severity=2),
            SymptomMapping(symptom_keywords="eye,vision,blind", specialization="Ophthalmologist", severity=2),
            SymptomMapping(symptom_keywords="ear,hearing,nose,throat,sore throat", specialization="ENT Specialist", severity=1),
            SymptomMapping(symptom_keywords="pregnancy,pregnant,delivery,baby", specialization="Gynecologist", severity=2),
            SymptomMapping(symptom_keywords="mental,depression,anxiety,stress", specialization="Psychiatrist", severity=2),
            SymptomMapping(symptom_keywords="diabetes,sugar,blood sugar", specialization="General Physician", severity=2),
            SymptomMapping(symptom_keywords="blood pressure,hypertension", specialization="Cardiologist", severity=2),
            SymptomMapping(symptom_keywords="general,checkup,check up,health", specialization="General Physician", severity=1),
        ]
        
        # Add all data to session
        session.add_all(sample_doctors)
        session.add_all(sample_medicines)
        session.add_all(sample_labs)
        session.add_all(symptom_mappings)
        
        # Commit changes
        session.commit()
        print("Sample data added successfully")
        print(f"  - {len(sample_doctors)} doctors")
        print(f"  - {len(sample_medicines)} medicines")
        print(f"  - {len(sample_labs)} laboratories")
        print(f"  - {len(symptom_mappings)} symptom mappings")
        
    except Exception as e:
        session.rollback()
        print(f"Error initializing database: {e}")
        raise
    finally:
        session.close()


# Create global database instance
database = Database()
