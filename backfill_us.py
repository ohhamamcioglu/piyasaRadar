import json
import yfinance as yf
import concurrent.futures
import math

def sanitize_float(val):
    if isinstance(val, float):
        if math.isnan(val) or val == float('inf') or val == float('-inf'):
            return None
    return val

def sanitize_data(data):
    if isinstance(data, dict):
        return {k: sanitize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_data(i) for i in data]
    else:
        return sanitize_float(data)

def fetch_history(ticker):
    try:
        hist = yf.Ticker(ticker).history(period="1y")
        if not hist.empty:
            return ticker, sanitize_data(hist['Close'].tolist())
    except:
        pass
    return ticker, []

print("Loading existing midas_all_data.json...")
with open("midas_all_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

stocks = data.get("data", [])
print(f"Found {len(stocks)} stocks.")

print("Fetching historical prices concurrently...")
fiyat_map = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    futures = {executor.submit(fetch_history, stock['ticker']): stock['ticker'] for stock in stocks}
    for future in concurrent.futures.as_completed(futures):
        ticker, hist = future.result()
        fiyat_map[ticker] = hist

print("Applying history to stocks...")
for stock in stocks:
    stock["fiyat_gecmisi"] = fiyat_map.get(stock["ticker"], [])

print("Fetching US Macro Indicators...")
macros = {}
macro_tickers = {"SP500": "^GSPC", "Nasdaq": "^IXIC", "VIX": "^VIX"}
for name, ticker in macro_tickers.items():
    try:
        hist = yf.Ticker(ticker).history(period="1y")
        if not hist.empty:
            macros[name] = sanitize_data(hist['Close'].tolist())
            print(f"Fetched {name}")
    except Exception as e:
        print(f"Error fetching {name}: {e}")

data["macros"] = macros
data["data"] = stocks

print("Saving updated midas_all_data.json...")
with open("midas_all_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
print("Done!")
