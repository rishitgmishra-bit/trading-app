import streamlit as st
import yfinance as yf

st.set_page_config(layout="wide")

st.title("📈 TradeView Pro (Real-Time)")

# ===================== SYMBOLS =====================
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

WATCHLIST = {
    "Gold (XAU/USD)": "XAUUSD=X",
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "Apple": "AAPL",
    "NVIDIA": "NVDA",
    "Tesla": "TSLA",
    "Reliance": "RELIANCE.NS",
    "TCS": "TCS.NS"
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
            type="primary" if st.session_state.tf == tf else "secondary",
            key=f"tf_{tf}"
        ):
            st.session_state.tf = tf

    symbol = SYMBOLS[selected]
    interval = TIMEFRAMES[st.session_state.tf]

    st.markdown(f"### {selected} ({st.session_state.tf})")

    # ===================== TRADINGVIEW =====================
    st.components.v1.html(f"""
    <div id="tv_chart"></div>

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
        "container_id": "tv_chart"
    }});
    </script>
    """, height=650)

# ===================== WATCHLIST =====================
with col2:
    st.markdown("## 📊 Watchlist")

    @st.cache_data(ttl=5)
    def get_price(ticker):
        try:
            data = yf.download(ticker, period="1d", interval="1m", progress=False)

            if data is None or data.empty:
                return None

            data = data.dropna()

            if len(data) < 2:
                return None

            price = float(data["Close"].iloc[-1])
            prev = float(data["Close"].iloc[-2])

            change = price - prev
            pct = (change / prev) * 100

            return price, change, pct

        except:
            return None

    for name, ticker in WATCHLIST.items():

        result = get_price(ticker)

        if result:
            price, change, pct = result
            color = "green" if change >= 0 else "red"

            # 🔥 CLICKABLE WATCHLIST ITEM
            if st.button(f"{name}   {price:.2f} ({pct:.2f}%)", key=name):
                st.session_state.asset = name
                st.rerun()

            # info display
            st.markdown(f"""
            <div style='margin-bottom:12px'>
                <span style='color:{color}; font-size:14px'>
                    {price:.2f} ({pct:.2f}%)
                </span>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.write(f"{name} - No data")

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
            st.write("No news available")

    except:
        st.write("News unavailable")
