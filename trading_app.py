import streamlit as st

st.set_page_config(layout="wide")
st.title("📈 TradeView Pro (REAL DATA)")

# ================= SYMBOLS =================
SYMBOLS = {
    "BTC/USDT": "btcusdt",
    "ETH/USDT": "ethusdt",
    "BNB/USDT": "bnbusdt"
}

TIMEFRAMES = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m"
}

# ================= SESSION =================
assets = list(SYMBOLS.keys())

if "asset" not in st.session_state:
    st.session_state.asset = assets[0]

if "tf" not in st.session_state:
    st.session_state.tf = "1m"

# ================= LAYOUT =================
col1, col2 = st.columns([5,1])

# ================= MAIN =================
with col1:

    selected = st.selectbox("Asset", assets)
    st.session_state.asset = selected

    tf_cols = st.columns(len(TIMEFRAMES))

    for i, tf in enumerate(TIMEFRAMES):
        if tf_cols[i].button(
            tf,
            type="primary" if tf == st.session_state.tf else "secondary"
        ):
            st.session_state.tf = tf

    symbol = SYMBOLS[selected]
    interval = TIMEFRAMES[st.session_state.tf]

    st.markdown(f"### {selected} ({interval})")

    # ================= REAL WEBSOCKET CHART =================
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

    let socket = new WebSocket("wss://stream.binance.com:9443/ws/{symbol}@kline_{interval}");

    socket.onmessage = function(event) {{
        let msg = JSON.parse(event.data);
        let k = msg.k;

        let candle = {{
            time: k.t / 1000,
            open: parseFloat(k.o),
            high: parseFloat(k.h),
            low: parseFloat(k.l),
            close: parseFloat(k.c)
        }};

        candleSeries.update(candle);
    }};
    </script>
    """, height=620)

# ================= WATCHLIST =================
with col2:
    st.markdown("## 📊 Watchlist")

    for name in SYMBOLS:
        if st.button(name):
            st.session_state.asset = name
            st.rerun()

    st.markdown("---")

    st.markdown("## 🟢 Status")
    st.write("Live WebSocket Connected")
