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

    @st.cache_data(ttl=300)  # Cache for 5 minutes
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
        # Create candlestick chart
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

        # Show latest data
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

    st.write("**Disclaimer:** This is not financial advice. Invest based on your research and risk tolerance. These are general suggestions based on historical performance and market trends.")

    usa_recommendations = {
        "Apple (AAPL)": "Strong brand, consistent innovation in tech, dividends, and growth in services.",
        "Nvidia (NVDA)": "Leader in AI and GPUs, high growth in data centers and gaming.",
        "Microsoft (MSFT)": "Dominant in cloud (Azure), software, and AI integration.",
        "Google (GOOGL)": "Monopoly in search, growing cloud and AI revenues.",
        "Tesla (TSLA)": "EV leader, energy storage, and autonomous driving potential."
    }

    india_recommendations = {
        "Coforge (COFORGE.NS)": "Indian IT services company with strong growth in digital transformation.",
        "Reliance Industries (RELIANCE.NS)": "Diversified conglomerate with strong presence in energy, telecom, and retail.",
        "Infosys (INFY.NS)": "Leading Indian IT firm with global clients and steady growth.",
        "HDFC Bank (HDFCBANK.NS)": "Major private bank with robust financials and digital banking focus.",
        "Tata Consultancy Services (TCS.NS)": "Top IT services company with consistent performance and global expansion."
    }

    rec_tab1, rec_tab2 = st.tabs(["USA Market Stocks", "Indian Market Stocks"])

    def display_recommendations(rec_dict, title):
        st.subheader(title)
        st.write("Hover over the charts for details. Data is delayed.")
        cols = st.columns(2)
        col_idx = 0
        for stock, reason in rec_dict.items():
            ticker = stock.split('(')[1].strip(')')
            with cols[col_idx % 2]:
                st.markdown(f"**{stock}**")
                st.write(reason)
                try:
                    data = yf.download(ticker, period='1y', interval='1d')
                    if isinstance(data.columns, pd.MultiIndex):
                        data.columns = data.columns.droplevel(1)
                    if not data.empty:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price'))
                        fig.update_layout(
                            title=f"{stock} - Last Year",
                            xaxis_title="Date",
                            yaxis_title="Price",
                            height=300,
                            margin=dict(l=20, r=20, t=40, b=20)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.write("No data available.")
                except Exception as e:
                    st.write(f"Error loading chart: {str(e)}")
            col_idx += 1

    with rec_tab1:
        display_recommendations(usa_recommendations, "USA Market Recommendations")

    with rec_tab2:
        display_recommendations(india_recommendations, "Indian Market Recommendations")

with tab3:
    st.header("Latest Market News")

    news_tab1, news_tab2 = st.tabs(["USA Stock Market", "Indian Stock Market"])

    with news_tab1:
        st.subheader("USA Market News")
        # Sample news for demo
        sample_news_usa = [
            {"title": "Apple Reports Strong Q4 Earnings", "date": "2026-03-15", "link": "https://www.apple.com/newsroom/"},
            {"title": "Fed Signals Interest Rate Pause", "date": "2026-03-14", "link": "https://www.federalreserve.gov/"},
            {"title": "Tech Stocks Rally on AI Optimism", "date": "2026-03-13", "link": "https://www.cnbc.com/technology/"},
            {"title": "Nvidia Surpasses Market Expectations", "date": "2026-03-12", "link": "https://nvidianews.nvidia.com/"},
            {"title": "Market Outlook for 2026", "date": "2026-03-11", "link": "https://www.investopedia.com/"}
        ]
        for item in sample_news_usa:
            st.write(f"**{item['title']}**")
            st.write(f"Published: {item['date']}")
            st.write(f"[Read more]({item['link']})")
            st.write("---")

    with news_tab2:
        st.subheader("Indian Market News")
        # Sample news for demo
        sample_news_india = [
            {"title": "Sensex Hits New High Amid Reforms", "date": "2026-03-15", "link": "https://www.bseindia.com/"},
            {"title": "RBI Keeps Repo Rate Unchanged", "date": "2026-03-14", "link": "https://www.rbi.org.in/"},
            {"title": "IT Stocks Lead Market Gains", "date": "2026-03-13", "link": "https://www.nseindia.com/"},
            {"title": "TCS Expands Global Operations", "date": "2026-03-12", "link": "https://www.tcs.com/"},
            {"title": "Indian Economy Growth Forecast", "date": "2026-03-11", "link": "https://www.economictimes.com/"}
        ]
        for item in sample_news_india:
            st.write(f"**{item['title']}**")
            st.write(f"Published: {item['date']}")
            st.write(f"[Read more]({item['link']})")
            st.write("---")

st.sidebar.markdown("---")
st.sidebar.write("Welcome")

st.markdown(
    """
    <div style='position: fixed; right: 20px; bottom: 10px; color: gray; font-size: 16px; z-index: 9999;'>Rishit</div>
    """,
    unsafe_allow_html=True
)

