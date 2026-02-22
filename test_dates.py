import requests
import json

url = "https://www.getmidas.com/wp-json/midas-api/v1/midas_bilnaco_date"
headers = {"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"}

# Let's try sending 8 dates
params = {
    "code": "A1CAP",
    "date1": "2025-12", "date2": "2025-9", "date3": "2025-6", "date4": "2025-3",
    "date5": "2024-12", "date6": "2024-9", "date7": "2024-6", "date8": "2024-3",
    "consildated1": 1, "consildated2": 1, "consildated3": 1, "consildated4": 1,
    "consildated5": 1, "consildated6": 1, "consildated7": 1, "consildated8": 1,
    "bilanco": "true"
}

r = requests.get(url, params=params, headers=headers)
try:
    data = r.json()
    if isinstance(data, str): data = json.loads(data)
    print("Length of bilanco array with 8 dates:", len(data.get("bilanco", [])))
except Exception as e:
    print("Failed:", e)
