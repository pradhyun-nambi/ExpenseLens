"""Tests for src/loader.py. Each validation rule gets its own test."""

import pytest

from src.loader import CSVValidationError, load_transactions


def write_csv(tmp_path, text):
    """Helper: write text to a temporary CSV and return its path."""
    path = tmp_path / "test.csv"
    path.write_text(text)
    return path


def test_valid_csv_loads(tmp_path):
    path = write_csv(
        tmp_path,
        "date,description,amount\n2025-01-05,Client payment,1500\n2025-01-09,Adobe,-52.99\n",
    )
    df = load_transactions(path)
    assert len(df) == 2
    assert df["amount"].iloc[1] == -52.99


def test_missing_column(tmp_path):
    path = write_csv(tmp_path, "date,description\n2025-01-05,Client payment\n")
    with pytest.raises(CSVValidationError, match="amount"):
        load_transactions(path)


def test_completely_empty_file(tmp_path):
    path = write_csv(tmp_path, "")
    with pytest.raises(CSVValidationError, match="empty"):
        load_transactions(path)


def test_header_only_file(tmp_path):
    path = write_csv(tmp_path, "date,description,amount\n")
    with pytest.raises(CSVValidationError, match="empty"):
        load_transactions(path)


def test_bad_date(tmp_path):
    path = write_csv(
        tmp_path,
        "date,description,amount\n2025-01-05,Client payment,1500\nnot-a-date,Adobe,-52.99\n",
    )
    with pytest.raises(CSVValidationError, match="date"):
        load_transactions(path)


def test_non_numeric_amount(tmp_path):
    path = write_csv(
        tmp_path,
        "date,description,amount\n2025-01-05,Client payment,1500\n2025-01-09,Adobe,abc\n",
    )
    with pytest.raises(CSVValidationError, match="amount"):
        load_transactions(path)