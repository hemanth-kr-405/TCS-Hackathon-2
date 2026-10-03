"""
Retail Entity Extractor — Identifies structured entities, bare references, and resolves context pronouns.
"""
import re
from typing import Dict, Any, Optional, List

ORDER_ID_PATTERNS = [
    r"#?order\s*([a-zA-Z0-9]{4,10})\b",
    r"#([a-zA-Z0-9]{4,10})\b",
    r"\border\s*id:?\s*([a-zA-Z0-9]{4,10})\b",
    r"\border\s*([0-9]{4,8})\b",
    r"^([0-9]{4,8})$",  # Bare numeric response like "45821"
]

PRODUCT_KEYWORDS = {
    "laptop": "Wireless Laptop / Notebook",
    "notebook": "Wireless Laptop / Notebook",
    "probook": "Wireless Laptop / Notebook",
    "headphones": "Bluetooth Wireless Headphones",
    "headphone": "Bluetooth Wireless Headphones",
    "shoe": "Footwear",
    "shoes": "Footwear",
    "apparel": "Apparel & Garments",
    "dress": "Apparel & Garments",
    "shirt": "Apparel & Garments",
    "glassware": "Home & Kitchen Glassware",
    "kitchen": "Home & Kitchen Appliances",
    "phone": "Smart Accessories",
}

ACTION_KEYWORDS = {
    "replacement": "replacement",
    "replace": "replacement",
    "exchange": "replacement",
    "refund": "refund",
    "return": "return",
    "cancel": "cancellation",
    "cancellation": "cancellation",
    "track": "tracking",
    "where": "tracking",
    "late": "delivery_delay",
    "delay": "delivery_delay",
}


class RetailEntityExtractor:
    """Extracts Order ID, Product, Action, and Amounts with context reference resolution."""

    def extract(
        self,
        text: str,
        existing_context: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Extracts entities from `text` while maintaining `existing_context`
        and performing reference resolution against recent conversation history.
        """
        extracted = existing_context.copy() if existing_context else {}
        if not text or not isinstance(text, str):
            return extracted

        clean_text = text.strip()
        text_lower = clean_text.lower()

        # 1. Order ID Extraction (including bare numbers like "45821")
        found_order_id = None
        for pattern in ORDER_ID_PATTERNS:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                found_order_id = match.group(1).upper()
                break

        if found_order_id:
            extracted["order_id"] = found_order_id
        elif not extracted.get("order_id") and history:
            # Check if previous assistant message asked for order number
            last_bot_msgs = [h for h in history if h.get("sender") == "bot"]
            if last_bot_msgs:
                last_bot_text = (last_bot_msgs[-1].get("text") or "").lower()
                if any(k in last_bot_text for k in ["order number", "order id", "what's your order", "provide your order"]):
                    # If user text is pure digits or short alphanumeric code
                    bare_match = re.search(r"([a-zA-Z0-9]{4,8})", clean_text)
                    if bare_match:
                        extracted["order_id"] = bare_match.group(1).upper()

        # 2. Product Extraction
        for kw, canonical in PRODUCT_KEYWORDS.items():
            if re.search(rf"\b{kw}\b", text_lower):
                extracted["product"] = canonical
                break

        # 3. Requested Action Extraction
        for kw, action in ACTION_KEYWORDS.items():
            if re.search(rf"\b{kw}\b", text_lower):
                extracted["requested_action"] = action
                break

        # 4. Pronoun & Bare Reference Resolution
        if any(pronoun in text_lower.split() for pronoun in ["it", "this", "that", "them"]):
            extracted["has_pronoun_reference"] = True
            # Reference resolves to previously remembered order_id or product
            if extracted.get("order_id"):
                extracted["resolved_reference"] = f"Order #{extracted['order_id']}"
            elif extracted.get("product"):
                extracted["resolved_reference"] = extracted["product"]

        # 5. Currency / Amount Extraction
        amount_match = re.search(r"(\$\d+(?:\.\d{2})?|\d+\s*dollars)", text_lower)
        if amount_match:
            extracted["amount"] = amount_match.group(1)

        return extracted


entity_extractor = RetailEntityExtractor()
