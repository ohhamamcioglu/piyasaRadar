import yfinance as yf
import pandas as pd
import json
import time
import concurrent.futures
import random
import os
from datetime import datetime
from us_backtest import run_us_backtest
from bist_utils import calculate_piotroski, calculate_altman_z, calculate_yasar_erdinc_score, calculate_roe_stability, calculate_magic_formula, calculate_canslim_score, calculate_strategic_radars, calculate_master_score
from us_utils import fetch_all_us_tickers

def calculate_graham_number(info):
    try:
        eps = info.get('trailingEps')
        book_value = info.get('bookValue')
        if eps and book_value and eps > 0 and book_value > 0:
            return (22.5 * eps * book_value) ** 0.5
        return None
    except:
        return None

def get_stock_data(ticker):
    try:
        # For US stocks, yfinance usually doesn't need a suffix, or maybe just ticker
        full_ticker = ticker 
        # Some might need cleanup, but Midas tickers usually pure (AAPL, TSLA)
        
        stock = yf.Ticker(full_ticker)
        info = stock.info
        
        tech_res, prices_res = calculate_technicals(stock) or (None, [])
        
        # Summary dict with all fundamental metrics
        data = {
            "ticker": ticker,
            "name": info.get('longName'),
            "sector": info.get('sector'),
            "industry": info.get('industry'),
            "price": info.get('currentPrice') or info.get('regularMarketPrice'),
            "market_cap": info.get('marketCap'),
            "currency": info.get('currency', 'USD'),
            
            "valuation": {
                "pe_trailing": info.get('trailingPE'),
                "pe_forward": info.get('forwardPE'),
                "peg_ratio": info.get('pegRatio'),
                "pb_ratio": info.get('priceToBook'),
                "ev_ebitda": info.get('enterpriseToEbitda'),
                "ev_revenue": info.get('enterpriseToRevenue'),
                "ps_ratio": info.get('priceToSalesTrailing12Months')
            },
            
            "profitability": {
                "roe": info.get('returnOnEquity'),
                "roa": info.get('returnOnAssets'),
                "net_margin": info.get('profitMargins'),
                "operating_margin": info.get('operatingMargins'),
                "gross_margin": info.get('grossMargins'),
                "ebitda_margin": info.get('ebitdaMargins'),
                "roe_stability": calculate_roe_stability(stock),
                "ceyreklik_kar_trendi": stock.quarterly_income_stmt.loc['Net Income'].tolist()[::-1] if not stock.quarterly_income_stmt.empty else []
            },
            
            "growth": {
                "revenue_growth": info.get('revenueGrowth'),
                "earnings_growth": info.get('earningsGrowth'),
                "earnings_quarterly_growth": info.get('earningsQuarterlyGrowth')
            },
            
            "solvency": {
                "debt_to_equity": info.get('debtToEquity'),
                "current_ratio": info.get('currentRatio'),
                "quick_ratio": info.get('quickRatio'),
                "interest_coverage": info.get('earningsBeforeInterestAndTaxes') / info.get('interestExpense') if info.get('interestExpense') else None
            },
            
            "dividends_performance": {
                "dividend_yield": info.get('dividendYield'),
                "payout_ratio": info.get('payoutRatio'),
                "beta": info.get('beta'),
                "52w_high": info.get('fiftyTwoWeekHigh'),
                "52w_low": info.get('fiftyTwoWeekLow')
            },

            "cash_flow": {
                "free_cash_flow": info.get('freeCashflow'),
                "operating_cash_flow": info.get('operatingCashflow'),
                "price_to_free_cash_flow": info.get('marketCap') / info.get('freeCashflow') if (info.get('marketCap') and info.get('freeCashflow')) else None
            },

            "targets_consensus": {
                "target_high": info.get('targetHighPrice'),
                "target_low": info.get('targetLowPrice'),
                "target_mean": info.get('targetMeanPrice'),
                "target_median": info.get('targetMedianPrice'),
                "recommendation": info.get('recommendationKey'),
                "number_of_analysts": info.get('numberOfAnalystOpinions')
            },

            "efficiency": {
                "revenue_per_employee": (info.get('totalRevenue') / info.get('fullTimeEmployees')) if (info.get('totalRevenue') and info.get('fullTimeEmployees')) else None,
                "revenue_per_share": info.get('revenuePerShare'),
                "asset_turnover": (info.get('totalRevenue') / info.get('totalAssets')) if (info.get('totalRevenue') and info.get('totalAssets')) else None,
                "operating_income": info.get('operatingIncome')
            },
            
            "scores": {
                "piotroski_f_score": calculate_piotroski(stock),
                "altman_z_score": calculate_altman_z(stock),
                "graham_number": calculate_graham_number(info),
                "yasar_erdinc_score": 0, # Placeholder
                "magic_formula": calculate_magic_formula(stock, info),
                "canslim_score": 0, # Placeholder
                "strategic_radars": {} # Placeholder
            },
            
            "technicals": tech_res,
            "fiyat_gecmisi": prices_res,
            "last_updated": datetime.now().isoformat()
        }
        
        # Now calculate the scores using the collected data
        data["scores"]["yasar_erdinc_score"] = calculate_yasar_erdinc_score(data)
        data["scores"]["canslim_score"] = calculate_canslim_score(data)
        data["scores"]["strategic_radars"] = calculate_strategic_radars(data)
        data["scores"]["master_score"] = calculate_master_score(data)
        
        return data
    except Exception as e:
        print(f"Error for {ticker}: {e}")
        return None

