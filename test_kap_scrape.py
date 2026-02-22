import requests
from bs4 import BeautifulSoup

def test_kap_scrape(disclosure_id):
    url = f"https://www.kap.org.tr/tr/Bildirim/{disclosure_id}"
    print(f"Scraping {url}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check for XBRL tags or structured tables
    # Note: Financial reports often load data into a 'Finansal Tablolar' tab via JS.
    # If the data is not in the initial HTML, we might need a different approach.
    
    print("Title:", soup.title.text)
    
    # Look for 'Finansal Tablo' related content
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables.")
    
    for i, table in enumerate(tables[:5]):
        print(f"\nTable {i} sample:")
        print(table.text[:200].strip())

if __name__ == "__main__":
    # Sample disclosure ID from research
    test_kap_scrape("1558047")
