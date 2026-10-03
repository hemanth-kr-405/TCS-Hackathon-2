"""
Long-Term & Short-Term Customer Memory Service for TCS Retail AI.

Stores customer preferences, previous orders, complaint history, sentiment trajectory,
and unresolved issue counts across multi-turn sessions.
"""
import datetime
import logging
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)


class CustomerMemoryService:
    """Manages short-term and long-term customer memory stores."""

    def __init__(self):
        # In-memory customer profile store for demo
        self._memory_store: Dict[str, Dict[str, Any]] = {
            "DEMO-1024": {
                "customer_id": "DEMO-1024",
                "customer_name": "Sarah Jenkins",
                "vip_status": "Gold VIP Member",
                "preferred_products": ["Summer Apparel", "Silk Dresses"],
                "previous_orders": ["#45821", "#39201", "#28104"],
                "previous_complaints": [
                    {
                        "date": "2026-09-20",
                        "issue": "Late Delivery #45821",
                        "sentiment": "Negative",
                        "status": "Unresolved",
                    }
                ],
                "previous_sentiments": ["Neutral", "Negative", "Negative"],
                "unresolved_issues_count": 1,
                "conversation_summaries": [
                    "Customer inquired about order #45821 tracking update. Delivery delayed by carrier."
                ],
                "risk_history": [0.45, 0.68],
            }
        }

    def get_memory(self, customer_id: str) -> Dict[str, Any]:
        """Fetch long-term memory profile for customer."""
        clean_id = str(customer_id).strip().upper()
        if clean_id in self._memory_store:
            return self._memory_store[clean_id]
        
        # Initialize baseline memory for new customer
        new_memory = {
            "customer_id": clean_id,
            "customer_name": "Customer",
            "vip_status": "Standard",
            "preferred_products": [],
            "previous_orders": [],
            "previous_complaints": [],
            "previous_sentiments": [],
            "unresolved_issues_count": 0,
            "conversation_summaries": [],
            "risk_history": [],
        }
        self._memory_store[clean_id] = new_memory
        return new_memory

    def update_memory(self, customer_id: str, interaction_data: Dict[str, Any]):
        """Update customer memory with latest interaction results."""
        clean_id = str(customer_id).strip().upper()
        mem = self.get_memory(clean_id)

        if interaction_data.get("sentiment"):
            mem["previous_sentiments"].append(interaction_data["sentiment"])
            # Keep last 10 sentiments
            mem["previous_sentiments"] = mem["previous_sentiments"][-10:]

        if interaction_data.get("issue") and interaction_data.get("sentiment") == "Negative":
            mem["previous_complaints"].append({
                "date": datetime.datetime.utcnow().strftime("%Y-%m-%d"),
                "issue": interaction_data["issue"],
                "sentiment": "Negative",
                "status": "Active",
            })
            mem["unresolved_issues_count"] += 1

        if interaction_data.get("summary"):
            mem["conversation_summaries"].append(interaction_data["summary"])
            mem["conversation_summaries"] = mem["conversation_summaries"][-5:]

        logger.info(f"CUSTOMER MEMORY UPDATED | customer_id={clean_id} | complaints={mem['unresolved_issues_count']}")

    def calculate_customer_risk(self, customer_id: str, current_sentiment: str, current_score: float) -> Tuple[float, List[str]]:
        """
        Calculate Customer Risk Score (0.0 to 1.0) based on:
        - Current sentiment & score
        - Sentiment velocity / drop
        - Unresolved complaints count
        - Repeat contacts & escalation history
        """
        mem = self.get_memory(customer_id)
        reasons = []
        risk_score = 0.20 # Baseline risk

        # 1. Current Sentiment
        if current_sentiment == "Negative":
            risk_score += 0.30
            reasons.append("Current interaction negative")
        elif current_sentiment == "Positive":
            risk_score -= 0.10

        # 2. Sentiment Drop / Velocity
        sent_hist = mem["previous_sentiments"]
        if len(sent_hist) >= 2 and sent_hist[-2] in ("Positive", "Neutral") and current_sentiment == "Negative":
            risk_score += 0.25
            reasons.append("Sentiment dropped rapidly (Velocity high)")

        # 3. Unresolved Complaints Count
        unresolved = mem["unresolved_issues_count"]
        if unresolved > 0:
            risk_score += min(unresolved * 0.15, 0.30)
            reasons.append(f"{unresolved} unresolved complaints on record")

        risk_score = round(max(0.0, min(1.0, risk_score)), 2)
        return risk_score, reasons


customer_memory = CustomerMemoryService()
