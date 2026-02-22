import requests
url = "https://www.getmidas.com/canli-borsa/a1cap-hisse/"
text = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
with open("a1cap_midas.html", "w", encoding="utf-8") as f:
    f.write(text)
