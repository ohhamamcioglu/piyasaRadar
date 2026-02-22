import requests
import json

url = "https://www.getmidas.com/wp-json/midas-api/v1/midas_stock_time"
headers = {"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"}

# Test codes found by subagent
codes = ["USDTRY", "EURTRY", "GAUTRY", "XU100", "A1CAP"]

for c in codes:
    params = {"code": c, "time": "1Y"}
    
    r = requests.get(url, headers=headers, params=params, timeout=10)
    print(f"\n--- Testing {c} (1 Year) ---")
    if r.status_code == 200:
        try:
            data = r.json()
            if isinstance(data, str): data = json.loads(data)
            
            if "data" in data and len(data["data"]) > 0:
                print(f"Success! Fetched {len(data['data'])} data points.")
                print(f"First data point: {data['data'][0]}")
                print(f"Last data point: {data['data'][-1]}")
            else:
                print("No data array found in response.")
                print(str(data)[:200])
        except Exception as e:
            print("Parse error:", e)
    else:
        print("HTTP Error:", r.status_code)

