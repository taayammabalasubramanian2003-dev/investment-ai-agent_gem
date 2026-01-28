

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="AI Investment Analyst", layout="wide")

st.title("🤖 AI Investment Analyst Agent")
st.caption("Beginner-friendly investment assistant")

# ----------------------------
# PHASE 1 – INVESTOR PROFILE
# ----------------------------
st.header("👤 Investor Profile")

name = st.text_input("Your Name")
age = st.number_input("Age", min_value=18, max_value=100)
income = st.number_input("Monthly Income (₹)", step=1000)
savings = st.number_input("Monthly Savings (₹)", step=1000)
risk = st.slider("Risk Appetite (%)", 1, 20, 5)

choice = st.radio(
    "What do you want?",
    ["Analyze a Stock", "Portfolio Allocation"]
)

# ----------------------------
# PHASE 2 – STOCK ANALYSIS
# ----------------------------
if choice == "Analyze a Stock":

    st.header("📊 Stock Analysis")

    symbol = st.text_input("Enter Stock Symbol (e.g., INFY.NS)")
    mode = st.selectbox("Mode", ["INVESTOR", "TRADER"])

    if st.button("Analyze Stock"):

        stock = yf.Ticker(symbol)

        period = "5y" if mode == "INVESTOR" else "6mo"
        df = stock.history(period=period)

        df.reset_index(inplace=True)

        # ----------------------------
        # MOVING AVERAGES
        # ----------------------------
        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()

        trend = "BULLISH" if df["MA20"].iloc[-1] > df["MA50"].iloc[-1] else "BEARISH"

        # ----------------------------
        # RSI
        # ----------------------------
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))

        rsi = round(df["RSI"].iloc[-1], 2)
        rsi_signal = "BULLISH" if rsi >= 50 else "BEARISH"

        # ----------------------------
        # MACD
        # ----------------------------
        ema12 = df["Close"].ewm(span=12).mean()
        ema26 = df["Close"].ewm(span=26).mean()

        df["MACD"] = ema12 - ema26
        df["SIGNAL"] = df["MACD"].ewm(span=9).mean()

        macd_signal = "BULLISH" if df["MACD"].iloc[-1] > df["SIGNAL"].iloc[-1] else "BEARISH"

        # ----------------------------
        # CANDLESTICK CHART
        # ----------------------------
        st.subheader("📈 Price Action")

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

        # ----------------------------
        # INDICATOR OUTPUT
        # ----------------------------
        st.subheader("📉 Technical Indicators")

        col1, col2, col3 = st.columns(3)

        col1.metric("Trend", trend)
        col2.metric("RSI", rsi)
        col3.metric("MACD", macd_signal)

        # ----------------------------
        # FUNDAMENTALS
        # ----------------------------
        st.subheader("🏦 Fundamental Analysis")

        info = stock.info

        st.write("**Sector:**", info.get("sector"))
        st.write("**P/E Ratio:**", info.get("trailingPE"))
        st.write("**EPS:**", info.get("trailingEps"))
        st.write("**Market Cap:**", info.get("marketCap"))

        # ----------------------------
        # LAYMAN EXPLANATION
        # ----------------------------
        st.subheader("🧠 AI Explanation")

        if trend == "BULLISH" and rsi_signal == "BULLISH":
            st.success("Stock shows strength. Suitable for gradual investment.")
        elif trend == "BEARISH":
            st.warning("Trend is weak. Better to wait.")
        else:
            st.info("Signals are mixed. Observe before investing.")

# ----------------------------
# PHASE 2 COMPLETE
# ----------------------------

