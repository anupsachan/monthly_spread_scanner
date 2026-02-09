import yfinance as yf
import pandas as pd
import yaml
import streamlit as st
from rules import RULES

st.set_page_config(page_title="Monthly Spread Scanner", page_icon="📈", layout="wide")

with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

def load_monthly_data(ticker, months):
    df = yf.Ticker(ticker).history(period=f"{months}mo", interval="1mo", auto_adjust=False)
    df = df.dropna()
    df.index = df.index.tz_localize(None)
    df["Month"] = df.index.strftime('%b %Y') 
    return df.reset_index(drop=True)

def evaluate_rules(prev_row, curr_row):
    for rule in RULES:
        result = rule(prev_row, curr_row)
        if result: return result
    return "RED"

def run_backtest_to_list():
    # We build a list of dicts instead of a complex DataFrame
    final_data = []
    for ticker in CONFIG["tickers"]:
        df = load_monthly_data(ticker, CONFIG["history_buffer"])
        row_data = {"Ticker": ticker}
        start = len(df) - CONFIG["months_to_test"]
        for i in range(start, len(df)):
            if i <= 0: continue
            month = df.iloc[i]["Month"]
            status = evaluate_rules(df.iloc[i-1], df.iloc[i])
            row_data[month] = status
        final_data.append(row_data)
    return final_data

st.title("📈 Monthly Credit Spread Scanner")

if st.button('🚀 Run Scanner Now'):
    with st.spinner('Fetching historical data...'):
        results = run_backtest_to_list()
        
        if results:
            # OUT OF THE BOX: Build the table using standard Markdown 
            # This bypasses the Arrow/LargeUtf8 error completely.
            headers = results[0].keys()
            header_row = "| " + " | ".join(headers) + " |"
            separator = "| " + " | ".join(["---"] * len(headers)) + " |"
            
            table_rows = []
            for row in results:
                formatted_row = []
                for key, val in row.items():
                    if val == "RED":
                        formatted_row.append(f"🔴 {val}")
                    elif key == "Ticker":
                        formatted_row.append(f"**{val}**")
                    else:
                        formatted_row.append(f"🟢 {val}")
                table_rows.append("| " + " | ".join(formatted_row) + " |")
            
            full_markdown_table = f"{header_row}\n{separator}\n" + "\n".join(table_rows)
            st.markdown(full_markdown_table)
            st.success("Scan Complete!")