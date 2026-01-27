import streamlit as st
st.title("Zyzzo's AI Investment Agent")
st.write("Welcome! My agents are preparing your analysis...")
from crewai import Agent, Task, Crew
import streamlit as st

# Step A: Define your Agents (The Job Descriptions)
educator = Agent(
    role='Financial Educator',
    goal='Explain investment concepts simply to beginners',
    backstory='You are a friendly mentor who makes finance easy to understand for 21-year-olds.',
    allow_delegation=False,
    verbose=True
)

researcher = Agent(
    role='Stock Market Researcher',
    goal='Analyze 5-year price trends and current news',
    backstory='You are an expert analyst who looks at historical data and sector trends.',
    allow_delegation=False,
    verbose=True
)

# Step B: Define the Tasks (The Instructions)
task1 = Task(
    description='Explain the difference between SIP, Equity, and Bonds to a new investor.',
    agent=educator,
    expected_output='A concise, 3-line summary of investment types.'
)

task2 = Task(
    description='Analyze the 5-year performance of the selected stock and summarize the current news.',
    agent=researcher,
    expected_output='A summary of price trends and key news headlines.'
)
