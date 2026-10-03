"""Pydantic request/response schemas for TCS Retail Sentiment Platform."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ─── Sentiment ────────────────────────────────────────────────────────────────

class SentimentAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, example="The product quality is excellent!")
    source: Optional[str] = Field("review", example="review")
    customer_id: Optional[str] = Field(None, example="cust_001")

    model_config = {"json_schema_extra": {"example": {"text": "Great delivery speed!"}}}


class SentimentAnalyzeResponse(BaseModel):
    text: str
    sentiment: str
    sentiment_score: float
    confidence: float
    intent: str
    emotion: str
    aspect: str
    probabilities: Dict[str, float]


class BatchAnalyzeRequest(BaseModel):
    items: List[str] = Field(..., max_length=100)


class BatchAnalyzeResponse(BaseModel):
    results: List[SentimentAnalyzeResponse]
    summary: Dict[str, Any]


# ─── Feedback ─────────────────────────────────────────────────────────────────

class FeedbackCreate(BaseModel):
    text: str = Field(..., min_length=3)
    customer_id: Optional[str] = None
    source: Optional[str] = "review"
    product: Optional[str] = None
    category: Optional[str] = "General"
    rating: Optional[int] = Field(None, ge=1, le=5)


class FeedbackResponse(BaseModel):
    id: int
    customer_id: Optional[str] = None
    text: str
    source: str
    product: Optional[str] = None
    category: str
    sentiment: str
    sentiment_score: float
    confidence: float
    intent: str
    emotion: str
    aspect: str
    rating: Optional[int] = None
    is_synthetic: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Chat ─────────────────────────────────────────────────────────────────────

class ChatSessionCreate(BaseModel):
    customer_name: Optional[str] = "Customer"


class ChatMessageCreate(BaseModel):
    session_id: str
    message: str = Field(..., min_length=1)
    llm_provider: Optional[str] = "auto"


class ChatMessageResponse(BaseModel):
    id: int
    session_id: str
    sender: str
    text: str
    turn_number: Optional[int] = 1
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    confidence: Optional[float] = 0.85
    intent: Optional[str] = None
    emotion: Optional[str] = None
    issue: Optional[str] = None
    empathetic_response: Optional[str] = None
    sentiment_change: Optional[bool] = False
    sentiment_direction: Optional[str] = "stable"
    triggered_escalation: bool = False
    llm_provider: Optional[str] = None
    llm_status: Optional[str] = None
    timestamp: datetime

    model_config = {"from_attributes": True}


class ChatSessionResponse(BaseModel):
    session_id: str
    customer_name: str
    status: str
    conversation_state: Optional[str] = "NEW"
    initial_sentiment: str
    current_sentiment: str
    sentiment_score: float
    sentiment_trend: str
    current_issue: Optional[str] = None
    current_issue_category: Optional[str] = None
    current_issue_severity: Optional[str] = None
    escalation_status: str
    escalation_score: Optional[float] = 0.0
    escalation_reasons: Optional[str] = None
    is_escalated: bool
    assigned_agent: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse] = []

    model_config = {"from_attributes": True}


class Phase2ChatAnalysis(BaseModel):
    sentiment: str
    confidence: float
    intent: str
    emotion: str
    issue: Optional[str] = None
    llm_provider: Optional[str] = None
    llm_status: Optional[str] = None


class Phase2ChatContext(BaseModel):
    previous_sentiment: str
    current_sentiment: str
    sentiment_change: bool
    sentiment_direction: str
    conversation_state: str


class Phase2ChatEscalation(BaseModel):
    should_escalate: bool
    score: float
    severity: str
    reasons: List[str] = []


class Phase2ChatMessageResponse(BaseModel):
    id: int
    session_id: str
    sender: str
    text: str
    assistant_response: str
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    intent: Optional[str] = None
    emotion: Optional[str] = None
    triggered_escalation: bool = False
    llm_provider: Optional[str] = None
    llm_status: Optional[str] = None
    timestamp: datetime
    analysis: Phase2ChatAnalysis
    context: Phase2ChatContext
    escalation: Phase2ChatEscalation



class SentimentTurnItem(BaseModel):
    turn: int
    sentiment: str
    confidence: float
    sentiment_score: float
    timestamp: str


class SentimentTimelineResponse(BaseModel):
    session_id: str
    overall_trend: str
    trajectory: List[SentimentTurnItem]


# ─── Issues ───────────────────────────────────────────────────────────────────

class RecurringIssueResponse(BaseModel):
    id: int
    issue_key: Optional[str] = None
    title: str
    description: str
    category: str
    frequency: int
    severity: str
    average_sentiment: float
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Recommendations ──────────────────────────────────────────────────────────

class BusinessRecommendationResponse(BaseModel):
    id: int
    recommendation_key: Optional[str] = None
    title: str
    description: str
    category: str
    priority: str
    evidence: Optional[str] = None
    estimated_impact: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Escalations ─────────────────────────────────────────────────────────────

class EscalationResponse(BaseModel):
    id: int
    session_id: str
    customer_name: str
    reason: str
    severity: str
    status: str
    assigned_agent: str
    sentiment_score: float
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class EscalationUpdate(BaseModel):
    status: Optional[str] = None
    assigned_agent: Optional[str] = None


# ─── Analytics ────────────────────────────────────────────────────────────────

class AnalyticsOverviewResponse(BaseModel):
    total_feedback: int
    positive_count: int
    neutral_count: int
    negative_count: int
    positive_pct: float
    neutral_pct: float
    negative_pct: float
    average_sentiment_score: float
    csat_percentage: float
    active_escalations: int
    resolved_issues: int
    escalation_rate: float
    sentiment_distribution: Optional[Dict[str, int]] = None
    intent_distribution: Optional[Dict[str, int]] = None
    emotion_distribution: Optional[Dict[str, int]] = None
    category_sentiment: Optional[Dict[str, Dict[str, int]]] = None
    recent_feedback: Optional[List[Dict[str, Any]]] = None
    top_recurring_issues: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None


# ─── Model Evaluation ────────────────────────────────────────────────────────

class ModelMetricsResponse(BaseModel):
    model_name: str
    version: str
    trained_at: str
    training_samples: int
    test_samples: int
    accuracy: float
    precision_macro: float
    recall_macro: float
    f1_macro: float
    confusion_matrix: List[List[int]]
    labels: List[str]
    classification_report: Dict[str, Any]