def calculate_technicals(stock):
    try:
        # Fetch 1 year of history for SMA200 and RSI
        hist = stock.history(period="1y")
        if hist.empty or len(hist) < 200:
            return None
        
        closes = hist['Close']
        current_price = closes.iloc[-1]
        
        # SMA
        sma_50 = closes.rolling(window=50).mean().iloc[-1]
        sma_200 = closes.rolling(window=200).mean().iloc[-1]
        
        # RSI (14)
        delta = closes.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi_14 = 100 - (100 / (1 + rs)).iloc[-1]
        
        # Momentum (Returns)
        # 10 Day (~7 trading days)
        ret_10d = (current_price / closes.iloc[-7] - 1) if len(closes) > 7 else None
        # 1 Month (~21 trading days)
        ret_1m = (current_price / closes.iloc[-21] - 1) if len(closes) > 21 else None
        # 3 Month (~63 trading days)
        ret_3m = (current_price / closes.iloc[-63] - 1) if len(closes) > 63 else None
        # 1 Year (~252 trading days)
        ret_1y = (current_price / closes.iloc[0] - 1)
        
        return {
            "sma_50": sma_50,
            "sma_200": sma_200,
            "rsi_14": rsi_14,
            "momentum_10d": ret_10d,
            "momentum_1m": ret_1m,
            "momentum_3m": ret_3m,
            "momentum_1y": ret_1y,
            "price_vs_sma200": (current_price / sma_200 - 1) if sma_200 else None
        }, closes.tolist()
    except Exception:
        return None, []


