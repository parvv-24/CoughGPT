"""
CoughGPT FastAPI Backend
========================
API server for disease prediction, drug recommendation, and AI explanations.
Loads ML models at startup via lifespan. All POST endpoints require X-API-Key auth.

Run: uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
"""

import sys
import os
import logging
from contextlib import asynccontextmanager

# Allow running `uvicorn main:app` from inside the backend/ folder
# by adding the project root to the Python path.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from backend.auth import verify_api_key
from backend.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    PredictDiseaseRequest,
    PredictDiseaseResponse,
    PredictDrugsRequest,
    PredictDrugsResponse,
    ExplainRequest,
    ExplainResponse,
    TranslateRequest,
    TranslateResponse,
    DetectLanguageRequest,
    DetectLanguageResponse,
    HealthResponse,
)
from backend.ml_engine import load_models, are_models_loaded, predict_disease, predict_drugs
from backend.services.translator import (
    detect_language,
    translate_to_english,
    translate_from_english,
)
from backend.services.gemini import gemini_explain

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ---------- Lifespan (load models at startup) ----------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load ML models once on startup, cleanup on shutdown."""
    logger.info("Starting CoughGPT backend — loading models...")
    load_models()
    logger.info("Models loaded. Server ready.")
    yield
    logger.info("Shutting down CoughGPT backend.")


# ---------- FastAPI App ----------

app = FastAPI(
    title="CoughGPT API",
    description="AI-powered health analysis — disease prediction, drug recommendation, medical explanations.",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — allow Streamlit frontend (localhost:8501)
# TODO(security): Restrict origins to actual deployment domain in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8501", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key", "Content-Type"],
)


# ---------- Security Headers Middleware ----------

@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Cache-Control"] = "no-store"
    # TODO(security): Add strict CSP header for production deployment
    return response


# ---------- Health Endpoint (public) ----------

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check — no auth required."""
    return HealthResponse(
        status="ok",
        models_loaded=are_models_loaded(),
    )


# ---------- Protected Endpoints ----------

@app.post("/api/detect-language", response_model=DetectLanguageResponse)
async def api_detect_language(
    req: DetectLanguageRequest,
    _: str = Depends(verify_api_key),
):
    """Detect language of input text."""
    language, code = detect_language(req.text)
    return DetectLanguageResponse(language=language, code=code)


@app.post("/api/translate", response_model=TranslateResponse)
async def api_translate(
    req: TranslateRequest,
    _: str = Depends(verify_api_key),
):
    """Translate text between languages."""
    if req.target == "en":
        result = translate_to_english(req.text, req.source)
    else:
        result = translate_from_english(req.text, req.target)
    return TranslateResponse(translated=result)


@app.post("/api/predict-disease", response_model=PredictDiseaseResponse)
async def api_predict_disease(
    req: PredictDiseaseRequest,
    _: str = Depends(verify_api_key),
):
    """Predict disease from symptoms + recommend drugs."""
    disease = predict_disease(req.symptoms)
    drugs = predict_drugs(disease)
    return PredictDiseaseResponse(disease=disease, drugs=drugs)


@app.post("/api/predict-drugs", response_model=PredictDrugsResponse)
async def api_predict_drugs(
    req: PredictDrugsRequest,
    _: str = Depends(verify_api_key),
):
    """Predict drug recommendations for a condition."""
    drugs = predict_drugs(req.condition)
    return PredictDrugsResponse(drugs=drugs)


@app.post("/api/explain", response_model=ExplainResponse)
async def api_explain(
    req: ExplainRequest,
    _: str = Depends(verify_api_key),
):
    """Generate AI medical explanation via Gemini."""
    explanation = gemini_explain(req.text)
    return ExplainResponse(explanation=explanation)


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def api_analyze(
    req: AnalyzeRequest,
    _: str = Depends(verify_api_key),
):
    """
    Full analysis pipeline:
    1. Detect language
    2. Translate to English (if needed)
    3. Predict disease/drugs OR just drugs
    4. Generate Gemini explanation
    5. Translate results back (if needed)
    """
    user_input = req.user_input

    # Step 1: Detect language
    detected_language, lang_code = detect_language(user_input)

    # Step 2: Translate to English if needed
    if lang_code != "en":
        english_input = translate_to_english(user_input, lang_code)
    else:
        english_input = user_input

    # Step 3: Determine input type and predict
    if "," in english_input:
        # Symptoms — predict disease then drugs
        input_type = "symptoms"
        disease = predict_disease(english_input)
        drugs = predict_drugs(disease)
        disease_translated = translate_from_english(disease, lang_code) if lang_code != "en" else disease
        explain_target = disease
    else:
        # Condition — predict drugs directly
        input_type = "condition"
        disease = None
        disease_translated = None
        drugs = predict_drugs(english_input)
        explain_target = english_input

    # Step 4: Gemini explanation
    explanation_en = gemini_explain(explain_target)

    # Step 5: Translate explanation back if needed
    if lang_code != "en":
        explanation_translated = translate_from_english(explanation_en, lang_code)
    else:
        explanation_translated = explanation_en

    return AnalyzeResponse(
        detected_language=detected_language,
        language_code=lang_code,
        original_input=user_input,
        english_input=english_input,
        input_type=input_type,
        disease=disease,
        disease_translated=disease_translated,
        drugs=drugs,
        explanation=explanation_en,
        explanation_translated=explanation_translated,
    )
