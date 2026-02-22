import json
import os
from datetime import datetime

def manage_portfolio(data_file, portfolio_file='portfolio.json', top_n=10):
    """
    Ranks stocks by Master Score and suggests rebalancing relative to current portfolio.
    """
    if not os.path.exists(data_file):
        print(f"Error: Data file {data_file} not found.")
        return

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. Extract and Rank
    raw_data = data.get('data', data) # Handle both {data: [...]} and old {...} formats
    
    stocks = []
    # If it's a list (new format)
    if isinstance(raw_data, list):
        for item in raw_data:
            if isinstance(item, dict) and 'scores' in item:
                score = item['scores'].get('master_score') or 0
                stocks.append({
                    "ticker": item.get('ticker'),
                    "name": item.get('name', item.get('ticker')),
                    "score": score,
                    "price": item.get('price'),
                    "sector": item.get('sector')
                })
    # If it's a dict (old format)
    elif isinstance(raw_data, dict):
        for ticker, info in raw_data.items():
            if isinstance(info, dict) and 'scores' in info:
                score = info['scores'].get('master_score') or 0
                stocks.append({
                    "ticker": ticker,
                    "name": info.get('name', ticker),
                    "score": score,
                    "price": info.get('price'),
                    "sector": info.get('sector')
                })

    # Sort by Master Score descending
    stocks.sort(key=lambda x: x['score'], reverse=True)
    ideal_portfolio = stocks[:top_n]

    # 2. Load Current Portfolio
    current_portfolio = []
    if os.path.exists(portfolio_file):
        with open(portfolio_file, 'r', encoding='utf-8') as f:
            current_portfolio = json.load(f).get('holdings', [])

    current_tickers = {s['ticker'] for s in current_portfolio}
    ideal_tickers = {s['ticker'] for s in ideal_portfolio}

    # 3. Generate Rebalance Report
    to_sell = [t for t in current_tickers if t not in ideal_tickers]
    to_buy = [s for s in ideal_portfolio if s['ticker'] not in current_tickers]
    to_keep = [s for s in ideal_portfolio if s['ticker'] in current_tickers]

    print(f"\n=== PORTFOLIO REBALANCE REPORT ({datetime.now().strftime('%Y-%m-%d')}) ===")
    print(f"Strategy: Master Score Top {top_n}")
    
    if to_sell:
        print("\n[SELL] - Score dropped below Top 10:")
        for t in to_sell:
            print(f"  - {t}")
    else:
        print("\n[SELL] - No sales needed.")

    if to_buy:
        print("\n[BUY] - Entering Top 10 Leaders:")
        for s in to_buy:
            print(f"  - {s['ticker']} ({s['name']}) | Score: {s['score']}")
    else:
        print("\n[BUY] - portfolio is already optimal.")

    print("\n[HOLD] - Staying in Top 10:")
    for s in to_keep:
        print(f"  - {s['ticker']} | Score: {s['score']}")

    # 4. Update Portfolio File (Optional: only if user approves, but we'll save it as 'target_portfolio.json' for now)
    result = {
        "last_updated": datetime.now().isoformat(),
        "holdings": ideal_portfolio,
        "summary": {
            "avg_score": sum(s['score'] for s in ideal_portfolio) / top_n if top_n > 0 else 0,
            "sectors": {}
        }
    }
    
    # Calculate sector concentration
    for s in ideal_portfolio:
        sector = s.get('sector', 'Unknown')
        result['summary']['sectors'][sector] = result['summary']['sectors'].get(sector, 0) + 1

    with open(portfolio_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
        
    print(f"\nTarget portfolio saved to {portfolio_file}")

if __name__ == "__main__":
    # Process BIST Data
    print("\n--- PROCESSING BIST PORTFOLIO ---")
    manage_portfolio('bist_all_data.json', 'bist_portfolio.json')
    
    # Process US Data
    print("\n--- PROCESSING US PORTFOLIO ---")
    manage_portfolio('midas_all_data.json', 'us_portfolio.json')
