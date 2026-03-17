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
