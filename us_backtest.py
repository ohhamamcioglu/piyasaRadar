import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from us_utils import fetch_sp500_tickers  # Import US ticker fetcher

# --- CONFIG ---
BENCHMARK = "^GSPC"  # S&P 500 Index
RISK_FREE_RATE = 0.04  # ~4% US Treasury Yield

def calculate_piotroski(stock_info, financials):
    """
    Simplified Piotroski F-Score (0-9) for US Market.
    Adapted to use limited history available in free API.
    """
    score = 0
    try:
        # 1. ROA > 0 (Profitability)
        net_income = financials.loc['Net Income'].iloc[0]
        total_assets = financials.loc['Total Assets'].iloc[0]
        roa = net_income / total_assets
        if roa > 0: score += 1
        
        # 2. Operating Cash Flow > 0
        ocf = stock_info.get('operatingCashflow', 0)
        if ocf and ocf > 0: score += 1
        
        # 3. ROA Increasing (Momentum) - Requires historical data, skipping for simple proxy
        
        # 4. Accruals (OCF > Net Income) - Quality
        if ocf and ocf > net_income: score += 1
        
        # ... (Simplified for backtest speed)
        # Adding dummy points for "Good Fundamentals" based on margins
        if stock_info.get('profitMargins', 0) > 0.10: score += 1 # High Margin
        if stock_info.get('debtToEquity', 100) < 1.0: score += 1 # Low Debt
        
    except:
        pass # Data missing
    
    return score 

def run_us_backtest(months=12):
    print(f"--- Starting US Market ({months} Months) Backtest ---")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months*30)
    
    # 1. Fetch S&P 500 Tickers
    tickers = fetch_sp500_tickers()
    # Limit to top 50 for quick validation (avoiding rate limits for now)
    # in production we would scan all 500
    tickers = tickers[:50] 
    print(f"Testing Strategy on {len(tickers)} S&P 500 Companies...")
    
    universe_scores = []
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            # Fetch minimal data for scoring (proxying past with current fundamentals for speed)
            info = stock.info
            hist = stock.history(period="1y") # Need price history for momentum
            
            if hist.empty: continue
            
            # --- STRATEGY SCORING ---
            
            # 1. Valuation (P/E)
            pe = info.get('trailingPE')
            if not pe or pe > 40: continue # Filter overvalued
            val_score = 100 / pe if pe > 0 else 0
            
            # 2. Momentum (Return vs SP500) - Calculated from price history
            price_ret_6m = (hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]
            mom_score = price_ret_6m * 100
            
            # 3. Quality (Margins)
            qual_score = (info.get('profitMargins', 0) * 100) + (info.get('returnOnEquity', 0) * 100)
            
            # SUPER SCORE
            final_score = (val_score * 0.4) + (qual_score * 0.3) + (mom_score * 0.3)
            
            universe_scores.append({
                'ticker': ticker,
                'super_score': final_score,
                'history': hist
            })
            
        except Exception as e:
            # print(f"Skip {ticker}: {e}")
            continue
            
    # Select Top 10 Stocks
    universe_scores.sort(key=lambda x: x['super_score'], reverse=True)
    top_10 = universe_scores[:10]
    
    print(f"\nTop 10 Picks for US Portfolio:")
    portfolio_return = 0
    for s in top_10:
        hist = s['history']
        # Calculate return over the period
        start_price = hist.iloc[0]['Close']
        end_price = hist.iloc[-1]['Close']
        ret = (end_price - start_price) / start_price
        portfolio_return += ret
        print(f"{s['ticker']}: Score {s['super_score']:.1f} | Return: {ret*100:.1f}%")
        
    if not top_10:
        print("No stocks selected.")
        return

    avg_portfolio_return = portfolio_return / len(top_10)
    
    # Benchmark Comparison (S&P 500)
    print("\nFetching Benchmark (^GSPC)...")
    bench = yf.Ticker(BENCHMARK)
    b_hist = bench.history(start=start_date, end=end_date)
    
    if b_hist.empty:
        b_return = 0.0
    else:
        b_return = (b_hist.iloc[-1]['Close'] - b_hist.iloc[0]['Close']) / b_hist.iloc[0]['Close']
    
    print(f"--- RESULTS ---")
    print(f"Strategy Return: {avg_portfolio_return*100:.2f}%")
    print(f"S&P 500 Return:  {b_return*100:.2f}%")
    print(f"ALPHA:           {(avg_portfolio_return - b_return)*100:.2f}%")

if __name__ == "__main__":
    run_us_backtest(12)
