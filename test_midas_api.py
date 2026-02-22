import requests

url = "https://www.getmidas.com/wp-json/midas-api/v1/midas_bilnaco_date?code=A1CAP&date1=2025-12&date2=2025-9&date3=2025-6&date4=2025-3&consildated1=1&consildated2=1&consildated3=1&consildated4=1&bilanco=true"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.getmidas.com/canli-borsa/a1cap-hisse/bilanco/"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success! First 200 chars:")
        print(response.text[:200])
    else:
        print("Failed. Headers or CF block.")
except Exception as e:
    print(f"Error: {e}")
