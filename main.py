# -*- coding: utf-8 -*-
import yfinance as yf
import pandas as pd
import yaml
import streamlit as st
import plotly.graph_objects as go  # Ensure this is imported globally
from rules import RULES

# --- 1. Load Config & Page Setup ---
with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

st.set_page_config(page_title="Master Scanner", layout="wide")

# --- 2. HIGH VISIBILITY & PULSE ANIMATION (CSS) ---
st.markdown("""
    <style>
    /* 1. High Visibility Dropdown */
    div[data-baseweb="select"] {
        border: 3px solid #09ab3b !important;
        border-radius: 10px !important;
        background-color: #f0f2f6 !important;
    }
    .stSelectbox label p {
        color: #09ab3b !important;
        font-weight: bold !important;
        font-size: 1.2rem !important;
    }

    /* 2. Pulse Animation for the Run Button */
    @keyframes pulse-green {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(9, 171, 59, 0.7); }
        70% { transform: scale(1.05); box-shadow: 0 0 0 10px rgba(9, 171, 59, 0); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(9, 171, 59, 0); }
    }

    div.stButton > button {
        animation: pulse-green 2s infinite;
        background-color: #09ab3b !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        width: 100%;
        height: 3.5em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Helper Functions ---
def get_display_name(ticker):
    return CONFIG.get("names", {}).get(ticker, ticker)

def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period="1d")
        return f"${data['Close'].iloc[-1]:.2f}"
    except:
        return "N/A"

def get_period_label(date, interval):
    if interval == "1d": return date.strftime('%b %d')
    if interval == "1wk": 
        w = (date.day - 1) // 7 + 1
        return f"Week {w}"
    if interval == "1mo": return date.strftime('%B %Y')
    if interval == "3mo": 
        q = (date.month - 1) // 3 + 1
        return f"Q{q}-{date.year}"
    return date.strftime('%Y-%m-%d')

def load_data(ticker, interval):
    period = "1y" if interval in ["1d", "1wk"] else "5y"
    df = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=False)
    df = df.dropna()
    df.index = df.index.tz_localize(None)
    return df

# --- 4. Main UI Header ---
st.title("📊 Master Credit Spread Scanner")

st.info("**Market Logic:** This scanner identifies reversals and gaps relative to the previous close.")
st.markdown("""
- <span style='color: #ff4b4b; font-weight: bold;'>RED</span>: No setup found.
- <span style='color: #09ab3b; font-weight: bold;'>GREEN (R1/R2)</span>: Setup identified.
""", unsafe_allow_html=True)

# --- 5. Ticker & Timeframe Selectors ---
col1, col2 = st.columns(2)

with col1:
    timeframe_choice = st.selectbox(
        "1. Select Timeframe to Scan:",
        ["Daily", "Weekly", "Monthly", "Quarterly"],
        index=2
    )

with col2:
    # Use friendly names in the dropdown list
    selected_ticker = st.selectbox(
        "2. Select Ticker for Graphic:",
        CONFIG["tickers"],
        format_func=get_display_name
    )

interval_map = {"Daily": "1d", "Weekly": "1wk", "Monthly": "1mo", "Quarterly": "3mo"}
selected_inv = interval_map[timeframe_choice]

# --- 6. Graphical Representation Widget ---
if selected_ticker:
    df_chart = load_data(selected_ticker, selected_inv)
    if len(df_chart) >= 2:
        last_2 = df_chart.iloc[-2:]
        labels = [get_period_label(d, selected_inv) for d in last_2.index]
        
        # This is where 'go' is used
        fig = go.Figure(data=[go.Candlestick(
            x=labels,
            open=last_2['Open'], high=last_2['High'],
            low=last_2['Low'], close=last_2['Close'],
            increasing_line_color='#09ab3b', decreasing_line_color='#ff4b4b'
        )])
        fig.update_layout(
            title=f"{get_display_name(selected_ticker)} Chart: {labels[0]} vs {labels[1]}",
            xaxis_rangeslider_visible=False,
            height=400,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

# --- 7. Scanner Execution ---
if st.button(f'🚀 RUN {timeframe_choice.upper()} SCAN NOW'):
    with st.spinner('Checking patterns...'):
        results = []
        for ticker in CONFIG["tickers"]:
            try:
                df = load_data(ticker, selected_inv)
                if len(df) < 3: continue
                
                name = get_display_name(ticker)
                price = get_live_price(ticker)
                
                res_prev, res_curr = "RED", "RED"
                for rule in RULES:
                    if res_prev == "RED": res_prev = rule(df.iloc[-3], df.iloc[-2]) or "RED"
                    if res_curr == "RED": res_curr = rule(df.iloc[-2], df.iloc[-1]) or "RED"
                
                results.append({
                    "Ticker": f"**{name}**<br><small>({price})</small>",
                    "prev_label": get_period_label(df.index[-2], selected_inv),
                    "curr_label": get_period_label(df.index[-1], selected_inv),
                    "prev_res": res_prev,
                    "curr_res": res_curr
                })
            except: continue

        if results:
            header = f"| Instrument | Previous ({results[0]['prev_label']}) | Current ({results[0]['curr_label']}) |"
            sep = "| :--- | :---: | :---: |"
            rows = []
            
            green_box = "<div style='background-color:#09ab3b; color:white; padding:8px; border-radius:5px; font-weight:bold; text-align:center;'>{}</div>"
            red_box = "<div style='background-color:#ff4b4b; color:white; padding:8px; border-radius:5px; font-weight:bold; text-align:center;'>{}</div>"
            
            for r in results:
                p_val = red_box.format(r['prev_res']) if r['prev_res'] == "RED" else green_box.format(r['prev_res'])
                c_val = red_box.format(r['curr_res']) if r['curr_res'] == "RED" else green_box.format(r['curr_res'])
                rows.append(f"| {r['Ticker']} | {p_val} | {c_val} |")
            
            st.markdown(header + "\n" + sep + "\n" + "\n".join(rows), unsafe_allow_html=True)
            st.success("Scan Complete!")