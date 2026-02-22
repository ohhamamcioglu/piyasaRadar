import requests
import json

endpoints = [
    "midas_bilnaco_date",
    "midas_gelir_date",
    "midas_gelir_tablosu",
    "midas_income_statement",
    "midas_income_date",
    "midas_nakit_date"
]
base_params = {
    "code": "A1CAP",
    "date1": "2025-12", "date2": "2025-9", "date3": "2025-6", "date4": "2025-3",
    "consildated1": 1, "consildated2": 1, "consildated3": 1, "consildated4": 1
}
headers = {"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"}

for ep in endpoints:
    url = f"https://www.getmidas.com/wp-json/midas-api/v1/{ep}"
    try:
        r = requests.get(url, params=base_params, headers=headers)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, str): 
                try: data = json.loads(data)
                except: pass
            
            if isinstance(data, dict):
                keys = list(data.keys())
                if keys:
                    first_key = keys[0]
                    arr = data[first_key]
                    if arr and isinstance(arr, list) and len(arr) > 0 and isinstance(arr[0], list) and len(arr[0]) > 0:
                        first_item = arr[0][1]['description'] if len(arr[0]) > 1 else 'N/A'
                        print(f"SUCCESS: {ep} -> Key: {first_key}, Items: {len(arr[0])}, First: {first_item}")
                    else:
                        print(f"OK (empty): {ep} -> {keys}")
                else:
                    print(f"OK (no keys): {ep}")
            else:
                print(f"OK (not dict): {ep} -> {type(data)}")
        else:
            print(f"404: {ep}")
    except Exception as e:
        print(f"Error on {ep}: {e}")
