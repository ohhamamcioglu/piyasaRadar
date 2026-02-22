import json

def analyze_multibagger_dna(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f).get('data', [])

    winners = []
    others = []

    for stock in data:
        tech = stock.get('teknik_analiz', {})
        if not tech: continue
        
        m1y = tech.get('momentum_1y')
        if m1y is None: continue

        if m1y > 1.0: # >100% gain
            winners.append(stock)
        else:
            others.append(stock)

    if not winners:
        print("No winners found (>100% gain).")
        return

    winner_stats = []
    
    for s in winners:
        ticker = s.get('sembol')
        scores = s.get('uzman_skorları', {})
        val = s.get('degerleme', {})
        profit = s.get('karlılık', {})
        tech = s.get('teknik_analiz', {})
        m_val = tech.get('momentum_1y', 0)
        
        # DNA Markers (1 year ago):
        current_cap = s.get('piyasa_degeri') or 0
        # Estimate starting market cap: Current / (1 + Gain)
        start_cap = current_cap / (1 + m_val) if m_val > -1 else current_cap
        
        # Small Cap 1 year ago (< 1B TL)
        was_small_cap = start_cap < 1e9
        
        # Turnaround: Look at oldest available quarterly profit vs current
        trend = profit.get('ceyreklik_kar_trendi', [])
        is_turnaround = False
        oldest_profit = 0
        if len(trend) >= 4:
            oldest_profit = trend[0] if trend[0] is not None else 0
            newest_profit = trend[-1] if trend[-1] is not None else 0
            # Condition 1: Was losing money or barely profitable, now deep in profit
            if oldest_profit <= 0 and newest_profit > 0:
                is_turnaround = True
            # Condition 2: Devasa kâr artışı (EPS Explosion)
            elif newest_profit > oldest_profit * 3 and oldest_profit > 0:
                is_turnaround = True
        
        # High Quality check (Current but proxy for discipline)
        high_quality = (scores.get('master_skor') or 0) > 60
        
        winner_stats.append({
            'sembol': ticker,
            'momentum': m_val,
            'start_cap': start_cap,
            'was_small_cap': was_small_cap,
            'is_turnaround': is_turnaround,
            'high_quality': high_quality,
            'piotroski': scores.get('piotroski_skoru') or 0,
            'roe': profit.get('ozsermaye_karlılıgı') or 0,
            'oldest_p': oldest_profit
        })

    print(f"Total Stocks: {len(data)}")
    print(f"Winners (>100% Gain): {len(winners)}")
    print("-" * 30)

    avg_roe = sum(w['roe'] for w in winner_stats) / len(winner_stats)
    small_cap_pct = sum(1 for w in winner_stats if w['was_small_cap']) / len(winner_stats)
    turnaround_pct = sum(1 for w in winner_stats if w['is_turnaround']) / len(winner_stats)
    high_qual_pct = sum(1 for w in winner_stats if w['high_quality']) / len(winner_stats)
    avg_pio = sum(w['piotroski'] for w in winner_stats) / len(winner_stats)

    print("Winner DNA (State 1 Year Ago):")
    print(f"Average Current ROE: {avg_roe:.2%}")
    print(f"Was Small Cap (<1B TL) Percentage: {small_cap_pct:.2%}")
    print(f"Turnaround/Profit Explosion Factor: {turnaround_pct:.2%}")
    print(f"High Quality (Master > 60) Compliance: {high_qual_pct:.2%}")
    print(f"Average Current Piotroski: {avg_pio:.2f}")

    print("\nTop 15 Winner 'Flashback' Analysis:")
    sorted_winners = sorted(winner_stats, key=lambda x: x['momentum'], reverse=True)
    header = f"{'Ticker':<8} | {'Gain':<10} | {'Start Cap':<12} | {'Turnaround?':<12} | {'Pio':<4} | {'ROE':<8}"
    print(header)
    print("-" * len(header))
    for w in sorted_winners[:15]:
        cap_str = f"{w['start_cap']/1e6:>7.1f}M" if w['start_cap'] < 1e9 else f"{w['start_cap']/1e9:>7.1f}B"
        print(f"{w['sembol']:<8} | {w['momentum']*100:>8.1f}% | {cap_str:<12} | {str(w['is_turnaround']):<12} | {w['piotroski']:<4} | {w['roe']:>7.1%}")

if __name__ == "__main__":
    analyze_multibagger_dna('bist_all_data.json')