def calculate_relative_scores(results):
    # Group by sector
    sectors = {}
    for r in results:
        s = r.get('sector')
        if not s: continue
        if s not in sectors: sectors[s] = []
        sectors[s].append(r)
    
    # Calculate medians
    sector_medians = {}
    for s, items in sectors.items():
        # Filter Nones and handle non-numeric strings like 'Infinity'
        pes = pd.to_numeric(pd.Series([x['valuation']['pe_trailing'] for x in items]), errors='coerce')
        pes = pes[pes.notna()]
        
        pbs = pd.to_numeric(pd.Series([x['valuation']['pb_ratio'] for x in items]), errors='coerce')
        pbs = pbs[pbs.notna()]
        
        sector_medians[s] = {
            'median_pe': pes.median() if not pes.empty else None,
            'median_pb': pbs.median() if not pbs.empty else None,
        }
    
    # Apply to results and calc Super Score
    for r in results:
        s = r.get('sector')
        
        # Standardized Scoring (BIST 2025 Weights)
        score = 0
        weights = 0
            
        # 1. Piotroski F-Score (Weight: 25)
        pio = r.get('scores', {}).get('piotroski_f_score')
        if pio is not None:
            score += (pio / 9) * 25
            weights += 25
            
        # 2. Altman Z-Score (Weight: 20)
        z = r.get('scores', {}).get('altman_z_score')
        if z is not None:
            # Normalize: 3.0+ is safe (100%), 1.8- is distressed (0%)
            z_norm = min(1.0, max(0, (z - 1.8) / 1.2)) * 100
            score += (z_norm / 100) * 20
            weights += 20
            
        # 3. Valuation: P/E (Weight: 20)
        try:
            pe = float(r['valuation']['pe_trailing'])
        except (TypeError, ValueError):
            pe = None
            
        median_pe = sector_medians.get(s, {}).get('median_pe') if s else None
        
        if pe and pe > 0:
            # Score based on median or absolute
            target_pe = median_pe if median_pe else 20
            pe_score = max(0, min(100, (target_pe / pe) * 50)) # 50 if AT median, 100 if Half median
            score += (pe_score / 100) * 20
            weights += 20

        # 4. Profitability: ROE (Weight: 15)
        try:
            roe = float(r['profitability']['roe'])
        except (TypeError, ValueError):
            roe = None
            
        if roe is not None:
            # 20% ROE = 100 points
            roe_score = min(100, max(0, roe * 500))
            score += (roe_score / 100) * 15
            weights += 15
            
        # 5. Growth: Revenue Growth (Weight: 10)
        try:
            rev_growth = float(r['growth']['revenue_growth'])
        except (TypeError, ValueError):
            rev_growth = None
            
        if rev_growth is not None:
            # 50% growth = 100 points
            growth_score = min(100, max(0, rev_growth * 200))
            score += (growth_score / 100) * 10
            weights += 10
            
        # 6. Momentum (Weight: 10)
        tech = r.get('technicals')
        if tech and tech.get('rsi_14') is not None:
            rsi = tech['rsi_14']
            # Ideal RSI between 40-60
            mom_score = 100 - abs(50 - rsi) * 2
            score += (max(0, mom_score) / 100) * 10
            weights += 10
            
        # Final Normalization
        final_score = (score / weights) * 100 if weights > 0 else None
        
        if 'scores' not in r: r['scores'] = {}
        r['scores']['super_score'] = final_score
        r['relative_valuation'] = {
            'sector_median_pe': median_pe,
            'discount_premium_pe': ((pe - median_pe)/median_pe) if (pe and median_pe and median_pe > 0) else None
        }

    return results

def calculate_sector_rankings(results):
    # Group by sector
    sectors = {}
    for r in results:
        s = r.get('sector')
        if not s: continue
        if s not in sectors: sectors[s] = []
        sectors[s].append(r)
        
    for s, items in sectors.items():
        total = len(items)
        if total < 2: continue
        
        # P/E (Lower is better)
        items_pe = []
        for i in items:
            try:
                val = float(i['valuation'].get('pe_trailing'))
                items_pe.append((val, i))
            except (TypeError, ValueError):
                continue
        items_pe.sort(key=lambda x: x[0])
        items_pe = [x[1] for x in items_pe]
        
        for idx, item in enumerate(items_pe, 1):
            if 'rankings' not in item: item['rankings'] = {}
            item['rankings']['pe_rank'] = f"{idx}/{len(items)}"
            
        # Super Score (Higher is better)
        items_score = []
        for i in items:
            try:
                val = float(i.get('scores', {}).get('super_score'))
                items_score.append((val, i))
            except (TypeError, ValueError):
                continue
        items_score.sort(key=lambda x: x[0], reverse=True)
        items_score = [x[1] for x in items_score]
        
        for idx, item in enumerate(items_score, 1):
             if 'rankings' not in item: item['rankings'] = {}
             item['rankings']['super_score_rank'] = f"{idx}/{len(items)}"

    return results

