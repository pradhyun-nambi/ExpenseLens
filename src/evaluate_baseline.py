"""Measure how well the keyword baseline does on labeled transactions.

Run from the project root with:  python -m src.evaluate_baseline
"""

from pathlib import Path

import pandas as pd

from src.baseline import predict_category

LABELED_PATH = Path(__file__).parent.parent / "data" / "labeled_transactions.csv"


def load_labeled_expenses(path=LABELED_PATH):
    """Read the labeled CSV and keep only expenses that have a correct answer."""
    df = pd.read_csv(path)
    # Expenses are negative amounts; inflows have a blank category, so we skip them
    return df[(df["amount"] < 0) & df["category"].notna()].copy()


def score_baseline(df):
    """Add a 'predicted' column (the baseline's guess) and a 'correct' column (True/False)."""
    df = df.copy()
    df["predicted"] = df["description"].map(predict_category)
    df["correct"] = df["predicted"] == df["category"]
    return df


if __name__ == "__main__":
    scored = score_baseline(load_labeled_expenses())

    print(f"Rows scored: {len(scored)}")
    print(f"Overall accuracy: {scored['correct'].mean():.1%}")
    print(f"Rows with no keyword match: {(scored['predicted'] == 'unknown').sum()}")

    print("\nAccuracy by category:")
    by_category = scored.groupby("category")["correct"].mean().map("{:.1%}".format)
    print(by_category.to_string())

    print("\nMistakes (description, right answer, baseline's guess):")
    mistakes = scored.loc[~scored["correct"], ["description", "category", "predicted"]]
    print(mistakes.to_string(index=False))