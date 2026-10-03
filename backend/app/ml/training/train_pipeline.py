"""
Training Pipeline — TCS Retail Sentiment Intelligence Platform
==============================================================
Run this script ONCE to train models and save them to disk.
FastAPI loads saved models at startup — it does NOT retrain.

Usage:
    cd backend
    python -m app.ml.training.train_pipeline
"""
import os
import sys
import json
import joblib
import datetime
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report,
)

# Add backend/ to path when run directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from app.ml.datasets.dataset_generator import generate_retail_dataset

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "models")
DATA_SEED = 42
TEST_SIZE = 0.20


from app.ml.text_cleaner import clean_customer_text

def build_pipeline(C: float = 2.0, max_features: int = 5000) -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=max_features,
            preprocessor=clean_customer_text,
            sublinear_tf=True,
        )),
        ("clf", LogisticRegression(
            C=C, max_iter=600, random_state=DATA_SEED, solver="lbfgs",
        )),
    ])


# ─── Evaluation Helpers ──────────────────────────────────────────────────────

def evaluate_pipeline(pipeline: Pipeline, X_test, y_test, labels) -> dict:
    y_pred = pipeline.predict(X_test)
    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, average="macro", zero_division=0))
    rec = float(recall_score(y_test, y_pred, average="macro", zero_division=0))
    f1 = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
    cm = confusion_matrix(y_test, y_pred, labels=labels).tolist()
    report = classification_report(y_test, y_pred, labels=labels, output_dict=True, zero_division=0)
    return {
        "accuracy": round(acc, 4),
        "precision_macro": round(prec, 4),
        "recall_macro": round(rec, 4),
        "f1_macro": round(f1, 4),
        "confusion_matrix": cm,
        "labels": list(labels),
        "classification_report": report,
    }


# ─── Main Training Routine ───────────────────────────────────────────────────

def run_training(n_samples: int = 1200, save: bool = True) -> dict:
    os.makedirs(MODELS_DIR, exist_ok=True)
    print(f"\n{'='*60}")
    print("  TCS Retail Sentiment - Model Training Pipeline")
    print(f"{'='*60}")

    # 1. Generate / Load dataset
    print(f"\n[1/6] Generating synthetic dataset ({n_samples} samples)...")
    df = generate_retail_dataset(n_samples, seed=DATA_SEED)

    # 2. Validate
    print("[2/6] Validating dataset...")
    df = df.dropna(subset=["text", "sentiment", "intent", "emotion"])
    df = df[df["text"].str.strip().str.len() > 5]
    df = df.drop_duplicates(subset=["text"])
    print(f"      Clean records: {len(df)}")

    # 3. Split
    print("[3/6] Splitting train / test (80/20, stratified by sentiment)...")
    X = df["text"]
    y_sent = df["sentiment"]
    y_intent = df["intent"]
    y_emotion = df["emotion"]

    X_train, X_test, ys_train, ys_test = train_test_split(
        X, y_sent, test_size=TEST_SIZE, random_state=DATA_SEED, stratify=y_sent
    )
    _, _, yi_train, yi_test = train_test_split(
        X, y_intent, test_size=TEST_SIZE, random_state=DATA_SEED, stratify=y_sent
    )
    _, _, ye_train, ye_test = train_test_split(
        X, y_emotion, test_size=TEST_SIZE, random_state=DATA_SEED, stratify=y_sent
    )
    print(f"      Train: {len(X_train)} | Test: {len(X_test)}")

    # 4. Train models
    print("[4/6] Training pipelines...")

    sentiment_pipe = build_pipeline(C=2.0, max_features=6000)
    sentiment_pipe.fit(X_train, ys_train)
    print("      [OK] Sentiment pipeline trained")

    intent_pipe = build_pipeline(C=1.5, max_features=5000)
    intent_pipe.fit(X_train, yi_train)
    print("      [OK] Intent pipeline trained")

    emotion_pipe = build_pipeline(C=1.5, max_features=5000)
    emotion_pipe.fit(X_train, ye_train)
    print("      [OK] Emotion pipeline trained")

    # 5. Evaluate
    print("[5/6] Evaluating models on held-out test set...")
    sent_labels = sorted(df["sentiment"].unique())
    intent_labels = sorted(df["intent"].unique())
    emotion_labels = sorted(df["emotion"].unique())

    sent_metrics = evaluate_pipeline(sentiment_pipe, X_test, ys_test, sent_labels)
    intent_metrics = evaluate_pipeline(intent_pipe, X_test, yi_test, intent_labels)
    emotion_metrics = evaluate_pipeline(emotion_pipe, X_test, ye_test, emotion_labels)

    print(f"\n  Sentiment  - Accuracy: {sent_metrics['accuracy']:.4f}  F1: {sent_metrics['f1_macro']:.4f}")
    print(f"  Intent     - Accuracy: {intent_metrics['accuracy']:.4f}  F1: {intent_metrics['f1_macro']:.4f}")
    print(f"  Emotion    - Accuracy: {emotion_metrics['accuracy']:.4f}  F1: {emotion_metrics['f1_macro']:.4f}")

    if sent_metrics["accuracy"] < 0.80:
        print(f"\n  NOTE: Sentiment accuracy ({sent_metrics['accuracy']:.2%}) < 80% target.")
        print("  Reporting actual score. Consider expanding dataset for improvement.")

    # 6. Save
    if save:
        print("\n[6/6] Saving models and metadata...")

        joblib.dump(sentiment_pipe, os.path.join(MODELS_DIR, "sentiment_pipeline.joblib"))
        joblib.dump(intent_pipe,   os.path.join(MODELS_DIR, "intent_pipeline.joblib"))
        joblib.dump(emotion_pipe,  os.path.join(MODELS_DIR, "emotion_pipeline.joblib"))

        metadata = {
            "model_name": "TF-IDF + Logistic Regression",
            "version": "1.0.0",
            "trained_at": datetime.datetime.utcnow().isoformat() + "Z",
            "training_samples": int(len(X_train)),
            "test_samples": int(len(X_test)),
            "total_samples": int(len(df)),
            "seed": DATA_SEED,
            "sentiment": sent_metrics,
            "intent": intent_metrics,
            "emotion": emotion_metrics,
        }
        meta_path = os.path.join(MODELS_DIR, "model_metadata.json")
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"  Models saved -> {os.path.abspath(MODELS_DIR)}/")
        print("  [OK] sentiment_pipeline.joblib")
        print("  [OK] intent_pipeline.joblib")
        print("  [OK] emotion_pipeline.joblib")
        print("  [OK] model_metadata.json")

    print(f"\n{'='*60}")
    print("  Training complete.")
    print(f"{'='*60}\n")
    return metadata


if __name__ == "__main__":
    run_training(n_samples=1200, save=True)
