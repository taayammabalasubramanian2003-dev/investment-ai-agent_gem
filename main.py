import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="AI Investment Analyst",
    layout="wide"
)

# =========================
# HEADER
# =========================
st.title("🤖 AI Investment Analyst Agent")
st.caption("Beginner-friendly, transparent investment assistant")

# =========================
# SESSION STATE INIT
# =========================
if "profile_created" not in st.session_state:
    st.session_state.profile_created = False

# =========================
# INVESTOR PROFILE (ONCE)
# =========================
st.header("👤 Investor Profile")

with st.form("profile_form"):
    name = st.text_input("Your Name")
    age = st.number_input("Age", min_value=18, max_value=100)
    income = st.number_input("Monthly Income (₹)", min_value=0)
    savings = st.number_input("Monthly Savings (₹)", min_value=0)
    risk = st.slider("Risk Appetite (%)", 1, 20)

    submitted = st.form_submit_button("Save Profile")

if submitted:
    st.session_state.name = name
    st.session_state.age = age
    st.session_state.income = income
    st.session_state.savings = savings
    st.session_state.risk = risk
    st.session_state.profile_created = True
    st.success("✅ Profile saved successfully")

# Stop execution until profile is created
if not st.session_state.profile_created:
    st.stop()

st.divider()

# =========================
# USER INTENT
# =========================
choice = st.radio(
    "What do you want to do?",
    ["Analyze a Stock", "Portfolio Allocation"]
)

# ============================================================
# ======================= PHASE 2 =============================
# ============================================================
if choice == "Analyze a Stock":
    st.header("📊 Stock Analysis")

    symbol = st.text_input("Enter Stock Symbol (e.g., INFY.NS)")
    mode = st.selectbox("Mode", ["INVESTOR", "TRADER"])

    if st.button("Analyze Stock") and symbol:
        period = "5y" if mode == "INVESTOR" else "6mo"
        interval = "1mo" if mode == "INVESTOR" else "1d"

        stock = yf.Ticker(symbol)
        df = stock.history(period=period, interval=interval)

        if df.empty:
            st.error("No data found. Check symbol.")
            st.stop()

        df.reset_index(inplace=True)

        # -------------------------
        # MOVING AVERAGES
        # -------------------------
        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()

        # -------------------------
        # CANDLESTICK
        # -------------------------
        st.subheader("🕯️ Price Action")

        fig = go.Figure()
        fig.add_candlestick(
            x=df["Date"],
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"]
        )
        fig.add_trace(go.Scatter(x=df["Date"], y=df["MA20"], name="MA20"))
        fig.add_trace(go.Scatter(x=df["Date"], y=df["MA50"], name="MA50"))
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        trend = "BULLISH" if df["MA20"].iloc[-1] > df["MA50"].iloc[-1] else "BEARISH"
        st.success(f"📈 Trend: {trend}")
        st.caption("Trend based on Moving Average crossover")

        # -------------------------
        # RSI
        # -------------------------
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        rs = gain.rolling(14).mean() / loss.rolling(14).mean()
        df["RSI"] = 100 - (100 / (1 + rs))

        rsi_val = df["RSI"].iloc[-1]
        rsi_signal = "BULLISH" if rsi_val > 50 else "BEARISH"

        st.subheader("📉 RSI Indicator")
        st.line_chart(df.set_index("Date")["RSI"])
        st.write(f"RSI: **{round(rsi_val,2)} → {rsi_signal}**")
        st.caption("RSI measures momentum strength")

        # -------------------------
        # MACD
        # -------------------------
        ema12 = df["Close"].ewm(span=12, adjust=False).mean()
        ema26 = df["Close"].ewm(span=26, adjust=False).mean()
        df["MACD"] = ema12 - ema26
        df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

        macd_signal = "BULLISH" if df["MACD"].iloc[-1] > df["Signal"].iloc[-1] else "BEARISH"

        st.subheader("📊 MACD Indicator")
        st.line_chart(df.set_index("Date")[["MACD", "Signal"]])
        st.write(f"MACD Signal: **{macd_signal}**")
        st.caption("MACD confirms trend direction")

       
        # 🔑 SAVE FOR PHASE 4 (FIXED)
        st.session_state.trend = trend
        st.session_state.rsi_value = rsi_val
        st.session_state.macd_signal = macd_signal
        st.session_state.stock_analyzed = True



        # -------------------------
        # FUNDAMENTAL ANALYSIS
        # -------------------------
        st.header("🏦 Fundamental Analysis")

        try:
            info = stock.get_info()
            st.write("**Sector:**", info.get("sector", "N/A"))
            st.write("**P/E Ratio:**", info.get("trailingPE", "N/A"))
            st.write("**EPS:**", info.get("trailingEps", "N/A"))
            st.write("**Market Cap:**", info.get("marketCap", "N/A"))

            st.info(
                "📌 Fundamental data is fetched from **Yahoo Finance free API**. "
                "It includes valuation, profitability, and size metrics."
            )
        except:
            st.warning(
                "⚠️ Fundamental data temporarily unavailable due to free API limits.\n"
                "Technical analysis remains unaffected."
            )

