"""Main ETL pipeline: ingest → categorize → anomaly detection → persist to DB."""
import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session

from app.etl.ingest import load_csv
from app.etl.categorize import categorize_transactions
from app.etl.anomaly import run_pipeline as detect_anomalies
from app.db.models import Transaction


def run(csv_path: str | Path, db: Session) -> dict:
    """Full pipeline for a single CSV file.

    Returns a summary dict with counts of loaded/anomaly rows.
    """
    path = Path(csv_path)

    # 1. Ingest
    df = load_csv(path)

    # 2. Categorize
    df = categorize_transactions(df)

    # 3. Anomaly detection (train + annotate)
    df = detect_anomalies(df)

    # 4. Persist to database (upsert-style: skip duplicates by source_file+date+description+amount)
    inserted = 0
    skipped = 0
    for _, row in df.iterrows():
        exists = (
            db.query(Transaction)
            .filter_by(
                source_file=row["source_file"],
                date=row["date"],
                description=row["description"],
                amount=row["amount"],
            )
            .first()
        )
        if exists:
            skipped += 1
            continue

        txn = Transaction(
            date=row["date"],
            description=row["description"],
            amount=row["amount"],
            category=row["category"],
            is_anomaly=bool(row["is_anomaly"]),
            anomaly_score=float(row["anomaly_score"]),
            source_file=row["source_file"],
        )
        db.add(txn)
        inserted += 1

    db.commit()

    anomaly_count = int(df["is_anomaly"].sum())
    return {
        "file": path.name,
        "total_rows": len(df),
        "inserted": inserted,
        "skipped": skipped,
        "anomalies_detected": anomaly_count,
    }
