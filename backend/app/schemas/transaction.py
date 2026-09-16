from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class TransactionInput(BaseModel):
    amount: float = Field(..., ge=1, le=1_000_000)
    transaction_frequency: int = Field(..., ge=0, le=250)
    transaction_hour: int = Field(..., ge=0, le=23)
    location_mismatch: bool = False
    device_change: bool = False
    account_age_days: int = Field(..., ge=0, le=3650)
    previous_transaction_count: int = Field(..., ge=0, le=10000)
    failed_transaction_count: int = Field(..., ge=0, le=100)
    international_transaction: bool = False
    unusual_transaction: bool = False


class PredictionResponse(BaseModel):
    transaction_id: str
    fraud_probability: float
    risk_score: int
    risk_level: str
    decision: str
    reasons: List[str]
    model_version: str
    timestamp: datetime


class TransactionRecord(PredictionResponse):
    amount: float
    transaction_hour: int

