from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List


def db_path() -> Path:
    root = Path(__file__).resolve().parents[2]
    return Path(os.getenv("DATABASE_PATH", root / "data" / "risklens.db"))


def connect() -> sqlite3.Connection:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                amount REAL NOT NULL,
                transaction_hour INTEGER NOT NULL,
                risk_score INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                decision TEXT NOT NULL,
                fraud_probability REAL NOT NULL,
                reasons TEXT NOT NULL,
                payload TEXT NOT NULL
            )
            """
        )


def save_transaction(record: Dict[str, Any], payload: Dict[str, Any]) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["transaction_id"],
                record["timestamp"],
                payload["amount"],
                payload["transaction_hour"],
                record["risk_score"],
                record["risk_level"],
                record["decision"],
                record["fraud_probability"],
                json.dumps(record["reasons"]),
                json.dumps(payload),
            ),
        )


def list_transactions(limit: int = 100) -> List[Dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM transactions ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()
    return [_format(row) for row in rows]


def analytics() -> Dict[str, Any]:
    with connect() as conn:
        rows = conn.execute("SELECT risk_level, risk_score, timestamp FROM transactions").fetchall()
    total = len(rows)
    counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    trend: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        counts[row["risk_level"]] += 1
        day = row["timestamp"][:10]
        trend.setdefault(day, {"date": day, "avgRisk": 0, "count": 0})
        trend[day]["avgRisk"] += row["risk_score"]
        trend[day]["count"] += 1
    for item in trend.values():
        item["avgRisk"] = round(item["avgRisk"] / item["count"], 1)
    return {
        "total_transactions": total,
        "high_risk": counts["HIGH"],
        "medium_risk": counts["MEDIUM"],
        "low_risk": counts["LOW"],
        "estimated_fraud_rate": round((counts["HIGH"] / total) * 100, 2) if total else 0,
        "risk_distribution": [{"name": key, "value": value} for key, value in counts.items()],
        "trend": sorted(trend.values(), key=lambda item: item["date"]),
    }


def alerts(limit: int = 10) -> List[Dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM transactions
            WHERE risk_level = 'HIGH'
            ORDER BY risk_score DESC, timestamp DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [_format(row) for row in rows]


def _format(row: sqlite3.Row) -> Dict[str, Any]:
    data = dict(row)
    data["reasons"] = json.loads(data["reasons"])
    return data
