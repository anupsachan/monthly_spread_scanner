import yfinance as yf
import pandas as pd
import yaml
import streamlit as st
from rules import RULES

# --- 1. Page Configuration (Best for Mobile) ---
st.set_page_config(
    page_title="Monthly Spread Scanner",
    page_icon="📈",
    layout="wide"
)

# --- 2. Load Config ---
with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

# --- 3. Data Logic (Unchanged from original) ---
def load_monthly_data(ticker, months):
    # auto_adjust=False is critical for getting standard Open/Close values
    df = yf.Ticker(ticker).history(period=f"{months}mo", interval="1mo", auto_adjust=False)
    df = df.dropna()
    # Remove timezone for clean processing
    df.index = df.index.tz_localize(None)
    df["Month"] = df.index.to_period("M").astype(str)
    return df.reset_index(drop=True)

def evaluate_rules(prev_row, curr_row):
    for rule in RULES:
        result = rule(prev_row, curr_row)
        if result:
            return result
    return "RED"

def run_backtest():
    matrix = {}
    for ticker in CONFIG["tickers"]:
        df = load_monthly_data(ticker, CONFIG["history_buffer"])
        results = {}
        start = len(df) - CONFIG["months_to_test"]
        for i in range(start, len(df)):
            if i <= 0: continue
            prev_row = df.iloc[i - 1]
            curr_row = df.iloc[i]
            month = curr_row["Month"]
            results[month] = evaluate_rules(prev_row, curr_row)
        matrix[ticker] = results
    return pd.DataFrame(matrix).T

# --- 4. Streamlit UI (The "Web" Part) ---
st.title("📈 Monthly Credit Spread Scanner")
st.markdown("Automated setup identification for Call and Put spreads.")

# Styling function for the web table
def style_cells(val):
    if val == "RED":
        return 'background-color: #ff4b4b; color: white; font-weight: bold'
    return 'background-color: #09ab3b; color: white; font-weight: bold'

if st.button('🚀 Run Scanner Now'):
    with st.spinner('Fetching historical data from Yahoo Finance...'):
        # Run the actual logic
        matrix_df = run_backtest()
        
        # Display the styled dataframe
        # .style.applymap() allows us to color the "RED" and "Setup" cells
        # .map() is the modern replacement for .applymap() in the Styler object
        styled_df = matrix_df.style.map(style_cells)        
        st.dataframe(styled_df, use_container_width=True)
        st.success("Scan Complete! Green cells indicate high-probability spread setups.")

# --- 5. User Guide ---
with st.expander("ℹ️ How to read this chart"):
    st.write("""
    - **RED**: No setup found for this month.
    - **R1-CALL**: Bullish setup identified based on Rule 1.
    - **R2-PUT**: Bearish setup identified based on Rule 2.
    """)