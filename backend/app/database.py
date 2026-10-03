from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Handle SQLite vs PostgreSQL arguments
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def _ensure_schema():
    """Ensure missing columns in SQLite tables exist."""
    try:
        with engine.connect() as conn:
            # Check chat_sessions columns
            res = conn.exec_driver_sql("PRAGMA table_info(chat_sessions)").fetchall()
            cols = [r[1] for r in res] if res else []
            if cols:
                if "conversation_state" not in cols:
                    conn.exec_driver_sql("ALTER TABLE chat_sessions ADD COLUMN conversation_state VARCHAR(50) DEFAULT 'NEW'")
                if "current_issue" not in cols:
                    conn.exec_driver_sql("ALTER TABLE chat_sessions ADD COLUMN current_issue VARCHAR(100)")
                if "current_issue_category" not in cols:
                    conn.exec_driver_sql("ALTER TABLE chat_sessions ADD COLUMN current_issue_category VARCHAR(100)")
                if "current_issue_severity" not in cols:
                    conn.exec_driver_sql("ALTER TABLE chat_sessions ADD COLUMN current_issue_severity VARCHAR(20)")
                if "escalation_score" not in cols:
                    conn.exec_driver_sql("ALTER TABLE chat_sessions ADD COLUMN escalation_score FLOAT DEFAULT 0.0")
                if "escalation_reasons" not in cols:
                    conn.exec_driver_sql("ALTER TABLE chat_sessions ADD COLUMN escalation_reasons TEXT")

            # Check chat_messages columns
            res_m = conn.exec_driver_sql("PRAGMA table_info(chat_messages)").fetchall()
            cols_m = [r[1] for r in res_m] if res_m else []
            if cols_m:
                if "turn_number" not in cols_m:
                    conn.exec_driver_sql("ALTER TABLE chat_messages ADD COLUMN turn_number INTEGER DEFAULT 1")
                if "confidence" not in cols_m:
                    conn.exec_driver_sql("ALTER TABLE chat_messages ADD COLUMN confidence FLOAT DEFAULT 0.85")
                if "issue" not in cols_m:
                    conn.exec_driver_sql("ALTER TABLE chat_messages ADD COLUMN issue VARCHAR(100)")
                if "sentiment_change" not in cols_m:
                    conn.exec_driver_sql("ALTER TABLE chat_messages ADD COLUMN sentiment_change BOOLEAN DEFAULT 0")
                if "sentiment_direction" not in cols_m:
                    conn.exec_driver_sql("ALTER TABLE chat_messages ADD COLUMN sentiment_direction VARCHAR(20) DEFAULT 'stable'")
    except Exception:
        pass


_ensure_schema()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
