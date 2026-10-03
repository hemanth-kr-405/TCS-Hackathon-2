import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models.db_models import FeedbackItem, RecurringIssue, BusinessRecommendation, Escalation, ChatSession
from app.ml.datasets.dataset_generator import generate_retail_dataset
from app.ml.inference.inference_engine import inference_engine

from app.routers import sentiment, chat, feedback, analytics, escalations, model_eval

# Ensure DB tables are created and ML models loaded
Base.metadata.create_all(bind=engine)
inference_engine.load()

def seed_initial_data():
    """Seeds rich initial dataset if database is newly initialized."""
    db = SessionLocal()
    try:
        if db.query(FeedbackItem).count() == 0:
            print("Seeding synthetic retail feedback dataset...")
            df = generate_retail_dataset(500)
            
            # Seed Feedback items
            feedback_objs = []
            for idx, row in df.iterrows():
                obj = FeedbackItem(
                    customer_id=row.get('customer_id', f"cust_{idx}"),
                    text=row['text'],
                    source=row.get('source', row.get('channel', 'review')),
                    category=row['category'],
                    product=row.get('product', row.get('product_name', None)),
                    rating=int(row['rating']) if 'rating' in row and row['rating'] else None,
                    sentiment=row['sentiment'],
                    sentiment_score=float(row['sentiment_score']),
                    confidence=float(row.get('confidence', 0.85)),
                    intent=row['intent'],
                    emotion=row['emotion'],
                    aspect=row['aspect'],
                    is_synthetic=True,
                    created_at=datetime.datetime.utcnow()
                )
                feedback_objs.append(obj)
            db.bulk_save_objects(feedback_objs)

            # Seed Recurring Issues
            issues_data = [
                {
                    "issue_key": "ISSUE_REFUND_DELAY",
                    "title": "Delayed Refund Processing on Returned Apparel",
                    "category": "Billing & Refunds",
                    "description": "Multiple customers reporting 14+ day delay receiving credit card refunds for apparel exchanges.",
                    "frequency": 42,
                    "severity": "High",
                    "average_sentiment": -0.82,
                    "status": "Open"
                },
                {
                    "issue_key": "ISSUE_DAMAGED_PACKAGING",
                    "title": "Damaged Courier Packaging for Glassware & Kitchen",
                    "category": "Shipping & Delivery",
                    "description": "Shipping transit causes box crushing on Home & Kitchen fragility packages.",
                    "frequency": 29,
                    "severity": "High",
                    "average_sentiment": -0.76,
                    "status": "In Progress"
                },
                {
                    "issue_key": "ISSUE_APP_TRACKING_BUG",
                    "title": "Order Tracking Status Not Refreshing in Mobile App",
                    "category": "Technical Support",
                    "description": "Customers see 'In Transit' even after parcel delivery confirmation by carrier.",
                    "frequency": 35,
                    "severity": "Medium",
                    "average_sentiment": -0.55,
                    "status": "Open"
                },
                {
                    "issue_key": "ISSUE_SIZING_DISCREPANCY",
                    "title": "Size Chart Discrepancy for Men's & Women's Footwear",
                    "category": "Fashion",
                    "description": "Footwear fits 1 to 2 sizes smaller than standardized size guide specifications.",
                    "frequency": 18,
                    "severity": "Medium",
                    "average_sentiment": -0.48,
                    "status": "Resolved"
                },
                {
                    "issue_key": "ISSUE_HEADPHONE_BATTERY",
                    "title": "Headphone Battery Drain after Firmware Update 2.1",
                    "category": "Electronics",
                    "description": "Battery degrades from 20 hours to 4 hours after recent firmware release.",
                    "frequency": 51,
                    "severity": "Critical",
                    "average_sentiment": -0.91,
                    "status": "Open"
                }
            ]

            for iss in issues_data:
                db.add(RecurringIssue(**iss))

            # Seed Business Recommendations
            recs_data = [
                {
                    "recommendation_key": "REC_AUTOMATE_REFUNDS",
                    "title": "Automate Standard Apparel Return Credits",
                    "category": "Billing & Operations",
                    "description": "Implement instant credit card refund triggers upon first carrier scan to eliminate 14-day refund delay complaint spike.",
                    "priority": "High",
                    "estimated_impact": "+18% CSAT improvement in Fashion category",
                    "status": "New"
                },
                {
                    "recommendation_key": "REC_REINFORCE_PACKAGING",
                    "title": "Upgrade Fragile Item Outer Packaging",
                    "category": "Logistics & Supply Chain",
                    "description": "Switch Home & Kitchen glassware fulfillment to double-walled corrugated boxes with foam inserts.",
                    "priority": "High",
                    "estimated_impact": "-65% damage return claims",
                    "status": "In Review"
                },
                {
                    "recommendation_key": "REC_FIRMWARE_HOTFIX",
                    "title": "Deploy Emergency Firmware Hotfix v2.1.1",
                    "category": "Electronics Engineering",
                    "description": "Fix Bluetooth power state management issue causing rapid battery discharge on wireless headphones.",
                    "priority": "Critical",
                    "estimated_impact": "Mitigate critical brand reputation risk",
                    "status": "Implemented"
                }
            ]

            for rec in recs_data:
                db.add(BusinessRecommendation(**rec))

            # Seed Initial Demo Chat Session & Escalation Sample
            demo_sess = ChatSession(
                session_id="chat_demo_escalation",
                customer_id="cust_demo",
                customer_name="Sarah Jenkins",
                status="Escalated",
                conversation_state="ESCALATED",
                initial_sentiment="Negative",
                current_sentiment="Negative",
                sentiment_score=-0.89,
                sentiment_trend="Declining",
                is_escalated=True,
                assigned_agent="Senior Support Team"
            )
            db.add(demo_sess)
            db.commit()

            esc_sample = Escalation(
                session_id="chat_demo_escalation",
                customer_name="Sarah Jenkins",
                severity="Critical",
                reason="High customer anger: Charged twice for defective headphones and refund delayed by 2 weeks.",
                sentiment_score=-0.89,
                status="Pending",
                assigned_agent="Senior Resolution Team"
            )
            db.add(esc_sample)

            db.commit()
            print("Dataset and initial operational records successfully seeded.")
    except Exception as e:
        print(f"Error during startup data seeding: {e}")
    finally:
        db.close()

# Seed initial data on startup
seed_initial_data()

@asynccontextmanager
async def lifespan(app: FastAPI):
    inference_engine.load()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers under API Prefix (/api and /api/v1 for compatibility)
for prefix in [settings.API_V1_STR, "/api/v1"]:
    app.include_router(sentiment.router, prefix=prefix)
    app.include_router(chat.router, prefix=prefix)
    app.include_router(feedback.router, prefix=prefix)
    app.include_router(analytics.router, prefix=prefix)
    app.include_router(escalations.router, prefix=prefix)
    app.include_router(model_eval.router, prefix=prefix)


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs_url": "/docs",
        "version": settings.VERSION
    }
