from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support, roc_auc_score
from sklearn.model_selection import train_test_split

from app.services.risk_engine import FEATURES
from train import DATA_PATH, MODEL_PATH, generate_synthetic_data


ROOT = Path(__file__).resolve().parent
REPORT_PATH = ROOT / "reports" / "evaluation.json"


def evaluate() -> dict:
    if not DATA_PATH.exists():
        DATA_PATH.parent.mkdir(exist_ok=True)
        generate_synthetic_data().to_csv(DATA_PATH, index=False)
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Model missing. Run `python train.py` first.")

    df = pd.read_csv(DATA_PATH)
    _, x_test, _, y_test = train_test_split(
        df[FEATURES], df["is_fraud"], test_size=0.25, random_state=42, stratify=df["is_fraud"]
    )
    bundle = joblib.load(MODEL_PATH)
    model = bundle["model"]
    probability = model.predict_proba(x_test)[:, 1]
    threshold = float(bundle.get("decision_threshold", 0.5))
    prediction = (probability >= threshold).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, prediction, average="binary", zero_division=0
    )
    report = {
        "dataset": "Synthetic transaction data for demonstration only",
        "model_name": bundle.get("model_name"),
        "model_version": bundle.get("model_version"),
        "decision_threshold": round(threshold, 2),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
        "roc_auc": round(float(roc_auc_score(y_test, probability)), 4),
        "confusion_matrix": confusion_matrix(y_test, prediction).tolist(),
        "classification_report": classification_report(y_test, prediction, output_dict=True, zero_division=0),
        "candidate_scores": bundle.get("candidate_scores", {}),
    }
    REPORT_PATH.parent.mkdir(exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    evaluate()
