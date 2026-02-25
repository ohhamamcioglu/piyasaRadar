from bist_scanner import get_stock_data
import json

test_ticker = "THYAO"
print(f"Testing Pure Midas Data for: {test_ticker}")
data = get_stock_data(test_ticker)

if data:
    print("\n--- Succesfully Fetched Data ---")
    print(f"Name: {data.get('name')}")
    print(f"Sector: {data.get('sector')}")
    print(f"Price: {data.get('price')}")
    print(f"Master Score: {data.get('scores', {}).get('master_score')}")
    # print(json.dumps(data, indent=4, ensure_ascii=False))
else:
    print("\n--- Failed to Fetch Data ---")
