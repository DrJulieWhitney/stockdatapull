
# app.py
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path

###############################################################################
# Helper functions
###############################################################################

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

@st.cache_data(show_spinner=False)
def fetch_history(ticker: str, start: datetime, end: datetime) -> pd.DataFrame:
    """Download adjusted close prices and return a tidy dataframe."""
    df = yf.download(ticker, start=start, end=end, progress=False)["Adj Close"]
    df = df.to_frame(name="adj_close").dropna()
    df["pct_change"] = (df["adj_close"] / df["adj_close"].iloc[0] - 1) * 100
    csv_path = DATA_DIR / f"{ticker}_{start.date()}_{end.date()}.csv"
    df.to_csv(csv_path)
    return df

###############################################################################
# Streamlit UI
###############################################################################

st.set_page_config(page_title="10-Year Stock Visualizer", layout="wide")

st.title("📈 Ten-Year Stock Visualizer")

# -------------- 1. Ticker entry area ----------------------------------------
col1, col2 = st.columns([3, 1])
with col1:
    new_ticker = st.text_input("Enter a ticker symbol (e.g., AAPL)", "")
with col2:
    if st.button("Add") and new_ticker.strip():
        tickers = st.session_state.setdefault("tickers", [])
        if new_ticker.upper() not in tickers:
            tickers.append(new_ticker.upper())
        else:
            st.warning(f"{new_ticker.upper()} already in list")

st.write("**Current list:**", st.session_state.get("tickers", []))
if st.button("Clear list"):
    st.session_state["tickers"] = []

# -------------- 2. Fetch data & visualize -----------------------------------
if st.session_state.get("tickers"):
    end = datetime.today()
    start = end - timedelta(days=365 * 10)

    # Always include S&P 500 for comparison
    compare_index = "^GSPC"
    full_list = st.session_state["tickers"] + [compare_index]

    # Download in one batch (yfinance handles list input nicely)
    raw = yf.download(full_list, start=start, end=end, progress=False)["Adj Close"].dropna()
    raw = raw.rename(columns={compare_index: "S&P500"})

    # Save individual CSVs and build percent-change dataframe
    pct_df = pd.DataFrame(index=raw.index)
    for col in raw.columns:
        df_single = raw[[col]].copy()
        df_single["pct_change"] = (df_single[col] / df_single[col].iloc[0] - 1) * 100
        pct_df[col] = df_single["pct_change"]
        # Persist
        csv_path = DATA_DIR / f"{col}_{start.date()}_{end.date()}.csv"
        df_single.to_csv(csv_path)

    # -------------- 3. Tabs ---------------------------------------------------
    tab1, tab2, tab3 = st.tabs(
        ["% Change vs S&P 500", "Placeholder Tab 2", "Placeholder Tab 3"]
    )

    with tab1:
        st.subheader("Percent price change over the last 10 years")
        st.line_chart(pct_df)

        # Optional download
        st.download_button(
            label="Download combined %-change CSV",
            data=pct_df.to_csv().encode("utf-8"),
            file_name="percent_change_10yr.csv",
            mime="text/csv",
        )

    with tab2:
        st.info("Add another visualization here – e.g., rolling 90-day volatility.")

    with tab3:
        st.info("Add another visualization here – e.g., maximum drawdown.")
else:
    st.info("Add at least one ticker, then click **Add**.")
