# API Reference — TCS Retail AI Platform

This document describes key REST API endpoints provided by the FastAPI backend (`http://localhost:8000`).

---

## 💬 Chat & Orchestration Endpoints

### 1. Execute Agentic Chat Pipeline
- **Method**: `POST`
- **Path**: `/api/v1/chat/orchestrate`
- **Description**: Submits customer message through the 10-step AI Orchestrator.

#### Request Body
```json
{
  "message": "Where is my order #45821?",
  "customer_id": "DEMO-1024",
  "history": [],
  "preferred_provider": "local"
}
```

#### Response Body
```json
{
  "response": "Your order #45821 has shipped and is scheduled to arrive on 28 Sep.",
  "sentiment": {
    "label": "Negative",
    "score": -0.65,
    "emotions": { "frustration": 0.72 }
  },
  "intent": {
    "primary_intent": "Delivery Complaint",
    "confidence": 0.92
  },
  "ai_decision": {
    "interaction_mode": "RETAIL_SUPPORT",
    "selected_tool": "get_order_status",
    "rag_required": false,
    "customer_risk_score": 0.42
  },
  "tool_result": {
    "tool": "get_order_status",
    "status": "SUCCESS",
    "output": { "order_id": "ORDER-45821", "status": "Shipped", "eta": "28 Sep" }
  },
  "sources": []
}
```

---

### 2. Reset Demo State
- **Method**: `POST`
- **Path**: `/api/v1/chat/reset-demo`
- **Description**: Resets demo session data and seeds baseline customer profile (`Sarah Jenkins`, `DEMO-1024`).

#### Response Body
```json
{
  "status": "SUCCESS",
  "message": "Demo state reset successfully.",
  "customer": {
    "customer_id": "DEMO-1024",
    "name": "Sarah Jenkins",
    "risk_score": 0.15
  }
}
```

---

## 📊 Analytics & Evaluation Endpoints

### 3. Evaluate Single Review Text
- **Method**: `POST`
- **Path**: `/api/v1/sentiment/predict`
- **Description**: Evaluates text for multi-dimensional sentiment polarity and emotion probabilities.

#### Request Body
```json
{
  "text": "The fabric torn on first wash. Very disappointed!"
}
```

#### Response Body
```json
{
  "sentiment": "Negative",
  "confidence": 0.94,
  "score": -0.88,
  "emotions": {
    "anger": 0.81,
    "frustration": 0.92,
    "joy": 0.02
  }
}
```

---

### 4. Fetch AI Operations Metrics
- **Method**: `GET`
- **Path**: `/api/v1/aiops/telemetry`
- **Description**: Returns live control plane status, tool invocation counts, and measured AI quality metrics.

#### Response Body
```json
{
  "status": "ONLINE",
  "tool_calls": 318,
  "rag_queries": 427,
  "groundedness_score": 0.94,
  "fallback_rate": 0.024,
  "registered_tools": 8
}
```
