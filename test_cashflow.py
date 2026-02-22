import requests
import json

url = "https://www.getmidas.com/wp-json/midas-api/v1/midas_bilnaco_date"
headers = {"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"}

def test_cf(name, params):
    r = requests.get(url, params=params, headers=headers)
    if r.status_code == 200:
        data = r.json()
        if isinstance(data, str): 
            try: data = json.loads(data)
            except: return
        if isinstance(data, dict):
            keys = list(data.keys())
            if keys:
                print(f"[{name}] returned Keys: {keys}")
                arr = data[keys[0]]
                if arr and isinstance(arr, list) and len(arr) > 0 and isinstance(arr[0], list) and len(arr[0]) > 1:
                    print(f"  First item: {arr[0][1]['description']}")

params = {
    "code": "A1CAP",
    "date1": "2025-12", "date2": "2025-9", "date3": "2025-6", "date4": "2025-3",
    "consildated1": 1, "consildated2": 1, "consildated3": 1, "consildated4": 1
}

test_cf("nakit=true", {**params, "nakit": "true"})
test_cf("tablo=3", {**params, "tablo": 3})
test_cf("tablo_tipi=3", {**params, "tablo_tipi": 3})
test_cf("nakit_akim=true", {**params, "nakit_akim": "true"})
