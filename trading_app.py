import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import oandapyV20
from oandapyV20.endpoints.pricing import PricingStream
import threading
from datetime import datetime

st.set_page_config(layout="wide")

# ===================== YOUR OANDA KEYS =====================
API_KEY = "YOUR_API_KEY"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"

client = oandapyV20.API(access_token=API_KEY)

# ===================== SELECT INSTRUMENT =====================
ASSETS = {
    "Gold (XAU/USD)": "XAU_USD",   # may not work on all accounts
    "EUR/USD": "EUR_USD",
    "GBP/USD": "GBP_USD",
    "USD/JPY": "USD_JPY"
}

selected = st.sidebar.selectbox("Select Asset", list(ASSETS.keys()))
instrument = ASSETS[selected]

# ===================== DATA STORAGE =====================
ticks = []
candles = []

# ===================== STREAM FUNCTION =====================
def stream_data():
    params = {"instruments": instrument}
    r = PricingStream(accountID=ACCOUNT_ID, params=params)

    for tick in client.request(r):
        if tick["type"] == "PRICE":
            bid = float(tick["bids"][0]["price"])
            ask = float(tick["asks"][0]["price"])
            price = (bid + ask) / 2

            ticks.append({
                "time": datetime.utcnow(),
                "price": price
            })

# Start streaming thread once
if "stream_started" not in st.session_state:
    threading.Thread(target=stream_data, daemon=True).start()
    st.session_state.stream_started = True

# ===================== CANDLE CREATION =====================
def build_candles():
    global candles

    if len(ticks) < 5:
        return

    df = pd.DataFrame(ticks)

    # resample into 1-minute candles
    df.set_index("time", inplace=True)

    ohlc = df["price"].resample("1min").ohlc().dropna()

    candles = ohlc.reset_index()

# ===================== UI =====================

st.title("🔥 Real-Time Trading (OANDA)")

placeholder = st.empty()

# ===================== MAIN LOOP =====================
while True:
    build_candles()

    if len(candles) > 5:

        latest_price = candles["close"].iloc[-1]

        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=candles["time"],
            open=candles["open"],
            high=candles["high"],
            low=candles["low"],
            close=candles["close"],
            increasing_line_color="#00ff88",
            decreasing_line_color="#ff4444"
        ))

        fig.update_layout(
            template="plotly_dark",
            height=600,
            xaxis_rangeslider_visible=False
        )

        with placeholder.container():
            st.metric("Price", f"{latest_price:.4f}")
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.write("Waiting for data...")

    st.sleep(1)
