import streamlit as st
import yfinance as yf

st.set_page_config(layout="wide")

st.title("📈 TradeView Pro (Custom Chart)")

# ===================== SYMBOLS =====================
SYMBOLS = {
    "Gold (XAU/USD)": "XAUUSD",
    "EUR/USD": "EURUSD",
    "GBP/USD": "GBPUSD",
    "USD/JPY": "USDJPY",
    "Apple": "AAPL",
    "NVIDIA": "NVDA",
    "Tesla": "TSLA",
    "Reliance": "RELIANCE",
    "TCS": "TCS"
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

TIMEFRAMES = ["1m", "5m", "15m", "1H", "1D"]

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
    for i, tf in enumerate(TIMEFRAMES):
        if tf_cols[i].button(
            tf,
            type="primary" if st.session_state.tf == tf else "secondary",
            key=f"tf_{tf}"
        ):
            st.session_state.tf = tf

    st.markdown(f"### {selected} ({st.session_state.tf})")

    # ===================== CUSTOM CANDLE CHART =====================
    st.components.v1.html(f"""
    <div id="chart" style="height:600px;"></div>

    <script src="https://unpkg.com/lightweight-charts@4.1.3/dist/lightweight-charts.standalone.production.js"></script>

    <script>
    const chart = LightweightCharts.createChart(document.getElementById('chart'), {{
        layout: {{ background: {{ color: '#0a0a0a' }}, textColor: '#d1d4dc' }},
        grid: {{
            vertLines: {{ color: '#1e1e1e' }},
            horzLines: {{ color: '#1e1e1e' }},
        }},
    }});

    const candleSeries = chart.addCandlestickSeries({{
        upColor: '#00ff88',
        downColor: '#ff4444',
        borderVisible: false,
        wickUpColor: '#00ff88',
        wickDownColor: '#ff4444'
    }});

    let data = [];
    let base = 100;

    for (let i = 0; i < 100; i++) {{
        let time = Math.floor(Date.now()/1000) - (100 - i) * 60;

        let open = base;
        let close = base + (Math.random() - 0.5) * 2;
        let high = Math.max(open, close) + Math.random();
        let low = Math.min(open, close) - Math.random();

        data.push({{
            time: time,
            open: Number(open.toFixed(2)),
            high: Number(high.toFixed(2)),
            low: Number(low.toFixed(2)),
            close: Number(close.toFixed(2))
        }});

        base = close;
    }}

    candleSeries.setData(data);

    setInterval(() => {{
        let last = data[data.length - 1];

        let open = last.close;
        let close = open + (Math.random() - 0.5) * 1;
        let high = Math.max(open, close);
        let low = Math.min(open, close);

        let newCandle = {{
            time: Math.floor(Date.now()/1000),
            open: Number(open.toFixed(2)),
            high: Number(high.toFixed(2)),
            low: Number(low.toFixed(2)),
            close: Number(close.toFixed(2))
        }};

        candleSeries.update(newCandle);
        data.push(newCandle);

    }}, 1000);
    </script>
    """, height=620)

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

            if st.button(f"{name}   {price:.2f} ({pct:.2f}%)", key=name):
                st.session_state.asset = name
                st.rerun()

            st.markdown(f"""
            <div style='margin-bottom:12px'>
                <span style='color:{color}'>
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

        for title, link in valid_news[:5]:
            st.markdown(f"[{title}]({link})")
            st.write("---")

    except:
        st.write("News unavailable")
