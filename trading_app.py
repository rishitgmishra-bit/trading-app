import streamlit as st
import yfinance as yf
import requests

st.set_page_config(layout="wide")

st.title("📈 TradeView Pro (Full Version)")

# ===================== API KEY =====================
NEWS_API_KEY = "YOUR_NEWS_API_KEY"

# ===================== SYMBOLS =====================
SYMBOLS = {
    # Forex
    "EUR/USD": "OANDA:EURUSD",
    "GBP/USD": "OANDA:GBPUSD",
    "USD/JPY": "OANDA:USDJPY",
    "Gold (XAU/USD)": "OANDA:XAUUSD",

    # US Stocks
    "Apple": "NASDAQ:AAPL",
    "NVIDIA": "NASDAQ:NVDA",
    "Tesla": "NASDAQ:TSLA",

    # 🇮🇳 Indian Stocks (RESTORED)
    "Reliance": "NSE:RELIANCE",
    "TCS": "NSE:TCS",
    "Infosys": "NSE:INFY",
    "HDFC Bank": "NSE:HDFCBANK",
    "ICICI Bank": "NSE:ICICIBANK"
}

# ===================== WATCHLIST =====================
WATCHLIST = {
    # Forex
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "Gold (XAU/USD)": "XAUUSD=X",

    # US Stocks
    "Apple": "AAPL",
    "NVIDIA": "NVDA",
    "Tesla": "TSLA",

    # 🇮🇳 Indian Stocks
    "Reliance": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS"
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

# ===================== SENTIMENT =====================
def ai_sentiment(text):
    text = text.lower()

    bullish = ["rise","gain","bull","surge","rally","strong"]
    bearish = ["fall","drop","bear","decline","weak"]

    if any(w in text for w in bullish):
        return "🟢 Bullish"
    elif any(w in text for w in bearish):
        return "🔴 Bearish"
    else:
        return "⚪ Neutral"

# ===================== NEWS =====================
def get_news(asset):

    query_map = {
        "EUR/USD": "US dollar forex market",
        "GBP/USD": "British pound forex",
        "USD/JPY": "Japanese yen forex",
        "Gold (XAU/USD)": "gold market",

        "Apple": "Apple stock",
        "NVIDIA": "NVIDIA AI stock",
        "Tesla": "Tesla stock",

        "Reliance": "Reliance Industries India",
        "TCS": "TCS IT India",
        "Infosys": "Infosys stock",
        "HDFC Bank": "HDFC Bank India",
        "ICICI Bank": "ICICI Bank India"
    }

    query = query_map.get(asset, "stock market")

    url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize=20&apiKey={NEWS_API_KEY}"

    try:
        res = requests.get(url)
        data = res.json()

        articles = data.get("articles", [])

        # 🔥 REMOVE DUPLICATES
        seen = set()
        unique = []

        for a in articles:
            title = a.get("title", "")
            if title and title not in seen:
                seen.add(title)
                unique.append(a)

        # fallback
        if len(unique) < 3:
            fallback = requests.get(
                f"https://newsapi.org/v2/top-headlines?category=business&language=en&apiKey={NEWS_API_KEY}"
            )
            return fallback.json().get("articles", [])

        return unique

    except:
        return []

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

    tf_cols = st.columns(len(TIMEFRAMES))

    for i, tf in enumerate(TIMEFRAMES):
        if tf_cols[i].button(
            tf,
            type="primary" if tf == st.session_state.tf else "secondary"
        ):
            st.session_state.tf = tf

    st.markdown(f"### {selected} ({st.session_state.tf})")

    # TradingView chart
    st.components.v1.html(f"""
    <div id="tv_chart"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({{
        "width": "100%",
        "height": 600,
        "symbol": "{SYMBOLS[selected]}",
        "interval": "{TIMEFRAMES[st.session_state.tf]}",
        "theme": "dark",
        "style": "1",
        "timezone": "Asia/Kolkata",
        "container_id": "tv_chart"
    }});
    </script>
    """, height=650)

# ===================== SIDEBAR =====================
with col2:

    st.markdown("## 📊 Watchlist")

    @st.cache_data(ttl=5)
    def get_price(ticker):
        try:
            d = yf.download(ticker, period="1d", interval="1m", progress=False)

            if d.empty or len(d) < 2:
                return None

            price = float(d["Close"].iloc[-1])
            prev = float(d["Close"].iloc[-2])

            pct = ((price - prev) / prev) * 100

            return price, pct
        except:
            return None

    for name, ticker in WATCHLIST.items():

        res = get_price(ticker)

        if res:
            price, pct = res
            color = "green" if pct >= 0 else "red"

            if st.button(f"{name} ({pct:.2f}%)"):
                st.session_state.asset = name
                st.rerun()

            st.markdown(f"<span style='color:{color}'>{price:.2f}</span>", unsafe_allow_html=True)

        else:
            st.write(f"{name} - No data")

    st.markdown("---")

    # ===================== NEWS =====================
    st.markdown("## 📰 Market News")

    articles = get_news(st.session_state.asset)

    for a in articles[:6]:
        title = a.get("title", "")
        url = a.get("url", "")

        sentiment = ai_sentiment(title)

        st.markdown(f"[{title}]({url})")
        st.write(sentiment)
        st.write("---")
