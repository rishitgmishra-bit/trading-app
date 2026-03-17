import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import math

st.set_page_config(layout="wide")

st.title("📈 TradeView Hybrid (Stable)")

# ===================== SYMBOLS =====================
SYMBOLS = {
    # Forex
    "Gold (XAU/USD)": "OANDA:XAUUSD",
    "EUR/USD": "OANDA:EURUSD",
    "GBP/USD": "OANDA:GBPUSD",
    "USD/JPY": "OANDA:USDJPY",

    # US Stocks
    "Apple": "NASDAQ:AAPL",
    "NVIDIA": "NASDAQ:NVDA",
    "Tesla": "NASDAQ:TSLA",

    # Indian Stocks
    "Reliance": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "Coforge": "COFORGE.NS",
    "Nifty 50": "^NSEI"
}

INDIAN = [
    "Reliance", "TCS", "Infosys",
    "HDFC Bank", "ICICI Bank",
    "Coforge", "Nifty 50"
]

TIMEFRAMES = {
    "1m": ("1d", "1m"),
    "5m": ("5d", "5m"),
    "15m": ("1mo", "15m"),
    "1H": ("3mo", "1h"),
    "1D": ("1y", "1d")
}

TV_INTERVAL = {
    "1m": "1",
    "5m": "5",
    "15m": "15",
    "1H": "60",
    "1D": "D"
}

# ===================== SESSION =====================
if "asset" not in st.session_state:
    st.session_state.asset = "EUR/USD"

if "tf" not in st.session_state:
    st.session_state.tf = "5m"

# ===================== LAYOUT =====================
col1, col2 = st.columns([5,1])

# ===================== MAIN =====================
with col1:

    selected = st.selectbox(
        "Asset",
        list(SYMBOLS.keys()),
        index=list(SYMBOLS.keys()).index(st.session_state.asset)
    )
    st.session_state.asset = selected

    # Timeframes
    tf_cols = st.columns(len(TIMEFRAMES))
    for i, tf in enumerate(TIMEFRAMES.keys()):
        if tf_cols[i].button(
            tf,
            type="primary" if st.session_state.tf == tf else "secondary"
        ):
            st.session_state.tf = tf

    st.markdown(f"### {selected} ({st.session_state.tf})")

    # ===================== HYBRID =====================
    if selected not in INDIAN:
        # 🔥 TradingView
        symbol = SYMBOLS[selected]
        interval = TV_INTERVAL[st.session_state.tf]

        st.components.v1.html(f"""
        <div id="tv_chart"></div>
        <script src="https://s3.tradingview.com/tv.js"></script>
        <script>
        new TradingView.widget({{
            "width": "100%",
            "height": 600,
            "symbol": "{symbol}",
            "interval": "{interval}",
            "theme": "dark",
            "container_id": "tv_chart"
        }});
        </script>
        """, height=650)

    else:
        # 🇮🇳 Indian fallback
        ticker = SYMBOLS[selected]
        period, interval = TIMEFRAMES[st.session_state.tf]

        data = yf.download(ticker, period=period, interval=interval)

        # 🔥 CLEAN DATA
        if not data.empty:
            data = data.dropna().tail(200)

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

            # 🔥 SAFE PRICE LINE
            price = data["Close"].iloc[-1]

            if isinstance(price, (int, float)) and not math.isnan(price):
                fig.add_hline(y=float(price), line_dash="dot", line_color="red")

            fig.update_layout(
                template="plotly_dark",
                height=600,
                xaxis_rangeslider_visible=False,
                plot_bgcolor="#000000",
                paper_bgcolor="#000000"
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.error("No data available")

# ===================== WATCHLIST =====================
with col2:
    st.markdown("## 📊 Watchlist")

    for name in SYMBOLS.keys():
        if st.button(name):
            st.session_state.asset = name
            st.rerun()
