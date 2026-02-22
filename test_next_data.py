import requests
from bs4 import BeautifulSoup
import json

headers = {"User-Agent": "Mozilla/5.0"}
url = "https://www.getmidas.com/canli-doviz/dolar-fiyat/"

r = requests.get(url, headers=headers, timeout=10)
if r.status_code == 200:
    soup = BeautifulSoup(r.text, 'html.parser')
    nxt = soup.find('script', id='__NEXT_DATA__')
    if nxt and nxt.string:
        try:
            data = json.loads(nxt.string)
            # Dump the keys to see where chart data might be
            print("Next.js Data Keys:", data.keys())
            props = data.get('props', {}).get('pageProps', {})
            print("PageProps Keys:", props.keys())
            
            # Check for anything looking like historical data
            for k, v in props.items():
                if isinstance(v, dict):
                    print(f"Prop '{k}' is dict with keys: {v.keys()}")
                elif isinstance(v, list):
                    print(f"Prop '{k}' is list of length {len(v)}")
                    if len(v) > 0:
                        print(f"First item: {str(v[0])[:100]}")
        except Exception as e:
            print("Error parsing JSON:", e)
else:
    print("Fetch failed.")
