import streamlit as st

st.set_page_config(layout="wide")

st.title("📈 TradeView Pro (Real-Time)")

# ===================== SYMBOL MAP =====================
SYMBOLS = {
    "Gold (XAU/USD)": "OANDA:XAUUSD",
    "EUR/USD": "OANDA:EURUSD",
    "GBP/USD": "OANDA:GBPUSD",
    "USD/JPY": "OANDA:USDJPY",
    "Apple": "NASDAQ:AAPL",
    "NVIDIA": "NASDAQ:NVDA",
    "Tesla": "NASDAQ:TSLA",
    "Reliance": "NSE:RELIANCE",
    "TCS": "NSE:TCS"
}

TIMEFRAMES = {
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

# ===================== UI =====================
col1, col2 = st.columns([5,1])

with col1:

    selected = st.selectbox(
        "Asset",
        list(SYMBOLS.keys()),
        index=list(SYMBOLS.keys()).index(st.session_state.asset)
    )
    st.session_state.asset = selected

    # timeframe buttons
    tf_cols = st.columns(len(TIMEFRAMES))

    for i, tf in enumerate(TIMEFRAMES.keys()):
        if tf_cols[i].button(
            tf,
            type="primary" if st.session_state.tf == tf else "secondary"
        ):
            st.session_state.tf = tf

    symbol = SYMBOLS[selected]
    interval = TIMEFRAMES[st.session_state.tf]

    # ===================== TRADINGVIEW WIDGET =====================
    st.components.v1.html(f"""
    <div id="tradingview_chart"></div>

    <script src="https://s3.tradingview.com/tv.js"></script>

    <script>
    new TradingView.widget({{
        "width": "100%",
        "height": 600,
        "symbol": "{symbol}",
        "interval": "{interval}",
        "timezone": "Asia/Kolkata",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#000000",
        "enable_publishing": false,
        "hide_top_toolbar": false,
        "save_image": false,
        "container_id": "tradingview_chart"
    }});
    </script>
    """, height=650)

# ===================== SIDE PANEL =====================
with col2:
    st.markdown("## 📊 Watchlist")

    for name in SYMBOLS.keys():
        st.write(f"• {name}")

    st.markdown("---")

    st.markdown("## 📰 News")
    st.write("Live news can be added next step")
