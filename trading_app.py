import streamlit as st
import yfinance as yf
import requests
import openai

st.set_page_config(layout="wide")

st.title("📈 TradeView Pro AI")

# ===================== API KEYS =====================
NEWS_API_KEY = "YOUR_NEWS_API_KEY"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"   # optional but recommended

openai.api_key = OPENAI_API_KEY

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

# ===================== SESSION =====================
if "asset" not in st.session_state:
    st.session_state.asset = "EUR/USD"

# ===================== LAYOUT =====================
col1, col2 = st.columns([5,1])

# ===================== AI SENTIMENT =====================
def ai_sentiment(text):

    if not OPENAI_API_KEY:
        # fallback
        text = text.lower()
        if any(w in text for w in ["rise","gain","bull","surge"]):
            return "🟢 Bullish"
        elif any(w in text for w in ["fall","drop","bear","decline"]):
            return "🔴 Bearish"
        else:
            return "⚪ Neutral"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Classify sentiment as Bullish, Bearish or Neutral"},
                {"role": "user", "content": text}
            ]
        )

        result = response.choices[0].message.content.lower()

        if "bull" in result:
            return "🟢 Bullish"
        elif "bear" in result:
            return "🔴 Bearish"
        else:
            return "⚪ Neutral"

    except:
        return "⚪ Neutral"

# ===================== NEWS =====================
def get_news(asset):

    query_map = {
        "EUR/USD": "forex euro dollar forecast",
        "GBP/USD": "forex pound dollar forecast",
        "USD/JPY": "yen forex market",
        "Gold (XAU/USD)": "gold market price",

        "Apple": "Apple stock news",
        "NVIDIA": "NVIDIA AI stock",
        "Tesla": "Tesla stock news"
    }

    query = query_map.get(asset, "stock market")

    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&pageSize=10&apiKey={NEWS_API_KEY}"

    try:
        res = requests.get(url)
        return res.json().get("articles", [])
    except:
        return []

# ===================== MAIN =====================
with col1:

    selected = st.selectbox("Asset", list(SYMBOLS.keys()))
    st.session_state.asset = selected

    st.markdown(f"### {selected}")

    # TradingView widget
    st.components.v1.html(f"""
    <div id="tv_chart"></div>

    <script src="https://s3.tradingview.com/tv.js"></script>

    <script>
    new TradingView.widget({{
        "width": "100%",
        "height": 600,
        "symbol": "{SYMBOLS[selected]}",
        "interval": "5",
        "timezone": "Asia/Kolkata",
        "theme": "dark",
        "style": "1",
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

            if data.empty:
                return None

            price = float(data["Close"].iloc[-1])
            prev = float(data["Close"].iloc[-2])

            pct = ((price - prev)/prev)*100

            return price, pct
        except:
            return None

    for name, ticker in WATCHLIST.items():

        res = get_price(ticker)

        if res:
            price, pct = res

            if st.button(f"{name} ({pct:.2f}%)"):
                st.session_state.asset = name
                st.rerun()

            st.write(f"{price:.2f}")

    st.markdown("---")

    # ===================== NEWS PANEL =====================
    st.markdown("## 📰 AI News + Sentiment")

    articles = get_news(st.session_state.asset)

    if articles:

        for article in articles[:5]:

            title = article.get("title", "")
            url = article.get("url", "")
            desc = article.get("description", "")

            sentiment = ai_sentiment(title + " " + desc)

            st.markdown(f"[{title}]({url})")
            st.write(sentiment)
            st.write("---")

    else:
        st.write("No news found")
