import requests

url = "https://www.getmidas.com/wp-json/midas-api/v1/midas_bilnaco_date"
base_params = {
    "code": "A1CAP",
    "date1": "2025-12", "date2": "2025-9", "date3": "2025-6", "date4": "2025-3",
    "consildated1": 1, "consildated2": 1, "consildated3": 1, "consildated4": 1
}
headers = {"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"}

# Test 1: No bilanco parameter
print("Test 1: No bilanco parameter")
r1 = requests.get(url, params=base_params, headers=headers).json()
if isinstance(r1, str): import json; r1 = json.loads(r1)
print(f"bilanco array length: {len(r1.get('bilanco', []))}")
if r1.get('bilanco'): print(f"First item: {r1['bilanco'][0][1]['description']}")

# Test 2: bilanco=false
base_params["bilanco"] = "false"
print("\nTest 2: bilanco=false")
r2 = requests.get(url, params=base_params, headers=headers).json()
if isinstance(r2, str): import json; r2 = json.loads(r2)
print(f"bilanco array length: {len(r2.get('bilanco', []))}")
if r2.get('bilanco'): print(f"First item: {r2['bilanco'][0][1]['description']}")

# Test 3: tablo=2
del base_params["bilanco"]
base_params["tablo"] = 2
print("\nTest 3: tablo=2")
r3 = requests.get(url, params=base_params, headers=headers).json()
if isinstance(r3, str): import json; r3 = json.loads(r3)
print(f"bilanco array length: {len(r3.get('bilanco', []))}")
if r3.get('bilanco'): print(f"First item: {r3['bilanco'][0][1]['description']}")

