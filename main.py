import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="AI Investment Analyst", layout="wide")

# =========================
# HEADER
# =========================
st.title("🤖 AI Investment Analyst Agent")
st.subheader("Beginner-friendly Investment Assistant")

# =========================
# INVESTOR PROFILE
# =========================
st.header("👤 Investor Profile")

name = st.text_input("Your Name")
age = st.number_input("Age", min_value=18, max_value=100)
income = st.number_input("Monthly Income (₹)", min_value=0)
savings = st.number_input("Monthly Savings (₹)", min_value=0)
risk = st.slider("Risk Appetite (%)", 1, 20)

st.divider()

# =========================
# USER INTENT
# =========================
choice = st.radio(
    "What do you want to do?",
    ["Analyze a Stock", "Portfolio Allocation"]
)

# =========================
# ANALYZE A STOCK
# =========================
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

        # =========================
        # MOVING AVERAGES
        # =========================
        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()

        # =========================
        # CANDLESTICK CHART
        # =========================
        st.subheader("🕯️ Price Action (Candlestick Chart)")

        fig = go.Figure()
        fig.add_candlestick(
            x=df["Date"],
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Price"
        )
        fig.add_trace(go.Scatter(x=df["Date"], y=df["MA20"], name="MA20"))
        fig.add_trace(go.Scatter(x=df["Date"], y=df["MA50"], name="MA50"))
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        trend = "BULLISH" if df["MA20"].iloc[-1] > df["MA50"].iloc[-1] else "BEARISH"
        st.success(f"📈 Trend: {trend}")
        st.caption("MA20 above MA50 = bullish trend")

        # =========================
        # RSI
        # =========================
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))

        rsi_value = df["RSI"].iloc[-1]
        rsi_signal = "BULLISH" if rsi_value > 50 else "BEARISH"

        st.subheader("📉 RSI Indicator")
        st.line_chart(df.set_index("Date")["RSI"])
        st.write(f"RSI Value: **{round(rsi_value,2)}** → {rsi_signal}")
        st.caption("RSI > 50 = strength | RSI < 50 = weakness")

        # =========================
        # MACD
        # =========================
        ema12 = df["Close"].ewm(span=12, adjust=False).mean()
        ema26 = df["Close"].ewm(span=26, adjust=False).mean()
        df["MACD"] = ema12 - ema26
        df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

        macd_signal = "BULLISH" if df["MACD"].iloc[-1] > df["Signal"].iloc[-1] else "BEARISH"

        st.subheader("📊 MACD Indicator")
        st.line_chart(df.set_index("Date")[["MACD", "Signal"]])
        st.write(f"MACD Signal: **{macd_signal}**")

        # =========================
        # FUNDAMENTAL ANALYSIS
        # =========================
        # =========================
        # FUNDAMENTAL ANALYSIS
        # =========================
        st.header("🏦 Fundamental Analysis")
        
        try:
            info = stock.get_info()
        
            sector = info.get("sector", "N/A")
            pe = info.get("trailingPE", "N/A")
            eps = info.get("trailingEps", "N/A")
            market_cap = info.get("marketCap", "N/A")
        
            st.write("**Sector:**", sector)
            st.write("**P/E Ratio:**", pe)
            st.write("**EPS:**", eps)
            st.write("**Market Cap:**", market_cap)
        
            st.info(
                "Fundamental data fetched from free Yahoo Finance API. "
                "Values may be delayed or limited."
            )
        
        except Exception:
            st.warning(
                "⚠️ Fundamental data temporarily unavailable due to free API limits.\n\n"
                "This does NOT affect technical analysis or investment logic."
            )

# =========================
# PORTFOLIO ALLOCATION (PREVIEW)
# =========================
else:
    st.header("💼 Portfolio Allocation (Preview – Phase 3)")
    st.warning("Portfolio allocation logic will be implemented in Phase 3.")
    st.write(
        """
        In the next phase, the agent will:
        - Ask investment duration
        - Ask sector preference
        - Split money across Equity, Gold, Debt, ETFs
        - Suggest top companies with manageable risk
        """
    )

# =========================
# FOOTER
# =========================
st.divider()
st.caption("Phase 2 complete: Visual analysis & transparent backend reasoning")

