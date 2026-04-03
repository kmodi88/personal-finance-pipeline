"""CSV ingestion: reads bank export CSVs, normalizes columns, and returns a DataFrame."""
import pandas as pd
from pathlib import Path


REQUIRED_COLUMNS = {"date", "description", "amount"}

# Common column aliases from different bank exports
COLUMN_ALIASES: dict[str, str] = {
    "transaction date": "date",
    "trans date": "date",
    "posting date": "date",
    "memo": "description",
    "payee": "description",
    "merchant": "description",
    "debit": "amount",
    "credit": "amount",
    "transaction amount": "amount",
}


def load_csv(filepath: str | Path) -> pd.DataFrame:
    """Load and normalize a bank CSV export into a standard DataFrame.

    Returns a DataFrame with columns: date (datetime.date), description (str), amount (float).
    Negative amounts = expenses, positive = income.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {filepath}")

    # encoding='utf-8-sig' strips the BOM (\ufeff) that Excel-saved CSVs often include
    df = pd.read_csv(path, encoding="utf-8-sig")

    # Normalize column names: lowercase + strip whitespace
    df.columns = [c.strip().lower() for c in df.columns]

    # Apply aliases for non-standard column names
    df = df.rename(columns=COLUMN_ALIASES)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"CSV is missing required columns: {missing}. "
            f"Columns found: {list(df.columns)}"
        )

    # Parse date
    df["date"] = pd.to_datetime(df["date"]).dt.date

    # Ensure amount is float
    df["amount"] = pd.to_numeric(df["amount"].astype(str).str.replace(",", ""), errors="coerce")
    df = df.dropna(subset=["amount"])

    # Keep only what we need + any extra columns
    df["description"] = df["description"].str.strip()
    df["source_file"] = path.name

    return df[["date", "description", "amount", "source_file"]].reset_index(drop=True)
