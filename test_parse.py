import requests
from bs4 import BeautifulSoup
url = "https://www.getmidas.com/canli-borsa/a1cap-hisse/"
text = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
soup = BeautifulSoup(text, 'html.parser')
print("--- PRICE Elements ---")
for el in soup.find_all(text=True):
    if "Son İşlem Fiyatı" in el.strip() or "51.1" in el.strip(): # known price
        parent = el.parent
        print(parent.name, parent.get("class"), parent.text.strip()[:100])
        grandparent = parent.parent
        if grandparent:
             print("  Grand:", grandparent.name, grandparent.get("class"))

print("\n--- Piyasa Değeri ---")
for b in soup.select('.data'):
    if 'Piyasa Değeri' in b.text:
       print(b.text.strip().replace('\n', ' '))
