"""Chat router — Phase 4 AI Orchestrator & Context-Aware Retail Chatbot APIs."""
import uuid
import json
import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.database import get_db
from app.models.db_models import ChatSession, ChatMessage, Escalation
from app.schemas.schemas import (
    ChatSessionCreate, ChatSessionResponse,
    ChatMessageCreate, SentimentTimelineResponse, SentimentTurnItem,
)
from app.ml.ai_orchestrator import ai_orchestrator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["AI Chatbot"])


@router.post("/sessions", response_model=ChatSessionResponse, summary="Start a new chat session")
def create_session(payload: ChatSessionCreate, db: Session = Depends(get_db)):
    session_id = f"chat_{uuid.uuid4().hex[:10]}"
    customer_name = payload.customer_name or "Customer"
    db_session = ChatSession(
        session_id=session_id,
        customer_name=customer_name,
        status="Active",
        conversation_state="NEW",
    )
    db.add(db_session)

    welcome = ChatMessage(
        session_id=session_id,
        sender="bot",
        text="Hi! 👋 I'm RetailAI. How can I help you today?",
        turn_number=1,
        sentiment="Neutral",
        sentiment_score=0.0,
        confidence=0.95,
        intent="Welcome",
        emotion="Neutral",
        triggered_escalation=False,
    )
    db.add(welcome)
    db.commit()
    db.refresh(db_session)
    return db_session


@router.get("/sessions", response_model=List[ChatSessionResponse], summary="List chat sessions")
def list_sessions(
    q: Optional[str] = Query(None, description="Search term for sessions"),
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(ChatSession)
    if q and q.strip():
        search_term = f"%{q.strip()}%"
        query = query.filter(
            (ChatSession.customer_name.ilike(search_term)) |
            (ChatSession.session_id.ilike(search_term)) |
            (ChatSession.current_issue.ilike(search_term))
        )
    return query.order_by(ChatSession.updated_at.desc()).limit(limit).all()


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse, summary="Get session")
def get_session(session_id: str, db: Session = Depends(get_db)):
    sess = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Chat session not found.")
    return sess


@router.delete("/sessions/{session_id}", summary="Delete chat session")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    sess = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Chat session not found.")
    
    # Delete associated messages
    db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
    # Delete associated escalations
    db.query(Escalation).filter(Escalation.session_id == session_id).delete()
    db.delete(sess)
    db.commit()
    return {"message": f"Session {session_id} deleted successfully."}


@router.get("/sessions/{session_id}/sentiment-timeline", response_model=SentimentTimelineResponse, summary="Get sentiment trajectory timeline")
def get_sentiment_timeline(session_id: str, db: Session = Depends(get_db)):
    sess = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Chat session not found.")

    user_msgs = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id,
        ChatMessage.sender == "user",
    ).order_by(ChatMessage.timestamp.asc()).all()

    trajectory = []
    for idx, m in enumerate(user_msgs, start=1):
        trajectory.append(
            SentimentTurnItem(
                turn=m.turn_number or idx,
                sentiment=m.sentiment or "Neutral",
                confidence=round(m.confidence or 0.85, 4),
                sentiment_score=round(m.sentiment_score or 0.0, 4),
                timestamp=m.timestamp.isoformat() if m.timestamp else datetime.datetime.utcnow().isoformat(),
            )
        )

    return SentimentTimelineResponse(
        session_id=session_id,
        overall_trend=sess.sentiment_trend or "Stable",
        trajectory=trajectory,
    )


@router.get("/llm-status", summary="Get LLM Engine Provider health & status")
def get_llm_status():
    from app.ml.llm_service import llm_service
    return llm_service.get_status()


