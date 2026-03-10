"""
Internationalization (i18n) Module for ADMA Healthcare Chatbot
Supports: English (en), Urdu (ur), Pashto (ps)

This module provides multilingual responses for the chatbot
"""

# Language codes
LANGUAGES = {
    "en": "English",
    "ur": "Urdu",
    "ps": "Pashto"
}

# Default language
DEFAULT_LANGUAGE = "en"


class Internationalization:
    """
    Class to handle multilingual responses
    """
    
    def __init__(self, language: str = "en"):
        """
        Initialize with a language code
        
        Args:
            language: Language code (en, ur, ps)
        """
        self.language = language if language in LANGUAGES else DEFAULT_LANGUAGE
    
    def get(self, key: str, default: str = None) -> str:
        """
        Get translation for a key
        
        Args:
            key: Translation key
            default: Default message if key not found
            
        Returns:
            Translated string
        """
        translations = TRANSLATIONS.get(self.language, TRANSLATIONS[DEFAULT_LANGUAGE])
        return translations.get(key, default or key)
    
    def set_language(self, language: str):
        """
        Set the current language
        
        Args:
            language: Language code
        """
        if language in LANGUAGES:
            self.language = language


# All translation strings
# Structure: {language_code: {key: translation}}
TRANSLATIONS = {
    # ============ ENGLISH ============
    "en": {
        # Greetings
        "greeting": "Hi! I'm your ADMA healthcare assistant. How can I help you today?",
        "greeting_alt": "Hello! Welcome to ADMA Health. What can I assist you with?",
        
        # Help options
        "help_options": "I can help you with:\n• Finding a doctor\n• Medicine information\n• Laboratory tests\n• Booking appointments\n\nWhat would you like?",
        "help_options_simple": "I can help you find doctors, medicines, or labs. What do you need?",
        
        # Symptoms inquiry
        "ask_symptoms": "What symptoms are you experiencing? Please describe in your own words.",
        "ask_symptoms_alt": "Can you tell me what problem you're having?",
        
        # Location inquiry
        "ask_location": "What is your location or city?",
        "ask_location_alt": "Where are you located?",
        "ask_location_gps": "Would you like to share your location for nearby doctors?",
        
        # Doctor related
        "finding_doctors": "Let me find the best specialists for your symptoms near {location}...",
        "doctors_found": "I found {count} doctors who can help with your symptoms:",
        "no_doctors_found": "Sorry, I couldn't find any doctors in {location} for your symptoms. Would you like to try a different location?",
        "doctor_info": "Dr. {name}\n  Specialization: {specialization}\n  Location: {area}, {city}\n  Experience: {experience} years\n  Fee: Rs. {fee}\n  Available: {days} ({hours})\n  Rating: {rating}★",
        
        # Medicine related
        "medicine_info": "Medicine: {name}\n  Generic: {generic}\n  Used for: {used_for}\n  Dose: {dose}\n  Timing: {timing}\n  Side effects: {side_effects}\n  Precautions: {precautions}\n  Prescription: {prescription}",
        "medicine_not_found": "I couldn't find information about that medicine. Please consult a doctor.",
        "medicine_disclaimer": "⚠️ Please note: This is only informational. Always consult a doctor before taking any medicine.",
        
        # Lab related
        "finding_labs": "Let me find laboratories in {location}...",
        "labs_found": "I found {count} laboratories near you:",
        "no_labs_found": "Sorry, I couldn't find any labs in {location}.",
        "lab_info": "Lab: {name}\n  Location: {area}, {city}\n  Tests: {tests}\n  Home Sample: {home}\n  Hours: {hours}\n  Rating: {rating}★",
        
        # Appointment booking
        "book_appointment": "Would you like to book an appointment with Dr. {name}?",
        "appointment_details": "Please provide:\n• Your name\n• Preferred date\n• Preferred time",
        "appointment_confirmed": "✅ Appointment Confirmed!\n\nDoctor: Dr. {name}\nDate: {date}\nTime: {time}\nPatient: {patient}\n\nYou will receive a confirmation SMS shortly.",
        "appointment_pending": "Your appointment request has been submitted. We will confirm shortly.",
        
        # Directions
        "get_directions": "📍 Get directions to {name}:\n{address}\n\nPhone: {phone}",
        
        # General responses
        "thank_you": "Thank you! Is there anything else I can help you with?",
        "goodbye": "Thank you for using ADMA Health. Take care! 🌟",
        "sorry": "I didn't understand that. Can you please rephrase?",
        "sorry_alt": "Sorry, I can help you find doctors, medicines information, or laboratories. What do you need?",
        
        # Duration related
        "ask_duration": "How long have you had these symptoms? (e.g., 2 days, 1 week)",
        
        # Language selection
        "select_language": "Please select your preferred language:\n1. English\n2. اردو (Urdu)\n3. پښتو (Pashto)",
        "language_changed": "Language changed to {language}. How can I help you?",
        
        # Medical disclaimer
        "medical_disclaimer": "⚠️ Please note: This chatbot provides general information only. Always consult a qualified healthcare professional for medical advice, diagnosis, or treatment.",
        
        # Error messages
        "error_generic": "Something went wrong. Please try again.",
        "error_database": "Database error. Please try again later.",
        
        # Confirmation prompts
        "confirm_yes": "Yes",
        "confirm_no": "No",
        "confirm_more_info": "Would you like more information?",
        
        # Urgency messages
        "emergency_warning": "⚠️ If you are experiencing a medical emergency, please call emergency services immediately!",
    },
    
    # ============ URDU ============
    "ur": {
        # Greetings
        "greeting": "السلام علیکم! میں آپ کا ADMA صحت معاون ہوں۔ آج میں آپ کی کیسے مدد کر سکتا ہوں؟",
        "greeting_alt": "ہیلو! ADMA Health میں خوش آمدید۔ میں آپ کی کیسے مدد کر سکتا ہوں؟",
        
        # Help options
        "help_options": "میں آپ کی مدد کر سکتا ہوں:\n• ڈاکٹر تلاش کرنے میں\n• ادویات کی معلومات\n• لیباریٹری ٹیسٹ\n• اپائنٹمنٹ بک کرنے میں\n\nآپ کو کیا چاہیے؟",
        "help_options_simple": "میں ڈاکٹر، ادویات، یا لیب تلاش کر سکتا ہوں۔ آپ کو کیا چاہیے؟",
        
        # Symptoms inquiry
        "ask_symptoms": "آپ کو کیا علامات ہیں؟ براہ کرم اپنے الفاظ میں بیان کریں۔",
        "ask_symptoms_alt": "کیا آپ بتا سکتے ہیں کہ آپ کا کیا مسئلہ ہے؟",
        
        # Location inquiry
        "ask_location": "آپ کا مقام یا شہر کیا ہے؟",
        "ask_location_alt": "آپ کہاں واقع ہیں؟",
        "ask_location_gps": "کیا آپ اپنے قریبی ڈاکٹروں کے لیے اپنا مقام شیئر کرنا چاہیں گے؟",
        
        # Doctor related
        "finding_doctors": "میں آپ کی علامات کے لیے {location} میں بہترین ماہرین تلاش کر رہا ہوں...",
        "doctors_found": "میں نے {count} ڈاکٹر تلاش کیے جو آپ کی مدد کر سکتے ہیں:",
        "no_doctors_found": "معذرت، میں آپ کی علامات کے لیے {location} میں کوئی ڈاکٹر نہیں مل سکا۔ کیا آپ دوسرا مقام آزمانا چاہیں گے؟",
        "doctor_info": "ڈاکٹر {name}\n  تخصص: {specialization}\n  مقام: {area}, {city}\n  تجربہ: {experience} سال\n  فیس: روپے {fee}\n  دستیاب: {days} ({hours})\n  ریٹنگ: {rating}★",
        
        # Medicine related
        "medicine_info": "دوا: {name}\n  جنریک: {generic}\n  استمال: {used_for}\n  خوراک: {dose}\n  وقت: {timing}\n  ضمنی اثرات: {side_effects}\n  احتیاط: {precautions}\n  نسخہ: {prescription}",
        "medicine_not_found": "میں اس دوا کی معلومات نہیں مل سکی۔ براہ کرم ڈاکٹر سے مشورہ کریں۔",
        "medicine_disclaimer": "⚠️ براہ کرم نوٹ کریں: یہ صرف معلوماتی ہے۔ ہمیشہ کسی ڈاکٹر سے مشورہ کریں۔",
        
        # Lab related
        "finding_labs": "میں {location} میں لیباریٹری تلاش کر رہا ہوں...",
        "labs_found": "میں نے آپ کے قریب {count} لیباریٹری تلاش کیے:",
        "no_labs_found": "معذرت، میں {location} میں کوئی لیب نہیں مل سکا۔",
        "lab_info": "لیب: {name}\n  مقام: {area}, {city}\n  ٹیسٹ: {tests}\n  گھر سے نمونہ: {home}\n  اوقات: {hours}\n  ریٹنگ: {rating}★",
        
        # Appointment booking
        "book_appointment": "کیا آپ ڈاکٹر {name} سے اپائنٹمنٹ بک کرنا چاہیں گے؟",
        "appointment_details": "براہ کرم فراہم کریں:\n• آپ کا نام\n• پسندیدہ تاریخ\n• پسندیدہ وقت",
        "appointment_confirmed": "✅ اپائنٹمنٹ تصدیق ہو گیا!\n\nڈاکٹر: ڈاکٹر {name}\nتاریخ: {date}\nوقت: {time}\nمریض: {patient}\n\nآپ کو جلدی تصدیقی ایس ایم ایس ملے گا۔",
        "appointment_pending": "آپ کی اپائنٹمنٹ کی درخواست جمع کر دی گئی ہے۔ ہم جلدی تصدیق کریں گے۔",
        
        # Directions
        "get_directions": "📍 {name} کی سمتیں حاصل کریں:\n{address}\n\nفون: {phone}",
        
        # General responses
        "thank_you": "شکریہ! کیا کوئی اور چیز ہے جس میں آپ کی مدد کر سکوں؟",
        "goodbye": "ADMA Health کا استعال کرنے کا شکریہ۔ خوش رہیں! 🌟",
        "sorry": "میں نے سمجھا نہیں۔ کیا آپ دوبارہ بیان کر سکتے ہیں؟",
        "sorry_alt": "معذرت، میں ڈاکٹر، ادویات، یا لیب کی معلومات دے سکتا ہوں۔ آپ کو کیا چاہیے؟",
        
        # Duration related
        "ask_duration": "آپ کو یہ علامات کب سے ہیں؟ (مثلاً 2 دن، 1 ہفتہ)",
        
        # Language selection
        "select_language": "براہ کرم اپنی پسندیدہ زبان انتخاب کریں:\n1. English\n2. اردو (Urdu)\n3. پښتو (Pashto)",
        "language_changed": "زبان {language} میں تبدیل ہو گئی۔ میں آپ کی کیسے مدد کر سکتا ہوں؟",
        
        # Medical disclaimer
        "medical_disclaimer": "⚠️ براہ کرم نوٹ کریں: یہ چیٹ بوٹ صرف عام معلومات فراہم کرتا ہے۔ طبی مشورے، تشخیص یا علاج کے لیے ہمیشہ کسی قابل ڈاکٹر سے رجوع کریں۔",
        
        # Error messages
        "error_generic": "کچھ غلط ہو گیا۔ براہ کرم دوبارہ کوشش کریں۔",
        "error_database": "ڈیٹابیس خرابی۔ براہ کرم دوبارہ کوشش کریں۔",
        
        # Confirmation prompts
        "confirm_yes": "جی ہاں",
        "confirm_no": "نہیں",
        "confirm_more_info": "کیا آپ مزید معلومات چاہیں گے؟",
        
        # Urgency messages
        "emergency_warning": "⚠️ اگر آپ کو طبی ایمرجنسی ہے، تو براہ کرم فوری طور پر ایمرجنسی سروسز کو کال کریں!",
    },
    
    # ============ PASHTO ============
    "ps": {
        # Greetings
        "greeting": "سلام! زه ستاسو د ADMA روغني مرستیال یم. نننۍ څنګه مرسته کولای شم؟",
        "greeting_alt": "هیلو! په ADMA Health کې ښه راغلاست. څنګه مرسته کولای شم؟",
        
        # Help options
        "help_options": "زه په لاندې څرګندونو کې مرسته کولای شم:\n• د ډاکټر پیدا کول\n• د دریو معلومات\n• معمولي ازمېښت\n• اپائنټمنټ کول\n\nتاسو ته څه اړتیا لري؟",
        "help_options_simple": "زه کولای شم ډاکټر، دریو، یا لیب پیدا کړم. تاسو ته څه اړتیا لري؟",
        
        # Symptoms inquiry
        "ask_symptoms": "تاسو کومې نښې لري؟ مهرباني وکړئ په خوښې سره بیان کړئ.",
        "ask_problems_alt": "ایا تاسو ویلای شئ چې تاسو کومه ستونزه لرئ؟",
        
        # Location inquiry
        "ask_location": "تاسو په کوم ځای یاست؟",
        "ask_location_alt": "تاسو کې یاست؟",
        "ask_location_gps": "ایا تاسو غواړئ خپل ځای د نږدې ډاکټرانو لپاره شریک کړئ؟",
        
        # Doctor related
        "finding_doctors": "زه د تاسو د نښو لپاره په {location} کې غوره متخصصین پیدا کوم...",
        "doctors_found": "زه {count} ډاکټران وموندل چې کولای شي تاسو سره مرسته وکړي:",
        "no_doctors_found": "بخښنه، زه په {location} کې د تاسو د نښو لپاره هیڅ ډاکټر ونه موند. ایا تاسو غواړئ بل ځای هڅوئ؟",
        "doctor_info": "ډاکټر {name}\n  تخصص: {specialization}\n  ځای: {area}, {city}\n  تجربه: {experience} کلونه\n  فیس: روپۍ {fee}\n  موجود: {days} ({hours})\n  ریټینګ: {rating}★",
        
        # Medicine related
        "medicine_info": "دری:{name}\n  عمومي نوم: {generic}\n  کارول: {used_for}\n  مقدار: {dose}\n  وخت: {timing}\n  عوارض: {side_effects}\n  احتیاط: {precautions}\n  نسخه: {prescription}",
        "medicine_not_found": "زه د دې دری معلومات ونه موندې. مهرباني وکړئ د ډاکټر سره مشوره وکړئ.",
        "medicine_disclaimer": "⚠️ مهرباني وکړئ توجه وکړئ: دا یوازې معلومات دی. تل د ډاکټر سره مشوره وکړئ.",
        
        # Lab related
        "finding_labs": "زه په {location} کې لیب پیدا کوم...",
        "labs_found": "زه تاسو ته {count} لیبونه وموندل:",
        "no_labs_found": "بخښنه، زه په {location} کې هیڅ لیب ونه موند.",
        "lab_info": "لیب: {name}\n  ځای: {area}, {city}\n  ازمېښتونه: {tests}\n  کور نمونه: {home}\n  ساعتونه: {hours}\n  ریټینګ: {rating}★",
        
        # Appointment booking
        "book_appointment": "ایا تاسو غواړئ د ډاکټر {name} سره اپائنټمنټ وکړئ؟",
        "appointment_details": "مهرباني وکړئ په لاندې ډول برابراۍ کړئ:\n• ستاسو نوم\n• غوښتلې نېټه\n• غوښتلې ساعت",
        "appointment_confirmed": "✅ اپائنټمنټ تایید شو!\n\nډاکټر: ډاکټر {name}\nنېټه: {date}\nساعت: {time}\nناروغ: {patient}\n\nتاسو به ډېر زر تصدیقی SMS ترلاسه کړئ.",
        "appointment_pending": "ستاسو اپائنټمنټ غوښتنه سپارل شوې ده. موږ به ډېر زر تایید کړو.",
        
        # Directions
        "get_directions": "📍 د {name} لارې ترلاسه کړئ:\n{address}\n\nتلفن: {phone}",
        
        # General responses
        "thank_you": "مننه! ایا هیڅ بل شی دی چې زه مرسته کولای شم؟",
        "goodbye": "د ADMA Health کارولو څخه مننه. ښه یاست! 🌟",
        "sorry": "زه پوه نشتم. ایا تاسو بیا بیان کولای شئ؟",
        "sorry_alt": "بخښنه، زه کولای شم ډاکټر، دریو، یا لیب معلومات ترلاسه کړم. تاسو ته څه اړتیا لري؟",
        
        # Duration related
        "ask_duration": "تاسو د دې نښو څخه څه وخت لرئ؟ (لکه ۲ ورځې، ۱ اونۍ)",
        
        # Language selection
        "select_language": "مهرباني وکړئ خپل غوره ژبه غوره کړئ:\n1. English\n2. اردو (Urdu)\n3. پښتو (Pashto)",
        "language_changed": "ژبه {language} بدله شوه. څنګه مرسته کولای شم؟",
        
        # Medical disclaimer
        "medical_disclaimer": "⚠️ مهرباني وکړئ توجه وکړئ: دا چیټ بوټ یوازې عام معلومات برابروي. تل د روغتیا متخصص سره مشوره وکړئ.",
        
        # Error messages
        "error_generic": "څه غلط شول. مهرباني وکړئ بیا هڅه وکړئ.",
        "error_database": "ډیټابیس خطا. مهرباني وکړئ بیا هڅه وکړئ.",
        
        # Confirmation prompts
        "confirm_yes": "هو",
        "confirm_no": "نه",
        "confirm_more_info": "ایا تاسو نور معلومات غواړئ؟",
        
        # Urgency messages
        "emergency_warning": "⚠️ که تاسو د روغتیا اورژنسي تجربه کوئ، مهرباني وکړئ د اورژنسي خدمت telefonate کړئ!",
    }
}


def get_translator(language: str = "en") -> Internationalization:
    """
    Get a translator instance for the specified language
    
    Args:
        language: Language code (en, ur, ps)
        
    Returns:
        Internationalization instance
    """
    return Internationalization(language)
