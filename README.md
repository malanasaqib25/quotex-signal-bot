# Signal Analysis Bot V9 — Real OHLC

V9 removes placeholder candles from the live-analysis path and adds a Twelve Data OHLC adapter.

Setup:
1. Create a Twelve Data account and obtain an API key.
2. Set the environment variable `TWELVE_DATA_API_KEY`.
3. Run `streamlit run app.py`.
4. The app fetches 1m, 5m, 15m, 1h and 4h OHLC and only produces a signal if all required data is available.

The Twelve Data time-series API provides OHLC time series for instruments including forex. Check your plan's rate limits and data entitlements before live use.

No broker order execution is included.
No 90–100% accuracy is promised; confidence is a setup-strength score and must be validated with out-of-sample testing.

## V10 API-key input
The Streamlit sidebar now accepts the Twelve Data API key directly for the current session. It is not stored by the app. For stronger security, a server-side environment variable is still preferable when deploying publicly.
