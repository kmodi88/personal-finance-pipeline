"""Tests for the Isolation Forest anomaly detection module."""
import pandas as pd
import pytest
import numpy as np

from app.etl.anomaly import train_model, detect_anomalies, run_pipeline


@pytest.fixture
def normal_df():
    """DataFrame of mostly normal transactions with one clear outlier."""
    amounts = [-15.99, -82.45, -54.20, -37.99, 3200.00, -6.75, -23.10,
               -18.50, -9.99, -91.30, -24.99, -12.85, -17.99, -14.99,
               -61.40, 750.00, -78.20, -112.34, -3.99, -31.75,
               -5000.00]  # ← obvious outlier
    return pd.DataFrame({
        "description": [f"TXN_{i}" for i in range(len(amounts))],
        "amount": amounts,
    })


def test_run_pipeline_adds_columns(normal_df):
    result = run_pipeline(normal_df)
    assert "is_anomaly" in result.columns
    assert "anomaly_score" in result.columns


def test_is_anomaly_is_boolean(normal_df):
    result = run_pipeline(normal_df)
    assert result["is_anomaly"].dtype == bool


def test_anomaly_score_in_range(normal_df):
    result = run_pipeline(normal_df)
    assert result["anomaly_score"].between(0, 1).all()


def test_outlier_is_flagged(normal_df):
    """The -5000 transaction should be detected as anomalous."""
    result = run_pipeline(normal_df)
    outlier_row = result[result["amount"] == -5000.00]
    assert not outlier_row.empty
    assert bool(outlier_row["is_anomaly"].values[0]) is True


def test_detect_anomalies_does_not_mutate_input(normal_df):
    model = train_model(normal_df)
    original_cols = list(normal_df.columns)
    detect_anomalies(normal_df, model)
    assert list(normal_df.columns) == original_cols


def test_anomaly_count_within_contamination(normal_df):
    """Anomaly count should be close to contamination rate (5%)."""
    result = run_pipeline(normal_df)
    rate = result["is_anomaly"].mean()
    assert rate <= 0.20  # generous upper bound
