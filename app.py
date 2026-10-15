"""ExpenseLens: cash-flow dashboard plus expense classifier with human review."""

from pathlib import Path

import pandas as pd
import streamlit as st

from src.classify import (
    CATEGORY_OPTIONS,
    DEFAULT_THRESHOLD,
    apply_corrections,
    classify_transactions,
    to_csv_bytes,
)
from src.evaluate_baseline import load_labeled_expenses
from src.loader import CSVValidationError, load_transactions
from src.model import dedupe_descriptions, train_model
from src.providers import KeywordProvider, TfidfProvider

SAMPLE_PATH = Path(__file__).parent / "data" / "sample.csv"


def monthly_summary(df):
    """Total inflows, outflows, and net cash for each month."""
    df = df.copy()
    df["Month"] = df["date"].dt.to_period("M").astype(str)  # e.g. "2025-03"

    inflows = df[df["amount"] > 0].groupby("Month")["amount"].sum()
    # Outflows are negative in the CSV; show them as positive numbers
    outflows = df[df["amount"] < 0].groupby("Month")["amount"].sum().abs()

    summary = pd.DataFrame({"Inflows": inflows, "Outflows": outflows}).fillna(0)
    summary["Net cash"] = summary["Inflows"] - summary["Outflows"]
    summary.index.name = "Month"
    return summary.reset_index()


@st.cache_resource
def get_tfidf_provider():
    """Train the model once and reuse it (Streamlit re-runs this script on every click)."""
    labeled = dedupe_descriptions(load_labeled_expenses())
    return TfidfProvider(train_model(labeled))


st.title("ExpenseLens")
st.caption("Small-business cash-flow dashboard and expense classifier (synthetic demo data)")

# Let the user upload a CSV, otherwise fall back to the sample file
uploaded = st.file_uploader("Upload a transactions CSV", type="csv")
if uploaded is not None:
    source = uploaded
else:
    source = SAMPLE_PATH
    st.info("No file uploaded, showing data/sample.csv")

# Load and validate; show a friendly error instead of a crash
try:
    transactions = load_transactions(source)
except CSVValidationError as err:
    st.error(str(err))
    st.stop()
except FileNotFoundError:
    st.error("Could not find data/sample.csv. Upload a CSV instead.")
    st.stop()

# ---------- Cash flow (Day 2) ----------
summary = monthly_summary(transactions)
col1, col2, col3 = st.columns(3)
col1.metric("Total inflows", f"${summary['Inflows'].sum():,.2f}")
col2.metric("Total outflows", f"${summary['Outflows'].sum():,.2f}")
col3.metric("Net cash", f"${summary['Net cash'].sum():,.2f}")

st.subheader("Monthly cash flow")
st.dataframe(summary, hide_index=True, width="stretch")
st.bar_chart(summary.set_index("Month")[["Inflows", "Outflows"]])

# ---------- Classify and review (Day 5) ----------
st.subheader("Categorize expenses")

# Pick which provider guesses the categories
providers = {p.name: p for p in [KeywordProvider(), get_tfidf_provider()]}
choice = st.selectbox("Classifier", list(providers), index=1)
threshold = st.slider(
    "Flag for review when confidence is below",
    min_value=0.0, max_value=1.0, value=DEFAULT_THRESHOLD, step=0.05,
)

classified = classify_transactions(transactions, providers[choice], threshold)
expenses = classified[classified["amount"] < 0]

if expenses.empty:
    st.info("No expenses (negative amounts) to categorize in this file.")
    st.stop()

st.write(
    f"**{int(expenses['needs_review'].sum())}** of {len(expenses)} expenses need review. "
    "Flagged rows are listed first. Change any category using its dropdown."
)

# Show flagged rows first, least confident at the top
review_table = expenses.sort_values(["needs_review", "confidence"], ascending=[False, True])
review_table = review_table[
    ["date", "description", "amount", "category", "predicted_category", "confidence", "needs_review"]
].copy()
review_table["date"] = review_table["date"].dt.date

edited = st.data_editor(
    review_table,
    column_config={
        "category": st.column_config.SelectboxColumn(
            "Category (editable)", options=CATEGORY_OPTIONS, required=True
        ),
        "predicted_category": "Model guess",
        "confidence": st.column_config.NumberColumn("Confidence", format="%.2f"),
        "needs_review": st.column_config.CheckboxColumn("Needs review"),
    },
    disabled=["date", "description", "amount", "predicted_category", "confidence", "needs_review"],
    hide_index=True,
    width="stretch",
)

# Put the person's edits back into the full table
final = apply_corrections(classified, edited)

st.write(f"Corrections made: **{int(final['corrected'].sum())}**")

st.subheader("Spending by category")
by_category = final[final["amount"] < 0].groupby("category")["amount"].sum().abs()
st.bar_chart(by_category)

st.download_button(
    "Download categorized CSV",
    data=to_csv_bytes(final),
    file_name="expenselens_categorized.csv",
    mime="text/csv",
)