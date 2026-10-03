"""Feedback router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.db_models import FeedbackItem
from app.schemas.schemas import FeedbackCreate, FeedbackResponse
from app.ml.inference.inference_engine import inference_engine

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("", response_model=FeedbackResponse, status_code=201, summary="Submit feedback")
def submit_feedback(payload: FeedbackCreate, db: Session = Depends(get_db)):
    """Submit customer feedback. ML analysis runs automatically."""
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Feedback text cannot be empty.")

    if inference_engine.is_loaded:
        pred = inference_engine.predict(payload.text)
        sentiment      = pred["sentiment"]
        sentiment_score = pred["sentiment_score"]
        confidence     = pred["confidence"]
        intent         = pred["intent"]
        emotion        = pred["emotion"]
        aspect         = pred["aspect"]
    else:
        sentiment, sentiment_score, confidence = "Neutral", 0.0, 0.5
        intent, emotion, aspect = "General Inquiry", "Neutral", "General Experience"

    item = FeedbackItem(
        customer_id=payload.customer_id or "anonymous",
        text=payload.text,
        source=payload.source or "review",
        product=payload.product,
        category=payload.category or "General",
        sentiment=sentiment,
        sentiment_score=sentiment_score,
        confidence=confidence,
        intent=intent,
        emotion=emotion,
        aspect=aspect,
        rating=payload.rating,
        is_synthetic=False,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("", response_model=List[FeedbackResponse], summary="List feedback")
def list_feedback(
    skip: int = 0,
    limit: int = 50,
    sentiment: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(FeedbackItem)
    if sentiment:
        q = q.filter(FeedbackItem.sentiment == sentiment)
    if category:
        q = q.filter(FeedbackItem.category == category)
    return q.order_by(FeedbackItem.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{feedback_id}", response_model=FeedbackResponse, summary="Get feedback item")
def get_feedback(feedback_id: int, db: Session = Depends(get_db)):
    item = db.query(FeedbackItem).filter(FeedbackItem.id == feedback_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Feedback item not found.")
    return item


@router.post("/upload-csv", summary="Upload CSV Dataset for Instant ML Sentiment Analysis")
def upload_csv_dataset(
    file_content: str,
    db: Session = Depends(get_db)
):
    """Parses CSV text payload, analyzes sentiment via ML inference, and ingests records."""
    import csv
    import io

    lines = file_content.strip().split("\n")
    if len(lines) < 2:
        raise HTTPException(status_code=400, detail="CSV file must contain a header row and data rows.")

    reader = csv.DictReader(io.StringIO(file_content))
    ingested = 0

    for row in reader:
        # Detect text column
        text = row.get("Review Text") or row.get("text") or row.get("review") or row.get("Feedback") or ""
        if not text or not text.strip():
            continue

        cat = row.get("Department Name") or row.get("category") or row.get("Class Name") or "General"
        rating_str = row.get("Rating") or row.get("rating")
        try:
            rating = int(rating_str) if rating_str else None
        except ValueError:
            rating = None

        if inference_engine.is_loaded:
            pred = inference_engine.predict(text)
            sentiment       = pred["sentiment"]
            sentiment_score = pred["sentiment_score"]
            confidence      = pred["confidence"]
            intent          = pred["intent"]
            emotion         = pred["emotion"]
            aspect          = pred["aspect"]
        else:
            sentiment, sentiment_score, confidence = "Neutral", 0.0, 0.5
            intent, emotion, aspect = "General Inquiry", "Neutral", "General Experience"

        item = FeedbackItem(
            customer_id=row.get("Customer ID") or f"cust_csv_{ingested+1}",
            text=text,
            source="csv_upload",
            product=row.get("Title") or row.get("product"),
            category=cat,
            rating=rating,
            sentiment=sentiment,
            sentiment_score=sentiment_score,
            confidence=confidence,
            intent=intent,
            emotion=emotion,
            aspect=aspect,
            is_synthetic=False,
        )
        db.add(item)
        ingested += 1
        if ingested >= 500: # cap single batch for performance
            break

    db.commit()
    return {"status": "success", "ingested_count": ingested, "message": f"Successfully analyzed and ingested {ingested} dataset records."}

