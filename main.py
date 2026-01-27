import streamlit as st
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import yfinance as yf

# 1. SETUP: Connect to Gemini using your Secret Key
# Make sure you have added GEMINI_API_KEY in Streamlit Cloud Secrets
gemini_key = st.secrets["GEMINI_API_KEY"]
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    verbose=True,
    temperature=0.5,
    google_api_key=gemini_key
)

# 2. UI: Create the User Interface
st.set_page_config(page_title="AI Investment Advisor", layout="wide")
st.title("📈 Multi-Agent Investment Advisory System")
st.markdown("Your 24/7 Digital Financial Analyst and Portfolio Manager.")

with st.sidebar:
    st.header("User Profile")
    age = st.number_input("Age", min_value=18, max_value=100, value=21)
    income = st.number_input("Annual Income ($)", min_value=0, value=50000)
    capital = st.number_input("Investment Capital ($)", min_value=0, value=5000)
    risk_appetite = st.selectbox("Risk Appetite", ["Low", "Medium", "High"])
    
stock_ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, RELIANCE.NS)", value="AAPL")

# 3. AGENTS: Define the Experts
educator = Agent(
    role='Financial Educator',
    goal='Explain investment concepts simply to beginners',
    backstory='You make finance easy for students by explaining terms like SIP and Equity clearly.',
    llm=llm,
    allow_delegation=False
)

researcher = Agent(
    role='Stock Market Researcher',
    goal=f'Analyze {stock_ticker} 5-year trends and current news',
    backstory='You are an expert at fetching financial data and identifying market sentiment.',
    llm=llm,
    allow_delegation=True
)

advisor = Agent(
    role='Portfolio Advisor',
    goal='Provide a customized investment plan',
    backstory='You combine market data with user risk profiles to give Buy/Sell/Hold advice.',
    llm=llm,
    allow_delegation=False
)

# 4. TASKS: Assign the Work
task_educate = Task(
    description=f"Explain what investing in {stock_ticker} means for a {age}-year-old with {risk_appetite} risk.",
    agent=educator,
    expected_output="A simple 2-line explanation of the investment type."
)

task_analyze = Task(
    description=f"Analyze the 5-year price history of {stock_ticker} and find the latest news.",
    agent=researcher,
    expected_output="A summary of historical performance and current market mood."
)

task_recommend = Task(
    description=f"Based on the analysis and the user's capital of {capital}, suggest a Buy, Sell, or Hold action.",
    agent=advisor,
    expected_output="A clear recommendation with a breakdown of how many shares to buy."
)

# 5. EXECUTION: Run the Crew
if st.button("Run Full Investment Analysis"):
    with st.spinner("Agents are collaborating on your analysis..."):
        investment_crew = Crew(
            agents=[educator, researcher, advisor],
            tasks=[task_educate, task_analyze, task_recommend],
            process=Process.sequential
        )
        
        result = investment_crew.kickoff()
        
        st.success("Analysis Complete!")
        st.markdown("### 🤖 Agent Recommendations")
        st.write(result)
