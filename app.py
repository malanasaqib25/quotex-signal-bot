import os
import streamlit as st
import pandas as pd

from market_data import fetch_ohlc
from signal_engine import analyze
from license import validate_license

st.set_page_config(page_title="Signal Analysis Bot V9", page_icon="📊", layout="wide")
st.title("📊 Signal Analysis Bot — V9")
st.caption("Real OHLC analysis • manual trading only • no broker order execution")

pairs=["EUR/USD","GBP/USD","USD/JPY","AUD/USD","USD/CAD","USD/CHF","NZD/USD","XAU/USD"]

with st.sidebar:
    pair=st.selectbox("Pair",pairs)
    api_key=st.text_input("Twelve Data API key",type="password",
                          help="Paste your Twelve Data key here. It is used only for this session.")
    key=st.text_input("Lifetime license key",type="password")
    if key:
        st.success("✅ Lifetime license active" if validate_license(key) else "❌ Invalid license")

    st.divider()
    st.write("Data source: Twelve Data")
    if os.getenv("TWELVE_DATA_API_KEY"):
        st.success("Market-data API key detected")
    else:
        st.warning("Add TWELVE_DATA_API_KEY to enable real OHLC.")

if not api_key:
    st.info("Paste your Twelve Data API key in the sidebar. The app will not substitute fake candles for live data.")
    st.stop()

timeframes=["1m","5m","15m","1h","4h"]
frames={}
errors=[]

for tf in timeframes:
    try:
        # Pass the session-only key directly; it is not written to disk.
        frames[tf]=fetch_ohlc(pair,tf,300,api_key=api_key)
    except Exception as e:
        errors.append(f"{tf}: {e}")

if errors:
    st.error("Real-data fetch failed; no signal will be generated.")
    for e in errors: st.write("•",e)
    st.stop()

result=analyze(frames)

a,b,c,d=st.columns(4)
a.metric("Pair",pair)
b.metric("Signal",result["signal"])
c.metric("Confidence score",f"{result['confidence']}%")
d.metric("Setup",result["strength"])

if result["signal"]=="UP":
    st.success("🟢 UP")
elif result["signal"]=="DOWN":
    st.error("🔴 DOWN")
else:
    st.warning("⚪ NO TRADE")

st.caption("Confidence is a setup-strength score, not a guaranteed probability of winning.")

st.subheader("Live OHLC status")
st.write(f"Latest 1m candle: {frames['1m']['datetime'].iloc[-1]}")
st.write(f"Latest 1m close: {frames['1m']['close'].iloc[-1]}")

st.subheader("Multi-timeframe confirmation")
rows=[]
for tf,x in result["timeframes"].items():
    rows.append([tf,x["signal"],f"{x['confidence']}%",x["trend"],x["score"],
                 "—" if x["adx"] is None else f"{x['adx']:.1f}"])
st.dataframe(pd.DataFrame(rows,columns=["TF","Signal","Strength","Trend","Score","ADX"]),
             use_container_width=True,hide_index=True)

st.subheader("Analysis")
for r in result["reasons"]: st.write("•",r)

st.info("The bot only analyzes market data. It does not place Quotex orders. Verify the provider's data entitlement and that its pricing is appropriate for your intended use before relying on it.")
