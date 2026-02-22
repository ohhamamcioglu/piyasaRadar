import json
import os
from datetime import datetime

# Import post-processing functions
from us_scanner import calculate_relative_scores as us_rel_scores, calculate_sector_rankings as us_rankings, generate_ai_insight as us_ai
from bist_scanner import calculate_relative_scores as bist_rel_scores, calculate_sector_rankings as bist_rankings, generate_ai_insight as bist_ai

def force_history_update():
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 1. BIST Update
    if os.path.exists(f"checkpoint_{today}.json"):
        print("Processing BIST Checklist...")
        try:
            with open(f"checkpoint_{today}.json", 'r', encoding='utf-8') as f:
                data = json.load(f).get('data', [])
            
            # Post-Process
            data = bist_rel_scores(data)
            data = bist_rankings(data)
            for r in data:
                r['ai_insight'] = bist_ai(r)
                
            # Sanitize results before saving to ensure valid JSON
            def sanitize_float(val):
                if isinstance(val, float):
                    if val != val: # NaN check
                        return None
                    if val == float('inf') or val == float('-inf'):
                        return None
                return val

            def sanitize_data(data):
                if isinstance(data, dict):
                    return {k: sanitize_data(v) for k, v in data.items()}
                elif isinstance(data, list):
                    return [sanitize_data(i) for i in data]
                else:
                    return sanitize_float(data)

            data = sanitize_data(data)

            output = {
                "metadata": {
                    "date": today,
                    "scan_time": datetime.now().isoformat(),
                    "status": "PARTIAL_SCAN_FORCE_UPDATE",
                    "market": "BIST"
                },
                "data": data
            }
            
            fname = f"history/bist_data_{today}.json"
            with open(fname, "w", encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=4)
            print(f"Saved {fname} with {len(data)} stocks.")
            
        except Exception as e:
            print(f"BIST Update Failed: {e}")

    # 2. US Update
    if os.path.exists(f"us_checkpoint_{today}.json"):
        print("Processing US Checklist...")
        try:
            with open(f"us_checkpoint_{today}.json", 'r', encoding='utf-8') as f:
                data = json.load(f).get('data', [])
            
            # Post-Process
            data = us_rel_scores(data)
            data = us_rankings(data)
            for r in data:
                r['ai_insight'] = us_ai(r)
                
            data = sanitize_data(data)

            output = {
                "metadata": {
                    "date": today,
                    "scan_time": datetime.now().isoformat(),
                    "status": "PARTIAL_SCAN_FORCE_UPDATE",
                    "market": "US"
                },
                "data": data
            }
            
            fname = f"history/midas_data_{today}.json"
            with open(fname, "w", encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=4)
            print(f"Saved {fname} with {len(data)} stocks.")
            
        except Exception as e:
            print(f"US Update Failed: {e}")
    else:
        print("US Checkpoint not ready yet.")

if __name__ == "__main__":
    force_history_update()