@router.post("/message", summary="Send chat message through AI Orchestrator")
def send_message(payload: ChatMessageCreate, db: Session = Depends(get_db)):
    """Process a user message through the 10-step AI Orchestrator pipeline."""
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    logger.info(
        f"CHAT REQUEST RECEIVED | session_id: {payload.session_id} | "
        f"message_length: {len(payload.message)} | message: '{payload.message[:60]}' | "
        f"provider: {payload.llm_provider}"
    )

    # Get or auto-create session
    db_session = db.query(ChatSession).filter(
        ChatSession.session_id == payload.session_id
    ).first()
    if not db_session:
        db_session = ChatSession(
            session_id=payload.session_id,
            customer_name="Customer",
            status="Active",
            conversation_state="NEW",
        )
        db.add(db_session)
        db.commit()

    # Fetch history for context memory & reference resolution
    history = db.query(ChatMessage).filter(
        ChatMessage.session_id == payload.session_id
    ).order_by(ChatMessage.timestamp.asc()).all()

    history_dicts = [
        {
            "sender": m.sender,
            "text": m.text,
            "sentiment": m.sentiment,
            "sentiment_score": m.sentiment_score or 0.0,
            "message": m.text,
            "issue": m.issue,
        }
        for m in history
    ]

    prev_esc_score = db_session.escalation_score or 0.0
    user_turn_count = len([m for m in history if m.sender == "user"]) + 1

    # Run AI Orchestrator Pipeline
    result = ai_orchestrator.orchestrate(
        message=payload.message,
        history=history_dicts,
        session_state=db_session.conversation_state or "NEW",
        session_escalation_score=prev_esc_score,
        preferred_provider=payload.llm_provider or "auto",
        customer_name=db_session.customer_name or "Customer",
        session_id=payload.session_id,
    )

    context_data = result["context"]
    escalation_data = result["escalation"]
    bot_text = result["response"]
    entities = result["entities"]

    # Persist user message
    user_msg = ChatMessage(
        session_id=payload.session_id,
        sender="user",
        text=payload.message,
        turn_number=user_turn_count,
        sentiment=result["sentiment"],
        sentiment_score=result["sentiment_score"],
        confidence=result["confidence"],
        intent=result["intent"],
        emotion=result["emotion"],
        issue=entities.get("requested_action") or entities.get("issue"),
        empathetic_response=bot_text,
        sentiment_change=context_data["sentiment_change"],
        sentiment_direction=context_data["sentiment_direction"],
        triggered_escalation=escalation_data["should_escalate"],
    )
    db.add(user_msg)

    # Persist bot response
    bot_msg = ChatMessage(
        session_id=payload.session_id,
        sender="bot",
        text=bot_text,
        turn_number=user_turn_count,
        sentiment="Neutral",
        sentiment_score=0.0,
        confidence=0.95,
        intent="Response",
        emotion="Satisfaction",
        triggered_escalation=False,
    )
    db.add(bot_msg)

    # Update session state & metrics
    db_session.current_sentiment = result["sentiment"]
    db_session.sentiment_score   = result["sentiment_score"]
    db_session.sentiment_trend   = context_data["sentiment_direction"].capitalize()
    db_session.conversation_state = context_data["conversation_state"]
    db_session.escalation_score  = escalation_data["score"]
    db_session.escalation_reasons = json.dumps(escalation_data["reasons"])
    if entities.get("order_id"):
        db_session.current_issue = f"Order #{entities['order_id']}"
    db_session.updated_at = datetime.datetime.utcnow()

    if escalation_data["should_escalate"] and not db_session.is_escalated:
        db_session.is_escalated      = True
        db_session.status            = "Escalated"
        db_session.escalation_status = "Triggered"
        db_session.assigned_agent    = "Senior Retail Specialist"

        esc_reason = "; ".join(escalation_data["reasons"]) if escalation_data["reasons"] else "Automated escalation criteria met"
        esc = Escalation(
            session_id=payload.session_id,
            customer_name=db_session.customer_name,
            severity=escalation_data["severity"],
            reason=esc_reason,
            sentiment_score=result["sentiment_score"],
            status="Pending",
            assigned_agent="Senior Support Team",
        )
        db.add(esc)

    db.commit()
    db.refresh(user_msg)

    logger.info(
        f"CHAT RESPONSE GENERATED | session_id: {payload.session_id} | "
        f"interaction_mode: {result.get('interaction_mode', 'UNKNOWN')} | "
        f"sentiment: {result['sentiment']} ({result['sentiment_score']}) | "
        f"intent: {result['intent']} | emotion: {result['emotion']} | "
        f"provider: {result.get('llm_provider')} | "
        f"llm_called: {'Fallback' not in str(result.get('llm_provider', ''))} | "
        f"fallback_used: {'Fallback' in str(result.get('llm_provider', ''))}"
    )

    return {
        "id": user_msg.id,
        "session_id": user_msg.session_id,
        "sender": user_msg.sender,
        "text": user_msg.text,
        "sentiment": user_msg.sentiment,
        "sentiment_score": user_msg.sentiment_score,
        "confidence": user_msg.confidence,
        "intent": user_msg.intent,
        "emotion": user_msg.emotion,
        "entities": entities,
        "empathetic_response": bot_text,
        "assistant_response": bot_text,
        "thinking_steps": result["thinking_steps"],
        "tools_executed": result["tools_executed"],
        "rag_sources": result["rag_sources"],
        "conversation_summary": result["conversation_summary"],
        "llm_provider": result.get("llm_provider"),
        "llm_status": result.get("llm_status"),
        "triggered_escalation": user_msg.triggered_escalation,
        "timestamp": user_msg.timestamp,
        "interaction_mode": result.get("interaction_mode", "RETAIL_SUPPORT"),
        "analysis": {
            "sentiment": result["sentiment"],
            "confidence": result["confidence"],
            "intent": result["intent"],
            "emotion": result["emotion"],
            "entities": entities,
            "llm_provider": result.get("llm_provider"),
            "llm_status": result.get("llm_status"),
            "interaction_mode": result.get("interaction_mode", "RETAIL_SUPPORT"),
        },
        "context": context_data,
        "escalation": escalation_data,
    }


