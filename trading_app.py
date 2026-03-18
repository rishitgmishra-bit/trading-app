import streamlit as st
import yfinance as yf
import requests

st.set_page_config(layout="wide")

st.title("📈 TradeView")

# ===================== API KEY =====================
NEWS_API_KEY = "3c7ed1a35fef49bb8d2c70b6553fbcdd"

# ===================== SYMBOLS =====================
SYMBOLS = {
    "Gold (XAU/USD)": "OANDA:XAUUSD",
    "EUR/USD": "OANDA:EURUSD",
    "GBP/USD": "OANDA:GBPUSD",
    "USD/JPY": "OANDA:USDJPY",
    "Apple": "NASDAQ:AAPL",
    "NVIDIA": "NASDAQ:NVDA",
    "Tesla": "NASDAQ:TSLA"
}

WATCHLIST = {
    "Gold (XAU/USD)": "XAUUSD=X",
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "Apple": "AAPL",
    "NVIDIA": "NVDA",
    "Tesla": "TSLA"
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

    bullish = ["rise","gain","bull","surge","rally","strong","growth"]
    bearish = ["fall","drop","bear","decline","weak","sell","loss"]

    if any(w in text for w in bullish):
        return "🟢 Bullish"
    elif any(w in text for w in bearish):
        return "🔴 Bearish"
    else:
        return "⚪ Neutral"

# ===================== NEWS FIX =====================
def get_news(asset):

    query_map = {
        "EUR/USD": "US dollar forex market",
        "GBP/USD": "British pound forex market",
        "USD/JPY": "Japanese yen forex market",
        "Gold (XAU/USD)": "gold price market",

        "Apple": "Apple stock",
        "NVIDIA": "NVIDIA AI stock",
        "Tesla": "Tesla stock"
    }

    query = query_map.get(asset, "global stock market")

    url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize=10&apiKey={"3c7ed1a35fef49bb8d2c70b6553fbcdd"}"

    try:
        res = requests.get(url)
        data = res.json()

        if data.get("status") != "ok":
            return []

        articles = data.get("articles", [])

        # 🔥 FALLBACK (never empty)
        if not articles:
            fallback_url = f"https://newsapi.org/v2/top-headlines?category=business&language=en&apiKey={"3c7ed1a35fef49bb8d2c70b6553fbcdd"}"
            res = requests.get(fallback_url)
            return res.json().get("articles", [])

        return articles

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

    # TradingView Chart
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

# ===================== SIDEBAR =====================
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

            pct = ((price - prev) / prev) * 100

            return price, pct
        except:
            return None

    for name, ticker in WATCHLIST.items():

        res = get_price(ticker)

        if res:
            price, pct = res
            color = "green" if pct >= 0 else "red"

            if st.button(f"{name}   {pct:.2f}%", key=name):
                st.session_state.asset = name
                st.rerun()

            st.markdown(f"<span style='color:{color}'>{price:.2f}</span>", unsafe_allow_html=True)

        else:
            st.write(f"{name} - No data")

    st.markdown("---")

    # ===================== NEWS =====================
    st.markdown("## 📰 Market News + Sentiment")

    articles = get_news(st.session_state.asset)

    if articles:

        for article in articles[:6]:

            title = article.get("title", "")
            url = article.get("url", "")
            desc = article.get("description", "")

            sentiment = ai_sentiment(title + " " + desc)

            st.markdown(f"[{title}]({url})")
            st.write(sentiment)
            st.write("---")

    else:
        st.warning("No news found (API limit or key issue)")
