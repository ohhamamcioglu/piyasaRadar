import midas_client
import json

client = midas_client.MidasClient()
fins = client.fetch_financial_statements("A1CAP")
if not fins:
    print("Failed")
else:
    print("--- BS ---")
    for item in fins.get("balance_sheet", []):
        print(f"{item['description']}")
            
    print("\n--- IS ---")
    for item in fins.get("income_statement", []):
        print(f"{item['description']}")
            
    print("\n--- CF ---")
    for item in fins.get("cash_flow_statement", []):
         print(f"{item['description']}")
