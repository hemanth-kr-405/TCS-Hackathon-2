"""
Agentic Tool Registry & Execution Engine for TCS Retail Intelligence Platform.

Enforces strict backend tool execution architecture:
LLM Request -> Backend Validator -> Tool Execution -> Tool Result -> Grounded Response.
"""
import datetime
import uuid
import logging
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)

# Deterministic Mock Database for Demo Tools
MOCK_ORDERS = {
    "45821": {
        "order_id": "45821",
        "customer_id": "DEMO-1024",
        "customer_name": "Sarah Jenkins",
        "status": "In Transit",
        "carrier": "FedEx Express",
        "tracking_number": "TRK9482019482",
        "product": "TCS Silk Summer Dress",
        "sku": "SKU-DRS-104",
        "order_date": (datetime.datetime.utcnow() - datetime.timedelta(days=3)).strftime("%Y-%m-%d"),
        "estimated_delivery": (datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
        "paid_amount": "$129.50",
        "delivery_address": "104 Market St, San Francisco, CA",
        "issue_flag": "delivery_delay",
        "return_eligible": True,
        "refund_status": "Eligible for Return / Exchange",
    },
    "10092": {
        "order_id": "10092",
        "customer_id": "DEMO-1025",
        "customer_name": "Priya Sharma",
        "status": "Delivered",
        "carrier": "BlueDart Express",
        "tracking_number": "TRK8820194102",
        "product": "TCS ProBook 15 Laptop",
        "sku": "SKU-LAP-902",
        "order_date": (datetime.datetime.utcnow() - datetime.timedelta(days=5)).strftime("%Y-%m-%d"),
        "estimated_delivery": datetime.datetime.utcnow().strftime("%Y-%m-%d"),
        "paid_amount": "$899.00",
        "delivery_address": "45 Park Avenue, New York, NY",
        "issue_flag": "damaged_product",
        "return_eligible": True,
        "refund_status": "Refund Approved ($899.00)",
    },
    "77201": {
        "order_id": "77201",
        "customer_id": "DEMO-1026",
        "customer_name": "David Miller",
        "status": "Processing",
        "carrier": "Standard Logistics",
        "tracking_number": "TRK7720190012",
        "product": "Cotton Casual Top",
        "sku": "SKU-TOP-201",
        "order_date": datetime.datetime.utcnow().strftime("%Y-%m-%d"),
        "estimated_delivery": (datetime.datetime.utcnow() + datetime.timedelta(days=3)).strftime("%Y-%m-%d"),
        "paid_amount": "$45.00",
        "delivery_address": "88 Pine St, Seattle, WA",
        "issue_flag": None,
        "return_eligible": True,
        "refund_status": "N/A",
    },
}

MOCK_CUSTOMERS = {
    "DEMO-1024": {
        "customer_id": "DEMO-1024",
        "customer_name": "Sarah Jenkins",
        "vip_tier": "Gold Member",
        "total_orders": 12,
        "preferred_category": "Dresses",
        "unresolved_complaints": 1,
        "previous_complaint_history": ["Late Delivery Order #45821", "Sizing Inquiry"],
        "risk_level": "Medium",
    },
    "DEMO-1025": {
        "customer_id": "DEMO-1025",
        "customer_name": "Priya Sharma",
        "vip_tier": "Platinum VIP",
        "total_orders": 28,
        "preferred_category": "Electronics",
        "unresolved_complaints": 2,
        "previous_complaint_history": ["Damaged Laptop", "Refund Processing Delay"],
        "risk_level": "High",
    }
}

MOCK_PRODUCTS = {
    "SKU-DRS-104": {
        "product_id": "SKU-DRS-104",
        "name": "TCS Silk Summer Dress",
        "category": "Dresses",
        "price": "$129.50",
        "stock": "In Stock (42 units)",
        "return_window_days": 30,
        "availability": True,
    },
    "SKU-LAP-902": {
        "product_id": "SKU-LAP-902",
        "name": "TCS ProBook 15 Laptop",
        "category": "Electronics",
        "price": "$899.00",
        "stock": "In Stock (15 units)",
        "return_window_days": 30,
        "availability": True,
    }
}


class ToolRegistry:
    """Registry of Backend Retail Tools with Validation & Execution Engine."""

    def __init__(self):
        self._tools = {
            "get_order_status": self.get_order_status,
            "get_customer_profile": self.get_customer_profile,
            "get_order_history": self.get_order_history,
            "check_refund_eligibility": self.check_refund_eligibility,
            "get_delivery_eta": self.get_delivery_eta,
            "check_product_availability": self.check_product_availability,
            "create_support_ticket": self.create_support_ticket,
            "escalate_to_agent": self.escalate_to_agent,
        }

    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Fetch live logistics tracking status for an order."""
        clean_id = str(order_id).strip().upper().replace("#", "")
        if clean_id in MOCK_ORDERS:
            return {"tool": "get_order_status", "status": "SUCCESS", "data": MOCK_ORDERS[clean_id]}
        return {
            "tool": "get_order_status",
            "status": "NOT_FOUND",
            "message": f"Order #{clean_id} not found in logistics database. Please verify Order ID.",
        }

    def get_customer_profile(self, customer_id: str) -> Dict[str, Any]:
        """Fetch customer VIP tier, history, and preferences."""
        clean_id = str(customer_id).strip().upper()
        if clean_id in MOCK_CUSTOMERS:
            return {"tool": "get_customer_profile", "status": "SUCCESS", "data": MOCK_CUSTOMERS[clean_id]}
        return {
            "tool": "get_customer_profile",
            "status": "SUCCESS",
            "data": {
                "customer_id": clean_id,
                "customer_name": "Standard Customer",
                "vip_tier": "Regular",
                "total_orders": 1,
                "preferred_category": "General Apparel",
                "unresolved_complaints": 0,
            }
        }

    def get_order_history(self, customer_id: str) -> Dict[str, Any]:
        """Fetch past order history for a customer."""
        clean_id = str(customer_id).strip().upper()
        history = [o for o in MOCK_ORDERS.values() if o.get("customer_id") == clean_id]
        if not history:
            history = [list(MOCK_ORDERS.values())[0]]
        return {"tool": "get_order_history", "status": "SUCCESS", "count": len(history), "orders": history}

    def check_refund_eligibility(self, order_id: str) -> Dict[str, Any]:
        """Check policy refund eligibility and processing status for an order."""
        clean_id = str(order_id).strip().upper().replace("#", "")
        if clean_id in MOCK_ORDERS:
            order = MOCK_ORDERS[clean_id]
            return {
                "tool": "check_refund_eligibility",
                "status": "SUCCESS",
                "order_id": clean_id,
                "eligible": order.get("return_eligible", True),
                "refund_status": order.get("refund_status", "Eligible for Refund"),
                "paid_amount": order["paid_amount"],
                "policy": "TCS 30-Day Money Back Guarantee",
            }
        return {
            "tool": "check_refund_eligibility",
            "status": "NOT_FOUND",
            "message": f"Order #{clean_id} not found for refund check.",
        }

    def get_delivery_eta(self, order_id: str) -> Dict[str, Any]:
        """Fetch carrier ETA and delivery priority trace."""
        res = self.get_order_status(order_id)
        if res["status"] == "SUCCESS":
            data = res["data"]
            return {
                "tool": "get_delivery_eta",
                "status": "SUCCESS",
                "order_id": data["order_id"],
                "estimated_delivery": data["estimated_delivery"],
                "carrier": data["carrier"],
                "tracking_number": data["tracking_number"],
            }
        return res

    def check_product_availability(self, product_id: str) -> Dict[str, Any]:
        """Check stock availability and warranty for product."""
        clean_id = str(product_id).strip().upper()
        if clean_id in MOCK_PRODUCTS:
            return {"tool": "check_product_availability", "status": "SUCCESS", "data": MOCK_PRODUCTS[clean_id]}
        return {
            "tool": "check_product_availability",
            "status": "SUCCESS",
            "data": {
                "product_id": clean_id,
                "name": f"Product {clean_id}",
                "stock": "In Stock",
                "availability": True,
            }
        }

    def create_support_ticket(self, customer_id: str, issue: str) -> Dict[str, Any]:
        """Create support ticket for customer issue."""
        ticket_id = f"TCK-{uuid.uuid4().hex[:6].upper()}"
        return {
            "tool": "create_support_ticket",
            "status": "SUCCESS",
            "ticket_id": ticket_id,
            "customer_id": customer_id,
            "issue": issue,
            "created_at": datetime.datetime.utcnow().isoformat(),
        }

    def escalate_to_agent(self, session_id: str, reason: str) -> Dict[str, Any]:
        """Create human supervisor escalation ticket."""
        esc_id = f"ESC-{uuid.uuid4().hex[:6].upper()}"
        return {
            "tool": "escalate_to_agent",
            "status": "SUCCESS",
            "escalation_id": esc_id,
            "session_id": session_id,
            "assigned_agent": "Senior Support Specialist",
            "reason": reason,
        }

    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Safely validate and execute tool by name."""
        if tool_name not in self._tools:
            return {
                "tool": tool_name,
                "status": "FAILED",
                "message": f"Tool '{tool_name}' not registered in backend Tool Registry.",
            }
        try:
            func = self._tools[tool_name]
            result = func(**kwargs)
            logger.info(f"TOOL EXECUTION SUCCESS | tool={tool_name} | status={result.get('status')}")
            return result
        except Exception as e:
            logger.error(f"TOOL EXECUTION ERROR | tool={tool_name} | error={e}")
            return {
                "tool": tool_name,
                "status": "ERROR",
                "message": f"Error executing tool '{tool_name}': {str(e)}",
            }


tool_registry = ToolRegistry()
