import requests
from bs4 import BeautifulSoup
import re
url = "https://www.getmidas.com/canli-borsa/a1cap-hisse/"
text = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
soup = BeautifulSoup(text, 'html.parser')
for script in soup.find_all('script'):
    if script.string and "5Y" in script.string and "chart" in script.string.lower():
        print(script.string[:500])
        print("...")
        print(script.string[-500:])
