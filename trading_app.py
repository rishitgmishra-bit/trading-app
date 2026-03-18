import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import time

st.set_page_config(layout="wide")

st.title("📈 TradeView Pro (Fixed Final)")

# ===================== WATCHLIST =====================
WATCHLIST = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",

    "Apple": "AAPL",
    "NVIDIA": "NVDA",
    "Tesla": "TSLA",
    "Microsoft": "MSFT"
}

# ===================== SESSION =====================
if "selected" not in st.session_state:
    st.session_state.selected = "EUR/USD"

col1, col2 = st.columns([4,1])

# ===================== DATA =====================
@st.cache_data(ttl=5)
def get_data(symbol, timeframe):

    if timeframe == "5m":
        interval = "5m"
        period = "1d"
    elif timeframe == "15m":
        interval = "15m"
        period = "5d"
    elif timeframe == "1h":
        interval = "1h"
        period = "1mo"
    else:
        interval = "1d"
        period = "6mo"

    try:
        data = yf.download(symbol, period=period, interval=interval)

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)

        return data.dropna()

    except:
        return pd.DataFrame()

# ===================== INDICATORS =====================
def add_indicators(df, is_forex):

    df["EMA"] = df["Close"].ewm(span=20).mean()

    if not is_forex and "Volume" in df.columns:
        df["VWAP"] = (df["Volume"] * (df["High"] + df["Low"] + df["Close"]) / 3).cumsum() / df["Volume"].cumsum()

    delta = df["Close"].diff()
    gain = (delta.clip(lower=0)).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    return df

# ===================== MAIN =====================
with col1:

    st.subheader(st.session_state.selected)

    timeframe = st.selectbox("Timeframe", ["5m","15m","1h","1d"])

    ticker = WATCHLIST[st.session_state.selected]
    is_forex = "=X" in ticker

    data = get_data(ticker, timeframe)

    if not data.empty:

        data = add_indicators(data, is_forex)

        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close']
        ))

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["EMA"],
            line=dict(color="blue"),
            name="EMA"
        ))

        if not is_forex and "VWAP" in data:
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
        rsi_fig = go.Figure()
        rsi_fig.add_trace(go.Scatter(
            x=data.index,
            y=data["RSI"],
            line=dict(color="purple")
        ))
        rsi_fig.update_layout(template="plotly_dark", height=200)
        st.plotly_chart(rsi_fig, use_container_width=True)

    else:
        st.warning("⚠️ No data available (Yahoo limitation)")

# ===================== WATCHLIST =====================
with col2:

    st.markdown("## 📊 Watchlist")

    @st.cache_data(ttl=5)
    def get_price(symbol):
        try:
            d = yf.download(symbol, period="1d", interval="1m")

            if d.empty or len(d) < 2:
                return None

            price = float(d["Close"].iloc[-1])
            prev = float(d["Close"].iloc[-2])

            pct = ((price - prev)/prev)*100
            return float(price), float(pct)

        except:
            return None

    for name, symbol in WATCHLIST.items():

        res = get_price(symbol)

        if res:
            price, pct = res

            color = "green" if float(pct) >= 0 else "red"   # ✅ FIXED ERROR

            if st.button(name):
                st.session_state.selected = name
                st.rerun()

            st.markdown(
                f"<span style='color:{color}'>{price:.2f} ({pct:.2f}%)</span>",
                unsafe_allow_html=True
            )
        else:
            st.write(f"{name} - no data")

    st.markdown("---")

    # ===================== NEWS =====================
    st.markdown("## 📰 News")

    try:
        news = yf.Ticker(ticker).news

        if news:
            for item in news[:5]:
                title = item.get("title")
                link = item.get("link")

                if title:
                    st.markdown(f"[{title}]({link})")
                    st.write("---")
        else:
            st.write("No news")

    except:
        st.write("News error")

# ===================== AUTO REFRESH =====================
time.sleep(5)
st.rerun()
