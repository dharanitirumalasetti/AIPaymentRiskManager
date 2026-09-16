from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


FEATURES = [
    "amount",
    "transaction_frequency",
    "transaction_hour",
    "location_mismatch",
    "device_change",
    "account_age_days",
    "previous_transaction_count",
    "failed_transaction_count",
    "international_transaction",
    "unusual_transaction",
]


@dataclass
class RiskResult:
    score: int
    level: str
    decision: str
    reasons: List[str]


def to_feature_row(payload) -> Dict[str, float]:
    return {
        "amount": float(payload.amount),
        "transaction_frequency": int(payload.transaction_frequency),
        "transaction_hour": int(payload.transaction_hour),
        "location_mismatch": int(payload.location_mismatch),
        "device_change": int(payload.device_change),
        "account_age_days": int(payload.account_age_days),
        "previous_transaction_count": int(payload.previous_transaction_count),
        "failed_transaction_count": int(payload.failed_transaction_count),
        "international_transaction": int(payload.international_transaction),
        "unusual_transaction": int(payload.unusual_transaction),
    }


def behavioral_signals(row: Dict[str, float]) -> tuple[int, List[str]]:
    points = 0
    reasons: List[str] = []

    checks = [
        (row["amount"] >= 50000, 14, "Unusually high transaction amount"),
        (row["transaction_frequency"] >= 20, 12, "Abnormal transaction frequency"),
        (row["transaction_hour"] <= 5, 8, "Transaction occurred during unusual hours"),
        (row["location_mismatch"] == 1, 12, "Location mismatch detected"),
        (row["device_change"] == 1, 10, "New or changed device detected"),
        (row["account_age_days"] <= 14, 9, "Very new account"),
        (row["previous_transaction_count"] <= 2, 5, "Limited transaction history"),
        (row["failed_transaction_count"] >= 3, 12, "Multiple failed transaction attempts"),
        (row["international_transaction"] == 1, 7, "International transaction"),
        (row["unusual_transaction"] == 1, 11, "Marked as unusual compared with customer behavior"),
    ]

    for triggered, weight, reason in checks:
        if triggered:
            points += weight
            reasons.append(reason)

    return min(points, 55), reasons


def classify(score: int) -> tuple[str, str]:
    if score >= 70:
        return "HIGH", "REVIEW / BLOCK"
    if score >= 30:
        return "MEDIUM", "STEP-UP VERIFICATION / MONITOR"
    return "LOW", "APPROVE"


def score_transaction(fraud_probability: float, row: Dict[str, float]) -> RiskResult:
    signal_points, reasons = behavioral_signals(row)
    ml_points = round(float(fraud_probability) * 70)
    score = max(0, min(100, ml_points + signal_points))
    level, decision = classify(score)

    if not reasons:
        reasons.append("No major behavioral risk indicators detected")
    elif len(reasons) > 5:
        reasons = reasons[:5]

    return RiskResult(score=score, level=level, decision=decision, reasons=reasons)

