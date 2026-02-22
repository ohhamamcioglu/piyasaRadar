import yfinance as yf
import requests
from xbrl_parser import parse_kap_html

def demo_output(ticker, disclosure_id):
    print(f"=== BIST Real-Time Analysis Output Demo ===")
    print(f"Ticker: {ticker}")
    print(f"KAP Disclosure ID: {disclosure_id}")
    
    # 1. Fetch Real-time Price
    print("\n[Action] Fetching real-time price from yfinance...")
    stock = yf.Ticker(f"{ticker}.IS")
    price = stock.fast_info['last_price']
    print(f"Result: {ticker} Current Price = {price:.2f} TL")
    
    # 2. Fetch & Parse Financials
    print("\n[Action] Fetching and parsing KAP disclosure HTML...")
    url = f"https://www.kap.org.tr/tr/Bildirim/{disclosure_id}"
    resp = requests.get(url)
    financials = parse_kap_html(resp.text)
    
    # 3. Combined Analysis
    print("\n[Analysis Results]")
    if 'error' in financials:
        print(f"Error: {financials['error']}")
    else:
        revenue = financials.get('revenue', 0)
        net_profit = financials.get('net_profit', 0)
        equity = financials.get('equity', 0)
        
        roe = (net_profit / equity * 100) if equity else 0
        
        print(f"Revenue (TTM/Period): {revenue:,.0f} TL")
        print(f"Net Profit: {net_profit:,.0f} TL")
        print(f"Total Equity: {equity:,.0f} TL")
        print(f"Calculated ROE: {roe:.2f}%")
        
        # Valuation from yfinance
        info = stock.info
        print(f"yfinance Trailing P/E (F/K): {info.get('trailingPE')}")
        print(f"yfinance P/B (PD/DD): {info.get('priceToBook')}")
    
    print("\n===========================================")

if __name__ == "__main__":
    # Using the verified sample ADGYO (ID: 1558047)
    demo_output("ADGYO", "1558047")
