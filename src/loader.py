"""Load and validate a transactions CSV for ExpenseLens."""

import pandas as pd

# The columns every CSV must have.
REQUIRED_COLUMNS = ["date", "description", "amount"]


class CSVValidationError(ValueError):
    """Raised when the CSV is missing, empty, or has bad data."""


def _row_list(mask, df, limit=5):
    """Turn a True/False mask into readable row numbers.
    +2 because the header is row 1 and pandas counts from 0."""
    rows = (df.index[mask] + 2).tolist()
    text = ", ".join(str(r) for r in rows[:limit])
    if len(rows) > limit:
        text += f" ... and {len(rows) - limit} more"
    return text


def load_transactions(source):
    """Read a CSV (file path or uploaded file) and return a clean DataFrame.

    Raises CSVValidationError with a plain-English message if anything is wrong.
    """
    # 1. Empty file (no content at all)
    try:
        df = pd.read_csv(source)
    except pd.errors.EmptyDataError:
        raise CSVValidationError("The CSV file is empty (no transactions found).") from None

    # 2. Header only, no data rows
    if df.empty:
        raise CSVValidationError("The CSV file is empty (no transactions found).")

    # 3. Missing columns (ignore capitalization and stray spaces in headers)
    df.columns = [str(c).strip().lower() for c in df.columns]
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise CSVValidationError(
            f"Missing required column(s): {', '.join(missing)}. "
            f"Expected columns: {', '.join(REQUIRED_COLUMNS)}."
        )

    # 4. Bad dates: errors="coerce" turns anything unreadable into NaT (blank)
    dates = pd.to_datetime(df["date"], errors="coerce")
    bad_dates = dates.isna()
    if bad_dates.any():
        raise CSVValidationError(
            "Invalid or missing date in row(s): "
            f"{_row_list(bad_dates, df)}. Use a consistent format like YYYY-MM-DD."
        )

    # 5. Non-numeric amounts: same trick with numbers
    amounts = pd.to_numeric(df["amount"], errors="coerce")
    bad_amounts = amounts.isna()
    if bad_amounts.any():
        examples = df["amount"][bad_amounts].head(3).tolist()
        raise CSVValidationError(
            f"Non-numeric amount in row(s): {_row_list(bad_amounts, df)} "
            f"(found {examples}). Amounts must be plain numbers like -49.99."
        )

    # Everything passed: return only the columns we need, with proper types
    clean = df[REQUIRED_COLUMNS].copy()
    clean["date"] = dates
    clean["amount"] = amounts
    return clean