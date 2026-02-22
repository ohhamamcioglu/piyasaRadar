import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
}

try:
    print("--- MACRO INDICATORS ---")
    r_macro = requests.get("https://www.getmidas.com/canli-borsa/", headers=headers, timeout=10)
    soup_macro = BeautifulSoup(r_macro.text, 'html.parser')
    for text in ['BIST 100', 'Dolar', 'Euro', 'Gram Altın', 'BIST', 'USD', 'EUR']:
        elem = soup_macro.find(string=lambda t: t and text in t)
        if elem:
            # Print parent block text
            parent = elem.parent
            if parent.parent: 
                parent = parent.parent
            print(f"Found '{text}': {parent.text.strip().replace(chr(10), ' ')}")

except Exception as e:
    print("Macro error:", e)

try:
    print("\n--- COMPANY INFO (A1CAP) ---")
    r_comp = requests.get("https://www.getmidas.com/canli-borsa/a1cap-hisse/", headers=headers, timeout=10)
    soup_comp = BeautifulSoup(r_comp.text, 'html.parser')

    for text in ['Ortaklık Yapısı', 'Ortaklar', 'Hakkında', 'Kuruluş']:
        elem = soup_comp.find(string=lambda t: t and text in t)
        if elem:
            parent = elem.parent
            for _ in range(3):
                if parent.parent: parent = parent.parent
            print(f"Found '{text}' block:")
            print(parent.text.strip().replace('  ', '').replace(chr(10), '\n'))
except Exception as e:
    print("Comp error:", e)
