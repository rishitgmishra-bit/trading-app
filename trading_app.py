import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import time

st.title("Simple Trading Chart Viewer")

# Create tabs
tab1, tab2, tab3 = st.tabs(["Chart Viewer", "Investment Recommendations", "Market News"])

with tab1:
    st.header("Stock Chart Viewer")

    st.sidebar.header("Chart Settings")

    # Stock selection
    stock = st.sidebar.selectbox("Select Stock", ["AAPL", "NVDA", "GOOGL", "MSFT", "TSLA", "COFORGE.NS"], index=0, key="stock_select")

    # Timeframe selection
    timeframe = st.sidebar.selectbox("Timeframe", ["1d", "5d", "1mo", "3mo", "6mo", "1y"], index=2, key="timeframe_select")

    # Interval
    interval = st.sidebar.selectbox("Interval", ["1m", "5m", "15m", "30m", "1h", "1d"], index=5, key="interval_select")

    # Refresh button
    refresh = st.sidebar.button("Refresh Data", key="refresh_btn")

    st.write(f"Displaying {timeframe} chart for {stock} with {interval} intervals.")

    @st.cache_data(ttl=300)
    def get_data(ticker, period, interval):
        data = yf.download(ticker, period=period, interval=interval)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        return data.dropna()

    if refresh or 'data' not in st.session_state:
        with st.spinner("Fetching data..."):
            st.session_state.data = get_data(stock, timeframe, interval)

    data = st.session_state.data

    if not data.empty:
        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Candlesticks'
        )])

        fig.update_layout(
            title=f"{stock} Candlestick Chart ({timeframe})",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            xaxis_rangeslider_visible=False
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Latest Data")
        latest = data.iloc[-1]
        st.write(f"**Date:** {data.index[-1].strftime('%Y-%m-%d %H:%M')}")
        st.write(f"**Open:** {latest['Open']:.2f}")
        st.write(f"**High:** {latest['High']:.2f}")
        st.write(f"**Low:** {latest['Low']:.2f}")
        st.write(f"**Close:** {latest['Close']:.2f}")
        st.write(f"**Volume:** {latest['Volume']:,}")

    else:
        st.error("No data available for the selected parameters.")

with tab2:
    st.header("Long-Term Investment Recommendations for 2026")

    st.write("**Disclaimer:** This is not financial advice.")

    usa_recommendations = {
        "Apple (AAPL)": "Strong brand and services growth.",
        "Nvidia (NVDA)": "AI and GPU leader.",
        "Microsoft (MSFT)": "Cloud + AI dominance.",
        "Google (GOOGL)": "Search + AI growth.",
        "Tesla (TSLA)": "EV and energy potential."
    }

    india_recommendations = {
        "Coforge (COFORGE.NS)": "Digital IT growth.",
        "Reliance (RELIANCE.NS)": "Diversified giant.",
        "Infosys (INFY.NS)": "Stable IT.",
        "HDFC Bank (HDFCBANK.NS)": "Strong banking.",
        "TCS (TCS.NS)": "Top IT firm."
    }

    rec_tab1, rec_tab2 = st.tabs(["USA", "India"])

    def display_recommendations(rec_dict):
        cols = st.columns(2)
        for i, (stock, reason) in enumerate(rec_dict.items()):
            ticker = stock.split('(')[1].strip(')')
            with cols[i % 2]:
                st.markdown(f"**{stock}**")
                st.write(reason)

                data = yf.download(ticker, period='1y', interval='1d')
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.droplevel(1)

                if not data.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=data.index, y=data['Close']))
                    fig.update_layout(height=250)
                    st.plotly_chart(fig, use_container_width=True)

    with rec_tab1:
        display_recommendations(usa_recommendations)

    with rec_tab2:
        display_recommendations(india_recommendations)

with tab3:
    st.header("Market News")

    news_tab1, news_tab2 = st.tabs(["USA", "India"])

    sample_news = [
        {"title": "Market Rally Continues", "date": "2026-03-15"},
        {"title": "Fed Policy Update", "date": "2026-03-14"},
        {"title": "Tech Stocks Surge", "date": "2026-03-13"}
    ]

    with news_tab1:
        for item in sample_news:
            st.write(f"**{item['title']}** ({item['date']})")

    with news_tab2:
        for item in sample_news:
            st.write(f"**{item['title']}** ({item['date']})")

st.sidebar.markdown("---")
st.sidebar.write("Welcome")

st.markdown(
    "<div style='position: fixed; right: 20px; bottom: 10px;'>Rishit</div>",
    unsafe_allow_html=True
)
