import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(layout="wide")

st.title("📈 TradeView Lite (Streamlit)")

# ===================== TABS =====================
tab1, tab2, tab3 = st.tabs(["Chart Viewer", "Investment Ideas", "Market News"])

# ===================== TAB 1 =====================
with tab1:
    st.sidebar.header("Chart Settings")

    STOCKS = {
        "Apple": "AAPL",
        "NVIDIA": "NVDA",
        "Google": "GOOGL",
        "Microsoft": "MSFT",
        "Tesla": "TSLA",
        "Coforge (India)": "COFORGE.NS"
    }

    stock_name = st.sidebar.selectbox("Select Asset", list(STOCKS.keys()))
    ticker = STOCKS[stock_name]

    timeframe = st.sidebar.selectbox("Timeframe", ["1d", "5d", "1mo", "3mo", "6mo", "1y"])
    interval = st.sidebar.selectbox("Interval", ["1m", "5m", "15m", "30m", "1h", "1d"])

    st.subheader(f"{stock_name} Chart")

    # ===================== DATA =====================
    @st.cache_data(ttl=60)
    def get_data():
        data = yf.download(ticker, period=timeframe, interval=interval)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        return data.dropna()

    data = get_data()

    if not data.empty:
        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close']
        )])

        fig.update_layout(
            xaxis_rangeslider_visible=False,
            template="plotly_dark",
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

        # ===================== LATEST =====================
        latest = data.iloc[-1]
        st.markdown("### Latest Data")
        st.write(f"Close: {latest['Close']:.2f}")
        st.write(f"High: {latest['High']:.2f}")
        st.write(f"Low: {latest['Low']:.2f}")
    else:
        st.error("No data available")

# ===================== TAB 2 =====================
with tab2:
    st.header("📊 Investment Ideas")

    ideas = {
        "Apple": "Strong ecosystem, consistent growth",
        "NVIDIA": "AI leader, strong demand",
        "Microsoft": "Cloud + AI dominance",
        "Reliance": "India growth + diversification",
        "TCS": "Stable IT giant"
    }

    for name, desc in ideas.items():
        st.markdown(f"### {name}")
        st.write(desc)
        try:
            data = yf.download(STOCKS.get(name, "AAPL"), period="1y")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data.index, y=data['Close']))
            fig.update_layout(height=250, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.write("Chart unavailable")

# ===================== TAB 3 =====================
with tab3:
    st.header("📰 Market News")

    try:
        news = yf.Ticker("AAPL").news

        if news:
            for item in news[:10]:
                title = item.get("title", "No title")
                link = item.get("link", "#")
                st.markdown(f"### [{title}]({link})")
                st.write("---")
        else:
            st.write("No news available")

    except:
        st.write("News unavailable")

# ===================== SIDEBAR =====================
st.sidebar.markdown("---")
st.sidebar.write("👋 Welcome to TradeView Lite")
