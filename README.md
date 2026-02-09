# 📈 Monthly Spread Scanner

A lightweight Python-based stock analyzer designed to identify **Credit Spread** setup readiness. This tool scans historical monthly data to detect specific price action patterns (Rules) for Call and Put spreads.

---

## 🚀 Overview
The **Monthly Spread Scanner** automates the tedious process of checking monthly charts for specific reversal or continuation patterns. It generates a clean, color-coded matrix showing which tickers are ready for a trade and which are currently "RED" (no setup).

### Key Features:
* **Automated Backtesting:** Scans the last 12 months (customizable) for setup accuracy.
* **Rule-Based Logic:** Uses specific price action triggers (e.g., Gap-ups/downs relative to previous closes).
* **Multi-Ticker Support:** Analyzes high-cap stocks like AAPL, NVDA, and TSLA simultaneously.
* **Professional UI:** Visualizes data using a clean table format.

---

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **Data Source:** `yfinance` (Yahoo Finance API)
* **Data Handling:** `pandas`
* **UI/Terminal:** `rich` (for beautiful terminal tables)

---

## 📊 How the Rules Work
The scanner currently evaluates setups based on two core rules:

1.  **Rule 1 (CALL Spread):** Triggered when the previous month was bearish (Close < Open) and the current month opens below that close.
2.  **Rule 2 (PUT Spread):** Triggered when the previous month was bullish (Close > Open) and the current month opens above that close.

---

## 💻 Installation & Usage

### 1. Clone the repository
```bash
git clone [https://github.com/YOUR_USERNAME/monthly_spread_scanner.git](https://github.com/YOUR_USERNAME/monthly_spread_scanner.git)
cd monthly_spread_scanner