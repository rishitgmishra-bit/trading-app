import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import time

st.set_page_config(layout="wide")

st.title("📈 TradeView Style Chart")

# ===================== AUTO REFRESH =====================
if "last_update" not in st.session_state:
    st.session_state.last_update = time.time()

if time.time() - st.session_state.last_update > 5:
    st.session_state.last_update = time.time()
    st.rerun()

# ===================== ASSETS =====================
ASSETS = {
    "Gold (XAU/USD)": "XAUUSD=X",
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "NASDAQ": "^IXIC",
    "S&P 500": "^GSPC",
    "Tesla": "TSLA",
    "Apple": "AAPL"
}

# ===================== TIMEFRAME LOGIC =====================
TIMEFRAMES = {
    "1m": ("1d", "1m"),
    "5m": ("5d", "5m"),
    "15m": ("5d", "15m"),
    "1H": ("1mo", "1h"),
    "4H": ("3mo", "1h"),
    "1D": ("1y", "1d")
}

# ===================== DATA =====================
@st.cache_data(ttl=5)
def get_data(ticker, period, interval):
    data = yf.download(ticker, period=period, interval=interval)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)
    return data.dropna()

# ===================== UI =====================
col1, col2 = st.columns([5,1])

with col1:
    selected = st.selectbox("Select Asset", list(ASSETS.keys()))
    ticker = ASSETS[selected]

    # Timeframe buttons
    tf_cols = st.columns(len(TIMEFRAMES))
    selected_tf = None

    for i, tf in enumerate(TIMEFRAMES.keys()):
        if tf_cols[i].button(tf):
            st.session_state["tf"] = tf

    if "tf" not in st.session_state:
        st.session_state["tf"] = "1m"

    selected_tf = st.session_state["tf"]

    period, interval = TIMEFRAMES[selected_tf]

    st.markdown(f"### {selected} ({selected_tf})")

    data = get_data(ticker, period, interval)

    if not data.empty:
        latest = data.iloc[-1]
        price = latest["Close"]

        fig = go.Figure()

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            increasing_line_color='#00ff88',
            decreasing_line_color='#ff4444',
            line_width=1
        ))

        # Current price line
        fig.add_hline(y=price, line_dash="dot", line_color="red")

        # Support / Resistance style lines
        fig.add_hline(y=price * 0.995, line_color="white")
        fig.add_hline(y=price * 1.005, line_color="white")

        fig.update_layout(
            template="plotly_dark",
            height=700,
            xaxis_rangeslider_visible=False,
            plot_bgcolor="#000000",
            paper_bgcolor="#000000",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"""
        <span style='font-size:28px;color:#00ff88'>Price: {price:.2f}</span>
        """, unsafe_allow_html=True)

    else:
        st.error("No data available")

# ===================== SIDE PANEL =====================
with col2:
    st.markdown("## 📊 Watchlist")

    for name, tkr in ASSETS.items():
        data = get_data(tkr, "1d", "5m")

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

    st.markdown("---")

    # ===================== NEWS =====================
    st.markdown("## 📰 News")

    try:
        news = yf.Ticker("AAPL").news

        valid_news = []
        for item in news:
            title = item.get("title")
            link = item.get("link")

            if title and link:
                valid_news.append((title, link))

        if valid_news:
            for title, link in valid_news[:5]:
                st.markdown(f"[{title}]({link})")
                st.write("---")
        else:
            st.write("No valid news")

    except:
        st.write("News not available")
