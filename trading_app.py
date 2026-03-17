import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.title("📈 TradeView Hybrid")

# ===================== SYMBOL MAP =====================
SYMBOLS = {
    "Gold (XAU/USD)": "OANDA:XAUUSD",
    "EUR/USD": "OANDA:EURUSD",
    "GBP/USD": "OANDA:GBPUSD",
    "USD/JPY": "OANDA:USDJPY",

    "Apple": "NASDAQ:AAPL",
    "NVIDIA": "NASDAQ:NVDA",
    "Tesla": "NASDAQ:TSLA",

    # Indian stocks (handled separately)
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
    "HDFC Bank", "ICICI Bank", "Coforge", "Nifty 50"
]

TIMEFRAMES = {
    "1m": ("1d", "1m"),
    "5m": ("5d", "5m"),
    "15m": ("1mo", "15m"),
    "1H": ("3mo", "1h"),
    "1D": ("1y", "1d")
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

    # Timeframe buttons
    tf_cols = st.columns(len(TIMEFRAMES))
    for i, tf in enumerate(TIMEFRAMES.keys()):
        if tf_cols[i].button(
            tf,
            type="primary" if st.session_state.tf == tf else "secondary"
        ):
            st.session_state.tf = tf

    st.markdown(f"### {selected} ({st.session_state.tf})")

    # ===================== HYBRID LOGIC =====================
    if selected not in INDIAN:
        # 🔥 TradingView (real-time)
        symbol = SYMBOLS[selected]
        interval = st.session_state.tf.replace("m","").replace("H","60").replace("D","D")

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
        # 🇮🇳 Indian stocks (Plotly)
        ticker = SYMBOLS[selected]
        period, interval = TIMEFRAMES[st.session_state.tf]

        data = yf.download(ticker, period=period, interval=interval)

        if not data.empty:
            data = data.tail(200)

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

            # price line
            price = data["Close"].iloc[-1]
            fig.add_hline(y=price, line_dash="dot", line_color="red")

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
