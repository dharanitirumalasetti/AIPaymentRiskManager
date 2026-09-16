from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_invalid_prediction_input():
    response = client.post("/api/predict", json={"amount": -1})
    assert response.status_code == 422


def test_prediction_endpoint():
    payload = {
        "amount": 75000,
        "transaction_frequency": 26,
        "transaction_hour": 1,
        "location_mismatch": True,
        "device_change": True,
        "account_age_days": 5,
        "previous_transaction_count": 1,
        "failed_transaction_count": 4,
        "international_transaction": True,
        "unusual_transaction": True,
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["risk_level"] in {"LOW", "MEDIUM", "HIGH"}
    assert 0 <= body["risk_score"] <= 100
    assert body["reasons"]

