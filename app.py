"""ExpenseLens Day 2: basic cash-flow dashboard (no machine learning)."""

from pathlib import Path

import pandas as pd
import streamlit as st

from src.loader import CSVValidationError, load_transactions

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


st.title("ExpenseLens")
st.caption("Small-business cash-flow dashboard")

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

# Overall totals
summary = monthly_summary(transactions)
col1, col2, col3 = st.columns(3)
col1.metric("Total inflows", f"${summary['Inflows'].sum():,.2f}")
col2.metric("Total outflows", f"${summary['Outflows'].sum():,.2f}")
col3.metric("Net cash", f"${summary['Net cash'].sum():,.2f}")

# Monthly breakdown
st.subheader("Monthly cash flow")
st.dataframe(summary, hide_index=True, use_container_width=True)
st.bar_chart(summary.set_index("Month")[["Inflows", "Outflows"]])

# Raw transactions
st.subheader("Transactions")
table = transactions.copy()
table["date"] = table["date"].dt.date  # hide the 00:00:00 time part
st.dataframe(table, hide_index=True, use_container_width=True)