import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import time

st.set_page_config(layout="wide")

st.title("📈 TradeView Pro Max")

# ===================== WATCHLIST =====================
WATCHLIST = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "Gold (XAU/USD)": "GC=F",

    "Apple": "AAPL",
    "NVIDIA": "NVDA",
    "Tesla": "TSLA",
    "Microsoft": "MSFT"
}

# ===================== SESSION =====================
if "selected" not in st.session_state:
    st.session_state.selected = "EUR/USD"

# ===================== LAYOUT =====================
col1, col2 = st.columns([4,1])

# ===================== INDICATORS =====================
def add_indicators(df):

    # EMA
    df["EMA"] = df["Close"].ewm(span=20).mean()

    # VWAP
    df["VWAP"] = (df["Volume"] * (df["High"] + df["Low"] + df["Close"]) / 3).cumsum() / df["Volume"].cumsum()

    # RSI
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    return df

# ===================== MAIN CHART =====================
with col1:

    st.subheader(f"{st.session_state.selected}")

    timeframe = st.selectbox("Timeframe", ["5m","15m","1h","1d"], index=0)

    ticker = WATCHLIST[st.session_state.selected]

    @st.cache_data(ttl=5)
    def get_data(symbol):
        return yf.download(symbol, period="5d", interval=timeframe).dropna()

    data = get_data(ticker)

    if not data.empty:

        data = add_indicators(data)

        fig = go.Figure()

        # Candles
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name="Candles"
        ))

        # EMA
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["EMA"],
            line=dict(color="blue"),
            name="EMA"
        ))

        # VWAP
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["VWAP"],
            line=dict(color="orange"),
            name="VWAP"
        ))

        fig.update_layout(
            template="plotly_dark",
            height=600,
            xaxis_rangeslider_visible=False
        )

        st.plotly_chart(fig, use_container_width=True)

        # RSI
        st.markdown("### RSI")
        rsi_fig = go.Figure()
        rsi_fig.add_trace(go.Scatter(
            x=data.index,
            y=data["RSI"],
            line=dict(color="purple")
        ))
        rsi_fig.update_layout(template="plotly_dark", height=200)
        st.plotly_chart(rsi_fig, use_container_width=True)

    else:
        st.error("No data available")

# ===================== WATCHLIST =====================
with col2:

    st.markdown("## 📊 Watchlist")

    @st.cache_data(ttl=5)
    def get_price(symbol):
        try:
            d = yf.download(symbol, period="1d", interval="1m")
            d = d.dropna()
            if len(d) < 2:
                return None
            price = d["Close"].iloc[-1]
            prev = d["Close"].iloc[-2]
            pct = ((price - prev)/prev)*100
            return price, pct
        except:
            return None

    for name, symbol in WATCHLIST.items():
        res = get_price(symbol)

        if res:
            price, pct = res
            color = "green" if pct >= 0 else "red"

            if st.button(f"{name}"):
                st.session_state.selected = name
                st.rerun()

            st.markdown(f"<span style='color:{color}'>{price:.2f} ({pct:.2f}%)</span>", unsafe_allow_html=True)
        else:
            st.write(f"{name} - no data")

    st.markdown("---")

    # ===================== NEWS (FIXED) =====================
    st.markdown("## 📰 News")

    try:
        news = yf.Ticker("AAPL").news

        if news:
            for item in news[:8]:
                title = item.get("title", "No Title")
                link = item.get("link", "#")
                st.markdown(f"[{title}]({link})")
                st.write("---")
        else:
            st.write("No news found")

    except Exception as e:
        st.write("News loading error")

# ===================== AUTO REFRESH =====================
time.sleep(5)
st.rerun()
