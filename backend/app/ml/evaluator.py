from typing import Dict, Any
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report
from app.ml.sentiment_engine import SentimentEngine
from app.ml.dataset_generator import generate_retail_dataset

def evaluate_model_performance() -> Dict[str, Any]:
    """
    Evaluates ML model performance on a test split of synthetic/retail dataset.
    Returns empirical accuracy, precision, recall, F1, confusion matrix, and classification report.
    """
    df = generate_retail_dataset(600)
    
    X = df['text']
    y = df['sentiment']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

    engine = SentimentEngine()
    engine.sentiment_pipeline.fit(X_train, y_train)

    y_pred = engine.sentiment_pipeline.predict(X_test)

    labels = ["Negative", "Neutral", "Positive"]
    acc = float(accuracy_score(y_test, y_pred))
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='macro')
    cm = confusion_matrix(y_test, y_pred, labels=labels)

    report_dict = classification_report(y_test, y_pred, output_dict=True)

    return {
        "model_name": "TF-IDF + LogisticRegression (Baseline)",
        "accuracy": round(acc, 4),
        "precision_macro": round(float(precision), 4),
        "recall_macro": round(float(recall), 4),
        "f1_macro": round(float(f1), 4),
        "confusion_matrix": cm.tolist(),
        "labels": labels,
        "classification_report": report_dict,
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "last_trained": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    }
