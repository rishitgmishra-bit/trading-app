import streamlit as st
from streamlit_autorefresh import st_autorefresh
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(layout="wide")

st.title("📈 TradeView Live (Stable)")

# ===================== AUTO REFRESH =====================
st_autorefresh(interval=5000, key="datarefresh")  # every 5 sec

# ===================== ASSETS =====================
ASSETS = {
    "Gold (XAU/USD)": ["XAUUSD=X", "GC=F"],
    "EUR/USD": ["EURUSD=X"],
    "GBP/USD": ["GBPUSD=X"],
    "USD/JPY": ["USDJPY=X"],
    "Apple": ["AAPL"],
    "NVIDIA": ["NVDA"],
    "Tesla": ["TSLA"],
    "Reliance": ["RELIANCE.NS"],
    "TCS": ["TCS.NS"]
}

TIMEFRAMES = ["1m", "5m", "15m", "1H", "1D"]

def get_params(tf):
    return {
        "1m": ("1d", "1m"),
        "5m": ("5d", "5m"),
        "15m": ("1mo", "15m"),
        "1H": ("3mo", "1h"),
        "1D": ("1y", "1d")
    }[tf]

# ===================== SESSION =====================
if "asset" not in st.session_state:
    st.session_state.asset = "EUR/USD"

if "tf" not in st.session_state:
    st.session_state.tf = "5m"

# ===================== DATA =====================
@st.cache_data(ttl=5)
def get_data(tickers, period, interval):
    for t in tickers:
        try:
            data = yf.download(t, period=period, interval=interval)
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)
            data = data.dropna()
            if not data.empty:
                return data
        except:
            continue
    return pd.DataFrame()

# ===================== UI =====================
col1, col2 = st.columns([5,1])

with col1:

    selected = st.selectbox(
        "Asset",
        list(ASSETS.keys()),
        index=list(ASSETS.keys()).index(st.session_state.asset)
    )
    st.session_state.asset = selected
    tickers = ASSETS[selected]

    # Timeframes
    tf_cols = st.columns(len(TIMEFRAMES))
    for i, tf in enumerate(TIMEFRAMES):
        if tf_cols[i].button(
            tf,
            type="primary" if st.session_state.tf == tf else "secondary"
        ):
            st.session_state.tf = tf

    tf = st.session_state.tf
    period, interval = get_params(tf)

    st.markdown(f"### {selected} ({tf})")

    data = get_data(tickers, period, interval)

    if data.empty and tf == "1m":
        period, interval = "5d", "5m"
        data = get_data(tickers, period, interval)
        st.warning("1m unavailable → switched to 5m")

    if not data.empty:
        data = data.tail(200)
        price = data["Close"].iloc[-1]

        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            increasing_line_color='#00ff88',
            decreasing_line_color='#ff4444'
        ))

        fig.add_hline(y=price, line_dash="dot", line_color="red")

        fig.update_layout(
            template="plotly_dark",
            height=600,
            xaxis_rangeslider_visible=False,
            plot_bgcolor="#000000",
            paper_bgcolor="#000000",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            f"<h2 style='color:#00ff88'>Price: {price:.5f}</h2>",
            unsafe_allow_html=True
        )

    else:
        st.error("No data")

# ===================== WATCHLIST =====================
with col2:
    st.markdown("## 📊 Watchlist")

    for name, tickers in ASSETS.items():
        data = get_data(tickers, "1d", "5m")

        if not data.empty:
            price = data["Close"].iloc[-1]
            prev = data["Close"].iloc[-2]
            change = price - prev
            pct = (change / prev) * 100

            color = "green" if change >= 0 else "red"

            st.markdown(f"""
            **{name}**  
            <span style='color:{color}'>{price:.2f} ({pct:.2f}%)</span>
            """, unsafe_allow_html=True)
