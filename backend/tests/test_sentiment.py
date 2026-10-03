import pytest
from app.ml.sentiment_engine import SentimentEngine, preprocess_text

def test_preprocess_text():
    raw = "  Great product!!! Fast delivery & 100% recommended.  "
    clean = preprocess_text(raw)
    assert "great product" in clean
    assert "fast delivery" in clean

def test_sentiment_engine_prediction():
    engine = SentimentEngine()
    engine.train()

    pos_res = engine.predict("I absolutely love this product! Amazing quality and fast delivery.")
    assert pos_res["sentiment"] in ["Positive", "Neutral"]
    assert pos_res["sentiment_score"] > 0.0

    neg_res = engine.predict("Terrible customer service. Product broke after one day and refund was denied.")
    assert neg_res["sentiment"] in ["Negative", "Neutral"]
    assert neg_res["sentiment_score"] < 0.2
