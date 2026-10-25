import os
import requests
import pandas as pd

TWELVE_DATA_URL = "https://api.twelvedata.com/time_series"

TIMEFRAME_MAP = {
    "1m": "1min",
    "5m": "5min",
    "15m": "15min",
    "30m": "30min",
    "1h": "1h",
    "4h": "4h",
}

def fetch_ohlc(symbol, timeframe, outputsize=300, api_key=None):
    """
    Fetch real OHLC candles from Twelve Data.

    Set TWELVE_DATA_API_KEY in the environment before running.
    The provider supports forex symbols such as EUR/USD and returns OHLC
    time-series data. The returned candles are normalized for our engine.
    """
    api_key = api_key or os.getenv("TWELVE_DATA_API_KEY")
    if not api_key:
        raise RuntimeError("Twelve Data API key is not configured.")

    interval = TIMEFRAME_MAP.get(timeframe)
    if not interval:
        raise ValueError(f"Unsupported timeframe: {timeframe}")

    r = requests.get(
        TWELVE_DATA_URL,
        params={
            "symbol": symbol,
            "interval": interval,
            "outputsize": outputsize,
            "apikey": api_key,
            "timezone": "UTC",
            "order": "asc",
        },
        timeout=15,
    )
    r.raise_for_status()
    payload = r.json()

    if payload.get("status") == "error" or "values" not in payload:
        raise RuntimeError(payload.get("message", "Market-data provider returned no candles."))

    df = pd.DataFrame(payload["values"])
    required = ["datetime", "open", "high", "low", "close"]
    missing = [x for x in required if x not in df.columns]
    if missing:
        raise RuntimeError(f"Missing OHLC fields: {missing}")

    df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
    for col in ["open","high","low","close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["open","high","low","close"])
    df = df.sort_values("datetime").drop_duplicates("datetime").reset_index(drop=True)

    if len(df) < 80:
        raise RuntimeError(f"Only {len(df)} candles received; at least 80 are needed.")

    return df[["datetime","open","high","low","close"]]
