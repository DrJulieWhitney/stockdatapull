"""Utility for downloading QQQ price data and dividends."""
from __future__ import annotations
import pandas as pd
import yfinance as yf
def filter_first_day_month(data: pd.DataFrame) -> pd.DataFrame:
    """Return the first available row for each month.

    Parameters
    ----------
    data:
        DataFrame indexed by date containing daily price information.

    Returns
    -------
    pd.DataFrame
        DataFrame with the first row for each month in ``data``.
    """

    if not isinstance(data.index, pd.DatetimeIndex):
        raise TypeError("Data index must be a DatetimeIndex")

    # Resample to the first calendar day of each month and select the first row.
    monthly = data.resample("MS").first()
    return monthly
def main() -> None:
    """Download monthly QQQ data and dividend information."""
    start = "2022-01-01"
    end = "2024-12-31"

    ticker = yf.Ticker("QQQ")

    # Get daily OHLCV data and reduce to first row of each month
    daily = ticker.history(start=start, end=end, interval="1d")
    monthly = filter_first_day_month(daily)

    # Get dividend data within the period
    dividends = ticker.dividends.loc[start:end]

    # Save to CSV files
    monthly.to_csv("QQQ_monthly_ohlc.csv")
    dividends.to_csv("QQQ_dividends.csv")
if __name__ == "__main__":
    main()
