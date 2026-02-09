import yfinance as yf
import pandas as pd
import yaml
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rules import RULES

console = Console()

with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)


def load_monthly_data(ticker, months):
    df = yf.Ticker(ticker).history(period=f"{months}mo", interval="1mo", auto_adjust=False)
    df = df.dropna()
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
            if i <= 0:
                continue
            prev_row = df.iloc[i - 1]
            curr_row = df.iloc[i]
            month = curr_row["Month"]
            results[month] = evaluate_rules(prev_row, curr_row)
        matrix[ticker] = results
    return pd.DataFrame(matrix).T


def render(matrix):
    table = Table(title="Monthly Credit Spread Setup Readiness", show_lines=True)
    table.add_column("Ticker", style="bold", justify="center")
    for m in matrix.columns:
        table.add_column(m, justify="center")
    for ticker, row in matrix.iterrows():
        cells = []
        for val in row:
            if val == "RED":
                cells.append(Text("RED", style=CONFIG["ui"]["red_style"]))
            else:
                cells.append(Text(val, style=CONFIG["ui"]["green_style"]))
        table.add_row(ticker, *cells)
    console.print(table)


def main():
    console.print("\n[cyan]Running monthly spread setup scanner...[/cyan]\n")
    matrix = run_backtest()
    render(matrix)


if __name__ == "__main__":
    main()