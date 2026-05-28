"""
Gemini AI explanation service.
Uses Google Generative AI (Gemini 2.5 Flash) for medical explanations.
"""

import os
import logging

from google import genai
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Configure Gemini with API key from environment
_api_key = os.getenv("GEMINI_API_KEY")
if not _api_key:
    logger.error("GEMINI_API_KEY not found in environment. Gemini will not work.")
    _client = None
else:
    _client = genai.Client(api_key=_api_key)

_gemini_model = "gemini-2.5-flash"


def gemini_explain(text: str) -> str:
    """
    Generate a medical explanation using Gemini.
    Returns explanation string or error message.
    """
    try:
        if _client is None:
            return "⚠️ AI explanation temporarily unavailable. Please try again."
        response = _client.models.generate_content(
            model=_gemini_model,
            contents=(
                f"Explain {text} medically in 4 concise, easy-to-understand "
                f"sentences for a general audience."
            ),
        )
        return response.text
    except Exception as e:
        logger.error("Gemini explanation failed: %s", str(e))
        return "⚠️ AI explanation temporarily unavailable. Please try again."
