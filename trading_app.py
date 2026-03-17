import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import time
import threading

st.set_page_config(layout="wide")

st.title("📈 TradeView (Python Version)")

# ===================== ASSETS =====================

ASSETS = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "Gold (XAU/USD)": "GC=F",
    "Apple": "AAPL",
    "NVIDIA": "NVDA",
    "Microsoft": "MSFT",
    "Tesla": "TSLA",
    "Reliance": "RELIANCE.NS",
    "TCS": "TCS.NS"
}

# ===================== AUTO REFRESH =====================

def auto_refresh():
    time.sleep(5)  # 🔥 updates every 5 seconds
    st.rerun()

threading.Thread(target=auto_refresh).start()

# ===================== FUNCTIONS =====================

@st.cache_data(ttl=5)
def get_data(ticker, period, interval):
    data = yf.download(ticker, period=period, interval=interval)

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)

    return data.dropna()

@st.cache_data(ttl=60)
def get_news(ticker):
    try:
        stock = yf.Ticker(ticker)
        return stock.news[:5]
    except:
        return []

# ===================== SIDEBAR =====================

st.sidebar.header("⚙️ Settings")

selected = st.sidebar.selectbox("Select Asset", list(ASSETS.keys()))
ticker = ASSETS[selected]

timeframe = st.sidebar.selectbox(
    "Timeframe",
    ["1d", "5d", "1mo", "3mo", "6mo", "1y"]
)

interval = st.sidebar.selectbox(
    "Interval",
    ["1m", "5m", "15m", "30m", "1h", "1d"]
)

# Fix invalid combo
if timeframe == "1d" and interval == "1d":
    interval = "5m"

# ===================== MAIN LAYOUT =====================

col1, col2 = st.columns([3, 1])

# ===================== CHART =====================

with col1:
    st.subheader(f"{selected} Chart")

    data = get_data(ticker, timeframe, interval)

    if not data.empty:
        latest = data.iloc[-1]

        # Price display
        st.metric(
            "Price",
            f"{latest['Close']:.4f}"
        )

        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close']
        ))

        fig.update_layout(
            height=600,
            xaxis_rangeslider_visible=False,
            template="plotly_dark"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("No data available")

# ===================== NEWS =====================

with col2:
    st.subheader("📰 Latest News")

    news = get_news(ticker)

    if news:
        for item in news:
            title = item.get("title", "No Title")
            link = item.get("link", "#")

            st.markdown(f"**{title}**")
            st.markdown(f"[Read more]({link})")
            st.write("---")
    else:
        st.write("No news available")

# ===================== FOOTER =====================

st.markdown("---")
st.caption("Real-time simulation using yfinance (delayed data)")
