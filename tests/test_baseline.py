"""Tests for src/baseline.py and src/evaluate_baseline.py."""

import pandas as pd

from src.baseline import predict_category
from src.evaluate_baseline import load_labeled_expenses, score_baseline


def test_equipment_keyword():
    assert predict_category("Camera lens - B&H") == "equipment"


def test_software_keyword():
    assert predict_category("Adobe Creative Cloud") == "software"


def test_marketing_keyword():
    assert predict_category("Instagram ads - spring promo") == "marketing"


def test_travel_keyword():
    assert predict_category("Uber to airport") == "travel"


def test_office_supplies_keyword():
    assert predict_category("Printer paper - Staples") == "office supplies"


def test_unknown_when_no_keyword_matches():
    assert predict_category("AMZN Mktp US*2K4TR9") == "unknown"


def test_ignores_capitalization():
    assert predict_category("ADOBE CREATIVE CLOUD") == "software"


def test_matches_whole_words_only():
    # "Headset" contains the letters "ads", but it is not the word "ads"
    assert predict_category("Headset purchase") == "unknown"


def test_picks_category_with_most_matches():
    # "business cards" and "vistaprint" both point to marketing
    assert predict_category("Business cards - Vistaprint") == "marketing"


def test_score_baseline_marks_right_and_wrong():
    df = pd.DataFrame(
        {
            "description": ["Uber to airport", "AMZN Mktp US*1"],
            "category": ["travel", "equipment"],
        }
    )
    scored = score_baseline(df)
    assert scored["correct"].tolist() == [True, False]


def test_load_labeled_expenses_skips_inflows(tmp_path):
    path = tmp_path / "labeled.csv"
    path.write_text(
        "date,description,amount,category\n"
        "2026-01-05,Client payment,500,\n"
        "2026-01-06,Adobe,-59.99,software\n"
    )
    df = load_labeled_expenses(path)
    assert len(df) == 1
    assert df["category"].iloc[0] == "software"