import re

def clean_customer_text(text: str) -> str:
    """Clean and normalize raw customer feedback text for TF-IDF vectorization."""
    if not isinstance(text, str) or not text.strip():
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s!?,.]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
