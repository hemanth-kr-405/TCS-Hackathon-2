"""Sentiment analysis router."""
from fastapi import APIRouter, HTTPException
from app.schemas.schemas import (
    SentimentAnalyzeRequest, SentimentAnalyzeResponse,
    BatchAnalyzeRequest, BatchAnalyzeResponse,
)
from app.ml.inference.inference_engine import inference_engine

router = APIRouter(prefix="/sentiment", tags=["Sentiment Analysis"])


@router.post("/analyze", response_model=SentimentAnalyzeResponse, summary="Analyze single text")
def analyze_single(request: SentimentAnalyzeRequest):
    """Perform sentiment, intent, emotion and aspect analysis on a single text."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    if not inference_engine.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="ML models not loaded. Run the training pipeline first.",
        )
    return inference_engine.predict(request.text)


@router.post("/batch", response_model=BatchAnalyzeResponse, summary="Analyze batch of texts")
def analyze_batch(request: BatchAnalyzeRequest):
    """Batch sentiment analysis for up to 100 items."""
    if not request.items:
        raise HTTPException(status_code=400, detail="Items list cannot be empty.")
    if len(request.items) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 items per batch.")
    if not inference_engine.is_loaded:
        raise HTTPException(status_code=503, detail="ML models not loaded.")

    results = [inference_engine.predict(text) for text in request.items]
    pos = sum(1 for r in results if r["sentiment"] == "Positive")
    neu = sum(1 for r in results if r["sentiment"] == "Neutral")
    neg = sum(1 for r in results if r["sentiment"] == "Negative")
    avg_score = round(sum(r["sentiment_score"] for r in results) / len(results), 4)

    return {
        "results": results,
        "summary": {
            "total_items": len(results),
            "positive": pos,
            "neutral": neu,
            "negative": neg,
            "average_sentiment_score": avg_score,
        },
    }
