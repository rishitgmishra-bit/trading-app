import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import math

st.set_page_config(layout="wide")
st.title("📈 TradeView (Stable Build)")

# ================= SYMBOLS =================
SYMBOLS = {
    "Gold": "GC=F",
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",

    "Apple": "AAPL",
    "NVIDIA": "NVDA",
    "Tesla": "TSLA",

    "Reliance": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "Coforge": "COFORGE.NS",

    "Nifty 50": "^NSEI"
}

TIMEFRAMES = {
    "1m": ("1d","1m"),
    "5m": ("5d","5m"),
    "15m": ("1mo","15m"),
    "1H": ("3mo","1h"),
    "1D": ("1y","1d")
}

# ================= SESSION =================
if "asset" not in st.session_state:
    st.session_state.asset = "EUR/USD"

if "tf" not in st.session_state:
    st.session_state.tf = "5m"

# ================= DATA =================
@st.cache_data(ttl=10)
def get_data(ticker, period, interval):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df is None or df.empty:
            return pd.DataFrame()
        return df.dropna()
    except:
        return pd.DataFrame()

# ================= LAYOUT =================
col1, col2 = st.columns([5,1])

# ================= MAIN =================
with col1:

    selected = st.selectbox(
        "Asset",
        list(SYMBOLS.keys()),
        index=list(SYMBOLS.keys()).index(st.session_state.asset)
    )
    st.session_state.asset = selected

    # Timeframes
    tf_cols = st.columns(len(TIMEFRAMES))
    for i, tf in enumerate(TIMEFRAMES):
        if tf_cols[i].button(tf, type="primary" if tf==st.session_state.tf else "secondary"):
            st.session_state.tf = tf

    ticker = SYMBOLS[selected]
    period, interval = TIMEFRAMES[st.session_state.tf]

    # 🔥 Fix Indian 1m
    if interval == "1m" and ticker.endswith(".NS"):
        interval = "5m"
        period = "5d"
        st.warning("1m not supported → switched to 5m")

    data = get_data(ticker, period, interval)

    # 🔥 fallback
    if data.empty:
        data = get_data(ticker, "6mo", "1d")
        st.warning("Showing Daily data")

    if not data.empty and len(data) > 5:

        data = data.tail(150)

        # 🔥 Footprint style
        data["Delta"] = data["Close"] - data["Open"]

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

        fig.add_trace(go.Bar(
            x=data.index,
            y=data["Volume"],
            marker_color=[
                "#00ff88" if d >= 0 else "#ff4444"
                for d in data["Delta"]
            ],
            opacity=0.25,
            yaxis="y2"
        ))

        price = float(data["Close"].iloc[-1])
        fig.add_hline(y=price, line_dash="dot", line_color="red")

        fig.update_layout(
            template="plotly_dark",
            height=600,
            xaxis_rangeslider_visible=False,
            yaxis2=dict(overlaying='y', side='right', showgrid=False)
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("No usable data")

# ================= WATCHLIST =================
with col2:
    st.markdown("## 📊 Watchlist")

    for name, ticker in SYMBOLS.items():
        try:
            df = get_data(ticker, "1d", "5m")

            if not df.empty and len(df) > 2:
                last = df["Close"].iloc[-1]
                prev = df["Close"].iloc[-2]

                pct = ((last - prev)/prev)*100
                color = "green" if pct >= 0 else "red"

                if st.button(name):
                    st.session_state.asset = name
                    st.rerun()

                st.markdown(
                    f"<span style='color:{color}'>{last:.2f} ({pct:.2f}%)</span>",
                    unsafe_allow_html=True
                )

            else:
                st.write(f"{name} - No data")

        except:
            st.write(f"{name} - Error")

    st.markdown("---")

    # ================= NEWS =================
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
