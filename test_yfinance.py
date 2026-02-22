import yfinance as yf
import pandas as pd

def test_ticker(symbol):
    print(f"Testing {symbol}...")
    ticker = yf.Ticker(symbol)
    
    print("\n--- Income Statement ---")
    income_stmt = ticker.income_stmt
    print(income_stmt.head())
    
    print("\n--- Balance Sheet ---")
    balance_sheet = ticker.balance_sheet
    print(balance_sheet.head())
    
    print("\n--- Info ---")
    info = ticker.info
    print(f"P/E (Trailing): {info.get('trailingPE')}")
    print(f"Forward P/E: {info.get('forwardPE')}")
    print(f"PEG Ratio: {info.get('pegRatio')}")
    print(f"Price to Book: {info.get('priceToBook')}")

if __name__ == "__main__":
    test_ticker("THYAO.IS")
    test_ticker("ASELS.IS")
