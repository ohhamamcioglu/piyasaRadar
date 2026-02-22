import requests
from bs4 import BeautifulSoup
import re
import json

headers = {"User-Agent": "Mozilla/5.0"}
urls = [
    "https://www.getmidas.com/canli-doviz/dolar-fiyat/",
    "https://www.getmidas.com/canli-doviz/euro-fiyat/",
    "https://www.getmidas.com/canli-altin/gram-altin-fiyat/",
    "https://www.getmidas.com/canli-borsa/bist-100-endeksi/"
]

for u in urls:
    r = requests.get(u, headers=headers, timeout=10)
    print(f"\n--- {u.split('/')[-2]} ---")
    if r.status_code == 200:
        # Search script tags
        scripts = BeautifulSoup(r.text, 'html.parser').find_all('script')
        found_data = False
        for s in scripts:
            if s.string and ("HistoricalPriceStore" in s.string or "dataPoints" in s.string or "var data" in s.string):
                # Look for array brackets
                match = re.search(r'\[\s*\{.*?\}\s*\]', s.string, re.DOTALL)
                if match:
                    data = match.group(0)
                    print(f"Found array match, length: {len(data)}")
                    print(data[:150], "...")
                    found_data = True
                    break
        if not found_data:
             # Look for specific Next.js json
             nxt = BeautifulSoup(r.text, 'html.parser').find('script', id='__NEXT_DATA__')
             if nxt:
                 print("Found NEXT_DATA block length:", len(nxt.string))
             else:
                 print("No chart data easily found.")
    else:
        print(f"Failed to fetch {u}, status: {r.status_code}")
