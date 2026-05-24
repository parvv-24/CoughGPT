"""
Language detection and translation service.
Uses deep-translator (Google Translate) and langdetect.
"""

import logging

from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException

logger = logging.getLogger(__name__)

# Language code to name mapping — ONLY INDIAN LANGUAGES
LANGUAGE_NAMES: dict[str, str] = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "te": "Telugu",
    "mr": "Marathi",
    "ta": "Tamil",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "ur": "Urdu",
    "or": "Odia",
    "as": "Assamese",
    "ks": "Kashmiri",
    "sd": "Sindhi",
    "sa": "Sanskrit",
    "ne": "Nepali",
}


def detect_language(text: str) -> tuple[str, str]:
    """
    Detect language of input text — restricted to Indian languages.
    Returns (language_name, language_code). Defaults to English if unknown.
    """
    try:
        lang_code = detect(text)

        if lang_code not in LANGUAGE_NAMES:
            return "English", "en"

        language_name = LANGUAGE_NAMES.get(lang_code, "English")
        return language_name, lang_code
    except LangDetectException:
        return "English", "en"


def translate_to_english(text: str, source_lang_code: str) -> str:
    """Translate text to English. Returns original if already English or on failure."""
    if source_lang_code == "en":
        return text

    try:
        translated = GoogleTranslator(source=source_lang_code, target="en").translate(text)
        return translated
    except Exception as e:
        logger.warning("Translation to English failed: %s. Using original text.", str(e))
        return text


def translate_from_english(text: str, target_lang_code: str) -> str:
    """Translate text from English to target language. Returns original on failure."""
    if target_lang_code == "en":
        return text

    try:
        translated = GoogleTranslator(source="en", target=target_lang_code).translate(text)
        return translated
    except Exception as e:
        logger.warning("Translation from English failed: %s", str(e))
        return text
