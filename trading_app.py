import streamlit as st
import yfinance as yf

st.set_page_config(layout="wide")

st.title("📈 TradeView Pro (Advanced)")

# ===================== EXCHANGE TOGGLE =====================
exchange = st.sidebar.selectbox("Select Exchange", ["NSE", "BSE"])

suffix = ".NS" if exchange == "NSE" else ".BO"

# ===================== SYMBOL MAP =====================
SYMBOLS = {
    "Gold (XAU/USD)": "OANDA:XAUUSD",
    "EUR/USD": "OANDA:EURUSD",
    "GBP/USD": "OANDA:GBPUSD",
    "USD/JPY": "OANDA:USDJPY",

    "Apple": "NASDAQ:AAPL",
    "NVIDIA": "NASDAQ:NVDA",
    "Tesla": "NASDAQ:TSLA",

    # 🇮🇳 Indian Stocks
    "Reliance": f"{exchange}:RELIANCE",
    "TCS": f"{exchange}:TCS",
    "Infosys": f"{exchange}:INFY",
    "HDFC Bank": f"{exchange}:HDFCBANK",
    "ICICI Bank": f"{exchange}:ICICIBANK",
    "Coforge": f"{exchange}:COFORGE",

    # 🔥 Index
    "Nifty 50": f"{exchange}:NIFTY"
}

# ===================== WATCHLIST =====================
WATCHLIST = {
    "Gold": "XAUUSD=X",
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",

    "Apple": "AAPL",
    "NVIDIA": "NVDA",
    "Tesla": "TSLA",

    "Reliance": f"RELIANCE{suffix}",
    "TCS": f"TCS{suffix}",
    "Infosys": f"INFY{suffix}",
    "HDFC Bank": f"HDFCBANK{suffix}",
    "ICICI Bank": f"ICICIBANK{suffix}",
    "Coforge": f"COFORGE{suffix}",

    "Nifty 50": "^NSEI"
}

# ===================== TIMEFRAMES =====================
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

    # Timeframes
    tf_cols = st.columns(len(TIMEFRAMES))
    for i, tf in enumerate(TIMEFRAMES.keys()):
        if tf_cols[i].button(
            tf,
            type="primary" if st.session_state.tf == tf else "secondary"
        ):
            st.session_state.tf = tf

    symbol = SYMBOLS[st.session_state.asset]
    interval = TIMEFRAMES[st.session_state.tf]

    st.markdown(f"### {st.session_state.asset} ({st.session_state.tf})")

    # 🔥 TradingView chart (fixed reload issue)
    st.components.v1.html(f"""
    <div id="tv_chart_{symbol}"></div>

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
        "container_id": "tv_chart_{symbol}"
    }});
    </script>
    """, height=650)

# ===================== WATCHLIST =====================
with col2:
    st.markdown("## 📊 Watchlist")

    @st.cache_data(ttl=5)
    def get_price(ticker):
        try:
            data = yf.download(ticker, period="1d", interval="1m")
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

            # 🔥 CLICKABLE WATCHLIST
            if st.button(f"{name} ({price:.2f}) {pct:.2f}%"):
                st.session_state.asset = name
                st.rerun()

            st.markdown(f"""
            <span style='color:{color}'>
                {price:.2f} ({pct:.2f}%)
            </span>
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

        for title, link in valid_news[:5]:
            st.markdown(f"[{title}]({link})")
            st.write("---")

    except:
        st.write("News unavailable")
