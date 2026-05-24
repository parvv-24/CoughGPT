"""
Pydantic request/response schemas for CoughGPT API.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ---------- Requests ----------

class AnalyzeRequest(BaseModel):
    """Full analysis request — symptoms or condition text."""
    user_input: str = Field(..., min_length=1, max_length=2000, description="Symptoms (comma-separated) or condition name")


class PredictDiseaseRequest(BaseModel):
    symptoms: str = Field(..., min_length=1, max_length=2000)


class PredictDrugsRequest(BaseModel):
    condition: str = Field(..., min_length=1, max_length=500)


class ExplainRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    source: str = Field(..., min_length=2, max_length=5, description="Source language code")
    target: str = Field(..., min_length=2, max_length=5, description="Target language code")


class DetectLanguageRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)


# ---------- Responses ----------

class HealthResponse(BaseModel):
    status: str
    models_loaded: bool


class PredictDiseaseResponse(BaseModel):
    disease: str
    drugs: list[str]


class PredictDrugsResponse(BaseModel):
    drugs: list[str]


class ExplainResponse(BaseModel):
    explanation: str


class TranslateResponse(BaseModel):
    translated: str


class DetectLanguageResponse(BaseModel):
    language: str
    code: str


class AnalyzeResponse(BaseModel):
    """Full analysis result from orchestrator endpoint."""
    detected_language: str
    language_code: str
    original_input: str
    english_input: str
    input_type: str  # "symptoms" or "condition"
    disease: Optional[str] = None
    disease_translated: Optional[str] = None
    drugs: list[str] = []
    explanation: str = ""
    explanation_translated: str = ""
