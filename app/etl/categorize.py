"""Rule-based auto-categorization using keyword matching on transaction descriptions."""
import re
import pandas as pd

# Each entry: (category_name, [keywords...])
# Order matters — first match wins
CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("Income",         ["direct dep", "payroll", "freelance payment", "zelle from"]),
    ("Rent/Mortgage",  ["rent payment", "mortgage", "hoa"]),
    ("Groceries",      ["wholefds", "whole foods", "trader joe", "kroger", "safeway", "publix", "aldi", "sprouts"]),
    ("Restaurants",    ["chipotle", "mcdonald", "starbucks", "dunkin", "doordash", "uber eats", "grubhub", "restaurant", "dining", "pizza", "taco", "burger", "diner", "cafe"]),
    ("Transportation", ["uber trip", "lyft", "chevron", "shell oil", "bp#", "exxon", "mobil", "gas station", "mta", "transit", "parking"]),
    ("Utilities",      ["electric bill", "gas bill", "water bill", "internet", "comcast", "att bill", "verizon bill", "utility"]),
    ("Subscriptions",  ["netflix", "spotify", "hulu", "disney+", "apple.com/bill", "amazon prime", "youtube premium", "hbo max"]),
    ("Healthcare",     ["doctor copay", "dental", "pharmacy", "cvs", "walgreens", "rite aid", "health", "medical", "copay", "hospital"]),
    ("Shopping",       ["amazon.com", "target", "walmart", "best buy", "costco", "ebay", "etsy", "macy", "nordstrom"]),
    ("Fitness",        ["planet fitness", "equinox", "gym", "peloton", "ymca"]),
    ("Finance",        ["credit card payment", "loan payment", "chase", "bank of america", "atm withdrawal", "transfer"]),
    ("Entertainment",  ["casino", "ticketmaster", "amc theatre", "regal cinema", "steam", "playstation", "xbox"]),
]


def categorize_description(description: str) -> str:
    """Return the category for a single transaction description."""
    lower = description.lower()
    for category, keywords in CATEGORY_RULES:
        if any(kw in lower for kw in keywords):
            return category
    return "Other"


def categorize_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Add a 'category' column to a transactions DataFrame."""
    df = df.copy()
    df["category"] = df["description"].apply(categorize_description)
    return df
