import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import time
import threading

st.set_page_config(layout="wide")
st.title("Advanced Trading Dashboard")

# ===================== STOCK MAP =====================

STOCKS = {
    "Apple (AAPL)": "AAPL",
    "NVIDIA (NVDA)": "NVDA",
    "Microsoft (MSFT)": "MSFT",
    "Google (GOOGL)": "GOOGL",
    "Tesla (TSLA)": "TSLA",
    "Coforge (COFORGE.NS)": "COFORGE.NS",
    "Reliance Industries (RELIANCE.NS)": "RELIANCE.NS",
    "TCS (TCS.NS)": "TCS.NS",
    "Infosys (INFY.NS)": "INFY.NS",
    "HDFC Bank (HDFCBANK.NS)": "HDFCBANK.NS"
}

# ===================== FUNCTIONS =====================

@st.cache_data(ttl=60)
def get_data(ticker, period, interval):
    data = yf.download(ticker, period=period, interval=interval)

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)

    return data.dropna()

def add_indicators(data):
    data["EMA20"] = data["Close"].ewm(span=20).mean()

    data["VWAP"] = (data["Close"] * data["Volume"]).cumsum() / data["Volume"].cumsum()

    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()

    rs = gain / loss
    data["RSI"] = 100 - (100 / (1 + rs))

    return data

def generate_signals(data):
    data["Signal"] = 0

    for i in range(1, len(data)):
        if data["Close"].iloc[i] > data["EMA20"].iloc[i] and data["RSI"].iloc[i] < 30:
            data.loc[data.index[i], "Signal"] = 1
        elif data["Close"].iloc[i] < data["EMA20"].iloc[i] and data["RSI"].iloc[i] > 70:
            data.loc[data.index[i], "Signal"] = -1

    return data

def get_news(ticker):
    try:
        stock = yf.Ticker(ticker)
        return stock.news[:5]
    except:
        return []

# ===================== TABS =====================

tab1, tab2, tab3 = st.tabs(["Chart", "Investments", "News"])

# ===================== TAB 1 =====================

with tab1:
    st.header("Live Chart")

    selected_stock = st.sidebar.selectbox("Stock", list(STOCKS.keys()))
    stock = STOCKS[selected_stock]

    timeframe = st.sidebar.selectbox(
        "Timeframe",
        ["1d", "5d", "1mo", "3mo", "6mo", "1y"]
    )

    interval = st.sidebar.selectbox(
        "Interval",
        ["1m", "5m", "15m", "30m", "1h", "1d"]
    )

    if timeframe == "1d" and interval == "1d":
        interval = "5m"

    data = get_data(stock, timeframe, interval)

    if not data.empty:
        data = add_indicators(data)
        data = generate_signals(data)

        latest = data.iloc[-1]

        col1, col2, col3 = st.columns(3)
        col1.metric("Price", f"{latest['Close']:.2f}")
        col2.metric("High", f"{latest['High']:.2f}")
        col3.metric("Low", f"{latest['Low']:.2f}")

        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name="Candles"
        ))

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["EMA20"],
            name="EMA 20"
        ))

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["VWAP"],
            name="VWAP"
        ))

        buy = data[data["Signal"] == 1]
        sell = data[data["Signal"] == -1]

        fig.add_trace(go.Scatter(
            x=buy.index,
            y=buy["Close"],
            mode="markers",
            marker=dict(symbol="triangle-up", size=10),
            name="BUY"
        ))

        fig.add_trace(go.Scatter(
            x=sell.index,
            y=sell["Close"],
            mode="markers",
            marker=dict(symbol="triangle-down", size=10),
            name="SELL"
        ))

        fig.update_layout(
            title=f"{selected_stock} Chart",
            xaxis_rangeslider_visible=False,
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("RSI")

        rsi_fig = go.Figure()
        rsi_fig.add_trace(go.Scatter(
            x=data.index,
            y=data["RSI"]
        ))

        rsi_fig.add_hline(y=70)
        rsi_fig.add_hline(y=30)

        st.plotly_chart(rsi_fig, use_container_width=True)

    else:
        st.error("No data found.")

# ===================== TAB 2 =====================

with tab2:
    st.header("Investment Ideas")

    cols = st.columns(3)

    for i, (name, ticker) in enumerate(STOCKS.items()):
        with cols[i % 3]:
            st.markdown(f"### {name}")

            data = get_data(ticker, "6mo", "1d")

            if not data.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=data["Close"]
                ))

                fig.update_layout(height=250)
                st.plotly_chart(fig, use_container_width=True)

# ===================== TAB 3 =====================

with tab3:
    st.header("Market News")

    news_tab1, news_tab2 = st.tabs(["USA", "India"])

    with news_tab1:
        news = get_news("AAPL")

        if news:
            for item in news:
                title = item.get("title", "No Title Available")
                link = item.get("link", "#")

                st.markdown(f"### {title}")
                st.markdown(f"[Read more]({link})")
                st.write("---")
        else:
            st.write("No news available.")

    with news_tab2:
        news = get_news("RELIANCE.NS")

        if news:
            for item in news:
                title = item.get("title", "No Title Available")
                link = item.get("link", "#")

                st.markdown(f"### {title}")
                st.markdown(f"[Read more]({link})")
                st.write("---")
        else:
            st.write("No news available.")

# ===================== AUTO REFRESH =====================

def auto_refresh():
    time.sleep(60)
    st.rerun()

threading.Thread(target=auto_refresh).start()

# ===================== FOOTER =====================

st.markdown(
    "<div style='position: fixed; right: 20px; bottom: 10px;'>Rishit</div>",
    unsafe_allow_html=True
)
