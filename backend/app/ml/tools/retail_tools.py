"""
Backend Tool / Function Registry — Authoritative Data Tools for TCS Retail Support.
"""
import datetime
import uuid
from typing import Dict, Any, Optional, List, Tuple
from app.ml.rag.knowledge_base import knowledge_base

# Deterministic Mock Retail Database for Orders & Products
MOCK_ORDER_DATABASE = {
    "45821": {
        "order_id": "45821",
        "customer_name": "Sarah Jenkins",
        "status": "In Transit",
        "carrier": "FedEx Express",
        "tracking_number": "TRK9482019482",
        "product": "Wireless Laptop / Notebook",
        "sku": "SKU-LAP-902",
        "order_date": (datetime.datetime.utcnow() - datetime.timedelta(days=2)).strftime("%Y-%m-%d"),
        "estimated_delivery": (datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
        "issue_flag": "delivery_delay",
        "paid_amount": "$899.00",
        "delivery_address": "104 Market St, San Francisco, CA",
        "refund_status": "Eligible for Refund / Exchange",
    },
    "10092": {
        "order_id": "10092",
        "customer_name": "Priya Sharma",
        "status": "Delivered",
        "carrier": "BlueDart Express",
        "tracking_number": "TRK8820194102",
        "product": "Bluetooth Wireless Headphones",
        "sku": "SKU-AUD-110",
        "order_date": (datetime.datetime.utcnow() - datetime.timedelta(days=5)).strftime("%Y-%m-%d"),
        "estimated_delivery": datetime.datetime.utcnow().strftime("%Y-%m-%d"),
        "issue_flag": "damaged_product",
        "paid_amount": "$149.50",
        "delivery_address": "45 Park Avenue, New York, NY",
        "refund_status": "Refund Approved & Processing ($149.50)",
    },
    "77201": {
        "order_id": "77201",
        "customer_name": "David Miller",
        "status": "Processing",
        "carrier": "Standard Courier",
        "tracking_number": "TRK7720190012",
        "product": "Home & Kitchen Glassware Set",
        "sku": "SKU-KIT-304",
        "order_date": datetime.datetime.utcnow().strftime("%Y-%m-%d"),
        "estimated_delivery": (datetime.datetime.utcnow() + datetime.timedelta(days=3)).strftime("%Y-%m-%d"),
        "issue_flag": None,
        "paid_amount": "$79.99",
        "delivery_address": "88 Pine St, Seattle, WA",
        "refund_status": "N/A",
    },
}

MOCK_PRODUCT_DATABASE = {
    "wireless laptop": {
        "product_name": "TCS ProBook 15 Wireless Laptop",
        "sku": "SKU-LAP-902",
        "category": "Electronics",
        "price": "$899.00",
        "stock": "In Stock (42 units available)",
        "warranty": "1-Year Limited Hardware Warranty",
        "return_eligible": True,
        "return_window_days": 30,
    },
    "headphones": {
        "product_name": "TCS Sonic Pro Wireless Headphones",
        "sku": "SKU-AUD-110",
        "category": "Electronics",
        "price": "$149.50",
        "stock": "In Stock (120 units available)",
        "warranty": "1-Year Battery & Hardware Warranty",
        "return_eligible": True,
        "return_window_days": 30,
    },
    "glassware": {
        "product_name": "TCS Premium Glassware Dining Set",
        "sku": "SKU-KIT-304",
        "category": "Home & Kitchen",
        "price": "$79.99",
        "stock": "In Stock (15 units available)",
        "warranty": "Breakage Guarantee on Delivery",
        "return_eligible": True,
        "return_window_days": 30,
    },
}


def get_order_status(order_id: str) -> Dict[str, Any]:
    """Retrieve verified order tracking and shipping status."""
    clean_id = str(order_id).strip().upper().replace("#", "")
    if clean_id in MOCK_ORDER_DATABASE:
        return {"tool": "get_order_status", "success": True, "data": MOCK_ORDER_DATABASE[clean_id]}
    return {
        "tool": "get_order_status",
        "success": False,
        "message": f"Order #{clean_id} not found in live logistics database. Please verify the order number.",
    }


def get_product_details(product_id_or_name: str) -> Dict[str, Any]:
    """Retrieve product specifications, warranty info, and return policy eligibility."""
    query = str(product_id_or_name).strip().lower()
    for key, data in MOCK_PRODUCT_DATABASE.items():
        if key in query or query in key or data["sku"].lower() in query:
            return {"tool": "get_product_details", "success": True, "data": data}
    return {
        "tool": "get_product_details",
        "success": False,
        "message": f"Product '{product_id_or_name}' catalog specs not found. Default 30-day warranty applies.",
    }


def get_refund_status(order_id: str) -> Dict[str, Any]:
    """Retrieve verified refund transaction status."""
    clean_id = str(order_id).strip().upper().replace("#", "")
    if clean_id in MOCK_ORDER_DATABASE:
        order = MOCK_ORDER_DATABASE[clean_id]
        return {
            "tool": "get_refund_status",
            "success": True,
            "order_id": clean_id,
            "refund_status": order.get("refund_status", "Approved & Processing"),
            "estimated_credit_days": "3-5 business days",
            "amount": order["paid_amount"],
        }
    return {
        "tool": "get_refund_status",
        "success": False,
        "message": f"No active refund record found for Order #{clean_id}.",
    }


def get_delivery_estimate(order_id: str) -> Dict[str, Any]:
    """Retrieve estimated delivery date and carrier trace."""
    res = get_order_status(order_id)
    if res["success"]:
        d = res["data"]
        return {
            "tool": "get_delivery_estimate",
            "success": True,
            "order_id": d["order_id"],
            "status": d["status"],
            "estimated_delivery": d["estimated_delivery"],
            "carrier": d["carrier"],
            "tracking_number": d["tracking_number"],
        }
    return res


def search_policy(query: str) -> Dict[str, Any]:
    """Retrieve grounded retail policy documents for query."""
    docs = knowledge_base.retrieve(query, top_k=2)
    return {"tool": "search_policy", "success": True, "documents": docs}


def create_escalation(session_id: str, customer_name: str = "Customer", reason: str = "Customer frustration", priority: str = "High") -> Dict[str, Any]:
    """Trigger real escalation record creation for supervisor intervention."""
    esc_id = f"esc_{uuid.uuid4().hex[:8]}"
    return {
        "tool": "create_escalation",
        "success": True,
        "escalation_id": esc_id,
        "session_id": session_id,
        "customer_name": customer_name,
        "assigned_agent": "Senior Support Team Specialist",
        "priority": priority,
        "status": "Pending",
        "reason": reason,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }


def execute_tools_for_request(
    extracted_entities: Dict[str, Any],
    intent: str,
    user_message: str,
    session_id: str = "chat_default",
    customer_name: str = "Customer",
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Evaluates context, intent, and entities to execute appropriate backend tools.
    Returns Tuple of [list of tool result dicts, formatted string to inject into LLM system prompt].
    """
    tool_results = []
    prompt_lines = []

    order_id = extracted_entities.get("order_id")
    product = extracted_entities.get("product")
    action = extracted_entities.get("requested_action")

    # 1. Order Status / Delivery Tool
    if order_id and (intent in ("Order_Tracking", "Shipping_Delay", "Order_Status", "general_query", "Issue_Report", "RETAIL_DATA_REQUEST") or any(k in user_message.lower() for k in ["order", "track", "where", "delivery", "status"])):
        res = get_order_status(order_id)
        tool_results.append(res)
        if res["success"]:
            o = res["data"]
            prompt_lines.append(
                f"VERIFIED LIVE ORDER SYSTEM DATA FOR ORDER #{order_id}:\n"
                f"- Customer Name: {o['customer_name']}\n"
                f"- Product: {o['product']}\n"
                f"- Current Status: {o['status']}\n"
                f"- Carrier & Tracking: {o['carrier']} ({o['tracking_number']})\n"
                f"- Estimated Delivery Date: {o['estimated_delivery']}\n"
                f"- Total Paid: {o['paid_amount']}"
            )

    # 2. Refund Status Tool
    if order_id and (action == "refund" or intent in ("Refund_Request", "Billing_Issue")):
        res = get_refund_status(order_id)
        tool_results.append(res)
        if res["success"]:
            prompt_lines.append(
                f"VERIFIED REFUND SYSTEM DATA FOR ORDER #{order_id}:\n"
                f"- Refund Status: {res['refund_status']}\n"
                f"- Estimated Credit Arrival: {res['estimated_credit_days']}\n"
                f"- Refund Amount: {res['amount']}"
            )

    # 3. Product Catalog Tool
    if product or intent == "Product_Query":
        prod_query = product or user_message
        res = get_product_details(prod_query)
        if res["success"]:
            tool_results.append(res)
            p = res["data"]
            prompt_lines.append(
                f"VERIFIED PRODUCT CATALOG DATA:\n"
                f"- Product: {p['product_name']} ({p['sku']})\n"
                f"- Price: {p['price']} | Stock: {p['stock']}\n"
                f"- Warranty: {p['warranty']} (Return Window: {p['return_window_days']} days)"
            )

    # 4. Policy RAG Tool
    if intent in ("Return_Policy", "Refund_Request", "Warranty_Claim", "Policy_Query") or any(k in user_message.lower() for k in ["policy", "return", "refund", "warranty", "deliver"]):
        res = search_policy(user_message)
        tool_results.append(res)

    formatted_prompt_text = "\n\n".join(prompt_lines) if prompt_lines else ""
    return tool_results, formatted_prompt_text