# ============================================================
# ======================= PHASE 3 =============================
# ============================================================
else:
    st.header("💼 Personalized Portfolio Allocation")

    capital = st.number_input("Total Investment Amount (₹)", min_value=1000, step=500)
    horizon = st.selectbox(
        "Investment Horizon",
        ["Short-term (1–3 years)", "Medium-term (3–5 years)", "Long-term (5+ years)"]
    )

    assets = st.multiselect(
        "Choose Asset Types",
        ["Equity", "Debt", "Gold ETF"],
        default=["Equity", "Debt", "Gold ETF"]
    )

    if st.button("Generate Portfolio") and capital > 0:
        risk = st.session_state.risk

        if risk <= 5:
            allocation = {"Equity": 40, "Debt": 40, "Gold ETF": 20}
        elif risk <= 10:
            allocation = {"Equity": 60, "Debt": 25, "Gold ETF": 15}
        else:
            allocation = {"Equity": 75, "Debt": 15, "Gold ETF": 10}

        st.subheader("📊 Allocation Breakdown")

        for asset, pct in allocation.items():
            if asset in assets:
                amt = capital * pct / 100
                st.write(f"**{asset} → ₹{amt:.0f} ({pct}%)**")

        st.subheader("🏢 Suggested Investments")

        # =========================
        # EQUITY
        # =========================
        if "Equity" in assets:
            st.markdown("### 📈 Equity – Growth Engine")
        
            st.write(
                "✔ **Why Equity?** Equity helps your money grow faster over the long term by investing in businesses."
            )
        
            st.write(
                "• **HDFC Bank** – India’s largest private bank with stable profits and strong risk management."
            )
            st.write(
                "• **TCS** – Market leader in IT services with consistent revenue and global clients."
            )
            st.write(
                "• **Infosys** – Strong digital transformation focus and steady long-term growth."
            )
        
        # =========================
        # DEBT
        # =========================
        if "Debt" in assets:
            st.markdown("### 🏦 Debt – Capital Protection")
        
            st.write(
                "✔ **Why Debt?** Debt funds protect your capital and reduce overall portfolio risk."
            )
        
            st.write(
                "• **ICICI Pru Corporate Bond Fund** – Invests in high-quality corporate bonds for stable returns."
            )
            st.write(
                "• **HDFC Corporate Bond Fund** – Lower volatility with predictable income."
            )
        
        # =========================
        # GOLD ETF
        # =========================
        if "Gold ETF" in assets:
            st.markdown("### 🪙 Gold ETF – Risk Hedge")
        
            st.write(
                "✔ **Why Gold?** Gold protects against inflation, market crashes, and global uncertainty."
            )
        
            st.write(
                "• **GOLDBEES.NS** – Safest and most liquid gold ETF in India, tracks gold prices directly."
            )

        st.subheader("🧠 Why this portfolio?")
        st.info(
            f"""
            • Risk appetite: **{risk}%**  
            • Equity for growth  
            • Debt for stability  
            • Gold for inflation hedge  
            • Optimized for **{horizon}**
            """
        )

# =========================
# FOOTER
# =========================
st.divider()
st.caption("✅ Phase 2 & Phase 3 complete – Transparent AI Investment Agent")



# =========================
# PHASE 4: AI DECISION ENGINE
# =========================

st.header("🧠 Phase 4: AI Decision Agent")

# Safety check
if (
    "trend" not in st.session_state or
    "rsi_value" not in st.session_state or
    "macd_signal" not in st.session_state
):
    st.warning(
        "⚠️ Please analyze a stock in Phase 2 to activate AI Decision Agent."
    )

else:
    trend = st.session_state.trend
    rsi_value = st.session_state.rsi_value
    macd_signal = st.session_state.macd_signal

    score = 0

    if trend == "BULLISH":
        score += 1
    if rsi_value > 50:
        score += 1
    if macd_signal == "BULLISH":
        score += 1

    if score >= 2:
        decision = "BUY"
    elif score == 1:
        decision = "HOLD"
    else:
        decision = "WAIT"

    st.success(f"📌 AI Recommendation: **{decision}**")

    st.caption(
        "Decision is based on Trend + Momentum (RSI) + Strength (MACD)"
    )





# =========================
# FINANCIAL EDUCATOR AGENT
# =========================

st.header("🎓 Financial Educator")

with st.expander("📘 What do these indicators mean?"):
    st.write("**RSI (Relative Strength Index)**: Shows buying or selling pressure.")
    st.write("**MACD**: Shows momentum and trend strength.")
    st.write("**Moving Averages**: Show overall price direction.")
    st.write("**Diversification**: Reduces risk by spreading investments.")


# =========================
# PORTFOLIO PERFORMANCE MONITOR
# =========================

st.header("📈 Portfolio Performance Monitor")

monthly_return = np.random.uniform(-3, 6)

st.write(f"Simulated Monthly Return: **{round(monthly_return,2)}%**")

if monthly_return > 0:
    st.success("Portfolio performed well this month.")
else:
    st.warning("Market was weak. Long-term discipline is key.")


# =========================
# FINANCIAL PLANNING FORECAST
# =========================

st.header("🔮 Financial Planning Forecast")

monthly = st.number_input(
    "Monthly Investment (₹)",
    min_value=1000,
    max_value=50000,
    value=10000
)

years = st.slider(
    "Investment Duration (Years)",
    min_value=1,
    max_value=30,
    value=5
)

rate = 12 / 100 / 12
months = years * 12

future_value = monthly * ((1 + rate)**months - 1) / rate

st.success(
    f"Expected Value after {years} years: ₹{round(future_value,2)}"
)

st.caption(
    "Assumes 12% annual return with monthly compounding."
)


st.divider()
st.caption("✅ Phase 4 Complete – AI Decision, Education & Financial Planning")
