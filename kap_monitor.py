import requests
import time
import yfinance as yf
from xbrl_parser import parse_kap_html

KAP_API_URL = "https://www.kap.org.tr/tr/api/disclosure/list/main"
PROCESSED_DISCLOSURES = set()

def get_realtime_price(ticker):
    try:
        # Tickers on KAP are usually just codes, yfinance needs .IS for BIST
        yf_ticker = f"{ticker}.IS"
        stock = yf.Ticker(yf_ticker)
        return stock.fast_info['last_price']
    except Exception as e:
        print(f"Error fetching price for {ticker}: {e}")
        return None

def process_disclosure(disclosure):
    d_id = disclosure.get('disclosureIndex')
    ticker = disclosure.get('stockCodes')
    subject = disclosure.get('subject')
    publish_date = disclosure.get('publishDate')
    
    if not ticker:
        return None

    print(f"\n[NEW REPORT] {ticker} - {subject} (ID: {d_id})")
    
    # Fetch disclosure HTML
    url = f"https://www.kap.org.tr/tr/Bildirim/{d_id}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            print(f"Failed to fetch disclosure {d_id}")
            return None

        # Build basic return object
        result = {
            "disclosureIndex": d_id,
            "ticker": ticker,
            "subject": subject,
            "publishDate": publish_date,
            "url": url,
            "financials": None,
            "analysis": ""
        }

        # If it's a financial report (FR), try to parse detailed metrics
        if disclosure.get('disclosureClass') == 'FR':
            financials = parse_kap_html(resp.text)
            if financials:
                result["financials"] = financials
                # Simple Analysis Summary
                net_profit = financials.get('net_profit', 0)
                revenue = financials.get('revenue', 0)
                result["analysis"] = f"Net Kâr: {net_profit:,.0f} TL | Satışlar: {revenue:,.0f} TL"

        return result
    except Exception as e:
        print(f"Error processing disclosure {d_id}: {e}")
        return None

def monitor_kap(once=False):
    print("Monitoring KAP for new financial reports...")
    
    # Load history if exists
    history_file = "kap_history.json"
    latest_file = "latest_kap.json"
    
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            try:
                history = json.load(f)
                for item in history:
                    PROCESSED_DISCLOSURES.add(item.get('disclosureIndex'))
            except:
                history = []
    else:
        history = []

    while True:
        try:
            resp = requests.get(KAP_API_URL)
            if resp.status_code == 200:
                disclosures = resp.json()
                new_items = []
                for d in disclosures:
                    d_id = d.get('disclosureIndex')
                    # FR: Financial Report, ÖDA: Special Disclosure
                    is_important = d.get('disclosureClass') in ['FR', 'ÖDA']
                    if is_important and d_id not in PROCESSED_DISCLOSURES:
                        result = process_disclosure(d)
                        if result:
                            new_items.append(result)
                            history.insert(0, result) # Newest first
                        PROCESSED_DISCLOSURES.add(d_id)
                
                if new_items:
                    # Limit history to last 100 items
                    history = history[:100]
                    with open(history_file, 'w', encoding='utf-8') as f:
                        json.dump(history, f, ensure_ascii=False, indent=4)
                    
                    # Latest 5 for quick alert
                    with open(latest_file, 'w', encoding='utf-8') as f:
                        json.dump(history[:5], f, ensure_ascii=False, indent=4)
                    
                    # Update file index for frontend
                    try:
                        from shared_utils import update_file_list
                        update_file_list()
                    except Exception as e:
                        print(f"Error updating file index: {e}")
                    
                    print(f"Updated KAP snapshots with {len(new_items)} new items.")
            else:
                print(f"KAP API Error: {resp.status_code}")
        except Exception as e:
            print(f"Monitor error: {e}")
        
        if once: break
        time.sleep(60) # Poll every minute

if __name__ == "__main__":
    import os
    import json
    monitor_kap()
