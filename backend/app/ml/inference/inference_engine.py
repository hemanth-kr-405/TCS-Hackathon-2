"""
ML Inference Engine — loads saved joblib models and provides prediction APIs.
FastAPI uses this singleton. Models are NEVER retrained during inference.
"""
import os
import re
import json
import joblib
import numpy as np
from typing import Dict, Any, Optional

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "models")

_ASPECT_KEYWORDS = {
    "Delivery Speed & Packaging": [
        "delivery", "shipping", "courier", "package", "arrived", "late",
        "fast", "box", "damaged", "parcel", "transit",
    ],
    "Product Quality & Build": [
        "quality", "durable", "broken", "flimsy", "material", "works",
        "stopped", "battery", "design", "build", "defective", "cheap",
    ],
    "Customer Support Service": [
        "support", "agent", "service", "customer service", "help",
        "staff", "rude", "polite", "representative", "team",
    ],
    "Pricing & Value": [
        "price", "cost", "value", "expensive", "cheap", "worth",
        "discount", "money", "charge", "fee", "billing",
    ],
    "Refunds & Exchanges": [
        "refund", "return", "exchange", "money back", "cancelled",
        "charged", "billing", "credit",
    ],
    "Usability & Features": [
        "app", "website", "manual", "setup", "instructions", "easy",
        "hard", "bug", "crash", "interface",
    ],
}


from app.ml.text_cleaner import clean_customer_text

preprocess_text = clean_customer_text



def _extract_aspect(text: str) -> str:
    lower = preprocess_text(text)
    for aspect, kws in _ASPECT_KEYWORDS.items():
        if any(kw in lower for kw in kws):
            return aspect
    return "General Experience"


class InferenceEngine:
    """
    Loads pre-trained TF-IDF + Logistic Regression pipelines from disk.
    Raises RuntimeError if models are not found — run train_pipeline.py first.
    """

    def __init__(self):
        self._sentiment_pipe = None
        self._intent_pipe = None
        self._emotion_pipe = None
        self._metadata: Dict[str, Any] = {}
        self._loaded = False

    def load(self) -> bool:
        """Load all saved model pipelines. Returns True on success."""
        sent_path = os.path.join(MODELS_DIR, "sentiment_pipeline.joblib")
        int_path  = os.path.join(MODELS_DIR, "intent_pipeline.joblib")
        emo_path  = os.path.join(MODELS_DIR, "emotion_pipeline.joblib")
        meta_path = os.path.join(MODELS_DIR, "model_metadata.json")

        missing = [p for p in [sent_path, int_path, emo_path] if not os.path.exists(p)]
        if missing:
            print(f"[ml] WARNING: Model files not found: {missing}")
            print("[ml] Run: cd backend && python -m app.ml.training.train_pipeline")
            return False

        self._sentiment_pipe = joblib.load(sent_path)
        self._intent_pipe    = joblib.load(int_path)
        self._emotion_pipe   = joblib.load(emo_path)

        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                self._metadata = json.load(f)

        self._loaded = True
        print(f"[ml] Models loaded from {os.path.abspath(MODELS_DIR)}/")
        return True

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Run sentiment, intent, emotion and aspect inference on text.

        Returns dict matching SentimentAnalyzeResponse schema.
        """
        if not self._loaded:
            raise RuntimeError("Models not loaded. Run train_pipeline.py first.")

        if not text or not text.strip():
            return {
                "text": text,
                "sentiment": "Neutral",
                "sentiment_score": 0.0,
                "confidence": 1.0,
                "intent": "General Inquiry",
                "emotion": "Neutral",
                "aspect": "General Experience",
                "probabilities": {"Positive": 0.33, "Neutral": 0.34, "Negative": 0.33},
            }

        # Sentiment
        probs = self._sentiment_pipe.predict_proba([text])[0]
        classes = self._sentiment_pipe.classes_
        prob_dict = {cls: round(float(p), 4) for cls, p in zip(classes, probs)}
        sentiment = str(self._sentiment_pipe.predict([text])[0])
        confidence = round(float(np.max(probs)), 4)
        pos = prob_dict.get("Positive", 0.0)
        neg = prob_dict.get("Negative", 0.0)
        sentiment_score = round(pos - neg, 4)

        # Domain Sentiment Safety Rule Override for explicit retail complaints
        clean_text = preprocess_text(text)
        strong_neg_kws = ["late", "delayed", "hasn't arrived", "hasnt arrived", "broken", "damaged", "charged twice", "never arrived", "terrible", "horrible", "worst", "unacceptable", "refund"]
        strong_pos_kws = ["fits perfectly", "super fast", "love it", "excellent", "amazing", "wonderful", "great service", "perfect"]

        if any(kw in clean_text for kw in strong_neg_kws) and not any(kw in clean_text for kw in strong_pos_kws):
            sentiment = "Negative"
            if sentiment_score >= 0:
                sentiment_score = -0.68

        if any(kw in clean_text for kw in strong_pos_kws) and not any(kw in clean_text for kw in strong_neg_kws):
            sentiment = "Positive"
            if sentiment_score <= 0:
                sentiment_score = 0.85

        # Intent
        intent = str(self._intent_pipe.predict([text])[0])
        if "tracking" in clean_text or "late" in clean_text or "order #" in clean_text:
            intent = "Order Tracking"

        # Emotion
        emotion = str(self._emotion_pipe.predict([text])[0])
        if sentiment == "Negative" and emotion not in ("Frustration", "Anger", "Disappointment"):
            emotion = "Frustration"

        # Aspect (hybrid rule + ML)
        aspect = _extract_aspect(text)

        return {
            "text": text,
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "confidence": confidence,
            "intent": intent,
            "emotion": emotion,
            "aspect": aspect,
            "probabilities": prob_dict,
        }

    def predict_sentiment(self, text: str) -> Dict[str, Any]:
        """Convenience method returning full prediction dict for sentiment analysis."""
        return self.predict(text)

    def predict_intent(self, text: str) -> str:
        """Convenience method returning predicted intent label string."""
        return self.predict(text).get("intent", "General Inquiry")

    def predict_emotion(self, text: str) -> str:
        """Convenience method returning predicted emotion label string."""
        return self.predict(text).get("emotion", "Neutral")

    def get_status(self) -> Dict[str, Any]:
        return {
            "loaded": self._loaded,
            "model_name": self._metadata.get("model_name", "N/A"),
            "version": self._metadata.get("version", "N/A"),
            "trained_at": self._metadata.get("trained_at", "N/A"),
            "training_samples": self._metadata.get("training_samples", 0),
            "test_samples": self._metadata.get("test_samples", 0),
            "sentiment_accuracy": (
                self._metadata.get("sentiment", {}).get("accuracy", None)
            ),
        }


# ─── Singleton ────────────────────────────────────────────────────────────────
inference_engine = InferenceEngine()