@router.post("/sessions/{session_id}/escalate", summary="Trigger manual escalation")
def trigger_escalate(session_id: str, db: Session = Depends(get_db)):
    sess = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Chat session not found.")

    sess.is_escalated = True
    sess.status = "Escalated"
    sess.escalation_status = "Triggered"
    sess.conversation_state = "ESCALATED"
    sess.assigned_agent = "Senior Retail Agent"

    esc = Escalation(
        session_id=session_id,
        customer_name=sess.customer_name,
        severity="High",
        reason="Manual escalation requested by operator or customer",
        sentiment_score=sess.sentiment_score,
        status="Pending",
        assigned_agent="Senior Support Team",
    )
    db.add(esc)
    db.commit()
    db.refresh(sess)
    return {"message": "Session escalated successfully", "session": sess}


@router.post("/sessions/{session_id}/resolve", summary="Resolve chat session")
def resolve_session(session_id: str, db: Session = Depends(get_db)):
    sess = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Chat session not found.")

    sess.status = "Resolved"
    sess.conversation_state = "RESOLVED"
    sess.escalation_status = "Resolved"
    db.commit()
    db.refresh(sess)
    return {"message": "Session marked as resolved", "session": sess}


@router.post("/sessions/{session_id}/analyze-customer", summary="Generate AI Customer Summary")
def analyze_customer(session_id: str, db: Session = Depends(get_db)):
    """Generate structured AI diagnostic summary for a customer session."""
    sess = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Chat session not found.")

    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.timestamp.asc()).all()
    user_msgs = [m for m in messages if m.sender == "user"]
    
    latest_user_text = user_msgs[-1].text if user_msgs else "No customer input yet."
    main_issue = sess.current_issue or "Order delivery delay"
    
    if sess.is_escalated:
        escalation_status = "Escalation Active (Assigned to Senior Agent)"
    elif (sess.escalation_score or 0) > 0.4:
        escalation_status = "High Escalation Risk (Monitor closely)"
    else:
        escalation_status = "Not currently required"

    trend_desc = sess.sentiment_trend or "Stable"
    current_sent = sess.current_sentiment or "Neutral"

    return {
        "customer_id": f"DEMO-{sess.id if hasattr(sess, 'id') else 1024}",
        "customer_name": sess.customer_name or "Customer",
        "session_id": session_id,
        "main_issue": main_issue,
        "current_sentiment": current_sent,
        "sentiment_trajectory": f"{sess.initial_sentiment or 'Neutral'} → {current_sent} ({trend_desc})",
        "sentiment_score": sess.sentiment_score or 0.0,
        "likely_reason": f"Customer expressed concerns regarding '{latest_user_text[:80]}'",
        "recommended_action": "Confirm tracking status with carrier, verify refund eligibility, and offer express delivery resolution.",
        "escalation_status": escalation_status,
        "csat_risk": "High" if current_sent == "Negative" else "Medium" if current_sent == "Neutral" else "Low",
    }


@router.post("/reset-demo", summary="One-click Demo Environment Reset")
def reset_demo_environment(db: Session = Depends(get_db)):
    """Clear demo sessions, escalations, reset demo state and seed clean baseline data."""
    try:
        # Clear chat messages, sessions, escalations
        db.query(ChatMessage).delete()
        db.query(Escalation).delete()
        db.query(ChatSession).delete()
        db.commit()

        # Seed initial demo session
        new_session_id = f"demo_session_1024"
        demo_session = ChatSession(
            session_id=new_session_id,
            customer_name="Sarah Jenkins",
            status="Active",
            conversation_state="ACTIVE",
            initial_sentiment="Neutral",
            current_sentiment="Neutral",
            sentiment_score=0.0,
            sentiment_trend="Stable",
            is_escalated=False,
            current_issue="Order Tracking #45821",
        )
        db.add(demo_session)

        welcome_msg = ChatMessage(
            session_id=new_session_id,
            sender="bot",
            text="Hello Sarah! 👋 I'm RetailAI, your TCS AI assistant. How can I help with your order today?",
            turn_number=1,
            sentiment="Neutral",
            sentiment_score=0.0,
            confidence=0.98,
            intent="Welcome",
            emotion="Satisfaction",
            triggered_escalation=False,
        )
        db.add(welcome_msg)
        db.commit()

        return {
            "status": "success",
            "message": "Demo environment reset successfully. Baseline chat session created.",
            "demo_session_id": new_session_id,
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error resetting demo environment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset demo environment: {str(e)}")