def generate_ai_insight(data):
    try:
        ticker = data.get('ticker')
        sector = data.get('sector', 'Unknown Sector')
        
        # Scores
        scores = data.get('scores', {})
        super_score = scores.get('super_score')
        
        # Sub-dicts
        valuation = data.get('valuation', {})
        profitability = data.get('profitability', {})
        growth = data.get('growth', {})
        
        # Valuation
        val_rel = data.get('relative_valuation', {})
        discount = val_rel.get('discount_premium_pe')
        
        # Technicals
        tech = data.get('technicals') or {}
        rsi = tech.get('rsi_14')
        sma_diff = tech.get('price_vs_sma200')
        
        insight = []
        
        # 1. Valuation Insight
        if discount is not None:
            if discount < -0.30:
                insight.append(f"{ticker} is trading at a {abs(discount*100):.0f}% discount relative to its {sector} peers, suggesting potential undervaluation.")
            elif discount > 0.30:
                insight.append(f"{ticker} is trading at a {abs(discount*100):.0f}% premium compared to {sector} averages.")
            else:
                insight.append(f"{ticker} is fairly valued relative to its sector.")
        
        # 3. Technical & Momentum
        if rsi:
            if rsi > 70:
                insight.append(f"Technically, the stock is Overbought (RSI: {rsi:.0f}), indicating a potential pullback.")
            elif rsi < 30:
                insight.append(f"The stock is Oversold (RSI: {rsi:.0f}), which might trigger a rebound.")
            elif sma_diff and sma_diff > 0:
                 insight.append("Price is holding above the 200-day moving average, confirming a long-term uptrend.")

        # 4. Super Score Summary
        if super_score is not None:
            if super_score > 70:
                insight.append(f"Overall, {ticker} receives a **Strong Buy** rating with a Super Score of {super_score:.0f}/100.")
            elif super_score < 40:
                insight.append(f"The stock shows signs of weakness with a below-average score of {super_score:.0f}/100.")

        # 5. Expert Theory Evaluation (Yaşar Erdinç 5-Stage Funnel)
        ey_data = scores.get('yasar_erdinc_score', {})
        if isinstance(ey_data, dict):
            ey_score = ey_data.get('score', 0)
            stages = ey_data.get('stages_passed', 0)
            target = ey_data.get('roe_target_price')
            
            if stages >= 3:
                insight.append(f"Passed {stages}/5 stages in the Erdinç Selection Model (Score: {ey_score:.0f}/100).")
                if target and target > data.get('price', 0):
                    insight.append(f"Theoretical target price based on ROE model: {target:.2f} (Potential: +{((target/data.get('price'))-1)*100:.0f}%).")
        else:
            # Fallback
            ey_score = ey_data
            if ey_score and ey_score >= 70:
                insight.append(f"Strong fundamental efficiency based on Erdinç's ROE model ({ey_score:.0f}/100).")

        # 6. Joel Greenblatt's Magic Formula
        mf = scores.get('magic_formula', {})
        if mf:
            ey = mf.get('earnings_yield')
            roc = mf.get('roc')
            if ey and roc and ey > 0.10 and roc > 0.20:
                insight.append(f"Magic Formula Alert: High Earnings Yield (%{ey*100:.1f}) and high ROC (%{roc*100:.1f}), matching Joel Greenblatt's criteria.")

        # 7. CANSLIM Insight
        can = scores.get('canslim_score', {})
        if can and can.get('score', 0) >= 60:
            insight.append(f"CANSLIM Momentum: High growth potential detected with a score of {can.get('score', 0):.0f}/100.")

        # 8. Tuncay Turşucu's Strategic Radars
        radars = scores.get('strategic_radars', {})
        passed_list = [r.replace('radar_', 'Radar ') for r, v in radars.items() if v.get('passed')]
        if passed_list:
            insight.append(f"Strategic Signal: Matches Tuncay Turşucu's {', '.join(passed_list)} models.")
            if 'radar_3' in radars and radars['radar_3'].get('passed'):
                insight.append("Radar 3 (Cash Flow) match is particularly significant due to its high historical performance.")

        return " ".join(insight)
    except Exception as e:
        return f"AI Analysis failed: {str(e)}"

