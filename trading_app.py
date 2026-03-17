import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import time

st.set_page_config(layout="wide")

st.title("📈 Clean Trading Chart")

# ===================== AUTO REFRESH =====================
if "last_update" not in st.session_state:
    st.session_state.last_update = time.time()

if time.time() - st.session_state.last_update > 5:
    st.session_state.last_update = time.time()
    st.rerun()

# ===================== ASSETS =====================
ASSETS = {
    "Gold (XAU/USD)": ["XAUUSD=X", "GC=F"],  # fallback added
    "EUR/USD": ["EURUSD=X"],
    "GBP/USD": ["GBPUSD=X"],
    "USD/JPY": ["USDJPY=X"]
}

# ===================== SAFE TIMEFRAME ENGINE =====================
def get_safe_params(tf):
    if tf == "1m":
        return "1d", "1m"
    elif tf == "5m":
        return "5d", "5m"
    elif tf == "15m":
        return "1mo", "15m"
    elif tf == "1H":
        return "3mo", "1h"
    elif tf == "1D":
        return "1y", "1d"

# ===================== DATA =====================
@st.cache_data(ttl=5)
def get_data(tickers, period, interval):

    # Try multiple tickers (for gold fallback)
    for ticker in tickers:
        try:
            data = yf.download(ticker, period=period, interval=interval)

            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)

            data = data.dropna()

            if not data.empty:
                return data

        except:
            continue

    return pd.DataFrame()

# ===================== UI =====================
selected = st.selectbox("Select Asset", list(ASSETS.keys()))
tickers = ASSETS[selected]

TIMEFRAMES = ["1m", "5m", "15m", "1H", "1D"]

tf_cols = st.columns(len(TIMEFRAMES))

if "tf" not in st.session_state:
    st.session_state["tf"] = "5m"

for i, tf in enumerate(TIMEFRAMES):
    if tf_cols[i].button(tf):
        st.session_state["tf"] = tf

selected_tf = st.session_state["tf"]

period, interval = get_safe_params(selected_tf)

st.markdown(f"### {selected} ({selected_tf})")

# ===================== FETCH DATA =====================
data = get_data(tickers, period, interval)

# ===================== FALLBACK FIX =====================
if data.empty and selected_tf == "1m":
    # auto fallback if 1m fails
    period, interval = "5d", "5m"
    data = get_data(tickers, period, interval)
    st.warning("1m data unavailable → switched to 5m")

# ===================== CHART =====================
if not data.empty:

    data = data.tail(300)

    latest = data.iloc[-1]
    price = latest["Close"]

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        increasing_line_color='#00ff88',
        decreasing_line_color='#ff4444'
    ))

    fig.add_hline(y=price, line_dash="dot", line_color="red")

    fig.update_layout(
        template="plotly_dark",
        height=700,
        xaxis_rangeslider_visible=False,
        plot_bgcolor="#000000",
        paper_bgcolor="#000000",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
    <span style='font-size:28px;color:#00ff88'>Price: {price:.5f}</span>
    """, unsafe_allow_html=True)

else:
    st.error("No data available (yfinance limitation)")
