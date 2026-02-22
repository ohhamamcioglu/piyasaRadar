import requests
from bs4 import BeautifulSoup
import re

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

r = requests.get("https://www.getmidas.com/canli-borsa/", headers=headers, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')

print("--- MACRO LINKS ---")
for text in ['BIST 100', 'Dolar', 'Euro', 'Gram Altın']:
    elem = soup.find(string=lambda t: t and text in t)
    if elem:
        parent = elem.parent
        for _ in range(5):
            if parent and parent.name == 'a':
                print(f"{text} link: {parent.get('href')}")
                break
            if parent:
                parent = parent.parent

# Search for the script data format for charting on a sample stock page
print("\n--- CHART DATA FORMAT (A1CAP) ---")
r_stock = requests.get("https://www.getmidas.com/canli-borsa/a1cap-hisse/", headers=headers, timeout=10)
scripts = BeautifulSoup(r_stock.text, 'html.parser').find_all('script')
for s in scripts:
    if s.string and ('dataPoints' in s.string or 'chart' in s.string.lower() or 'series' in s.string.lower()):
        # Just grab a tiny sample of the script
        match = re.search(r'\[\{.*?\}\]', s.string)
        if match:
             print("Found array in script like:", match.group(0)[:100])
             break