def scan_us_market():
    tickers = fetch_all_us_tickers()
    if not tickers:
        print("No tickers found.")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    checkpoint_file = f"us_checkpoint_{today}.json"
    
    # Resume Logic
    processed_tickers = set()
    stored_results = []
    
    if os.path.exists(checkpoint_file):
        print(f"Resuming from checkpoint: {checkpoint_file}")
        with open(checkpoint_file, "r", encoding="utf-8") as f:
            try:
                stored_data = json.load(f)
                stored_results = stored_data.get("data", [])
                processed_tickers = {item["ticker"] for item in stored_results}
                print(f"Loaded {len(stored_results)} stocks from checkpoint.")
            except:
                print("Checkpoint corrupted, starting over.")
    
    remaining_tickers = [t for t in tickers if t not in processed_tickers]
    
    results = list(stored_results)
    
    # Check if existing results are missing new scores (Force Update for those)
    tickers_to_update = []
    for r in list(stored_results):
        if 'scores' not in r or 'master_score' not in r['scores']:
            tickers_to_update.append(r['ticker'])
            # Remove from results to avoid duplicates
            results = [x for x in results if x['ticker'] != r['ticker']]

    remaining_tickers.extend(tickers_to_update)
    remaining_tickers = sorted(list(set(remaining_tickers)))
    
    print(f"Scanning {len(remaining_tickers)} US stocks (Including {len(tickers_to_update)} missing new scores)...")
    
    # STEALTH MODE
    count = 0
    for ticker in remaining_tickers:
        res = get_stock_data(ticker)
        if res:
            results.append(res)
        
        count += 1
        if count % 10 == 0:
            print(f"Progress: {len(results)}/{len(tickers)} (Checkpoint Saved)")
            with open(checkpoint_file, "w", encoding="utf-8") as f:
                json.dump({"data": results}, f, ensure_ascii=False)
                
        # Random Delay (0.5 - 1.5s)
        time.sleep(random.uniform(0.5, 1.5))

    # Post-process
    print("Calculating relative valuations and scores...")
    results = calculate_relative_scores(results)
    
    print("Calculating sector rankings...")
    results = calculate_sector_rankings(results)

    print("Generating AI Wall Street Insights...")
    for r in results:
        r['ai_insight'] = generate_ai_insight(r)

    # Note: Skipping full backtest integration inside scan to avoid rate limits on historical fetch
    # using hardcoded alpha from previous test for now or simple message
    
    historical_file = f"history/midas_data_{today}.json"
    
    import math

    # Sanitize results before saving to ensure valid JSON
    def sanitize_float(val):
        if isinstance(val, float):
            if math.isnan(val) or val == float('inf') or val == float('-inf'):
                return None
        return val

    def sanitize_data(data):
        if isinstance(data, dict):
            return {k: sanitize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [sanitize_data(i) for i in data]
        else:
            return sanitize_float(data)

    results = sanitize_data(results)

    # Fetch Macro Indicators for US Market
    print("Fetching US Macro Indicators (1Y History)...")
    macros = {}
    try:
        macro_tickers = {"SP500": "^GSPC", "Nasdaq": "^IXIC", "VIX": "^VIX"}
        for name, ticker in macro_tickers.items():
            hist = yf.Ticker(ticker).history(period="1y")
            if not hist.empty:
                macros[name] = sanitize_data(hist['Close'].tolist())
    except Exception as e:
        print(f"Error fetching macros: {e}")

    final_output = {
        "metadata": {
            "date": today,
            "scan_time": datetime.now().isoformat(),
            "market": "US (Midas/S&P 500)",
            "strategy_performance_estimate": {
                "alpha": 0.1433, # From our backtest
                "message": "Strategy Outperforms S&P 500 by ~14%"
            }
        },
        "macros": macros,
        "data": results
    }

    if not os.path.exists('history'):
        os.makedirs('history')

    with open(historical_file, "w", encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=4)
        print(f"Historical snapshot saved: {historical_file}")

    with open("midas_all_data.json", "w", encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=4)
        print(f"Latest data updated: midas_all_data.json")
    
    # Update file index for frontend
    try:
        from shared_utils import update_file_list
        update_file_list()
    except Exception as e:
        print(f"Error updating file index: {e}")
    
    print(f"Total US stocks processed: {len(results)}")

if __name__ == "__main__":
    scan_us_market()
