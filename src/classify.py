"""Classify transactions, flag uncertain ones for review, apply corrections, export CSV."""

CATEGORIES = ["equipment", "software", "marketing", "travel", "office supplies"]

# Dropdown choices in the review table ("unknown" is what the keyword rules say when stuck)
CATEGORY_OPTIONS = CATEGORIES + ["unknown"]

# Predictions less confident than this get flagged for a human to check
DEFAULT_THRESHOLD = 0.45

EXPORT_COLUMNS = [
    "date", "description", "amount", "category",
    "predicted_category", "confidence", "needs_review", "corrected",
]


def classify_transactions(df, provider, threshold=DEFAULT_THRESHOLD):
    """Guess a category for every expense (negative amount) using the given provider.

    Adds these columns:
      predicted_category: the provider's guess
      confidence:         how sure the provider is (0 to 1)
      needs_review:       True when confidence is below the threshold
      category:           starts as the guess; the person can edit it
    Inflows (positive amounts) are left blank because we only categorize expenses.
    """
    out = df.copy()
    is_expense = out["amount"] < 0

    out["predicted_category"] = ""
    out["confidence"] = float("nan")

    if is_expense.any():
        guesses = provider.predict(out.loc[is_expense, "description"].tolist())
        out.loc[is_expense, "predicted_category"] = [category for category, _ in guesses]
        out.loc[is_expense, "confidence"] = [confidence for _, confidence in guesses]

    # Inflows have no confidence (blank), so they are never flagged
    out["needs_review"] = is_expense & (out["confidence"] < threshold)
    out["category"] = out["predicted_category"]
    return out


def apply_corrections(classified, edited):
    """Copy the person's edited categories back into the full table.
    Adds a 'corrected' column that is True where the final category differs from the guess."""
    final = classified.copy()
    final.loc[edited.index, "category"] = edited["category"]
    final["corrected"] = final["category"] != final["predicted_category"]
    return final


def to_csv_bytes(final):
    """Turn the final table into CSV bytes that a download button can send."""
    export = final[EXPORT_COLUMNS].copy()
    export["date"] = export["date"].dt.date  # drop the 00:00:00 time part
    return export.to_csv(index=False).encode("utf-8")