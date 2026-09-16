from __future__ import annotations

import os
from pathlib import Path

import joblib
import pandas as pd

from app.services.risk_engine import FEATURES


class ModelService:
    def __init__(self) -> None:
        root = Path(__file__).resolve().parents[2]
        default_path = root / "models" / "risk_model.joblib"
        self.model_path = Path(os.getenv("MODEL_PATH", default_path))
        self.bundle = None
        self.model_version = "untrained"

    def load(self) -> None:
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {self.model_path}. Run `python train.py` from backend/."
            )
        self.bundle = joblib.load(self.model_path)
        self.model_version = self.bundle.get("model_version", "risklens-synthetic-v1")

    def predict_probability(self, row: dict) -> float:
        if self.bundle is None:
            self.load()
        frame = pd.DataFrame([row], columns=FEATURES)
        model = self.bundle["model"]
        return float(model.predict_proba(frame)[0][1])


model_service = ModelService()
