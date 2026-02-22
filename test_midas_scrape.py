import requests
from bs4 import BeautifulSoup
import re

def scrape_midas_tickers():
    url = "https://www.getmidas.com/amerikan-borsasi/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        
        midas_tickers = set()
        
        # Regex to match /amerikan-borsasi/TICKER-hisse/
        pattern = re.compile(r'/amerikan-borsasi/([a-zA-Z0-9]+)-hisse/$')
        
        for link in links:
            href = link['href']
            match = pattern.search(href)
            if match:
                ticker = match.group(1).upper()
                # Filter out likely invalid or generic ones if any
                if len(ticker) <= 5: 
                    midas_tickers.add(ticker)
                    
        print(f"Found {len(midas_tickers)} unique tickers from Midas.")
        print(f"Sample: {list(midas_tickers)[:10]}")
        return list(midas_tickers)
        
    except Exception as e:
        print(f"Error scraping Midas: {e}")
        return []

if __name__ == "__main__":
    scrape_midas_tickers()
