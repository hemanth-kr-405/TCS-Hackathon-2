TCS Retail AI Platform

AI-powered Retail Customer Sentiment Intelligence Platform that combines real-time sentiment analysis, conversational AI, customer intent and emotion detection, recurring issue identification, agentic retail workflows, escalation intelligence, and business analytics.

Overview

The TCS Retail AI Platform analyzes customer reviews, feedback, surveys, and conversations to understand customer needs and transform them into actionable business insights.

Core Capabilities:

• Real-time Positive / Neutral / Negative sentiment analysis

• Customer intent detection

• Emotion detection

• Conversation context and sentiment trajectory

• Empathetic AI chatbot

• Agentic AI with planning, tool selection, execution, observation, and replanning

• Retail tools such as order lookup, product search, availability, return policy, refund status, and escalation

• Recurring issue detection

• Automatic escalation recommendations

• Business recommendations

• Enterprise analytics dashboard

• ML model evaluation and performance monitoring

AI Architecture

Customer Message

       ↓

Context Analysis

       ↓

Sentiment + Intent + Emotion

       ↓

Agent Planner

       ↓

Tool Selection

       ↓

Tool Execution

       ↓

Observation

       ↓

Replanning

       ↓

Response Validation

       ↓

Empathetic Response

       ↓

Memory + Analytics

The system uses real backend execution rather than static or hardcoded agent traces.

Machine Learning

The initial ML engine uses:

• TF-IDF

• Logistic Regression

• scikit-learn pipelines

• Real train/test evaluation

• Model persistence using joblib

Sentiment classes:

• Positive

• Neutral

• Negative

Supported intents:

• Refund / Return

• Order Tracking

• Technical Support

• Product Inquiry

• Complaint

• Praise

• General Inquiry

Supported emotions:

• Anger

• Frustration

• Joy

• Satisfaction

• Disappointment

• Neutral

Model evaluation includes:

• Accuracy

• Precision

• Recall

• F1 Score

• Confusion Matrix

• Classification Report

All displayed metrics are generated from actual model evaluation.

Agentic AI

The agent can dynamically:

1. Understand a customer request

2. Create a plan

3. Select a tool

4. Execute the tool

5. Observe the result

6. Replan when necessary

7. Validate the response

8. Update conversation memory

9. Escalate when appropriate

Available retail tools:

• Order Lookup

• Product Search

• Product Availability

• Return Policy

• Refund Status

• Customer Profile

• Knowledge Base

• Human Escalation

Example:

"My order ORD1024 is late and can I return it?"

→ Detect delivery + return intent

→ order_lookup

→ Observe actual order status

→ Replan

→ return_policy

→ Observe policy

→ Generate validated response

Enterprise Dashboard

The platform provides:

• Overview Dashboard

• AI Command Center

• AI Operations Center

• Dataset Explorer

• Feedback Analysis

• Sentiment Analytics

• Customer Intent

• Recurring Issues

• Escalations

• Business Recommendations

• Conversation History

• Model Evaluation

• Settings

The dashboard uses real backend data and does not rely on hardcoded analytics.

Technology Stack

Backend:

• Python

• FastAPI

• SQLAlchemy

• SQLite

• scikit-learn

• Pandas

• NumPy

• NLTK

• Pydantic

• Pytest

• HTTPX

Frontend:

• React

• TypeScript

• Vite

• Tailwind CSS

• Axios

• Recharts

• Framer Motion

• Lucide React

Project Structure

TCS-Hackathon-2/

├── backend/

│   ├── app/

│   │   ├── api/

│   │   ├── agent/

│   │   ├── database/

│   │   ├── ml/

│   │   ├── models/

│   │   ├── routers/

│   │   ├── schemas/

│   │   └── services/

│   ├── tests/

│   └── requirements.txt

├── frontend/

│   ├── src/

│   │   ├── components/

│   │   ├── pages/

│   │   ├── services/

│   │   ├── types/

│   │   └── utils/

│   └── package.json

├── data/

│   ├── raw/

│   ├── processed/

│   └── synthetic/

├── models/

├── docs/

├── README.md

└── .gitignore

Running the Project

Backend:

cd backend

python -m venv .venv

Windows:

.venv\Scripts\activate

Install:

pip install -r requirements.txt

Start:

uvicorn app.main:app --reload --port 8000

Frontend:

cd frontend

npm install

npm run dev

Frontend: http://localhost:5173

Backend: http://localhost:8000

Testing

Backend:

python -m pytest backend/tests -v

Frontend:

cd frontend

npm run build

Security

Never commit:

• API keys

• Passwords

• Database credentials

• Authentication tokens

• Production secrets

Use .env files locally and commit only .env.example.

Development Phases

Phase 1 — Core Platform

• FastAPI backend

• Database

• ML engine

• Sentiment analysis

• Intent detection

• Emotion detection

• Analytics

• Enterprise dashboard

• Model evaluation

Phase 2 — Conversational Intelligence

• Conversation context

• Sentiment trajectory

• Empathetic chatbot

• Escalation intelligence

• Conversation history

Phase 2A — Agentic Retail AI

• Agent orchestrator

• Agent state

• Tool registry

• Retail tools

• Multi-step execution

• Tool observation

• Replanning

• Agent memory

• Real execution trace

Future Phases

• Advanced transformer models

• PostgreSQL

• Advanced issue clustering

• Improved recommendation engine

• Production deployment

• Enterprise authentication

• Advanced monitoring

Goal

Transform retail customer conversations into intelligent actions and measurable business insights:

Understand → Analyze → Act → Resolve → Learn

Built for the TCS Hackathon.
