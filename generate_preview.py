import json
import os
from datetime import datetime

def generate_preview():
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Files
    bist_cp = f"checkpoint_{today}.json"
    us_cp = f"us_checkpoint_{today}.json"
    
    # 1. BIST Preview
    if os.path.exists(bist_cp):
        try:
            with open(bist_cp, 'r', encoding='utf-8') as f:
                data = json.load(f)
                stocks = data.get('data', [])
                
            output = {
                "metadata": {
                    "date": today,
                    "scan_time": datetime.now().isoformat(),
                    "status": "PREVIEW (Scan in Progress)",
                    "count": len(stocks)
                },
                "data": stocks
            }
            
            with open("bist_preview.json", "w", encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=4)
            print(f"Generated bist_preview.json with {len(stocks)} stocks.")
        except Exception as e:
            print(f"Error generating BIST preview: {e}")
    else:
        print("No BIST checkpoint found.")

    # 2. US Preview
    if os.path.exists(us_cp):
        try:
            with open(us_cp, 'r', encoding='utf-8') as f:
                data = json.load(f)
                stocks = data.get('data', [])
                
            output = {
                "metadata": {
                    "date": today,
                    "scan_time": datetime.now().isoformat(),
                    "status": "PREVIEW (Scan in Progress)",
                    "count": len(stocks)
                },
                "data": stocks
            }
            
            with open("midas_preview.json", "w", encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=4)
            print(f"Generated midas_preview.json with {len(stocks)} stocks.")
        except Exception as e:
            print(f"Error generating US preview: {e}")
    else:
        print("No US checkpoint found yet (Scan just started/restarted).")

if __name__ == "__main__":
    generate_preview()
