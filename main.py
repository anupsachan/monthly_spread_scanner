import yfinance as yf
import pandas as pd
import yaml
import streamlit as st
from rules import RULES

# --- 1. Page Configuration (Optimized for Mobile) ---
st.set_page_config(
    page_title="Monthly Spread Scanner",
    page_icon="📈",
    layout="wide"
)

# --- 2. Load Config ---
with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

# --- 3. Data Logic ---
def load_monthly_data(ticker, months):
    # Fetch data from Yahoo Finance
    df = yf.Ticker(ticker).history(period=f"{months}mo", interval="1mo", auto_adjust=False)
    df = df.dropna()
    
    # Remove timezone and format date to 'Jan 2025' for cleaner mobile display
    df.index = df.index.tz_localize(None)
    df["Month"] = df.index.strftime('%b %Y') 
    
    return df.reset_index(drop=True)

def evaluate_rules(prev_row, curr_row):
    # Cycles through Rule 1 and Rule 2 defined in rules.py
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
    
    # 1. Create the DataFrame
    matrix_df = pd.DataFrame(matrix).T
    
    # 2. Reset the index so Tickers become a standard column
    matrix_df = matrix_df.reset_index().rename(columns={'index': 'Ticker'})
    
    # 3. Force the entire container to standard Python objects
    # This prevents 'LargeUtf8' by ensuring no high-perf Arrow types remain
    matrix_df = matrix_df.astype(object)
    
    return matrix_df
# --- 4. Streamlit UI ---
st.title("📈 Monthly Credit Spread Scanner")
st.markdown("Automated setup identification for Call and Put spreads.")

# Styling function for the web table colors
def style_cells(val):
    if val == "RED":
        return 'background-color: #ff4b4b; color: white; font-weight: bold'
    return 'background-color: #09ab3b; color: white; font-weight: bold'

if st.button('🚀 Run Scanner Now'):
    with st.spinner('Fetching historical data from Yahoo Finance...'):
        # Run the backtest logic
        matrix_df = run_backtest()
        
        # .map() is used for element-wise styling in modern Pandas
        styled_df = matrix_df.style.map(style_cells)        
        
        # Display the interactive dataframe
        st.dataframe(styled_df, use_container_width=True)
        st.success("Scan Complete! Green cells indicate potential spread setups.")

# --- 5. User Guide ---
with st.expander("ℹ️ How to read this chart"):
    st.write("""
    - **RED**: No setup found for this month.
    - **R1-CALL**: Bullish setup (Rule 1).
    - **R2-PUT**: Bearish setup (Rule 2).
    """)