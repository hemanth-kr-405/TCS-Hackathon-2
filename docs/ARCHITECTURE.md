# System Architecture — TCS Retail AI Platform

This document describes the end-to-end technical architecture, component responsibilities, data flow, and safety guardrails of the **TCS Retail AI Platform**.

---

## 🏗️ High-Level System Architecture

```
User / Customer / Supervisor
              │
      ┌───────▼────────┐
      │ React Frontend │ (TypeScript + Vite + Tailwind)
      └───────┬────────┘
              │ REST / JSON API
      ┌───────▼────────┐
      │ FastAPI Server │ (Python 3.11 Backend)
      └───────┬────────┘
              │
      ┌───────▼───────────────────────────────────────────────┐
      │               AGENTIC AI ORCHESTRATOR                  │
      │  (backend/app/ml/ai_orchestrator.py)                  │
      ├───────────┬───────────┬───────────┬───────────┬───────┤
      │ Sentiment │  Intent   │ Customer  │  RAG 2.0  │ Tool  │
      │  Engine   │  Engine   │  Memory   │ Retriever │ Sandbox
      └─────┬─────┴─────┬─────┴─────┬─────┴─────┬─────┴───┬───┘
            │           │           │           │         │
            └───────────┴───────────┼───────────┴─────────┘
                                    ▼
                          LLM PROVIDER ROUTER
                        (OpenAI / Grok / Local)
                                    │
                            RESPONSE VALIDATOR
                                    │
            ┌───────────────────────┼───────────────────────┐
            ▼                       ▼                       ▼
     Customer Response      Supervisor Handoff       AI Ops Telemetry
```

---

## 🧩 Component Responsibilities

### 1. React Frontend (`frontend/`)
- **Chatbot View**: Displays multi-turn messages, interactive decision trace badge ("How AI Decided"), live tool execution sandbox logs, preset demo scenario buttons, and RAG source drawer.
- **AI Operations View**: Telemetry dashboard showing operational status, tool call counts, and empirical AI quality scores (Relevance, Groundedness, Fallback rate).
- **Dataset Explorer**: Renders review distributions for the 23,486 Women's E-Commerce Clothing Reviews dataset with interactive filtering and CSV upload support.
- **Business Intelligence**: Visualizes department sentiment bar charts, recurring problem clusters, and AI-recommended mitigation strategies.

### 2. FastAPI Backend Core (`backend/app/`)
- **API Routers (`app/routers/` & `app/api/`)**: Manages endpoints for chat orchestration, demo reset (`/chat/reset-demo`), sentiment evaluation, and model benchmarks.
- **Data Models (`app/models/` & `app/database.py`)**: SQLite database handling session persistent memory, raw review datasets, and execution trace logs.

### 3. Agentic AI Core (`backend/app/ml/`)
- **AI Orchestrator (`ai_orchestrator.py`)**: Runs a 10-step sequence: Intake -> Sentiment -> Intent -> Memory -> RAG -> Decision -> Tool Execution -> Prompt Assembly -> Response Validation -> State Update.
- **Decision Engine (`decision_engine.py`)**: Evaluates context to produce structured `AIDecision` objects containing `interaction_mode`, `selected_tool`, `rag_required`, and `customer_risk_score`.
- **Tool Registry (`tool_registry.py`)**: Secure execution environment containing 8 validated retail tools (`get_order_status`, `check_refund_eligibility`, `escalate_to_agent`, etc.).
- **Customer Memory (`customer_memory.py`)**: Tracks multi-session sentiment trajectory, unresolved issue history, and calculates composite risk levels.
- **RAG 2.0 Retriever (`rag/knowledge_base.py`)**: Hybrid TF-IDF policy index providing similarity confidence, citations, and unsupported-claim fallbacks.

---

## 🔒 Security Architecture & Guardrails

1. **No Direct Code Execution**: The LLM is never given direct access to execute code or write to databases. It generates structured tool requests which are parsed and validated by the backend execution engine.
2. **Unsupported Policy Fallback**: If policy grounding confidence is low, the RAG engine forces an empirical fallback (*"I don't have enough verified policy information..."*) to eliminate policy hallucinations.
3. **Environment Isolation**: API secrets are loaded exclusively via environment variables and never logged or returned in client payloads.
