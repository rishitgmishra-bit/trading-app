# ===================== WATCHLIST =====================
with col2:
    st.markdown("## 📊 Watchlist")

    WATCHLIST = {
        "Gold": "XAUUSD=X",
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "USDJPY=X",
        "Apple": "AAPL",
        "NVIDIA": "NVDA",
        "Tesla": "TSLA",
        "Reliance": "RELIANCE.NS",
        "TCS": "TCS.NS"
    }

    @st.cache_data(ttl=5)
    def get_price(ticker):
        data = yf.download(ticker, period="1d", interval="1m")
        data = data.dropna()

        if len(data) < 2:
            return None

        price = data["Close"].iloc[-1]
        prev = data["Close"].iloc[-2]

        change = price - prev
        pct = (change / prev) * 100

        return price, change, pct

    for name, ticker in WATCHLIST.items():
        result = get_price(ticker)

        if result:
            price, change, pct = result
            color = "green" if change >= 0 else "red"

            st.markdown(f"""
            <div style='padding:8px;border-bottom:1px solid #222'>
                <b>{name}</b><br>
                <span style='color:{color}'>
                    {price:.2f} ({pct:.2f}%)
                </span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.write(f"{name} - No data")
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
