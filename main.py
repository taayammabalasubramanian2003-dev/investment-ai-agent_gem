import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="AI Investment Analyst", layout="wide")

# ==================================================
# HEADER
# ==================================================
st.title("🤖 AI Investment Analyst Agent")
st.subheader("Beginner-friendly Investment Assistant")

# ==================================================
# INVESTOR PROFILE (ONCE)
# ==================================================
st.header("👤 Investor Profile")

if "profile_created" not in st.session_state:
    st.session_state.profile_created = False

if not st.session_state.profile_created:
    name = st.text_input("Your Name")
    age = st.number_input("Age", min_value=18, max_value=100)
    income = st.number_input("Monthly Income (₹)", min_value=0)
    savings = st.number_input("Monthly Savings (₹)", min_value=0)
    risk = st.slider("Risk Appetite (%)", 1, 20)

    if st.button("Create Profile"):
        st.session_state.name = name
        st.session_state.age = age
        st.session_state.income = income
        st.session_state.savings = savings
        st.session_state.risk = risk
        st.session_state.profile_created = True
        st.success("✅ Profile Created Successfully")
        st.experimental_rerun()
else:
    st.success(
        f"""
        **Name:** {st.session_state.name}  
        **Age:** {st.session_state.age}  
        **Monthly Savings:** ₹{st.session_state.savings}  
        **Risk Appetite:** {st.session_state.risk}%
        """
    )

st.divider()

# ==================================================
# USER CHOICE
# ==================================================
choice = st.radio(
    "What do you want to do?",
    ["Analyze a Stock", "Portfolio Allocation"]
)

# ==================================================
# PHASE 2 – STOCK ANALYSIS
# ==================================================
if choice == "Analyze a Stock":

    st.header("📊 Stock Analysis")

    symbol = st.text_input("Enter Stock Symbol (e.g., INFY.NS, TCS.NS)")
    mode = st.selectbox("Mode", ["INVESTOR", "TRADER"])

    if st.button("Analyze Stock") and symbol:
        period = "5y" if mode == "INVESTOR" else "6mo"
        interval = "1mo" if mode == "INVESTOR" else "1d"

        stock = yf.Ticker(symbol)
        df = stock.history(period=period, interval=interval)
        df.reset_index(inplace=True)

        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()

        # Candlestick Chart
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
        st.plotly_chart(fig, use_container_width=True)

        trend = "BULLISH" if df["MA20"].iloc[-1] > df["MA50"].iloc[-1] else "BEARISH"
        st.success(f"📈 Trend: {trend}")

        # RSI
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        rs = gain.rolling(14).mean() / loss.rolling(14).mean()
        df["RSI"] = 100 - (100 / (1 + rs))

        rsi_val = round(df["RSI"].iloc[-1], 2)
        st.subheader("📉 RSI Indicator")
        st.line_chart(df.set_index("Date")["RSI"])
        st.write(f"RSI: **{rsi_val}** → {'BULLISH' if rsi_val > 50 else 'BEARISH'}")

        # MACD
        ema12 = df["Close"].ewm(span=12).mean()
        ema26 = df["Close"].ewm(span=26).mean()
        df["MACD"] = ema12 - ema26
        df["Signal"] = df["MACD"].ewm(span=9).mean()

        macd_signal = "BULLISH" if df["MACD"].iloc[-1] > df["Signal"].iloc[-1] else "BEARISH"
        st.subheader("📊 MACD")
        st.line_chart(df.set_index("Date")[["MACD", "Signal"]])
        st.write(f"MACD Signal: **{macd_signal}**")

        # Fundamental Analysis (Safe)
        st.header("🏦 Fundamental Analysis")
        try:
            info = stock.get_info()
            st.write("Sector:", info.get("sector"))
            st.write("P/E:", info.get("trailingPE"))
            st.write("EPS:", info.get("trailingEps"))
            st.write("Market Cap:", info.get("marketCap"))
        except:
            st.warning("⚠️ Fundamental data temporarily unavailable (Free API limit).")

# ==================================================
# PHASE 3 – PORTFOLIO ALLOCATION
# ==================================================
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

    if st.button("Generate Portfolio"):
        risk = st.session_state.risk

        if risk <= 5:
            allocation = {"Equity": 40, "Debt": 40, "Gold ETF": 20}
        elif risk <= 10:
            allocation = {"Equity": 60, "Debt": 25, "Gold ETF": 15}
        else:
            allocation = {"Equity": 75, "Debt": 15, "Gold ETF": 10}

        st.subheader("📊 Allocation Breakdown")
        for a, p in allocation.items():
            if a in assets:
                st.write(f"**{a} → ₹{round(capital*p/100,2)} ({p}%)**")

        st.subheader("🏢 Suggested Investments")

        if "Equity" in assets:
            st.write("📈 Equity: HDFC Bank, TCS, Infosys")
        if "Debt" in assets:
            st.write("🏦 Debt: ICICI Pru Corporate Bond, HDFC Bond Fund")
        if "Gold ETF" in assets:
            st.write("🪙 Gold ETF: GOLDBEES.NS")

        st.info(
            f"""
            **Why this portfolio?**
            - Risk Appetite: {risk}%
            - Horizon: {horizon}
            - Balanced growth + safety
            """
        )

st.divider()
st.caption("✅ Phase 2 & Phase 3 Complete — Single Profile, Multi-Agent Flow")
