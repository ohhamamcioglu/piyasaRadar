import yfinance as yf

try:
    ticker = yf.Ticker("THYAO.IS")
    hist = ticker.history(period="1mo")
    print(f"History length: {len(hist)}")
    if not hist.empty:
        print(f"Last price: {hist.iloc[-1]['Close']}")
        print("Success!")
    else:
        print("Empty history.")
except Exception as e:
    print(f"Error: {e}")
