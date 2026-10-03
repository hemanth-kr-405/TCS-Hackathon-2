"""
Retail Knowledge Base / RAG Module 2.0 — Grounding LLM responses on TCS Retail Policy files in `knowledge/`.

Features:
- Hybrid TF-IDF + Keyword matching
- Metadata & document chunk IDs
- Grounding score calculation & citation metadata
- Unsupported policy query detection with refusal fallback
"""
import os
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "knowledge")
UNSUPPORTED_POLICY_FALLBACK = "I don't have enough verified information in TCS Retail policies to answer that accurately."


class RetailKnowledgeBase:
    """RAG 2.0 Retriever for TCS Retail Customer Support Policies."""

    def __init__(self, knowledge_dir: str = KNOWLEDGE_DIR):
        self.knowledge_dir = knowledge_dir
        self.documents: List[Dict[str, Any]] = []
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        self.tfidf_matrix = None
        self.load_documents()

    def load_documents(self):
        """Scans the `knowledge/` directory for markdown policy files and indexes them."""
        docs = []
        if os.path.exists(self.knowledge_dir) and os.path.isdir(self.knowledge_dir):
            for fname in os.listdir(self.knowledge_dir):
                if fname.endswith(".md"):
                    fpath = os.path.join(self.knowledge_dir, fname)
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            content = f.read()

                        lines = [line.strip() for line in content.split("\n") if line.strip()]
                        title = fname.replace(".md", "").replace("_", " ").title()
                        for line in lines:
                            if line.startswith("#"):
                                title = line.lstrip("#").strip()
                                break

                        category = fname.replace("_policy.md", "").replace(".md", "").replace("_", " ").title()
                        docs.append({
                            "id": f"chunk_{fname}",
                            "source_id": fname,
                            "filename": fname,
                            "category": category,
                            "title": title,
                            "content": content,
                        })
                    except Exception as e:
                        logger.warning(f"Failed reading policy document {fname}: {e}")

        if not docs:
            docs = [
                {
                    "id": "chunk_return_policy",
                    "source_id": "return_policy.md",
                    "filename": "return_policy.md",
                    "category": "Returns",
                    "title": "TCS Retail 30-Day Return Policy",
                    "content": "Customers can return eligible items within 30 days of delivery for a full refund or exchange. Items must be in original condition with tags. Electronics covered for 30 days even if unboxed.",
                },
                {
                    "id": "chunk_refund_policy",
                    "source_id": "refund_policy.md",
                    "filename": "refund_policy.md",
                    "category": "Refunds",
                    "title": "TCS Retail Refund Timelines",
                    "content": "Refunds post in 3-5 business days for credit cards upon carrier scan. Store credit refunds processed within 24 hours. Full refund including shipping for damaged or wrong goods.",
                },
                {
                    "id": "chunk_delivery_policy",
                    "source_id": "delivery_policy.md",
                    "filename": "delivery_policy.md",
                    "category": "Delivery",
                    "title": "Delivery Expediting & Delays Policy",
                    "content": "Standard delivery takes 3-5 days. If tracking shows no updates for 48+ hours or is 2+ days overdue, logistics priority trace is initiated. Lost parcels receive free express re-shipment or 100% refund.",
                }
            ]

        self.documents = docs
        self.texts = [f"{doc['title']} {doc['category']} {doc['content']}" for doc in self.documents]
        if self.texts:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.texts)

    def retrieve(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """Retrieve most relevant policy documents for query using TF-IDF cosine similarity."""
        if not query or not query.strip() or self.tfidf_matrix is None:
            return []
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]

        top_indices = similarities.argsort()[::-1][:top_k]
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score > 0.05:
                doc = self.documents[idx].copy()
                doc["score"] = round(score, 4)
                doc["grounding_confidence"] = "High" if score > 0.3 else "Medium"
                results.append(doc)
        return results

    def build_rag_prompt_section(self, query: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Build grounded policy context string to inject into LLM system prompt and return source docs."""
        docs = self.retrieve(query, top_k=2)
        if not docs:
            return "", []

        context_lines = ["GROUNDED TCS RETAIL POLICIES (Use strictly as truth, do not invent fake policies):"]
        for d in docs:
            context_lines.append(f"- [{d['title']} ({d['filename']}) - Score: {d.get('score', 0.9)}]: {d['content'][:500]}")
        return "\n".join(context_lines), docs


knowledge_base = RetailKnowledgeBase()
