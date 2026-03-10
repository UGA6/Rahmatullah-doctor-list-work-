"""
Configuration settings for ADMA Healthcare Chatbot
This file contains all configuration variables for the application
"""
import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).parent

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/adma_healthcare.db")

# API Configuration
API_VERSION = "1.0.0"
API_TITLE = "ADMA Healthcare Chatbot API"
API_DESCRIPTION = "AI-powered healthcare chatbot for patients to find doctors, medicines, and lab services"

# Multilingual support
# Supported languages: English (en), Urdu (ur), Pashto (ps)
DEFAULT_LANGUAGE = "en"

# Chatbot Configuration
MAX_CONVERSATION_HISTORY = 100
SESSION_TIMEOUT_MINUTES = 30

# Medical disclaimer
MEDICAL_DISCLAIMER = "Please note: This is only for informational purposes. Always consult a qualified doctor for medical advice."

# Location services (simulated - in production, use real GPS API)
DEFAULT_LOCATION = "Karachi"

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "500"))

# Enable/Disable OpenAI (for fallback to keyword matching)
USE_OPENAI = os.getenv("USE_OPENAI", "true").lower() == "true"
