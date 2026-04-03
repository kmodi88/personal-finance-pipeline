"""Tests for the CSV ingestion module."""
import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path

from app.etl.ingest import load_csv


def write_csv(content: str) -> str:
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
    tmp.write(content)
    tmp.close()
    return tmp.name


def test_load_standard_csv():
    path = write_csv("Date,Description,Amount\n2026-01-01,STARBUCKS,-6.75\n2026-01-02,PAYROLL,3000.00\n")
    try:
        df = load_csv(path)
        assert len(df) == 2
        assert list(df.columns) == ["date", "description", "amount", "source_file"]
        assert df["amount"].iloc[0] == -6.75
        assert df["amount"].iloc[1] == 3000.00
    finally:
        os.unlink(path)


def test_load_csv_with_aliases():
    """Columns with bank-specific names should be normalized."""
    path = write_csv("Transaction Date,Memo,Transaction Amount\n2026-02-01,NETFLIX,-15.99\n")
    try:
        df = load_csv(path)
        assert "date" in df.columns
        assert "description" in df.columns
        assert "amount" in df.columns
    finally:
        os.unlink(path)


def test_load_csv_missing_column_raises():
    path = write_csv("Date,Amount\n2026-01-01,-10.00\n")
    try:
        with pytest.raises(ValueError, match="missing required columns"):
            load_csv(path)
    finally:
        os.unlink(path)


def test_load_csv_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_csv("/nonexistent/path/file.csv")


def test_source_file_is_set():
    path = write_csv("Date,Description,Amount\n2026-01-01,TEST,-1.00\n")
    try:
        df = load_csv(path)
        assert df["source_file"].iloc[0] == Path(path).name
    finally:
        os.unlink(path)


def test_amount_with_commas():
    path = write_csv('Date,Description,Amount\n2026-01-01,BIG PURCHASE,"-1,234.56"\n')
    try:
        df = load_csv(path)
        assert df["amount"].iloc[0] == pytest.approx(-1234.56)
    finally:
        os.unlink(path)
