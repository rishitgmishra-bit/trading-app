import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import time

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
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "USD/INR": "USDINR=X",
    "Gold (XAU/USD)": "XAUUSD=X"
}

# ===================== FUNCTIONS =====================

@st.cache_data(ttl=5)
def get_data(ticker):
    data = yf.download(ticker, period="1d", interval="1m")

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)

    return data.dropna()

def add_indicators(data):
    data["EMA20"] = data["Close"].ewm(span=20).mean()

    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()

    rs = gain / loss
    data["RSI"] = 100 - (100 / (1 + rs))

    return data

# ===================== UI =====================

selected_asset = st.sidebar.selectbox("Select Market", list(ASSETS.keys()))
ticker = ASSETS[selected_asset]

placeholder = st.empty()

# ===================== LOOP =====================

while True:
    data = get_data(ticker)

    if not data.empty:
        data = add_indicators(data)
        latest = data.iloc[-1]

        with placeholder.container():

            col1, col2, col3 = st.columns(3)
            col1.metric("Price", f"{latest['Close']:.5f}")
            col2.metric("High", f"{latest['High']:.5f}")
            col3.metric("Low", f"{latest['Low']:.5f}")

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
                y=data["EMA20"],
                name="EMA 20"
            ))

            fig.update_layout(
                title=f"{selected_asset}",
                xaxis_rangeslider_visible=False,
                height=600
            )

            st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("No data available")

    time.sleep(5)
