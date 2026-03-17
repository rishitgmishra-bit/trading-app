import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import threading
import time

st.set_page_config(layout="wide")

# ===================== AUTO REFRESH =====================
def auto_refresh():
    time.sleep(5)
    st.rerun()

threading.Thread(target=auto_refresh).start()

# ===================== ASSETS =====================

WATCHLIST = {
    "XAUUSD": "GC=F",
    "NASDAQ": "^IXIC",
    "S&P 500": "^GSPC",
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USOIL": "CL=F",
    "USDJPY": "USDJPY=X",
    "TESLA": "TSLA",
    "APPLE": "AAPL"
}

# ===================== FUNCTIONS =====================

@st.cache_data(ttl=5)
def get_data(ticker):
    data = yf.download(ticker, period="1d", interval="1m")
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)
    return data.dropna()

def add_ema(data):
    data["EMA20"] = data["Close"].ewm(span=20).mean()
    data["EMA50"] = data["Close"].ewm(span=50).mean()
    data["EMA200"] = data["Close"].ewm(span=200).mean()
    return data

@st.cache_data(ttl=60)
def get_news():
    try:
        news = yf.Ticker("AAPL").news
        return news if news else []
    except:
        return []

# ===================== LAYOUT =====================

left, right = st.columns([3, 1])

# ===================== CHART =====================

with left:
    st.markdown("## 📈 Trading Chart")

    selected = st.selectbox("Select Asset", list(WATCHLIST.keys()))
    ticker = WATCHLIST[selected]

    data = get_data(ticker)

    if not data.empty:
        data = add_ema(data)
        latest = data.iloc[-1]

        st.markdown(f"""
        ### {selected}
        <span style='font-size:30px;color:#00ff88'>{latest['Close']:.2f}</span>
        """, unsafe_allow_html=True)

        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close']
        ))

        fig.add_trace(go.Scatter(x=data.index, y=data["EMA20"], name="EMA20", line=dict(color="yellow")))
        fig.add_trace(go.Scatter(x=data.index, y=data["EMA50"], name="EMA50", line=dict(color="green")))
        fig.add_trace(go.Scatter(x=data.index, y=data["EMA200"], name="EMA200", line=dict(color="blue")))

        fig.update_layout(
            height=650,
            template="plotly_dark",
            xaxis_rangeslider_visible=False
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("No data")

# ===================== RIGHT PANEL =====================

with right:
    st.markdown("## 📊 Watchlist")

    for name, ticker in WATCHLIST.items():
        data = get_data(ticker)

        if not data.empty:
            price = data["Close"].iloc[-1]
            prev = data["Close"].iloc[-2]
            change = price - prev
            pct = (change / prev) * 100

            color = "green" if change >= 0 else "red"

            st.markdown(f"""
            **{name}**  
            <span style='color:{color}'>{price:.2f} ({pct:.2f}%)</span>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ===================== FIXED NEWS =====================

    st.markdown("## 📰 News")

    news = get_news()

    valid_news = []

    for item in news:
        title = item.get("title")
        link = item.get("link")

        # Only keep valid entries
        if title and link:
            valid_news.append((title, link))

    if valid_news:
        for title, link in valid_news[:5]:
            st.markdown(f"[{title}]({link})")
            st.write("---")
    else:
        st.write("No valid news available")
