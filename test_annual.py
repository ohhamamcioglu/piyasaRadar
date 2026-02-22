import requests
import json

url = "https://www.getmidas.com/wp-json/midas-api/v1/midas_bilnaco_date"
headers = {"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"}

# Let's try sending 4 annual dates
params = {
    "code": "A1CAP",
    "date1": "2024-12", "date2": "2023-12", "date3": "2022-12", "date4": "2021-12",
    "consildated1": 1, "consildated2": 1, "consildated3": 1, "consildated4": 1,
    "bilanco": "true"
}

r = requests.get(url, params=params, headers=headers)
try:
    data = r.json()
    if isinstance(data, str): data = json.loads(data)
    bs = data.get("bilanco", [])
    print(f"Returned {len(bs)} periods.")
    if len(bs) >= 2:
        # Print total assets for each period to verify
        for i, period in enumerate(bs):
            for item in period:
                if item.get("description") == "TOPLAM VARLIKLAR":
                    print(f"Period {i} Total Assets: {item.get('value')}")
                    break
except Exception as e:
    print("Failed:", e)
