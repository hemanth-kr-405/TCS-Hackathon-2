"""
SQLAlchemy ORM Models for TCS Retail Sentiment Intelligence Platform.
Designed for SQLite (Phase 1) with easy migration path to PostgreSQL.
"""
import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, Text, Index
)
from sqlalchemy.orm import relationship
from app.database import Base


class FeedbackItem(Base):
    __tablename__ = "feedback_items"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(100), default="anonymous", index=True)
    text = Column(Text, nullable=False)
    source = Column(String(50), default="review")          # review | chat | survey
    product = Column(String(150), nullable=True)
    category = Column(String(100), default="General")      # Electronics, Fashion, Home & Kitchen …
    sentiment = Column(String(20), nullable=False)         # Positive | Neutral | Negative
    sentiment_score = Column(Float, nullable=False)        # -1.0 → 1.0
    confidence = Column(Float, default=0.85)               # 0.0 → 1.0
    intent = Column(String(100), default="General Inquiry")
    emotion = Column(String(50), default="Neutral")
    aspect = Column(String(100), default="General")
    rating = Column(Integer, nullable=True)                # 1 – 5 stars
    is_synthetic = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        Index("ix_feedback_sentiment", "sentiment"),
        Index("ix_feedback_category", "category"),
        Index("ix_feedback_created_at", "created_at"),
    )


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    customer_id = Column(String(100), default="anonymous")
    customer_name = Column(String(100), default="Customer")
    status = Column(String(50), default="Active")          # Active | Escalated | Closed | Resolved
    conversation_state = Column(String(50), default="NEW") # NEW | ACTIVE | ISSUE_IDENTIFIED | RESOLUTION_IN_PROGRESS | ESCALATION_RECOMMENDED | ESCALATED | RESOLVED | CLOSED
    initial_sentiment = Column(String(20), default="Neutral")
    current_sentiment = Column(String(20), default="Neutral")
    sentiment_score = Column(Float, default=0.0)
    sentiment_trend = Column(String(50), default="Stable") # Improving | Declining | Stable | Worsening
    current_issue = Column(String(100), nullable=True)
    current_issue_category = Column(String(100), nullable=True)
    current_issue_severity = Column(String(20), nullable=True)
    escalation_status = Column(String(50), default="None") # None | Triggered | Resolved
    escalation_score = Column(Float, default=0.0)
    escalation_reasons = Column(Text, nullable=True)       # JSON string
    is_escalated = Column(Boolean, default=False)
    assigned_agent = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    messages = relationship(
        "ChatMessage", back_populates="session", cascade="all, delete-orphan"
    )
    escalations = relationship("Escalation", back_populates="session")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        String(100), ForeignKey("chat_sessions.session_id"), nullable=False, index=True
    )
    sender = Column(String(20), nullable=False)  # user | bot
    text = Column(Text, nullable=False)
    turn_number = Column(Integer, default=1)
    sentiment = Column(String(20), nullable=True)
    sentiment_score = Column(Float, nullable=True)
    confidence = Column(Float, default=0.85)
    intent = Column(String(100), nullable=True)
    emotion = Column(String(50), nullable=True)
    issue = Column(String(100), nullable=True)
    empathetic_response = Column(Text, nullable=True)
    sentiment_change = Column(Boolean, default=False)
    sentiment_direction = Column(String(20), default="stable") # stable | improved | worsened
    triggered_escalation = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")


class RecurringIssue(Base):
    __tablename__ = "recurring_issues"

    id = Column(Integer, primary_key=True, index=True)
    issue_key = Column(String(50), unique=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    frequency = Column(Integer, default=1)
    severity = Column(String(20), default="Medium")        # Critical | High | Medium | Low
    average_sentiment = Column(Float, default=-0.5)
    status = Column(String(50), default="Open")            # Open | In Progress | Resolved
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class BusinessRecommendation(Base):
    __tablename__ = "business_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    recommendation_key = Column(String(50), unique=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    priority = Column(String(20), default="Medium")        # Critical | High | Medium | Low
    evidence = Column(Text, nullable=True)
    estimated_impact = Column(String(200), default="Moderate CSAT improvement")
    status = Column(String(50), default="New")             # New | In Review | Implemented
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Escalation(Base):
    __tablename__ = "escalations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        String(100), ForeignKey("chat_sessions.session_id"), nullable=False, index=True
    )
    customer_name = Column(String(100), default="Customer")
    reason = Column(Text, nullable=False)
    severity = Column(String(20), default="High")          # Critical | High | Medium
    status = Column(String(50), default="Pending")         # Pending | Reviewed | Resolved
    assigned_agent = Column(String(100), default="Unassigned")
    sentiment_score = Column(Float, default=-0.8)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    session = relationship("ChatSession", back_populates="escalations")
