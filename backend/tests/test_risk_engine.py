from app.schemas.transaction import TransactionInput
from app.services.risk_engine import classify, score_transaction, to_feature_row


def test_classify_thresholds():
    assert classify(10)[0] == "LOW"
    assert classify(45)[0] == "MEDIUM"
    assert classify(80)[0] == "HIGH"


def test_high_risk_signals_raise_score():
    payload = TransactionInput(
        amount=90000,
        transaction_frequency=25,
        transaction_hour=2,
        location_mismatch=True,
        device_change=True,
        account_age_days=3,
        previous_transaction_count=0,
        failed_transaction_count=5,
        international_transaction=True,
        unusual_transaction=True,
    )
    result = score_transaction(0.75, to_feature_row(payload))
    assert result.score >= 70
    assert result.level == "HIGH"
    assert result.reasons

