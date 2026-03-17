import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import time
import threading

st.set_page_config(layout="wide")
st.title("Multi-Market Trading Dashboard")

# ===================== ASSETS =====================

ASSETS = {
    "Apple (AAPL)": "AAPL",
    "NVIDIA (NVDA)": "NVDA",
    "Microsoft (MSFT)": "MSFT",
    "Google (GOOGL)": "GOOGL",
    "Tesla (TSLA)": "TSLA",

    "Reliance (RELIANCE.NS)": "RELIANCE.NS",
    "TCS (TCS.NS)": "TCS.NS",
    "Infosys (INFY.NS)": "INFY.NS",

    # Forex
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "USD/INR": "USDINR=X",

    # Gold with fallback
    "Gold (XAU/USD)": ["XAUUSD=X", "GC=F"]
}

# ===================== FUNCTIONS =====================

def fetch_data(ticker, period, interval):
    try:
        data = yf.download(ticker, period=period, interval=interval)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        return data.dropna()
    except:
        return pd.DataFrame()

@st.cache_data(ttl=10)
def get_data(ticker, period, interval):
    # Handle gold fallback
    if isinstance(ticker, list):
        for t in ticker:
            data = fetch_data(t, period, interval)
            if not data.empty:
                return data
        return pd.DataFrame()
    else:
        data = fetch_data(ticker, period, interval)

        # fallback if empty
        if data.empty and interval == "1m":
            data = fetch_data(ticker, period, "5m")

        return data

def add_indicators(data):
    data["EMA20"] = data["Close"].ewm(span=20).mean()

    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()

    rs = gain / loss
    data["RSI"] = 100 - (100 / (1 + rs))

    return data

def get_news(ticker):
    try:
        stock = yf.Ticker(ticker if isinstance(ticker, str) else ticker[0])
        return stock.news[:5]
    except:
        return []

# ===================== TABS =====================

tab1, tab2, tab3 = st.tabs(["Chart", "Investments", "News"])

# ===================== TAB 1 =====================

with tab1:
    st.header("Live Chart")

    selected_asset = st.sidebar.selectbox("Market", list(ASSETS.keys()))
    ticker = ASSETS[selected_asset]

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

    data = get_data(ticker, timeframe, interval)

    if not data.empty:
        data = add_indicators(data)
        latest = data.iloc[-1]

        col1, col2, col3 = st.columns(3)
        col1.metric("Price", f"{latest['Close']:.5f}")
        col2.metric("High", f"{latest['High']:.5f}")
        col3.metric("Low", f"{latest['Low']:.5f}")

        fig = go.Figure()

        # Detect if OHLC exists properly
        if all(col in data.columns for col in ["Open", "High", "Low", "Close"]):
            fig.add_trace(go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name="Candles"
            ))
        else:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data["Close"],
                name="Price"
            ))

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["EMA20"],
            name="EMA 20"
        ))

        fig.update_layout(
            title=f"{selected_asset}",
            xaxis_rangeslider_visible=False,
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

        # RSI
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
        st.error("No data available")

# ===================== TAB 2 =====================

with tab2:
    st.header("Investment Ideas")

    cols = st.columns(3)

    for i, (name, ticker) in enumerate(ASSETS.items()):
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
            else:
                st.write("No data")

# ===================== TAB 3 =====================

with tab3:
    st.header("Market News")

    news = get_news("AAPL")

    if news:
        for item in news:
            title = item.get("title", "No Title")
            link = item.get("link", "#")

            st.markdown(f"### {title}")
            st.markdown(f"[Read more]({link})")
            st.write("---")
    else:
        st.write("No news available.")

# ===================== AUTO REFRESH =====================

def auto_refresh():
    time.sleep(10)
    st.rerun()

threading.Thread(target=auto_refresh).start()

# ===================== FOOTER =====================

st.markdown(
    "<div style='position: fixed; right: 20px; bottom: 10px;'>Rishit</div>",
    unsafe_allow_html=True
)
