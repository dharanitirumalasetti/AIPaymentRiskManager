from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.transaction import PredictionResponse, TransactionInput
from app.services.model_service import model_service
from app.services.risk_engine import score_transaction, to_feature_row
from app.services.storage import alerts, analytics, init_db, list_transactions, save_transaction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("risklens")


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    try:
        model_service.load()
        logger.info("Loaded model version %s", model_service.model_version)
    except FileNotFoundError as exc:
        logger.warning(str(exc))
    yield


app = FastAPI(
    title="RiskLens AI API",
    description="Synthetic-data payment risk scoring prototype.",
    version="1.0.0",
    lifespan=lifespan,
)

origins = os.getenv("API_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5175",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "model_version": model_service.model_version}


@app.post("/api/predict", response_model=PredictionResponse)
def predict(payload: TransactionInput) -> PredictionResponse:
    try:
        row = to_feature_row(payload)
        probability = model_service.predict_probability(row)
        risk = score_transaction(probability, row)
        timestamp = datetime.now(timezone.utc)
        response = {
            "transaction_id": f"txn_{uuid4().hex[:10]}",
            "fraud_probability": round(probability, 4),
            "risk_score": risk.score,
            "risk_level": risk.level,
            "decision": risk.decision,
            "reasons": risk.reasons,
            "model_version": model_service.model_version,
            "timestamp": timestamp.isoformat(),
        }
        save_transaction(response, row)
        return PredictionResponse(**response)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/transactions")
def transactions(limit: int = 100) -> list:
    return list_transactions(limit=min(max(limit, 1), 500))


@app.get("/api/analytics")
def get_analytics() -> dict:
    return analytics()


@app.get("/api/alerts")
def get_alerts(limit: int = 10) -> list:
    return alerts(limit=min(max(limit, 1), 50))
