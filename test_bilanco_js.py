import requests
from bs4 import BeautifulSoup
url = "https://www.getmidas.com/canli-borsa/a1cap-hisse/bilanco/"
text = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
with open("a1cap_bilanco.html", "w", encoding="utf-8") as f:
    f.write(text)
