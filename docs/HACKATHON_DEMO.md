# TCS Hackathon — 5-Minute Pitch & Demo Script 🎬

Follow this step-by-step demonstration guide to present the **TCS Retail AI Platform** to hackathon judges.

---

## ⏱️ Pitch Timeline (5 Minutes)

### 0:00 — Problem Statement & Platform Intro (30s)
- **Presenter**: *"Traditional retail chatbots are either rigid menu bots or unpredictable AI models that hallucinate policies. We built the TCS Retail AI Platform — an enterprise-grade agentic customer intelligence system."*
- **Action**: Show main dashboard. Toggle **Presentation Mode** in top right header to demonstrate judge-ready UI.

### 0:30 — Scenario A: Happy Customer Interaction (30s)
- **Action**: Click **"Preset A: Happy Customer"** in Chatbot View.
- **Query**: *"I loved the silk dress I bought! Is it in stock in navy blue?"*
- **Highlight**:
  - Show positive sentiment score ($\mathbf{+0.85}$, Joy).
  - Open **AI Decision Trace**: Point out `Interaction Mode: GENERAL_CHAT`, `Tool: check_product_availability`.

### 1:00 — Scenario B: Delivery Complaint & Tool Sandbox (40s)
- **Action**: Click **"Preset B: Delivery Complaint"**.
- **Query**: *"Where is my order #45821? It was supposed to arrive yesterday!"*
- **Highlight**:
  - Show negative sentiment ($\mathbf{-0.65}$, Frustration).
  - Show **Tool Execution Box**: `get_order_status(order_id="ORDER-45821")` -> Output: `Shipped, ETA: 28 Sep`.
  - Highlight how the LLM safely answered using validated backend tool output.

### 1:40 — Scenario D: Refund Policy Query & RAG 2.0 Grounding (40s)
- **Action**: Click **"Preset D: Refund Policy"**.
- **Query**: *"What is your return policy for worn items?"*
- **Highlight**:
  - Open **RAG Source Viewer** drawer.
  - Show cited policy chunk: `return_policy.md (Score: 0.91)`.
  - Point out **ANSWER GROUNDED ✓** badge and lack of policy hallucination.

### 2:20 — Scenario C: Angry Customer & Proactive Supervisor Handoff (40s)
- **Action**: Click **"Preset C: Angry Customer"**.
- **Query**: *"My second order was also damaged! I want an immediate refund or I will escalate!"*
- **Highlight**:
  - Show Customer Memory tracking: Customer `Sarah Jenkins` (3 past complaints).
  - Point to **Customer Risk Score: 82% (HIGH)**.
  - Show **🚨 Supervisor Handoff Package** with recommended action buttons.

### 3:00 — Scenario E & Reset State (30s)
- **Action**: Click **"Preset E: Sentiment Recovery"**, then click **"✨ Reset Demo"** to restore baseline state.

### 3:30 — AI Control Plane & Telemetry (40s)
- **Action**: Navigate to **AI Operations Center** (`/aiops`).
- **Highlight**:
  - Point out real-time tool execution metrics, groundedness score ($94\%$), fallback rate ($2.4\%$), and registered tools table.

### 4:10 — Business Intelligence & Model Evaluation (50s)
- **Action**: Navigate to **Dataset Explorer** (23,486 reviews) and **Business Intelligence**.
- **Highlight**:
  - Show root-cause clustering (e.g. delivery delays in Bengaluru warehouse).
  - Conclude with value proposition: *"Moving from conversational AI to an autonomous retail intelligence platform."*
