import yfinance as yf
import pandas as pd
import yaml
import streamlit as st
from rules import RULES

st.set_page_config(page_title="Master Spread Scanner", page_icon="📈", layout="wide")

# --- 1. Load Config ---
with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

# Get styles from config with defaults
GREEN_STYLE = CONFIG.get("ui", {}).get("green_style", "🟢")
RED_STYLE = CONFIG.get("ui", {}).get("red_style", "🔴")

def get_period_label(date, interval):
    """Standardizes date labels for the multi-view table."""
    if interval == "1d": return date.strftime('%b %d')
    if interval == "1wk": return f"Wk {date.strftime('%d')}"
    if interval == "1mo": return date.strftime('%b %y')
    if interval == "3mo": return f"Q{(date.month-1)//3 + 1}-{date.year % 100}"
    return date.strftime('%Y-%m-%d')

def load_data(ticker, interval):
    """Fetches data for a specific timeframe."""
    period = "1y" if interval in ["1d", "1wk"] else "5y"
    df = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=False)
    df = df.dropna()
    df.index = df.index.tz_localize(None)
    return df

def evaluate_rules(prev_row, curr_row):
    """Runs technical rules from rules.py."""
    for rule in RULES:
        result = rule(prev_row, curr_row)
        if result: return result
    return "RED"

def run_master_scan():
    """Loops through all intervals for all tickers."""
    intervals = ["1d", "1wk", "1mo", "3mo"]
    master_results = []

    for ticker in CONFIG["tickers"]:
        for inv in intervals:
            try:
                df = load_data(ticker, inv)
                if len(df) < 2: continue
                
                curr_idx = len(df) - 1
                prev_idx = len(df) - 2
                
                label_prev = get_period_label(df.index[prev_idx], inv)
                label_curr = get_period_label(df.index[curr_idx], inv)
                
                res_prev = evaluate_rules(df.iloc[prev_idx-1], df.iloc[prev_idx])
                res_curr = evaluate_rules(df.iloc[prev_idx], df.iloc[curr_idx])
                
                master_results.append({
                    "Ticker": ticker,
                    "Timeframe": inv.replace("1d","Daily").replace("1wk","Weekly").replace("1mo","Monthly").replace("3mo","Quarterly"),
                    "prev_label": label_prev,
                    "curr_label": label_curr,
                    "prev_res": res_prev,
                    "curr_res": res_curr
                })
            except Exception:
                continue
    return master_results

st.title("📈 Master Credit Spread Scanner")

if st.button('🚀 Run Full Market Scan'):
    with st.spinner('Scanning all intervals...'):
        results = run_master_scan()
        
        if results:
            # Markdown Table Construction
            header = "| Ticker | Timeframe | Previous Period | Current Period |"
            sep = "| --- | --- | --- | --- |"
            
            rows = []
            for r in results:
                # Ticker label logic
                t_cell = f"**{r['Ticker']}**" if r['Timeframe'] == "Daily" else ""
                
                # Apply Style from Config
                p_icon = RED_STYLE if r['prev_res'] == "RED" else GREEN_STYLE
                c_icon = RED_STYLE if r['curr_res'] == "RED" else GREEN_STYLE
                
                p_text = f"{p_icon} {r['prev_res']}"
                c_text = f"{c_icon} {r['curr_res']}"
                
                rows.append(f"| {t_cell} | {r['Timeframe']} | {p_text} <br> <small>{r['prev_label']}</small> | {c_text} <br> <small>{r['curr_label']}</small> |")
            
            st.markdown(header + "\n" + sep + "\n" + "\n".join(rows), unsafe_allow_html=True)
            st.success("Scan Complete!")