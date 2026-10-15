"""Edge cases: odd inputs that could break the classifier, review flags, or export."""

import io

import pandas as pd

from src.classify import (
    CATEGORY_OPTIONS,
    EXPORT_COLUMNS,
    apply_corrections,
    classify_transactions,
    to_csv_bytes,
)
from src.evaluate_baseline import load_labeled_expenses
from src.model import dedupe_descriptions, train_model
from src.providers import TfidfProvider


class FakeProvider:
    name = "fake"

    def __init__(self, category="travel", confidence=0.5):
        self.category = category
        self.confidence = confidence

    def predict(self, descriptions):
        return [(self.category, self.confidence) for _ in descriptions]


def make_df(amounts):
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-03-01"] * len(amounts)),
            "description": [f"Item {i}" for i in range(len(amounts))],
            "amount": amounts,
        }
    )


def edited_expenses(classified):
    return classified[classified["amount"] < 0][["category"]].copy()


def test_zero_amount_is_neither_inflow_nor_expense():
    out = classify_transactions(make_df([0.0, -10.0]), FakeProvider())
    assert out.loc[0, "predicted_category"] == ""
    assert out.loc[0, "needs_review"] == False  # noqa: E712


def test_empty_table_does_not_crash():
    empty = pd.DataFrame(
        {
            "date": pd.to_datetime([]),
            "description": pd.Series([], dtype=str),
            "amount": pd.Series([], dtype=float),
        }
    )
    classified = classify_transactions(empty, FakeProvider())
    final = apply_corrections(classified, edited_expenses(classified))
    exported = pd.read_csv(io.BytesIO(to_csv_bytes(final)))
    assert len(exported) == 0
    assert list(exported.columns) == EXPORT_COLUMNS


def test_all_inflows_means_nothing_to_review():
    out = classify_transactions(make_df([100.0, 200.0]), FakeProvider())
    assert out["needs_review"].sum() == 0


def test_no_edits_means_no_corrections():
    classified = classify_transactions(make_df([-1.0, -2.0, 5.0]), FakeProvider())
    final = apply_corrections(classified, edited_expenses(classified))
    assert final["corrected"].sum() == 0


def test_changing_a_category_back_is_not_a_correction():
    classified = classify_transactions(make_df([-1.0, -2.0]), FakeProvider("travel"))
    edited = edited_expenses(classified)
    edited.loc[0, "category"] = "software"
    edited.loc[0, "category"] = "travel"  # person changes their mind
    final = apply_corrections(classified, edited)
    assert final["corrected"].sum() == 0


def test_threshold_extremes():
    df = make_df([-1.0, -2.0])
    assert classify_transactions(df, FakeProvider(confidence=0.99), threshold=0.0)["needs_review"].sum() == 0
    assert classify_transactions(df, FakeProvider(confidence=0.99), threshold=1.0)["needs_review"].sum() == 2


def test_classify_does_not_modify_the_input_table():
    df = make_df([-1.0, 5.0])
    before = df.copy()
    classify_transactions(df, FakeProvider())
    pd.testing.assert_frame_equal(df, before)


def test_export_with_unknown_category():
    classified = classify_transactions(make_df([-1.0]), FakeProvider("unknown", 0.0))
    final = apply_corrections(classified, edited_expenses(classified))
    exported = pd.read_csv(io.BytesIO(to_csv_bytes(final)))
    assert exported.loc[0, "category"] == "unknown"
    assert exported.loc[0, "needs_review"] == True  # noqa: E712


def test_dropdown_options_include_unknown():
    assert "unknown" in CATEGORY_OPTIONS


def test_real_model_handles_strange_descriptions():
    labeled = dedupe_descriptions(load_labeled_expenses())
    provider = TfidfProvider(train_model(labeled))
    weird = ["", "   ", "!!!", "12345", "x" * 500, "CAFÉ ☕ München"]
    results = provider.predict(weird)
    assert len(results) == len(weird)
    for category, confidence in results:
        assert category in CATEGORY_OPTIONS
        assert 0.0 <= confidence <= 1.0