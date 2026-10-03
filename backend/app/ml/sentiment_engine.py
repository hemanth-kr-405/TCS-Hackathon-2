import re
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from app.ml.dataset_generator import generate_retail_dataset

def preprocess_text(text: str) -> str:
    """Clean and normalize raw customer feedback text."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s!?,.]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

class SentimentEngine:
    def __init__(self):
        self.is_trained = False
        
        # Scikit-Learn Pipelines
        self.sentiment_pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=3500, preprocessor=preprocess_text)),
            ('clf', LogisticRegression(C=2.0, max_iter=500, random_state=42))
        ])
        
        self.intent_pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=3500, preprocessor=preprocess_text)),
            ('clf', LogisticRegression(C=1.5, max_iter=500, random_state=42))
        ])

        self.emotion_pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=3500, preprocessor=preprocess_text)),
            ('clf', LogisticRegression(C=1.5, max_iter=500, random_state=42))
        ])

        self.last_train_metrics = {}

    def train(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        """Train sentiment, intent, and emotion pipelines on retail feedback dataset."""
        if df is None or len(df) == 0:
            df = generate_retail_dataset(600)

        X = df['text']
        y_sentiment = df['sentiment']
        y_intent = df['intent']
        y_emotion = df['emotion']

        # Train Sentiment Classifier
        self.sentiment_pipeline.fit(X, y_sentiment)
        
        # Train Intent Classifier
        self.intent_pipeline.fit(X, y_intent)

        # Train Emotion Classifier
        self.emotion_pipeline.fit(X, y_emotion)

        self.is_trained = True
        return {"samples": len(df), "status": "trained"}

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Predict sentiment, sentiment score (-1 to 1), confidence, intent, emotion, and aspect.
        """
        if not self.is_trained:
            self.train()

        clean = preprocess_text(text)
        if not clean:
            return {
                "text": text,
                "sentiment": "Neutral",
                "sentiment_score": 0.0,
                "confidence": 1.0,
                "intent": "General Inquiry",
                "emotion": "Neutral",
                "aspect": "General",
                "probabilities": {"Positive": 0.33, "Neutral": 0.34, "Negative": 0.33}
            }

        # Predict Sentiment
        probs = self.sentiment_pipeline.predict_proba([text])[0]
        classes = self.sentiment_pipeline.classes_
        prob_dict = {cls: float(round(prob, 4)) for cls, prob in zip(classes, probs)}
        
        predicted_sentiment = str(self.sentiment_pipeline.predict([text])[0])
        confidence = float(round(np.max(probs), 4))

        # Calculate continuous score between -1.0 and +1.0
        pos_prob = prob_dict.get("Positive", 0.0)
        neg_prob = prob_dict.get("Negative", 0.0)
        sentiment_score = round(pos_prob - neg_prob, 2)

        # Predict Intent
        intent = str(self.intent_pipeline.predict([text])[0])

        # Predict Emotion
        emotion = str(self.emotion_pipeline.predict([text])[0])

        # Extract Aspect based on keywords & text analysis
        aspect = self._extract_aspect(clean)

        return {
            "text": text,
            "sentiment": predicted_sentiment,
            "sentiment_score": sentiment_score,
            "confidence": confidence,
            "intent": intent,
            "emotion": emotion,
            "aspect": aspect,
            "probabilities": prob_dict
        }

    def _extract_aspect(self, text: str) -> str:
        """Rule & keyword based aspect extractor as fallback/enhancement."""
        keywords = {
            "Delivery Speed & Packaging": ["delivery", "shipping", "courier", "package", "arrived", "late", "fast", "box", "damaged"],
            "Product Quality & Build": ["quality", "durable", "broken", "flimsy", "material", "works", "stopped", "battery", "design"],
            "Customer Support Service": ["support", "agent", "service", "customer service", "help", "staff", "rude", "polite"],
            "Pricing & Value": ["price", "cost", "value", "expensive", "cheap", "worth", "discount", "money"],
            "Refunds & Exchanges": ["refund", "return", "exchange", "money back", "cancelled", "charged", "billing"],
            "Usability & Features": ["app", "website", "manual", "setup", "instructions", "easy", "hard", "bug", "crash"]
        }

        for aspect_name, kw_list in keywords.items():
            if any(kw in text for kw in kw_list):
                return aspect_name

        return "General Experience"

# Global ML Engine Instance
ml_engine = SentimentEngine()
