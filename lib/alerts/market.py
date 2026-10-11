from typing import Dict

import yfinance as yf
import pandas as pd

from lib.core.tokens import (
    JsonTKN,
    YfinanceTKN
)
from lib.core.utils import safe_float


def days_since_52w_high(
    ticker: str
) -> int:
    df: pd.DataFrame = yf.download(
        ticker,
        period="1y",
        interval="1d",
        progress=False,
        auto_adjust=True,
    )

    if df.empty:
        return -1
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    if "High" not in df.columns:
        return -1
    last_high_date: pd.Timestamp = df["High"].idxmax()
    days_since: int = (df.index[-1] - last_high_date).days
    return days_since


def calc_change(
    last_price,
    previous_close,
):
    if last_price is None:
        return 0.0, 0.0
    if previous_close is None or previous_close < 0.01:
        return 0.0, 0.0
    change = last_price - previous_close
    change_percentage = 100 * change / previous_close
    return change, change_percentage


def fetch_market(ticker_symbol: str) -> Dict[str, float]:
    ticker: yf.Ticker = yf.Ticker(ticker_symbol)
    fast_info: Dict[str, float] = ticker.fast_info

    # Basic price info
    last_price = safe_float(fast_info[YfinanceTKN.LAST_PRICE.key])
    previous_close = safe_float(fast_info[YfinanceTKN.PREVIOUS_CLOSE.key])
    _, change_percentage = calc_change(last_price, previous_close)

    # Historical data
    data_frame = ticker.history(period="1y", interval="1d")

    # Moving averages (NaN-safe)
    moving_average_10 = data_frame[YfinanceTKN.CLOSE.key].rolling(window=10, min_periods=1).mean()
    moving_average_20 = data_frame[YfinanceTKN.CLOSE.key].rolling(window=20, min_periods=1).mean()
    moving_average_30 = data_frame[YfinanceTKN.CLOSE.key].rolling(window=30, min_periods=1).mean()
    days_since_year_high: int = days_since_52w_high(ticker_symbol)
    return {
        JsonTKN.OPENING_QUOTE.key: safe_float(fast_info[YfinanceTKN.OPEN.key]),
        JsonTKN.CURRENT_QUOTE.key: last_price,
        JsonTKN.CURRENT_VOLUME.key: safe_float(fast_info[YfinanceTKN.LAST_VOLUME.key]),
        JsonTKN.AVERAGE_VOLUME.key: safe_float(fast_info[YfinanceTKN.AVG_VOLUME_10DAY.key]),
        JsonTKN.CHANGE.key: safe_float(change_percentage),
        JsonTKN.YEAR_LOW.key: safe_float(fast_info[YfinanceTKN.YEAR_LOW.key]),
        JsonTKN.YEAR_HIGH.key: safe_float(fast_info[YfinanceTKN.YEAR_HIGH.key]),
        JsonTKN.MOVING_AVERAGE_10.key: safe_float(moving_average_10.iloc[-1]),
        JsonTKN.MOVING_AVERAGE_20.key: safe_float(moving_average_20.iloc[-1]),
        JsonTKN.MOVING_AVERAGE_30.key: safe_float(moving_average_30.iloc[-1]),
        JsonTKN.DAYS_SINCE_YEAR_HIGH.key: days_since_year_high
    }
