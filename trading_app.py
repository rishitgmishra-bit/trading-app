import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import math
import time

st.set_page_config(layout="wide")

st.title("📈 TradeView Pro (Custom Engine)")

# ===================== EXCHANGE =====================
exchange = st.sidebar.selectbox("Exchange", ["NSE", "BSE"])
suffix = ".NS" if exchange == "NSE" else ".BO"

# ===================== SYMBOL MAP =====================
SYMBOLS = {
    "Gold": "GC=F",
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",

    "Apple": "AAPL",
    "NVIDIA": "NVDA",
    "Tesla": "TSLA",

    "Reliance": f"RELIANCE{suffix}",
    "TCS": f"TCS{suffix}",
    "Infosys": f"INFY{suffix}",
    "HDFC Bank": f"HDFCBANK{suffix}",
    "ICICI Bank": f"ICICIBANK{suffix}",
    "Coforge": f"COFORGE{suffix}",

    "Nifty 50": "^NSEI"
}

# ===================== TIMEFRAMES =====================
TIMEFRAMES = {
    "1m": ("1d", "1m"),
    "5m": ("5d", "5m"),
    "15m": ("1mo", "15m"),
    "1H": ("3mo", "1h"),
    "1D": ("1y", "1d")
}

# ===================== SESSION =====================
if "asset" not in st.session_state:
    st.session_state.asset = "EUR/USD"

if "tf" not in st.session_state:
    st.session_state.tf = "5m"

# ===================== LAYOUT =====================
col1, col2 = st.columns([5,1])

# ===================== DATA FUNCTION =====================
@st.cache_data(ttl=3)
def get_data(ticker, period, interval):
    try:
        data = yf.download(ticker, period=period, interval=interval)
        data = data.dropna()
        return data
    except:
        return pd.DataFrame()

# ===================== MAIN =====================
with col1:

    selected = st.selectbox(
        "Asset",
        list(SYMBOLS.keys()),
        index=list(SYMBOLS.keys()).index(st.session_state.asset)
    )
    st.session_state.asset = selected

    tf_cols = st.columns(len(TIMEFRAMES))
    for i, tf in enumerate(TIMEFRAMES):
        if tf_cols[i].button(tf, type="primary" if tf == st.session_state.tf else "secondary"):
            st.session_state.tf = tf

    ticker = SYMBOLS[selected]
    period, interval = TIMEFRAMES[st.session_state.tf]

    # 🔥 Fix Indian 1m issue
    if interval == "1m" and ticker.endswith((".NS", ".BO")):
        interval = "5m"
        period = "5d"
        st.warning("1m not supported → switched to 5m")

    data = get_data(ticker, period, interval)

    # 🔥 fallback
    if data.empty or len(data) < 10:
        data = get_data(ticker, "6mo", "1d")
        st.warning("Switched to Daily data")

    if not data.empty:

        data = data.tail(150)

        # 🔥 FOOTPRINT STYLE (delta)
        data["Delta"] = data["Close"] - data["Open"]

        fig = go.Figure()

        # Candles
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            increasing_line_color='#00ff88',
            decreasing_line_color='#ff4444'
        ))

        # Volume bars (footprint feel)
        fig.add_trace(go.Bar(
            x=data.index,
            y=data["Volume"],
            marker_color=[
                "#00ff88" if d >= 0 else "#ff4444"
                for d in data["Delta"]
            ],
            opacity=0.3,
            yaxis="y2"
        ))

        # Price line
        price = data["Close"].iloc[-1]
        if isinstance(price, (int, float)) and not math.isnan(price):
            fig.add_hline(y=float(price), line_dash="dot", line_color="red")

        fig.update_layout(
            template="plotly_dark",
            height=600,
            xaxis_rangeslider_visible=False,
            yaxis2=dict(overlaying='y', side='right', showgrid=False)
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("No data")

# ===================== WATCHLIST =====================
with col2:
    st.markdown("## 📊 Watchlist")

    for name, ticker in SYMBOLS.items():
        try:
            data = get_data(ticker, "1d", "1m")

            if len(data) > 2:
                last = data["Close"].iloc[-1]
                prev = data["Close"].iloc[-2]

                pct = ((last - prev) / prev) * 100
                color = "green" if pct >= 0 else "red"

                if st.button(f"{name}"):
                    st.session_state.asset = name
                    st.rerun()

                st.markdown(f"<span style='color:{color}'>{last:.2f} ({pct:.2f}%)</span>",
                            unsafe_allow_html=True)

        except:
            st.write(f"{name} - No data")

    st.markdown("---")

    # ===================== NEWS =====================
    st.markdown("## 📰 News")

    try:
        news = yf.Ticker("AAPL").news

        for item in news[:5]:
            title = item.get("title")
            link = item.get("link")

            if title and link:
                st.markdown(f"[{title}]({link})")
                st.write("---")

    except:
        st.write("News unavailable")

# 🔥 AUTO REFRESH
time.sleep(3)
st.rerun()
