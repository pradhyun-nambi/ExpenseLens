"""Tests for src/model.py and the challenge set."""

from pathlib import Path

import pandas as pd

from src.evaluate_baseline import load_labeled_expenses
from src.model import dedupe_descriptions, split_data, train_model

CHALLENGE_PATH = Path(__file__).parent.parent / "data" / "challenge_set.csv"
CATEGORIES = {"equipment", "software", "marketing", "travel", "office supplies"}


def make_small_dataset():
    """Tiny fake dataset: 5 categories, 8 unique descriptions each, plus some repeats."""
    rows = []
    for category in sorted(CATEGORIES):
        for i in range(8):
            rows.append({"description": f"{category} item {i}", "category": category})
    # Add repeats of the same description (some with different capitalization)
    rows.append({"description": "EQUIPMENT ITEM 0", "category": "equipment"})
    rows.append({"description": "software item 1 ", "category": "software"})
    return pd.DataFrame(rows)


def test_dedupe_keeps_one_row_per_description():
    df = pd.DataFrame(
        {
            "description": ["Adobe", "adobe ", "Uber"],
            "category": ["software", "software", "travel"],
        }
    )
    assert len(dedupe_descriptions(df)) == 2


def test_train_and_test_share_no_descriptions():
    train, test = split_data(make_small_dataset())
    train_set = set(train["description"].str.lower().str.strip())
    test_set = set(test["description"].str.lower().str.strip())
    assert train_set.isdisjoint(test_set)


def test_split_has_no_duplicates_inside_either_set():
    train, test = split_data(make_small_dataset())
    assert not train["description"].str.lower().str.strip().duplicated().any()
    assert not test["description"].str.lower().str.strip().duplicated().any()


def test_model_predicts_a_description_it_was_trained_on():
    train = pd.DataFrame(
        {
            "description": ["uber ride", "lyft ride", "adobe plan", "zoom plan",
                            "camera lens", "tripod stand"],
            "category": ["travel", "travel", "software", "software",
                         "equipment", "equipment"],
        }
    )
    model = train_model(train)
    assert model.predict(["uber ride"])[0] == "travel"
    assert model.predict(["adobe plan"])[0] == "software"


def test_challenge_set_has_valid_categories_and_no_repeats():
    challenge = pd.read_csv(CHALLENGE_PATH)
    assert set(challenge["category"]) == CATEGORIES
    assert not challenge["description"].str.lower().str.strip().duplicated().any()


def test_challenge_set_is_not_in_the_labeled_data():
    challenge = pd.read_csv(CHALLENGE_PATH)
    labeled = load_labeled_expenses()
    challenge_set = set(challenge["description"].str.lower().str.strip())
    labeled_set = set(labeled["description"].str.lower().str.strip())
    assert challenge_set.isdisjoint(labeled_set)