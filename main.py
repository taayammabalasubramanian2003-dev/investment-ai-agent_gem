import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="AI Investment Analyst", layout="wide")

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
# INVESTOR PROFILE
# =========================
st.header("👤 Investor Profile")

with st.form("profile_form"):
    name = st.text_input("Your Name")
    age = st.number_input("Age", 18, 100)
    income = st.number_input("Monthly Income (₹)", 0)
    savings = st.number_input("Monthly Savings (₹)", 0)
    risk = st.slider("Risk Appetite (%)", 1, 20)
    submitted = st.form_submit_button("Save Profile")

if submitted:
    st.session_state.update({
        "name": name,
        "age": age,
        "income": income,
        "savings": savings,
        "risk": risk,
        "profile_created": True
    })
    st.success("✅ Profile saved successfully")

if not st.session_state.profile_created:
    st.stop()

st.divider()

# =========================
# USER INTENT
# =========================
choice = st.radio("What do you want to do?", ["Analyze a Stock", "Portfolio Allocation"])

# ============================================================
# ======================= PHASE 2 =============================
# ============================================================
if choice == "Analyze a Stock":
    st.header("📊 Phase 2: Stock Analysis")

    symbol = st.text_input("Enter Stock Symbol (e.g., INFY.NS)")
    mode = st.selectbox("Mode", ["INVESTOR", "TRADER"])

    if st.button("Analyze Stock") and symbol:
        period = "5y" if mode == "INVESTOR" else "6mo"
        interval = "1mo" if mode == "INVESTOR" else "1d"

        stock = yf.Ticker(symbol)
        df = stock.history(period=period, interval=interval)

        if df.empty:
            st.error("No data found")
            st.stop()

        df.reset_index(inplace=True)

        # -------- Moving Averages --------
        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()

        st.subheader("🕯️ Price Action")
        fig = go.Figure()
        fig.add_candlestick(
            x=df["Date"], open=df["Open"],
            high=df["High"], low=df["Low"],
            close=df["Close"]
        )
        fig.add_trace(go.Scatter(x=df["Date"], y=df["MA20"], name="MA20"))
        fig.add_trace(go.Scatter(x=df["Date"], y=df["MA50"], name="MA50"))
        st.plotly_chart(fig, use_container_width=True)

        trend = "BULLISH" if df["MA20"].iloc[-1] > df["MA50"].iloc[-1] else "BEARISH"
        st.success(f"Trend: {trend}")

        # -------- RSI --------
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        rs = gain.rolling(14).mean() / loss.rolling(14).mean()
        df["RSI"] = 100 - (100 / (1 + rs))
        rsi_val = df["RSI"].iloc[-1]

        st.subheader("📉 RSI")
        st.line_chart(df.set_index("Date")["RSI"])

        # -------- MACD --------
        ema12 = df["Close"].ewm(span=12).mean()
        ema26 = df["Close"].ewm(span=26).mean()
        df["MACD"] = ema12 - ema26
        df["Signal"] = df["MACD"].ewm(span=9).mean()
        macd_signal = "BULLISH" if df["MACD"].iloc[-1] > df["Signal"].iloc[-1] else "BEARISH"

        st.subheader("📊 MACD")
        st.line_chart(df.set_index("Date")[["MACD", "Signal"]])

        # 🔑 SAVE FOR PHASE 4
        st.session_state.trend = trend
        st.session_state.rsi_value = rsi_val
        st.session_state.macd_signal = macd_signal

        # -------- Fundamentals --------
        st.header("🏦 Fundamental Analysis")
        try:
            info = stock.get_info()
            st.write("Sector:", info.get("sector"))
            st.write("P/E:", info.get("trailingPE"))
            st.write("EPS:", info.get("trailingEps"))
            st.write("Market Cap:", info.get("marketCap"))
            st.caption("Data source: Yahoo Finance (free API)")
        except:
            st.warning("Fundamental data unavailable (free API limit)")

# ============================================================
# ======================= PHASE 3 =============================
# ============================================================
else:
    st.header("💼 Phase 3: Portfolio Allocation")

    capital = st.number_input("Total Investment Amount (₹)", 1000, step=500)
    horizon = st.selectbox("Investment Horizon", [
        "Short-term (1–3 years)",
        "Medium-term (3–5 years)",
        "Long-term (5+ years)"
    ])

    assets = st.multiselect("Choose Asset Types",
        ["Equity", "Debt", "Gold ETF"],
        default=["Equity", "Debt", "Gold ETF"]
    )

    if st.button("Generate Portfolio"):
        risk = st.session_state.risk

        if risk <= 5:
            allocation = {"Equity": 40, "Debt": 40, "Gold ETF": 20}
        elif risk <= 10:
            allocation = {"Equity": 60, "Debt": 25, "Gold ETF": 15}
        else:
            allocation = {"Equity": 75, "Debt": 15, "Gold ETF": 10}

        st.subheader("Allocation")
        for a, p in allocation.items():
            if a in assets:
                st.write(f"{a}: ₹{capital*p/100:.0f}")

# ============================================================
# ======================= PHASE 4 =============================
# ============================================================
st.divider()
st.header("🧠 Phase 4: AI Decision Agent")

if not all(k in st.session_state for k in ["trend", "rsi_value", "macd_signal"]):
    st.warning("Please analyze a stock in Phase 2 to activate AI Decision Agent.")
else:
    score = 0
    if st.session_state.trend == "BULLISH": score += 1
    if st.session_state.rsi_value > 50: score += 1
    if st.session_state.macd_signal == "BULLISH": score += 1

    decision = "BUY" if score >= 2 else "HOLD" if score == 1 else "WAIT"
    st.success(f"AI Recommendation: **{decision}**")

# =========================
# EDUCATOR
# =========================
st.header("🎓 Financial Educator")
with st.expander("What do indicators mean?"):
    st.write("RSI: momentum strength")
    st.write("MACD: trend confirmation")
    st.write("Moving Average: direction")
    st.write("Diversification: risk control")

# =========================
# FORECAST
# =========================
st.header("🔮 Financial Planning Forecast")
monthly = st.number_input("Monthly Investment (₹)", 1000, 50000, 10000)
years = st.slider("Years", 1, 30, 5)
rate = 12 / 100 / 12
months = years * 12
fv = monthly * ((1 + rate)**months - 1) / rate
st.success(f"Expected Value after {years} years: ₹{round(fv,2)}")

st.caption("Assumes 12% annual return")

