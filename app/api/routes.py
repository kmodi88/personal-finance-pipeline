"""FastAPI routes for the finance analytics API."""
import os
import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Transaction
from app.etl import pipeline

router = APIRouter(prefix="/api")


# ── Upload & trigger pipeline ──────────────────────────────────────────────────

@router.post("/upload")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a bank CSV and run the full ETL pipeline on it."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        result = pipeline.run(tmp_path, db)
        result["file"] = file.filename
    finally:
        os.unlink(tmp_path)

    return result


# ── Summary / dashboard data ───────────────────────────────────────────────────

@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    """High-level stats: total income, total expenses, net, anomaly count."""
    rows = db.query(Transaction).all()
    if not rows:
        return {"income": 0, "expenses": 0, "net": 0, "anomalies": 0, "transactions": 0}

    income = sum(t.amount for t in rows if t.amount > 0)
    expenses = sum(t.amount for t in rows if t.amount < 0)
    anomalies = sum(1 for t in rows if t.is_anomaly)

    return {
        "income": round(income, 2),
        "expenses": round(expenses, 2),
        "net": round(income + expenses, 2),
        "anomalies": anomalies,
        "transactions": len(rows),
    }


@router.get("/transactions")
def get_transactions(
    limit: int = 100,
    offset: int = 0,
    category: str | None = None,
    anomaly_only: bool = False,
    db: Session = Depends(get_db),
):
    """Paginated list of transactions with optional filters."""
    q = db.query(Transaction)
    if category:
        q = q.filter(Transaction.category == category)
    if anomaly_only:
        q = q.filter(Transaction.is_anomaly == True)  # noqa: E712
    q = q.order_by(Transaction.date.desc())
    total = q.count()
    items = q.offset(offset).limit(limit).all()

    return {
        "total": total,
        "items": [
            {
                "id": t.id,
                "date": str(t.date),
                "description": t.description,
                "amount": t.amount,
                "category": t.category,
                "is_anomaly": t.is_anomaly,
                "anomaly_score": round(t.anomaly_score or 0, 4),
            }
            for t in items
        ],
    }


@router.get("/spending-by-category")
def spending_by_category(db: Session = Depends(get_db)):
    """Aggregate expenses grouped by category (for pie/bar chart)."""
    rows = (
        db.query(Transaction.category, func.sum(Transaction.amount).label("total"))
        .filter(Transaction.amount < 0)
        .group_by(Transaction.category)
        .order_by(func.sum(Transaction.amount))
        .all()
    )
    return [{"category": r.category, "total": round(abs(r.total), 2)} for r in rows]


@router.get("/monthly-cashflow")
def monthly_cashflow(db: Session = Depends(get_db)):
    """Income vs. expenses aggregated by month (for line chart)."""
    rows = db.query(Transaction).all()
    monthly: dict[str, dict] = {}

    for t in rows:
        key = t.date.strftime("%Y-%m")
        if key not in monthly:
            monthly[key] = {"month": key, "income": 0.0, "expenses": 0.0}
        if t.amount > 0:
            monthly[key]["income"] += t.amount
        else:
            monthly[key]["expenses"] += abs(t.amount)

    result = sorted(monthly.values(), key=lambda x: x["month"])
    for r in result:
        r["income"] = round(r["income"], 2)
        r["expenses"] = round(r["expenses"], 2)
        r["net"] = round(r["income"] - r["expenses"], 2)

    return result


@router.get("/anomalies")
def get_anomalies(db: Session = Depends(get_db)):
    """All flagged anomalous transactions sorted by anomaly score."""
    rows = (
        db.query(Transaction)
        .filter(Transaction.is_anomaly == True)  # noqa: E712
        .order_by(Transaction.anomaly_score.desc())
        .all()
    )
    return [
        {
            "id": t.id,
            "date": str(t.date),
            "description": t.description,
            "amount": t.amount,
            "category": t.category,
            "anomaly_score": round(t.anomaly_score or 0, 4),
        }
        for t in rows
    ]
