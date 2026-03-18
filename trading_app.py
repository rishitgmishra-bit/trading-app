import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import time

st.set_page_config(layout="wide")

st.title("📈 TradeView Pro")

# ===================== WATCHLIST =====================
WATCHLIST = {
    "Apple": "AAPL",
    "NVIDIA": "NVDA",
    "Tesla": "TSLA",
    "Microsoft": "MSFT",
    "Amazon": "AMZN",
    "Coforge": "COFORGE.NS"
}

# ===================== SESSION =====================
if "selected" not in st.session_state:
    st.session_state.selected = "Apple"

# ===================== LAYOUT =====================
col1, col2 = st.columns([4,1])

# ===================== MAIN CHART =====================
with col1:

    st.subheader(f"{st.session_state.selected} Chart")

    timeframe = st.selectbox("Timeframe", ["1d","5d","1mo","3mo","6mo","1y"])

    @st.cache_data(ttl=10)
    def get_data(symbol):
        data = yf.download(symbol, period=timeframe, interval="1m")
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        return data.dropna()

    ticker = WATCHLIST[st.session_state.selected]
    data = get_data(ticker)

    if not data.empty:
        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close']
        )])

        fig.update_layout(
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("No data available")

# ===================== SIDEBAR PANEL =====================
with col2:

    st.markdown("## 📊 Watchlist")

    @st.cache_data(ttl=5)
    def get_price(symbol):
        try:
            data = yf.download(symbol, period="1d", interval="1m")
            data = data.dropna()

            if len(data) < 2:
                return None

            price = float(data["Close"].iloc[-1])
            prev = float(data["Close"].iloc[-2])

            change = price - prev
            pct = (change / prev) * 100

            return price, pct
        except:
            return None

    for name, symbol in WATCHLIST.items():
        result = get_price(symbol)

        if result:
            price, pct = result
            color = "green" if pct >= 0 else "red"

            if st.button(f"{name} ({price:.2f}) {pct:.2f}%"):
                st.session_state.selected = name
                st.rerun()

        else:
            st.write(f"{name} - No data")

    st.markdown("---")

    # ===================== NEWS =====================
    st.markdown("## 📰 News")

    try:
        news = yf.Ticker("AAPL").news

        valid_news = []
        for item in news:
            title = item.get("title")
            link = item.get("link")

            if title and link:
                valid_news.append((title, link))

        for title, link in valid_news[:5]:
            st.markdown(f"[{title}]({link})")
            st.write("---")

    except:
        st.write("News unavailable")

# ===================== AUTO REFRESH =====================
time.sleep(5)
st.rerun()
