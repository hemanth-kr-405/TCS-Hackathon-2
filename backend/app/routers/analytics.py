"""Analytics router — all metrics computed from DB, no hardcoded values."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
from collections import Counter

from app.database import get_db
from app.models.db_models import FeedbackItem, RecurringIssue, Escalation, ChatSession, BusinessRecommendation
from app.schemas.schemas import (
    AnalyticsOverviewResponse, FeedbackResponse,
    RecurringIssueResponse, BusinessRecommendationResponse,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _distribution(items: List[str]) -> Dict[str, int]:
    return dict(Counter(items))


@router.get("/overview", summary="Dashboard overview KPIs")
def get_overview(db: Session = Depends(get_db)):
    """Returns all KPI metrics computed from database."""
    total = db.query(FeedbackItem).count()
    if total == 0:
        return {
            "total_feedback": 0, "positive_count": 0, "neutral_count": 0,
            "negative_count": 0, "positive_pct": 0.0, "neutral_pct": 0.0,
            "negative_pct": 0.0, "average_sentiment_score": 0.0,
            "csat_percentage": 0.0, "active_escalations": 0,
            "resolved_issues": 0, "escalation_rate": 0.0,
            "sentiment_distribution": {"Positive": 0, "Neutral": 0, "Negative": 0},
            "intent_distribution": {},
            "emotion_distribution": {},
            "category_sentiment": {},
            "recent_feedback": [],
            "top_recurring_issues": [],
            "recommendations": [],
        }

    pos = db.query(FeedbackItem).filter(FeedbackItem.sentiment == "Positive").count()
    neu = db.query(FeedbackItem).filter(FeedbackItem.sentiment == "Neutral").count()
    neg = db.query(FeedbackItem).filter(FeedbackItem.sentiment == "Negative").count()

    avg_score = db.query(func.avg(FeedbackItem.sentiment_score)).scalar() or 0.0
    active_esc = db.query(Escalation).filter(Escalation.status == "Pending").count()
    resolved = db.query(RecurringIssue).filter(RecurringIssue.status == "Resolved").count()

    chat_total = db.query(ChatSession).count()
    escalated_sessions = db.query(ChatSession).filter(ChatSession.is_escalated == True).count()
    escalation_rate = round(escalated_sessions / chat_total * 100, 1) if chat_total > 0 else 0.0

    feedback_items = db.query(FeedbackItem).all()
    intent_dist = _distribution([i.intent for i in feedback_items if i.intent])
    emotion_dist = _distribution([i.emotion for i in feedback_items if i.emotion])
    by_category: Dict[str, Dict[str, int]] = {}
    for item in feedback_items:
        cat = item.category or "General"
        by_category.setdefault(cat, {"Positive": 0, "Neutral": 0, "Negative": 0})
        by_category[cat][item.sentiment] = by_category[cat].get(item.sentiment, 0) + 1

    top_issues = db.query(RecurringIssue).order_by(RecurringIssue.frequency.desc()).limit(10).all()
    issues_list = [
        {
            "id": i.id,
            "issue_key": i.issue_key,
            "title": i.title,
            "category": i.category,
            "description": i.description,
            "frequency": i.frequency,
            "severity": i.severity,
            "average_sentiment": i.average_sentiment,
            "status": i.status,
            "created_at": i.created_at.isoformat() if i.created_at else None,
        }
        for i in top_issues
    ]

    recs_query = db.query(BusinessRecommendation).order_by(BusinessRecommendation.created_at.desc()).limit(10).all()
    recs_list = [
        {
            "id": r.id,
            "recommendation_key": r.recommendation_key,
            "title": r.title,
            "category": r.category,
            "description": r.description,
            "priority": r.priority,
            "evidence": r.evidence,
            "estimated_impact": r.estimated_impact,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in recs_query
    ]

    recent_list = [
        {
            "id": f.id,
            "customer_id": f.customer_id,
            "text": f.text,
            "source": f.source,
            "category": f.category,
            "product": f.product,
            "rating": f.rating,
            "sentiment": f.sentiment,
            "sentiment_score": f.sentiment_score,
            "confidence": f.confidence,
            "intent": f.intent,
            "emotion": f.emotion,
            "aspect": f.aspect,
            "created_at": f.created_at.isoformat() if f.created_at else None,
        }
        for f in feedback_items[-10:]
    ]

    return {
        "total_feedback": total,
        "positive_count": pos,
        "neutral_count": neu,
        "negative_count": neg,
        "positive_pct": round(pos / total * 100, 1),
        "neutral_pct": round(neu / total * 100, 1),
        "negative_pct": round(neg / total * 100, 1),
        "average_sentiment_score": round(float(avg_score), 4),
        "csat_percentage": round((pos + neu) / total * 100, 1),
        "active_escalations": active_esc,
        "resolved_issues": resolved,
        "escalation_rate": escalation_rate,
        "sentiment_distribution": {"Positive": pos, "Neutral": neu, "Negative": neg},
        "intent_distribution": intent_dist,
        "emotion_distribution": emotion_dist,
        "category_sentiment": by_category,
        "recent_feedback": recent_list,
        "top_recurring_issues": issues_list,
        "recommendations": recs_list,
    }


@router.get("/sentiment", summary="Sentiment distribution & trends")
def get_sentiment_analytics(db: Session = Depends(get_db)):
    """Sentiment breakdown by category, channel and over time."""
    items = db.query(FeedbackItem).all()

    dist = _distribution([i.sentiment for i in items])
    by_category: Dict[str, Dict] = {}
    for item in items:
        cat = item.category or "General"
        by_category.setdefault(cat, {"Positive": 0, "Neutral": 0, "Negative": 0})
        by_category[cat][item.sentiment] = by_category[cat].get(item.sentiment, 0) + 1

    by_source = _distribution([i.source for i in items])
    emotion_dist = _distribution([i.emotion for i in items if i.emotion])

    # Time-series (last 7 weeks bucketed by week)
    from collections import defaultdict
    import datetime
    weekly: Dict[str, Dict] = defaultdict(lambda: {"Positive": 0, "Neutral": 0, "Negative": 0})
    for item in items:
        if item.created_at:
            week_key = item.created_at.strftime("%Y-W%W")
            weekly[week_key][item.sentiment] += 1

    trend = [{"week": k, **v} for k, v in sorted(weekly.items())[-10:]]

    return {
        "distribution": dist,
        "by_category": by_category,
        "by_source": by_source,
        "emotion_distribution": emotion_dist,
        "trend": trend,
    }


@router.get("/intents", summary="Intent distribution")
def get_intent_analytics(db: Session = Depends(get_db)):
    """Intent frequency and sentiment by intent."""
    items = db.query(FeedbackItem).all()
    intent_dist = _distribution([i.intent for i in items if i.intent])

    intent_sentiment: Dict[str, Dict] = {}
    for item in items:
        if item.intent:
            intent_sentiment.setdefault(
                item.intent, {"Positive": 0, "Neutral": 0, "Negative": 0, "total": 0}
            )
            intent_sentiment[item.intent][item.sentiment] = (
                intent_sentiment[item.intent].get(item.sentiment, 0) + 1
            )
            intent_sentiment[item.intent]["total"] += 1

    return {
        "intent_distribution": intent_dist,
        "intent_by_sentiment": intent_sentiment,
        "top_intent": max(intent_dist, key=intent_dist.get) if intent_dist else "N/A",
    }


@router.get("/issues", summary="Recurring issues summary")
def get_issues_analytics(db: Session = Depends(get_db)):
    """Recurring issues ranked by frequency and severity."""
    issues = db.query(RecurringIssue).order_by(
        RecurringIssue.frequency.desc()
    ).all()

    severity_map = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
    by_severity = _distribution([i.severity for i in issues])
    by_status = _distribution([i.status for i in issues])

    return {
        "total_issues": len(issues),
        "by_severity": by_severity,
        "by_status": by_status,
        "issues": [
            {
                "id": i.id,
                "title": i.title,
                "category": i.category,
                "frequency": i.frequency,
                "severity": i.severity,
                "average_sentiment": i.average_sentiment,
                "status": i.status,
            }
            for i in issues
        ],
    }


@router.get("/recurring-issues", summary="Alias for recurring issues")
def get_recurring_issues_alias(db: Session = Depends(get_db)):
    return get_issues_analytics(db)


@router.get("/recommendations", summary="Business recommendations")
def get_recommendations_analytics(db: Session = Depends(get_db)):
    recs = db.query(BusinessRecommendation).order_by(
        BusinessRecommendation.created_at.desc()
    ).all()
    return [
        {
            "id": r.id,
            "recommendation_key": r.recommendation_key,
            "title": r.title,
            "category": r.category,
            "description": r.description,
            "priority": r.priority,
            "evidence": r.evidence,
            "estimated_impact": r.estimated_impact,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in recs
    ]
