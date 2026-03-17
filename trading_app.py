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
                    "Last": round(last, 2),
                    "Chg": round(chg, 2),
                    "Chg%": round(chg_pct, 2)
                })

            else:
                rows.append({
                    "Symbol": name,
                    "Last": "-",
                    "Chg": "-",
                    "Chg%": "-"
                })

        except:
            rows.append({
                "Symbol": name,
                "Last": "-",
                "Chg": "-",
                "Chg%": "-"
            })

    # 🔥 Convert to DataFrame
    import pandas as pd
    df = pd.DataFrame(rows)

    # 🔥 Style colors
    def color_change(val):
        try:
            if float(val) > 0:
                return "color: #00ff88"
            elif float(val) < 0:
                return "color: #ff4444"
        except:
            return ""
        return ""

    styled = df.style.applymap(color_change, subset=["Chg", "Chg%"])

    st.dataframe(styled, use_container_width=True, height=500)
