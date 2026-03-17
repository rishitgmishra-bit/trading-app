import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide")

st.title("Advanced Trading Dashboard")

# Auto refresh every 60 seconds
st_autorefresh(interval=60000, key="refresh")

# ===================== FUNCTIONS =====================

@st.cache_data(ttl=60)
def get_data(ticker, period, interval):
    data = yf.download(ticker, period=period, interval=interval)

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)

    return data.dropna()

def add_indicators(data):
    # EMA
    data["EMA20"] = data["Close"].ewm(span=20).mean()

    # VWAP
    data["VWAP"] = (data["Close"] * data["Volume"]).cumsum() / data["Volume"].cumsum()

    # RSI
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()

    rs = gain / loss
    data["RSI"] = 100 - (100 / (1 + rs))

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

    # Sidebar
    stock = st.sidebar.selectbox(
        "Stock",
        ["AAPL", "NVDA", "MSFT", "GOOGL", "TSLA", "COFORGE.NS"]
    )

    timeframe = st.sidebar.selectbox(
        "Timeframe",
        ["1d", "5d", "1mo", "3mo", "6mo", "1y"]
    )

    interval = st.sidebar.selectbox(
        "Interval",
        ["1m", "5m", "15m", "30m", "1h", "1d"]
    )

    # Fix invalid combos
    if timeframe == "1d" and interval == "1d":
        interval = "5m"

    with st.spinner("Fetching data..."):
        data = get_data(stock, timeframe, interval)

    if not data.empty:
        data = add_indicators(data)

        latest = data.iloc[-1]

        # ===== Metrics =====
        col1, col2, col3 = st.columns(3)
        col1.metric("Price", f"{latest['Close']:.2f}")
        col2.metric("High", f"{latest['High']:.2f}")
        col3.metric("Low", f"{latest['Low']:.2f}")

        # ===== Chart =====
        fig = go.Figure()

        # Candlestick
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
            y=data["EMA20"],
            line=dict(width=1),
            name="EMA 20"
        ))

        # VWAP
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["VWAP"],
            line=dict(width=1),
            name="VWAP"
        ))

        fig.update_layout(
            title=f"{stock} Chart",
            xaxis_rangeslider_visible=False,
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

        # ===== RSI =====
        st.subheader("RSI Indicator")

        rsi_fig = go.Figure()
        rsi_fig.add_trace(go.Scatter(
            x=data.index,
            y=data["RSI"],
            name="RSI"
        ))

        rsi_fig.add_hline(y=70)
        rsi_fig.add_hline(y=30)

        rsi_fig.update_layout(height=300)

        st.plotly_chart(rsi_fig, use_container_width=True)

    else:
        st.error("No data found.")

# ===================== TAB 2 =====================

with tab2:
    st.header("Investment Ideas (Long-Term)")

    st.write("Not financial advice.")

    stocks = [
        ("AAPL", "Strong ecosystem + services"),
        ("NVDA", "AI leader"),
        ("MSFT", "Cloud + AI"),
        ("GOOGL", "Search dominance"),
        ("TSLA", "EV + energy"),
        ("RELIANCE.NS", "India growth giant"),
        ("TCS.NS", "IT leader"),
        ("INFY.NS", "Stable IT"),
        ("HDFCBANK.NS", "Banking strength")
    ]

    cols = st.columns(3)

    for i, (ticker, reason) in enumerate(stocks):
        with cols[i % 3]:
            st.markdown(f"### {ticker}")
            st.write(reason)

            data = get_data(ticker, "6mo", "1d")

            if not data.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=data["Close"],
                    name="Price"
                ))

                fig.update_layout(height=250)
                st.plotly_chart(fig, use_container_width=True)

# ===================== TAB 3 =====================

with tab3:
    st.header("Live Market News")

    news_tab1, news_tab2 = st.tabs(["USA", "India"])

    with news_tab1:
        st.subheader("USA Market News")
        news = get_news("AAPL")

        for item in news:
            st.write(f"**{item['title']}**")
            st.write(f"[Read more]({item['link']})")
            st.write("---")

    with news_tab2:
        st.subheader("Indian Market News")
        news = get_news("RELIANCE.NS")

        for item in news:
            st.write(f"**{item['title']}**")
            st.write(f"[Read more]({item['link']})")
            st.write("---")

# ===================== FOOTER =====================

st.markdown(
    "<div style='position: fixed; right: 20px; bottom: 10px;'>Rishit</div>",
    unsafe_allow_html=True
)
