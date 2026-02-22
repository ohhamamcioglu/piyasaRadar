import requests
from bs4 import BeautifulSoup
import json

r = requests.get("https://www.getmidas.com/canli-borsa/a1cap-hisse/", timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')

ortaklar = soup.find(string=lambda t: t and "Ortaklık Yapısı" in t)
if ortaklar:
    parent = ortaklar.parent
    for _ in range(4):
        if parent: parent = parent.parent
    print("Found HTML for Ortaklar:")
    print(str(parent)[:2000])

print("\n--- CEO info HTML ---")
ceo = soup.find(string=lambda t: t and "CEO" in t)
if ceo:
    print(str(ceo.parent.parent.parent)[:1000])
