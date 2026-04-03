"""Tests for the auto-categorization module."""
import pandas as pd
import pytest

from app.etl.categorize import categorize_description, categorize_transactions


@pytest.mark.parametrize("description,expected", [
    ("WHOLEFDS #10 WHOLE FOODS",         "Groceries"),
    ("EMPLOYER DIRECT DEP",              "Income"),
    ("NETFLIX.COM",                      "Subscriptions"),
    ("CHEVRON GAS STATION",              "Transportation"),
    ("ELECTRIC BILL PAYMENT",            "Utilities"),
    ("PLANET FITNESS",                   "Fitness"),
    ("CVS/PHARMACY #8822",               "Healthcare"),
    ("AMAZON.COM*MK1234567",             "Shopping"),
    ("CHIPOTLE 1234",                    "Restaurants"),
    ("RENT PAYMENT",                     "Rent/Mortgage"),
    ("CHASE CREDIT CARD PAYMENT",        "Finance"),
    ("CASINO WITHDRAWAL",                "Entertainment"),
    ("UNKNOWN MERCHANT XYZ",             "Other"),
])
def test_categorize_description(description, expected):
    assert categorize_description(description) == expected


def test_categorize_transactions_adds_column():
    df = pd.DataFrame({
        "description": ["NETFLIX.COM", "WHOLEFDS #10", "EMPLOYER DIRECT DEP"],
        "amount": [-15.99, -82.00, 3200.00],
    })
    result = categorize_transactions(df)
    assert "category" in result.columns
    assert result["category"].tolist() == ["Subscriptions", "Groceries", "Income"]


def test_categorize_transactions_does_not_mutate_input():
    df = pd.DataFrame({"description": ["NETFLIX.COM"], "amount": [-15.99]})
    original_cols = list(df.columns)
    categorize_transactions(df)
    assert list(df.columns) == original_cols
