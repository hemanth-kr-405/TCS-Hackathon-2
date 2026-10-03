"""Escalations router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.db_models import Escalation
from app.schemas.schemas import EscalationResponse, EscalationUpdate

router = APIRouter(prefix="/escalations", tags=["Escalations"])


@router.get("", response_model=List[EscalationResponse], summary="List escalations")
def list_escalations(
    status: str = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    q = db.query(Escalation)
    if status:
        q = q.filter(Escalation.status == status)
    return q.order_by(Escalation.created_at.desc()).limit(limit).all()


@router.get("/{escalation_id}", response_model=EscalationResponse, summary="Get escalation")
def get_escalation(escalation_id: int, db: Session = Depends(get_db)):
    esc = db.query(Escalation).filter(Escalation.id == escalation_id).first()
    if not esc:
        raise HTTPException(status_code=404, detail="Escalation not found.")
    return esc


@router.patch("/{escalation_id}", response_model=EscalationResponse, summary="Update escalation")
def update_escalation(
    escalation_id: int,
    payload: EscalationUpdate,
    db: Session = Depends(get_db),
):
    esc = db.query(Escalation).filter(Escalation.id == escalation_id).first()
    if not esc:
        raise HTTPException(status_code=404, detail="Escalation not found.")
    if payload.status:
        esc.status = payload.status
    if payload.assigned_agent:
        esc.assigned_agent = payload.assigned_agent
    if payload.status == "Resolved":
        import datetime
        esc.resolved_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(esc)
    return esc


@router.get("/summary/stats", summary="Escalation statistics")
def escalation_stats(db: Session = Depends(get_db)):
    total = db.query(Escalation).count()
    pending = db.query(Escalation).filter(Escalation.status == "Pending").count()
    resolved = db.query(Escalation).filter(Escalation.status == "Resolved").count()
    critical = db.query(Escalation).filter(Escalation.severity == "Critical").count()
    return {
        "total": total,
        "pending": pending,
        "resolved": resolved,
        "critical": critical,
        "resolution_rate": round(resolved / total * 100, 1) if total > 0 else 0.0,
    }
