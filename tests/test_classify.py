"""Tests for flagging, corrections, and CSV export."""

import io

import numpy as np
import pandas as pd

from src.classify import (
    EXPORT_COLUMNS,
    apply_corrections,
    classify_transactions,
    to_csv_bytes,
)


class FakeProvider:
    """Returns fixed answers so tests don't depend on a real model."""

    name = "fake"

    def __init__(self, answers):
        self.answers = answers

    def predict(self, descriptions):
        return [self.answers[d] for d in descriptions]


def make_df():
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-03-02", "2026-03-03", "2026-03-04", "2026-03-05"]),
            "description": ["Deposit", "Adobe", "Mystery shop", "Borderline"],
            "amount": [650.0, -20.0, -30.0, -40.0],
        }
    )


ANSWERS = {
    "Adobe": ("software", 0.9),
    "Mystery shop": ("travel", 0.2),
    "Borderline": ("equipment", 0.45),
}


def test_low_confidence_is_flagged():
    out = classify_transactions(make_df(), FakeProvider(ANSWERS), threshold=0.45)
    assert out.loc[1, "needs_review"] == False  # noqa: E712
    assert out.loc[2, "needs_review"] == True  # noqa: E712


def test_confidence_equal_to_threshold_is_not_flagged():
    out = classify_transactions(make_df(), FakeProvider(ANSWERS), threshold=0.45)
    assert out.loc[3, "needs_review"] == False  # noqa: E712


def test_inflows_are_blank_and_never_flagged():
    out = classify_transactions(make_df(), FakeProvider(ANSWERS))
    assert out.loc[0, "predicted_category"] == ""
    assert np.isnan(out.loc[0, "confidence"])
    assert out.loc[0, "needs_review"] == False  # noqa: E712


def test_category_starts_as_the_guess():
    out = classify_transactions(make_df(), FakeProvider(ANSWERS))
    assert out.loc[2, "category"] == "travel"


def test_no_expenses_does_not_crash():
    df = make_df().iloc[:1]
    out = classify_transactions(df, FakeProvider({}))
    assert out["needs_review"].sum() == 0


def test_corrections_mark_only_changed_rows():
    classified = classify_transactions(make_df(), FakeProvider(ANSWERS))
    edited = classified[classified["amount"] < 0][["category"]].copy()
    edited.loc[2, "category"] = "software"  # person fixes the wrong guess
    final = apply_corrections(classified, edited)
    assert final["corrected"].tolist() == [False, False, True, False]
    assert final.loc[2, "category"] == "software"
    assert final.loc[2, "predicted_category"] == "travel"  # original guess is kept


def test_csv_export_has_expected_columns_and_clean_dates():
    classified = classify_transactions(make_df(), FakeProvider(ANSWERS))
    edited = classified[classified["amount"] < 0][["category"]].copy()
    edited.loc[2, "category"] = "software"
    final = apply_corrections(classified, edited)

    exported = pd.read_csv(io.BytesIO(to_csv_bytes(final)))
    assert list(exported.columns) == EXPORT_COLUMNS
    assert exported.loc[0, "date"] == "2026-03-02"  # no 00:00:00
    assert exported["corrected"].tolist() == [False, False, True, False]