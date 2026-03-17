import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import math

st.set_page_config(layout="wide")

st.title("📈 TradeView PRO")

# ================= SYMBOLS =================
SYMBOLS = {
    "Gold (XAU/USD)": "OANDA:XAUUSD",
    "EUR/USD": "OANDA:EURUSD",
    "GBP/USD": "OANDA:GBPUSD",
    "USD/JPY": "OANDA:USDJPY",

    "Apple": "AAPL",
    "NVIDIA": "NVDA",
    "Tesla": "TSLA",

    "Reliance": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "Coforge": "COFORGE.NS",
    "Nifty 50": "^NSEI"
}

INDIAN = ["Reliance","TCS","Infosys","HDFC Bank","ICICI Bank","Coforge","Nifty 50"]

TIMEFRAMES = {
    "1m": ("1d","1m"),
    "5m": ("5d","5m"),
    "15m": ("1mo","15m"),
    "1H": ("3mo","1h"),
    "1D": ("1y","1d")
}

TV_INTERVAL = {
    "1m":"1","5m":"5","15m":"15","1H":"60","1D":"D"
}

# ================= SESSION =================
if "asset" not in st.session_state:
    st.session_state.asset = "EUR/USD"

if "tf" not in st.session_state:
    st.session_state.tf = "5m"

# ================= LAYOUT =================
col1, col2, col3 = st.columns([4,1,1])

# ================= MAIN CHART =================
with col1:

    selected = st.selectbox(
        "Asset",
        list(SYMBOLS.keys()),
        index=list(SYMBOLS.keys()).index(st.session_state.asset)
    )
    st.session_state.asset = selected

    # TIMEFRAME BUTTONS
    tf_cols = st.columns(len(TIMEFRAMES))
    for i, tf in enumerate(TIMEFRAMES):
        if tf_cols[i].button(tf, type="primary" if tf==st.session_state.tf else "secondary"):
            st.session_state.tf = tf

    st.markdown(f"### {selected} ({st.session_state.tf})")

    # ================= HYBRID =================
    if selected not in INDIAN:
        symbol = SYMBOLS[selected]
        interval = TV_INTERVAL[st.session_state.tf]

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
        ticker = SYMBOLS[selected]
        period, interval = TIMEFRAMES[st.session_state.tf]

        # FIX 1m issue
        if interval == "1m":
            interval = "5m"
            period = "5d"
            st.warning("1m not supported → switched to 5m")

        data = yf.download(ticker, period=period, interval=interval)

        # FALLBACK
        if data.empty or data["Close"].isna().all():
            st.warning("Intraday unavailable → showing Daily")
            data = yf.download(ticker, period="6mo", interval="1d")

        if not data.empty:
            data = data.dropna().tail(200)

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

            price = data["Close"].iloc[-1]
            if isinstance(price,(int,float)) and not math.isnan(price):
                fig.add_hline(y=float(price), line_dash="dot", line_color="red")

            fig.update_layout(
                template="plotly_dark",
                height=600,
                xaxis_rangeslider_visible=False
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("No data available")

# ================= WATCHLIST =================
with col2:
    st.markdown("## 📊 Watchlist")

    rows = []

    for name, ticker in SYMBOLS.items():
        try:
            data = yf.download(ticker, period="1d", interval="1m")

            if not data.empty and len(data) > 2:
                last = data["Close"].iloc[-1]
                prev = data["Close"].iloc[-2]

                chg = last - prev
                chg_pct = (chg / prev) * 100

                rows.append({
                    "Symbol": name,
                    "Last": round(last,2),
                    "Chg": round(chg,2),
                    "Chg%": round(chg_pct,2)
                })
            else:
                rows.append({"Symbol": name, "Last": "-", "Chg": "-", "Chg%": "-"})

        except:
            rows.append({"Symbol": name, "Last": "-", "Chg": "-", "Chg%": "-"})

    df = pd.DataFrame(rows)

    def color(val):
        try:
            if float(val) > 0:
                return "color:#00ff88"
            elif float(val) < 0:
                return "color:#ff4444"
        except:
            return ""
        return ""

    st.dataframe(df.style.applymap(color, subset=["Chg","Chg%"]), height=600)

# ================= NEWS =================
with col3:
    st.markdown("## 📰 Market News")

    try:
        news = yf.Ticker("AAPL").news

        if news:
            for item in news[:8]:
                st.markdown(f"**{item.get('title','No title')}**")
                st.caption(item.get("publisher",""))
                st.write("---")
        else:
            st.write("No news available")

    except:
        st.write("News unavailable")
