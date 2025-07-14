import os
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta


@st.cache_data
# streamlit run "I:\scripts39\Git Repos\LLMFun\visualize_stocks.py"
def fetch_data(tickers, start_date, end_date, save_dir="."):
    os.makedirs(save_dir, exist_ok=True)
    df_dict = {}
    for ticker in tickers:
        data = yf.download(ticker, start=start_date, end=end_date)
        if not data.empty:
            if isinstance(data.index, pd.DatetimeIndex):
                if data.index.tz is not None:
                    data.index = data.index.tz_localize(None)
            else:
                try:
                    tmp_index = pd.to_datetime(data.index, utc=True)
                    if isinstance(tmp_index, pd.DatetimeIndex) and tmp_index.tz is not None:
                        tmp_index = tmp_index.tz_localize(None)
                    data.index = tmp_index
                except Exception:
                    pass
            data.index = pd.to_datetime(data.index, utc=True).tz_localize(None)
            df_dict[ticker] = data
            data.to_csv(os.path.join(save_dir, f"{ticker}_data.csv"))
    return df_dict


def main():
    st.title("Stock Price Change vs S&P 500")
    st.write("Enter stock tickers and visualize their percent change over the past ten years compared to the S&P 500.")

    tickers = st.text_input("Enter stock tickers separated by commas", value="AAPL,QQQ, NVDA, MP, RDDT, HPQ, LLY, KRRO").upper().split(',')
    tickers = [t.strip() for t in tickers if t.strip()]
    save_dir = st.text_input("Directory to save CSV files", value=".")

    if st.button("Load Data"):
        end_date = datetime.today().date()
        start_date = end_date - timedelta(days=365 * 10)
        all_tickers = tickers + ['^GSPC']
        data = fetch_data(all_tickers, start_date, end_date, save_dir)
        if not data:
            st.error("No data retrieved.")
            return

        pct_change_df = pd.DataFrame()
        for ticker, df in data.items():
            price_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
            df['Pct Change'] = (
                df[price_col].pct_change()
                .fillna(0)
                .add(1)
                .cumprod()
                .sub(1)
                .mul(100)
            )
            pct_change_df[ticker] = df['Pct Change']
        pct_change_df.index = data[next(iter(data))].index

        st.line_chart(pct_change_df)
        st.write("Data fetched and saved as CSV files.")

if __name__ == "__main__":
    main()
