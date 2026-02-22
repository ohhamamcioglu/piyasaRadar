import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

def fetch_midas_tickers():
    """
    Scrapes tickers from Midas 'Amerikan Borsası' page.
    Returns list of tickers (e.g., ['AAPL', 'TSLA', ...]).
    """
    url = "https://www.getmidas.com/amerikan-borsasi/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        
        midas_tickers = set()
        # Regex to match /amerikan-borsasi/TICKER-hisse/
        # Include dots for tickers like BRK.B
        pattern = re.compile(r'/amerikan-borsasi/([a-zA-Z0-9.]+)-hisse/?$')
        
        for link in links:
            href = link['href']
            match = pattern.search(href)
            if match:
                ticker = match.group(1).upper()
                # Convert dots to dashes for yfinance (BRK.B -> BRK-B)
                ticker = ticker.replace('.', '-')
                if len(ticker) <= 6: 
                    midas_tickers.add(ticker)
        
        print(f"Fetched {len(midas_tickers)} tickers from Midas.")
        return list(midas_tickers)
    except Exception as e:
        print(f"Error fetching from Midas: {e}")
        return []

def fetch_sp500_tickers():
    """
    Fetches the list of S&P 500 companies from Wikipedia.
    Returns a list of tickers (e.g., ['AAPL', 'MSFT', ...]).
    """
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        tables = pd.read_html(response.text)
        df = tables[0]
        tickers = df['Symbol'].tolist()
        # Clean tickers (e.g., BRK.B -> BRK-B for yfinance)
        tickers = [t.replace('.', '-') for t in tickers]
        return tickers
    except Exception as e:
        print(f"Error fetching S&P 500 tickers: {e}")
        # Fallback
        return [
            "AAPL", "MSFT", "GOOG", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "LLY",
            "V", "UNH", "XOM", "JPM", "JNJ", "MA", "PG", "HD", "AVGO", "MRK"
        ]

def fetch_all_us_tickers():
    """
    Combines Midas and S&P 500 tickers.
    Prioritizes Midas list.
    """
    midas = fetch_midas_tickers()
    if midas:
        return midas
    
    print("Midas fetch failed, falling back to S&P 500.")
    return fetch_sp500_tickers()

if __name__ == "__main__":
    tickers = fetch_all_us_tickers()
    print(f"Total unique tickers: {len(tickers)}")
