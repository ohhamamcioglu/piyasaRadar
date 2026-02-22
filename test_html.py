import requests
from bs4 import BeautifulSoup

url = "https://www.getmidas.com/canli-borsa/a1cap-hisse/bilanco/"
text = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
soup = BeautifulSoup(text, 'html.parser')

print("--- Dropdowns / Selects ---")
for select in soup.find_all('select'):
    print(f"Select ID: {select.get('id')}, Name: {select.get('name')}, Class: {select.get('class')}")
    for opt in select.find_all('option'):
        print(f"  Option: {opt.text.strip()} -> Value: {opt.get('value')}")

print("\n--- Any data attributes with API info? ---")
for form in soup.find_all('form'):
    print(f"Form action: {form.get('action')}")
