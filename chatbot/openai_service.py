"""
OpenAI Service Module for ADMA Healthcare Chatbot

This module handles all interactions with the OpenAI API for:
1. Generating natural chatbot responses
2. Intent detection using AI
3. Extracting medical entities (symptoms, medications, etc.)

Author: ADMA Development Team
Version: 1.0.0
"""

import json
import logging
from typing import Dict, List, Optional, Any
from openai import OpenAI
from sqlalchemy.orm import Session

from chatbot.config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
    OPENAI_MAX_TOKENS,
    USE_OPENAI,
    MEDICAL_DISCLAIMER
)

# Configure logging
logger = logging.getLogger(__name__)


class OpenAIService:
    """
    Service class for handling OpenAI API interactions
    """
    
    def __init__(self, db_session: Session = None):
        """
        Initialize OpenAI service
        
        Args:
            db_session: Optional database session for accessing healthcare data
        """
        self.db = db_session
        self.client = None
        self.is_available = False
        
        # Initialize OpenAI client if API key is configured
        if OPENAI_API_KEY and OPENAI_API_KEY != "your-openai-api-key-here":
            try:
                self.client = OpenAI(api_key=OPENAI_API_KEY)
                self.is_available = True
                logger.info(f"OpenAI service initialized with model: {OPENAI_MODEL}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.is_available = False
        else:
            logger.warning("OpenAI API key not configured. Using fallback responses.")
    
    def is_enabled(self) -> bool:
        """Check if OpenAI is enabled and available"""
        return USE_OPENAI and self.is_available
    
    def generate_response(
        self,
        message: str,
        conversation_history: List[Dict[str, str]] = None,
        language: str = "en",
        context: Dict[str, Any] = None,
        db_session: Session = None
    ) -> Dict[str, Any]:
        """
        Generate a chatbot response using OpenAI
        
        Args:
            message: User's input message
            conversation_history: Previous messages in the conversation
            language: User's preferred language
            context: Additional context (detected intent, extracted symptoms, etc.)
            
        Returns:
            Dictionary with response and metadata
        """
        if not self.is_enabled():
            return {
                "success": False,
                "error": "OpenAI not available",
                "bot_reply": None
            }
        
        try:
            # Build system prompt
            system_prompt = self._build_system_prompt(language, context)
            
            # Build messages for OpenAI
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history (last 10 messages)
            if conversation_history:
                recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
                messages.extend(recent_history)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=OPENAI_TEMPERATURE,
                max_tokens=OPENAI_MAX_TOKENS,
            )
            
            # Extract response
            bot_reply = response.choices[0].message.content
            
            # Parse structured data from response if available
            parsed_data = self._parse_response(bot_reply)
            
            return {
                "success": True,
                "bot_reply": bot_reply,
                "parsed_data": parsed_data,
                "model": OPENAI_MODEL,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            return {
                "success": False,
                "error": str(e),
                "bot_reply": None
            }
    
    def detect_intent(self, message: str, language: str = "en") -> Dict[str, Any]:
        """
        Detect user intent using OpenAI
        
        Args:
            message: User's input message
            language: User's preferred language
            
        Returns:
            Dictionary with detected intent and confidence
        """
        if not self.is_enabled():
            return {
                "success": False,
                "intent": "general",
                "confidence": 0.0
            }
        
        try:
            system_prompt = f"""You are a healthcare intent classifier. Analyze the user's message and classify their intent.

Available intents:
- doctor: User wants to find a doctor or medical specialist
- medicine: User wants information about a medicine or medication
- lab: User wants information about laboratory tests or services
- appointment: User wants to book an appointment
- greeting: User is greeting or saying hello
- goodbye: User is saying goodbye or thanking
- help: User is asking for help or what the chatbot can do
- emergency: User describes a medical emergency
- general: User's intent is not clear or doesn't fit above categories

Return your response as JSON with the following format:
{{
    "intent": "detected_intent",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}

Language: {language}
"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                "intent": result.get("intent", "general"),
                "confidence": result.get("confidence", 0.5),
                "reasoning": result.get("reasoning", "")
            }
            
        except Exception as e:
            logger.error(f"Error detecting intent: {e}")
            return {
                "success": False,
                "intent": "general",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def extract_entities(self, message: str, language: str = "en") -> Dict[str, Any]:
        """
        Extract medical entities from user message using OpenAI
        
        Args:
            message: User's input message
            language: User's preferred language
            
        Returns:
            Dictionary with extracted entities
        """
        if not self.is_enabled():
            return {
                "success": False,
                "symptoms": [],
                "medications": [],
                "locations": [],
                "durations": []
            }
        
        try:
            system_prompt = f"""You are a medical entity extractor. Analyze the user's message and extract relevant medical information.

Extract the following entities:
- symptoms: Medical symptoms mentioned (e.g., fever, headache, cough)
- medications: Medicines mentioned or asked about
- locations: Locations mentioned (cities, areas)
- durations: Time durations mentioned (e.g., "2 days", "a week")

Return your response as JSON:
{{
    "symptoms": ["symptom1", "symptom2"],
    "medications": ["medicine1"],
    "locations": ["location1"],
    "durations": ["duration1"]
}}

Language: {language}
"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                "symptoms": result.get("symptoms", []),
                "medications": result.get("medications", []),
                "locations": result.get("locations", []),
                "durations": result.get("durations", [])
            }
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return {
                "success": False,
                "symptoms": [],
                "medications": [],
                "locations": [],
                "durations": [],
                "error": str(e)
            }
    
    def _build_system_prompt(self, language: str, context: Dict[str, Any] = None) -> str:
        """
        Build the system prompt for OpenAI
        
        Args:
            language: User's preferred language
            context: Additional context about the conversation
            
        Returns:
            Formatted system prompt
        """
        # Language-specific greetings
        language_greetings = {
            "en": "You are a friendly and helpful healthcare assistant.",
            "ur": "آپ ایک دوستانہ اور مددگار صحت کے معاون ہیں۔",
            "ps": "تاسو یو دوستانه روغنی مرسته کوونکی یاستئ."
        }
        
        base_prompt = language_greetings.get(language, language_greetings["en"])
        
        system_prompt = f"""{base_prompt}

Your role is to help patients with:
1. Finding doctors and medical specialists
2. Getting information about medicines and medications
3. Finding laboratory tests and diagnostic services
4. General health information and guidance

IMPORTANT RULES:
- Always prioritize patient safety
- Never provide specific medical diagnoses
- Always include a medical disclaimer when discussing medications
- Ask clarifying questions when needed
- Be empathetic and patient
- Provide accurate information based on the context provided

Context: {json.dumps(context) if context else '{}'}

Medical Disclaimer (include in responses about medicines):
{MEDICAL_DISCLAIMER}

Remember: Your responses should be natural and conversational, not robotic. Use the patient's language ({language}) when possible.

If you don't have specific information, acknowledge that and offer to help find relevant doctors or resources.
"""
        return system_prompt
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Try to parse structured data from the AI response
        
        Args:
            response: Raw AI response
            
        Returns:
            Parsed data if found, empty dict otherwise
        """
        try:
            # Try to find JSON in the response
            # Look for markdown code blocks
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
                return json.loads(json_str)
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
                return json.loads(json_str)
            
            # Try to find standalone JSON object
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
                
        except (json.JSONDecodeError, ValueError):
            pass
        
        return {}


# ==================== Helper Functions ====================

def get_openai_service(db_session: Session = None) -> OpenAIService:
    """
    Get an instance of the OpenAI service
    
    Args:
        db_session: Optional database session
        
    Returns:
        OpenAIService instance
    """
    return OpenAIService(db_session)


def generate_ai_response(
    message: str,
    conversation_history: List[Dict[str, str]] = None,
    language: str = "en",
    context: Dict[str, Any] = None,
    db_session: Session = None
) -> Dict[str, Any]:
    """
    Convenience function to generate an AI response
    
    Args:
        message: User's input message
        conversation_history: Previous messages
        language: User's language
        context: Additional context
        db_session: Database session
        
    Returns:
        Response dictionary
    """
    service = OpenAIService(db_session)
    return service.generate_response(message, conversation_history, language, context)


def detect_intent_ai(
    message: str,
    language: str = "en",
    db_session: Session = None
) -> Dict[str, Any]:
    """
    Convenience function to detect intent using AI
    
    Args:
        message: User's input message
        language: User's language
        db_session: Database session
        
    Returns:
        Intent detection result
    """
    service = OpenAIService(db_session)
    return service.detect_intent(message, language)


def extract_entities_ai(
    message: str,
    language: str = "en",
    db_session: Session = None
) -> Dict[str, Any]:
    """
    Convenience function to extract medical entities using AI
    
    Args:
        message: User's input message
        language: User's language
        db_session: Database session
        
    Returns:
        Extracted entities
    """
    service = OpenAIService(db_session)
    return service.extract_entities(message, language)
