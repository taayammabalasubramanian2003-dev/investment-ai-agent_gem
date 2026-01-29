import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

#GEMINI SETUP
import google.generativeai as genai
import os
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ Gemini API key not found. Please check Streamlit Secrets.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-pro")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
#model = genai.GenerativeModel("gemini-pro")
model = genai.GenerativeModel("models/gemini-1.5-flash")
st.subheader("🧪 Gemini Test")

if os.getenv("GEMINI_API_KEY") is None:
    st.error("❌ Gemini API key not found. Check Streamlit Secrets.")
else:
    st.success("✅ Gemini API key detected")
    st.write(ai_explain("Say hello in one sentence"))

# =========================
# AI EXPLANATION FUNCTION
# =========================
def ai_explain(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "⚠️ AI explanation temporarily unavailable."
        
st.write(ai_explain("Say hello in one line"))
st.subheader("🧪 Gemini Test")
st.write(ai_explain("Say hello to a beginner investor in one line"))

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

def ai_explain(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return "⚠️ AI explanation temporarily unavailable."


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
        st.write(f"RSI: *{round(rsi_val,2)} → {rsi_signal}*")
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
        st.write(f"MACD Signal: *{macd_signal}*")
        st.caption("MACD confirms trend direction")

       
        # 🔑 SAVE FOR PHASE 4 (FIXED)
        # st.session_state.trend = trend
        # st.session_state.rsi_value = rsi_val
        # st.session_state.macd_signal = macd_signal
        # st.session_state.stock_analyzed = True
        st.session_state.trend = trend
        st.session_state.rsi_value = rsi_val
        st.session_state.macd_signal = macd_signal
        st.session_state.symbol = symbol
        st.session_state.stock_analyzed = True



        # -------------------------
        # FUNDAMENTAL ANALYSIS
        # -------------------------
        st.header("🏦 Fundamental Analysis")

        try:
            info = stock.get_info()
            st.write("*Sector:*", info.get("sector", "N/A"))
            st.write("*P/E Ratio:*", info.get("trailingPE", "N/A"))
            st.write("*EPS:*", info.get("trailingEps", "N/A"))
            st.write("*Market Cap:*", info.get("marketCap", "N/A"))

            st.info(
                "📌 Fundamental data is fetched from *Yahoo Finance free API*. "
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
                st.write(f"*{asset} → ₹{amt:.0f} ({pct}%)*")

        st.subheader("🏢 Suggested Investments")

        # =========================
        # EQUITY
        # =========================
        if "Equity" in assets:
            st.markdown("### 📈 Equity – Growth Engine")
        
            st.write(
                "✔ *Why Equity?* Equity helps your money grow faster over the long term by investing in businesses."
            )
        
            st.write(
                "• *HDFC Bank* – India’s largest private bank with stable profits and strong risk management."
            )
            st.write(
                "• *TCS* – Market leader in IT services with consistent revenue and global clients."
            )
            st.write(
                "• *Infosys* – Strong digital transformation focus and steady long-term growth."
            )
        
        # =========================
        # DEBT
        # =========================
        if "Debt" in assets:
            st.markdown("### 🏦 Debt – Capital Protection")
        
            st.write(
                "✔ *Why Debt?* Debt funds protect your capital and reduce overall portfolio risk."
            )
        
            st.write(
                "• *ICICI Pru Corporate Bond Fund* – Invests in high-quality corporate bonds for stable returns."
            )
            st.write(
                "• *HDFC Corporate Bond Fund* – Lower volatility with predictable income."
            )
        
        # =========================
        # GOLD ETF
        # =========================
        if "Gold ETF" in assets:
            st.markdown("### 🪙 Gold ETF – Risk Hedge")
        
            st.write(
                "✔ *Why Gold?* Gold protects against inflation, market crashes, and global uncertainty."
            )
        
            st.write(
                "• *GOLDBEES.NS* – Safest and most liquid gold ETF in India, tracks gold prices directly."
            )

        st.subheader("🧠 Why this portfolio?")
        st.info(
            f"""
            • Risk appetite: *{risk}%*  
            • Equity for growth  
            • Debt for stability  
            • Gold for inflation hedge  
            • Optimized for *{horizon}*
            """
        )

# =========================
# FOOTER
# =========================
st.divider()
st.caption("✅ Phase 2 & Phase 3 complete – Transparent AI Investment Agent")



# ============================================================
# ======================= PHASE 4 =============================
# ============================================================

# Phase 4 should run ONLY if stock was analyzed
#if choice == "Analyze a Stock":
if choice == "Analyze a Stock" and st.session_state.get("stock_analyzed", False):

    st.divider()
    st.header("🧠 Phase 4: AI Decision Agent")

    if "stock_analyzed" not in st.session_state:
        st.warning("⚠️ Analyze a stock in Phase 2 to activate AI Decision Agent.")
        st.stop()

    # Fetch saved values
    trend = st.session_state.trend
    rsi_value = st.session_state.rsi_value
    macd_signal = st.session_state.macd_signal
    stock_name = symbol.upper()

    # -------------------------
    # AI SCORING LOGIC
    # -------------------------
    score = 0
    reasons = []

    if trend == "BULLISH":
        score += 1
        reasons.append("Price trend is bullish (MA crossover)")
    else:
        reasons.append("Price trend is weak or bearish")

    if rsi_value > 50:
        score += 1
        reasons.append("RSI shows buying strength")
    else:
        reasons.append("RSI shows weak momentum")

    if macd_signal == "BULLISH":
        score += 1
        reasons.append("MACD confirms upward momentum")
    else:
        reasons.append("MACD does not confirm strength")

    # -------------------------
    # FINAL DECISION
    # -------------------------
    if score >= 2:
        decision = "BUY"
    elif score == 1:
        decision = "HOLD"
    else:
        decision = "WAIT"

    st.success(f"📌 *AI Recommendation for {stock_name}: {decision}*")

    st.subheader("🧠 Why this decision?")
    for r in reasons:
        st.write("•", r)

        explanation = ai_explain(f"""
    Stock: {st.session_state.symbol}
    Trend: {trend}
    RSI: {rsi_value}
    MACD: {macd_signal}
    
    Explain in simple words whether user should BUY, HOLD, WAIT or SELL.
    """)

    st.subheader("🤖 AI Reasoning (Why this decision?)")
    st.write(explanation)


    
    # -------------------------
    # EDUCATOR SECTION
    # -------------------------
    st.subheader("🎓 Indicator Explanation")

   # with st.expander("📘 What do these indicators mean?"):
    #    st.write("*RSI*: Measures buying vs selling pressure.")
     #   st.write("*MACD*: Confirms trend strength and direction.")
      #  st.write("*Moving Averages*: Show overall price direction.")
       # st.write("*Candlestick Charts*: Show market psychology.")
    with st.expander("📘 Learn these indicators"):
        st.write(ai_explain("""
        Explain RSI, MACD, Moving Averages and Candlestick charts
        in simple beginner-friendly language.
        """))

    # -------------------------
    # FINANCIAL PLANNING (WITH CHART)
    # -------------------------
    st.subheader("🔮 Financial Planning Forecast")

    monthly = st.number_input(
        "Monthly SIP Investment (₹)",
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

    fv = monthly * ((1 + rate) ** months - 1) / rate

    st.success(f"📈 Expected Value after {years} years: ₹{round(fv,2)}")

    # Chart
    values = []
    for m in range(1, months + 1):
        values.append(monthly * ((1 + rate) ** m - 1) / rate)

    chart_df = pd.DataFrame({
        "Month": range(1, months + 1),
        "Investment Value": values
    })

    st.write(ai_explain(f"""
    User invests ₹{monthly} monthly for {years} years.
    Explain SIP, compounding, and why long-term equity returns average ~12%.
    """))
    st.line_chart(chart_df.set_index("Month"))

    st.caption(
        "Assumes 12% annual return • Monthly SIP • Power of compounding"
    )
    st.subheader("🧠 How this money grows")




