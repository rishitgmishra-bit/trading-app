import streamlit as st

st.set_page_config(layout="wide")
st.title("📈 TradeView (Custom Engine)")

# ===================== SYMBOLS =====================
SYMBOLS = [
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "XAUUSD",
    "AAPL",
    "NVDA",
    "TSLA"
]

if "asset" not in st.session_state:
    st.session_state.asset = "EURUSD"

# ===================== LAYOUT =====================
col1, col2 = st.columns([5,1])

# ===================== MAIN =====================
with col1:

    selected = st.selectbox("Asset", SYMBOLS)
    st.session_state.asset = selected

    st.markdown(f"### {selected}")

    # 🔥 CUSTOM CHART (JS)
    st.components.v1.html(f"""
    <div id="chart" style="height:600px;"></div>

    <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>

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

    // 🔥 Generate initial candles
    let data = [];
    let base = 100;

    for (let i = 0; i < 100; i++) {{
        let open = base + (Math.random() - 0.5) * 2;
        let close = open + (Math.random() - 0.5) * 2;

        data.push({{
            time: Math.floor(Date.now()/1000) - (100-i)*60,
            open: open,
            high: Math.max(open, close),
            low: Math.min(open, close),
            close: close
        }});

        base = close;
    }}

    candleSeries.setData(data);

    // 🔥 LIVE UPDATES (simulated ticks)
    setInterval(() => {{
        let last = data[data.length - 1];

        let newClose = last.close + (Math.random() - 0.5) * 1;

        let candle = {{
            time: Math.floor(Date.now()/1000),
            open: last.close,
            high: Math.max(last.close, newClose),
            low: Math.min(last.close, newClose),
            close: newClose
        }};

        data.push(candle);
        candleSeries.update(candle);

    }}, 1000);
    </script>
    """, height=620)

# ===================== WATCHLIST =====================
with col2:
    st.markdown("## 📊 Watchlist")

    for sym in SYMBOLS:
        if st.button(sym):
            st.session_state.asset = sym
            st.rerun()

    st.markdown("---")

    # ===================== NEWS =====================
    st.markdown("## 📰 News")

    st.write("• Fed signals rate cuts")
    st.write("• Nifty hits new high")
    st.write("• Tesla beats earnings")
    st.write("• Gold rallies on inflation")
