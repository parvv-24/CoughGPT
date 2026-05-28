"""
ML Engine — loads FastText + sklearn models, provides prediction functions.
Models loaded once at startup via FastAPI lifespan.
"""

import os
import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
import joblib
from gensim.models.fasttext import FastText
from huggingface_hub import snapshot_download 

logger = logging.getLogger(__name__)

@dataclass
class MLModels:
    """Container for all loaded ML models and data."""
    symptom_model: object
    symptom_le: object
    symptom_ft: object
    drug_model: object
    drug_le: object
    drug_ft: object
    train_df: pd.DataFrame

_models: Optional[MLModels] = None

def load_models() -> MLModels:
    """Load all ML models from disk. Call once at startup."""
    global _models

    logger.info("Downloading ML models from Hugging Face...")
    
    MODELS_DIR = snapshot_download(
        repo_id="parvv-24/CoughGPT-Models", 
        token=os.getenv("HF_TOKEN")         
    )

    logger.info("Loading ML models from %s ...", MODELS_DIR)

    symptom_model = joblib.load(os.path.join(MODELS_DIR, "disease_classifier.pkl"))
    symptom_le = joblib.load(os.path.join(MODELS_DIR, "symptom_label_encoder.pkl"))
    symptom_ft = FastText.load(os.path.join(MODELS_DIR, "fasttext_symptom.model"))

    drug_model = joblib.load(os.path.join(MODELS_DIR, "condition_classifier.pkl"))
    drug_le = joblib.load(os.path.join(MODELS_DIR, "condition_label_encoder.pkl"))
    drug_ft = FastText.load(os.path.join(MODELS_DIR, "fasttext_drug_review.model"))

    train_df = pd.read_csv(os.path.join(MODELS_DIR, "drugsComTrain_raw.csv"))

    _models = MLModels(
        symptom_model=symptom_model,
        symptom_le=symptom_le,
        symptom_ft=symptom_ft,
        drug_model=drug_model,
        drug_le=drug_le,
        drug_ft=drug_ft,
        train_df=train_df,
    )

    logger.info("All ML models loaded successfully.")
    return _models

def get_models() -> MLModels:
    """Get loaded models. Raises if not loaded."""
    if _models is None:
        raise RuntimeError("ML models not loaded. Call load_models() first.")
    return _models


def are_models_loaded() -> bool:
    """Check if models have been loaded."""
    return _models is not None


def predict_disease(symptoms: str) -> str:
    """
    Predict disease from comma-separated symptom string.
    Returns disease name or 'Unknown'.
    """
    models = get_models()
    words = symptoms.lower().split(",")
    vecs = [models.symptom_ft.wv[w.strip()] for w in words if w.strip() in models.symptom_ft.wv]

    if not vecs:
        return "Unknown"

    avg_vec = np.mean(vecs, axis=0)
    pred = models.symptom_model.predict([avg_vec])
    return models.symptom_le.inverse_transform(pred)[0]


def predict_drugs(condition: str) -> list[str]:
    """
    Predict top 5 drugs for a condition.
    Returns list of drug names.
    """
    models = get_models()
    words = condition.lower().split()
    vecs = [models.drug_ft.wv[w] for w in words if w in models.drug_ft.wv]

    if not vecs:
        return []

    avg_vec = np.mean(vecs, axis=0)
    pred = models.drug_model.predict([avg_vec])
    predicted = models.drug_le.inverse_transform(pred)[0]

    df = models.train_df[models.train_df["condition"].str.lower() == predicted.lower()]
    drugs = df["drugName"].value_counts().head(5).index.tolist()

    return drugs
