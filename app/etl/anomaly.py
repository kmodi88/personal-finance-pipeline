"""Anomaly detection using scikit-learn Isolation Forest on transaction amounts."""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
from pathlib import Path

MODEL_PATH = Path(__file__).parent.parent.parent / "data" / "isolation_forest.joblib"

# contamination = expected proportion of anomalies in the dataset
CONTAMINATION = 0.05


def train_model(df: pd.DataFrame) -> IsolationForest:
    """Train an Isolation Forest on transaction amounts and save the model."""
    amounts = df[["amount"]].values
    model = IsolationForest(
        n_estimators=100,
        contamination=CONTAMINATION,
        random_state=42,
    )
    model.fit(amounts)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    return model


def load_model() -> IsolationForest:
    """Load a previously trained model from disk."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError("No trained model found. Run train_model() first.")
    return joblib.load(MODEL_PATH)


def detect_anomalies(df: pd.DataFrame, model: IsolationForest | None = None) -> pd.DataFrame:
    """Add 'is_anomaly' and 'anomaly_score' columns to a transactions DataFrame.

    IsolationForest returns:
      -1 → anomaly  |  1 → normal
    anomaly_score: higher (less negative) = more anomalous.
    """
    df = df.copy()

    if model is None:
        try:
            model = load_model()
        except FileNotFoundError:
            model = train_model(df)

    amounts = df[["amount"]].values
    predictions = model.predict(amounts)          # -1 or 1
    scores = model.decision_function(amounts)      # lower score = more anomalous

    df["is_anomaly"] = predictions == -1
    # Normalize score to 0–1 range where 1 = most anomalous
    df["anomaly_score"] = 1 - (scores - scores.min()) / (scores.max() - scores.min() + 1e-9)

    return df


def run_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """Train model on df, then annotate df with anomaly flags. Returns annotated df."""
    model = train_model(df)
    return detect_anomalies(df, model)
