import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import threading
import time

st.set_page_config(layout="wide")
st.title("Simple Trading Chart Viewer")

# ===================== AUTO REFRESH =====================
def auto_refresh():
    time.sleep(5)  # 🔥 update every 5 seconds
    st.rerun()

threading.Thread(target=auto_refresh).start()

# ===================== FUNCTIONS =====================

@st.cache_data(ttl=5)  # refresh data every 5 sec
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

# ===================== TABS =====================

tab1, tab2, tab3 = st.tabs(["Chart Viewer", "Investment Recommendations", "Market News"])

# ===================== TAB 1 =====================

with tab1:
    st.header("Stock Chart Viewer")

    st.sidebar.header("Chart Settings")

    stock = st.sidebar.selectbox(
        "Select Stock",
        ["AAPL", "NVDA", "GOOGL", "MSFT", "TSLA", "COFORGE.NS"]
    )

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

    st.write(f"Displaying {timeframe} chart for {stock} with {interval} intervals.")

    data = get_data(stock, timeframe, interval)

    if not data.empty:
        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close']
        ))

        fig.update_layout(
            title=f"{stock} Chart",
            xaxis_rangeslider_visible=False
        )

        st.plotly_chart(fig, use_container_width=True)

        latest = data.iloc[-1]
        st.subheader("Latest Data")

        st.write(f"**Price:** {latest['Close']:.2f}")
        st.write(f"**High:** {latest['High']:.2f}")
        st.write(f"**Low:** {latest['Low']:.2f}")

    else:
        st.error("No data available.")

# ===================== TAB 2 =====================

with tab2:
    st.header("Long-Term Investment Recommendations")

    stocks = [
        ("AAPL", "Strong ecosystem"),
        ("NVDA", "AI leader"),
        ("MSFT", "Cloud + AI"),
        ("GOOGL", "Search dominance"),
        ("TSLA", "EV growth"),
        ("RELIANCE.NS", "India growth"),
        ("TCS.NS", "IT leader"),
        ("INFY.NS", "Stable IT"),
        ("HDFCBANK.NS", "Banking giant")
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
                    y=data["Close"]
                ))

                fig.update_layout(height=250)
                st.plotly_chart(fig, use_container_width=True)

# ===================== TAB 3 =====================

with tab3:
    st.header("Live Market News")

    news_tab1, news_tab2 = st.tabs(["USA Market", "Indian Market"])

    with news_tab1:
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

    with news_tab2:
        news = get_news("RELIANCE.NS")

        if news:
            for item in news:
                title = item.get("title", "No Title")
                link = item.get("link", "#")

                st.markdown(f"### {title}")
                st.markdown(f"[Read more]({link})")
                st.write("---")
        else:
            st.write("No news available.")

# ===================== FOOTER =====================

st.sidebar.markdown("---")
st.sidebar.write("Welcome")

st.markdown(
    "<div style='position: fixed; right: 20px; bottom: 10px;'>Rishit</div>",
    unsafe_allow_html=True
)
