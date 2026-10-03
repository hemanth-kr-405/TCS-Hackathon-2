"""Model evaluation and status router."""
import os
import json
from fastapi import APIRouter, HTTPException
from app.ml.inference.inference_engine import inference_engine

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "models")

router = APIRouter(prefix="/model", tags=["Model Evaluation"])


@router.get("/status", summary="Model loading status")
def model_status():
    """Returns whether models are loaded and basic metadata."""
    return inference_engine.get_status()


@router.get("/evaluation", summary="Full model evaluation metrics")
def model_evaluation():
    """Returns actual evaluation metrics from training run (never hardcoded)."""
    meta_path = os.path.join(MODELS_DIR, "model_metadata.json")
    if not os.path.exists(meta_path):
        raise HTTPException(
            status_code=503,
            detail=(
                "Model metadata not found. "
                "Run: cd backend && python -m app.ml.training.train_pipeline"
            ),
        )
    with open(meta_path, "r") as f:
        metadata = json.load(f)

    sentiment = metadata.get("sentiment", {})
    intent    = metadata.get("intent", {})
    emotion   = metadata.get("emotion", {})

    return {
        "model_name": metadata.get("model_name", "TF-IDF + Logistic Regression"),
        "version": metadata.get("version", "1.0.0"),
        "trained_at": metadata.get("trained_at", "N/A"),
        "training_samples": metadata.get("training_samples", 0),
        "test_samples": metadata.get("test_samples", 0),
        "total_samples": metadata.get("total_samples", 0),
        "sentiment": {
            "accuracy": sentiment.get("accuracy"),
            "precision_macro": sentiment.get("precision_macro"),
            "recall_macro": sentiment.get("recall_macro"),
            "f1_macro": sentiment.get("f1_macro"),
            "confusion_matrix": sentiment.get("confusion_matrix"),
            "labels": sentiment.get("labels"),
            "classification_report": sentiment.get("classification_report"),
        },
        "intent": {
            "accuracy": intent.get("accuracy"),
            "f1_macro": intent.get("f1_macro"),
            "labels": intent.get("labels"),
        },
        "emotion": {
            "accuracy": emotion.get("accuracy"),
            "f1_macro": emotion.get("f1_macro"),
            "labels": emotion.get("labels"),
        },
    }


@router.get("/recommendations", summary="Business recommendations")
def get_recommendations():
    from app.database import SessionLocal
    from app.models.db_models import BusinessRecommendation
    db = SessionLocal()
    try:
        recs = db.query(BusinessRecommendation).order_by(
            BusinessRecommendation.created_at.desc()
        ).all()
        return [
            {
                "id": r.id,
                "title": r.title,
                "category": r.category,
                "description": r.description,
                "priority": r.priority,
                "evidence": r.evidence,
                "estimated_impact": r.estimated_impact,
                "status": r.status,
            }
            for r in recs
        ]
    finally:
        db.close()
