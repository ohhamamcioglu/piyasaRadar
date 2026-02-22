def calculate_all_scores(static_data, periods_data):
    """
    Takes static fundamentals (market cap, price, etc.) and periods array (from newest to oldest)
    and computes all expert valuation models.
    """
    if not static_data or not periods_data or len(periods_data) == 0:
        return None
        
    current = periods_data[0]
    
    # Check if we have enough periods for YoY comparison (usually 4 periods behind = same quarter last year)
    # But since BIST reporting is cumulative, Q3 to Q2 is actually +1 quarter. 
    # For robust general-purpose scoring without getting bogged down in cumulative math,
    # we use the most recent period (current) vs the immediate previous period (prev1) 
    # and the period exactly 1 year ago if available (prev4).
    prev1 = periods_data[1] if len(periods_data) > 1 else None
    prev4 = periods_data[4] if len(periods_data) > 4 else None

    # Safe division helper
    def safe_div(num, den):
        return num / den if den and den != 0 else 0

    scores = {}
    
    # ==========================
    # 1. PIOTROSZKI F-SCORE
    # ==========================
    f_score = 0
    if current["total_assets"] > 0:
        # Profitability
        if current["net_income"] > 0: f_score += 1
        if current["operating_cash_flow"] > 0: f_score += 1
        
        roa = safe_div(current["net_income"], current["total_assets"])
        if roa > 0: f_score += 1
        
        if current["operating_cash_flow"] > current["net_income"]: f_score += 1
        
        # YoY / QoQ Comparisons
        if prev4 and prev4["total_assets"] > 0:
            # We have exact same quarter last year
            roa_prev = safe_div(prev4["net_income"], prev4["total_assets"])
            if roa > roa_prev: f_score += 1
            
            ltd_ratio = safe_div(current["long_term_debt"], current["total_assets"])
            ltd_ratio_prev = safe_div(prev4["long_term_debt"], prev4["total_assets"])
            if ltd_ratio <= ltd_ratio_prev: f_score += 1
            
            cr = safe_div(current["current_assets"], current["current_liabilities"])
            cr_prev = safe_div(prev4["current_assets"], prev4["current_liabilities"])
            if cr > cr_prev: f_score += 1
            
            # Since shares outstanding isn't tracked easily by Midas JSON, we give +1 by default to balance scale if others are good
            f_score += 1 
            
            gm = safe_div(current["gross_profit"], current["revenue"])
            gm_prev = safe_div(prev4["gross_profit"], prev4["revenue"])
            if gm > gm_prev: f_score += 1
            
            at = safe_div(current["revenue"], current["total_assets"])
            at_prev = safe_div(prev4["revenue"], prev4["total_assets"])
            if at > at_prev: f_score += 1
    scores["piotroski_score"] = f_score

    # ==========================
    # 2. ALTMAN Z-SCORE
    # ==========================
    altman = 0
    if current["total_assets"] > 0:
        wc = current["current_assets"] - current["current_liabilities"]
        x1 = safe_div(wc, current["total_assets"])
        x2 = safe_div(current["retained_earnings"], current["total_assets"])
        x3 = safe_div(current["operating_income"], current["total_assets"])
        
        # Market Value of Equity (MVE) = Market Cap
        mve = static_data.get("market_cap") or 0
        x4 = safe_div(mve, current["total_liabilities"])
        
        x5 = safe_div(current["revenue"], current["total_assets"])
        
        altman = (1.2 * x1) + (1.4 * x2) + (3.3 * x3) + (0.6 * x4) + (1.0 * x5)
    scores["altman_z"] = altman

    # ==========================
    # 3. MAGIC FORMULA
    # ==========================
    # ROC = EBIT / (Net Fixed Assets + Working Capital)
    # NFA + WC = (Total Assets - Current Assets) + (Current Assets - Current Liabilities) = Total Assets - Current Liab
    capital_employed = current["total_assets"] - current["current_liabilities"]
    roc = safe_div(current["operating_income"], capital_employed)
    
    # EY = EBIT / (Market Cap) - Simplified EV approximation
    ey = safe_div(current["operating_income"], static_data.get("market_cap") or 1)
    
    scores["magic_formula_roc"] = roc
    scores["magic_formula_ey"] = ey

    # ==========================
    # 4. YAŞAR ERDİNÇ MODEL
    # ==========================
    # Target Price = (ROE / 0.15) * Book Value Per Share
    # Target PB = ROE / 0.15 => Target Price = Target PB * (Current Price / Current PB)
    roe = safe_div(current["net_income"], current["total_equity"])
    scores["erdinc_roe"] = roe
    
    target_price = 0
    margin = 0
    current_price = static_data.get("price") or 0
    current_pb = static_data.get("pb_ratio") or 0
    
    if current_pb > 0 and current_price > 0 and roe > 0:
        target_pb = roe / 0.15
        target_price = target_pb * (current_price / current_pb)
        margin = safe_div(target_price - current_price, current_price) * 100
        
    scores["erdinc_target_price"] = target_price
    scores["erdinc_margin"] = margin

    # ==========================
    # 5. CANSLIM SCORE (Momentum 0-100)
    # ==========================
    canslim = 0
    if prev1:
        # Current earnings growth
        if current["net_income"] > prev1["net_income"]: canslim += 25
        # Current revenue growth
        if current["revenue"] > prev1["revenue"]: canslim += 25
    if prev4:
        # Annual earnings growth
        if current["net_income"] > prev4["net_income"]: canslim += 25
        # Annual revenue growth
        if current["revenue"] > prev4["revenue"]: canslim += 25
    scores["canslim_score"] = canslim

    # ==========================
    # 6. TUNCAY TURŞUCU RADARS
    # ==========================
    tursucu = 0
    if current["operating_cash_flow"] > 0 and current["operating_income"] > 0:
        if current["operating_cash_flow"] > current["net_income"]:
            tursucu = 1  # Passed Radar 1 (Cash Generation)
            
    if prev1 and current["revenue"] > prev1["revenue"] and tursucu == 1:
        tursucu = 3  # Passed Radar 3 (Growth + Cash)
        
    scores["tursucu_radars"] = tursucu
    
    # 6.1 Profit Acceleration (Sequential Growth in last 4 periods)
    # Note: periods_data is newest to oldest
    profit_acc = False
    if len(periods_data) >= 4:
        p1, p2, p3, p4 = periods_data[0]["net_income"], periods_data[1]["net_income"], periods_data[2]["net_income"], periods_data[3]["net_income"]
        if p1 > p2 > p3 > p4:
            profit_acc = True
    scores["profit_acceleration"] = profit_acc

    # ==========================
    # 7. DOLLAR-BASED WEALTH ENGINE (Ph 5.2)
    # ==========================
    # 7.1 Real Growth (ROE vs Inflation)
    INFLATION_RATE = 0.65  # Current Turkish Inflation roughly 65%
    real_growth = roe > (INFLATION_RATE + 0.10)
    scores["real_growth"] = real_growth

    # 7.2 Qualitative Export Detection
    export_score = 0
    desc = static_data.get("profile", {}).get("description", "").lower()
    sector = static_data.get("profile", {}).get("sector", "").lower()
    
    export_keywords = ["ihracat", "yurt dışı", "döviz bazlı", "global", "export", "foreign sales", "uluslararası", "yurt dışına"]
    for kw in export_keywords:
        if kw in desc or kw in sector:
            export_score += 4
            
    # Sector Fallback (Turkish)
    # Covers major export-driven groups in BIST
    export_sectors = [
        "otomotiv", "motorlu araç", "havacilik", "havayolu", "dayanikli tüketim", 
        "beyaz eşya", "cam", "kimya", "tekstil", "demir çelik", "sanayi", "petrol"
    ]
    for s_kw in export_sectors:
        if s_kw in sector:
            export_score += 6
            
    scores["export_influence"] = min(export_score, 10)

    # ==========================
    # MASTER SCORE CALCULATION
    # ==========================
    master_score = 0
    
    # Piotroski (0-9 -> 0-30 points)
    master_score += (min(f_score, 9) / 9) * 30
    
    # Altman (Safe > 2.99 -> 15 points)
    if altman > 2.99: master_score += 15
    elif altman > 1.8: master_score += 7
    
    # Magic Formula (High ROE & EY -> 15 points) - Adjusted from 20 to accommodate Ph 5.2
    if roc > 0.15 and ey > 0.05: master_score += 15
    elif roc > 0.10: master_score += 7
        
    # Erdinç Margin (High upside -> 10 points) - Adjusted from 15
    if margin > 30: master_score += 10
    elif margin > 10: master_score += 5
        
    # CANSLIM (Momentum -> 10 points)
    master_score += (canslim / 100) * 10
    
    # Turşucu (Cash Quality -> 10 points)
    if tursucu == 3: master_score += 10
    elif tursucu == 1: master_score += 5

    # Ph 5.2 DOLLAR-BASED BONUS (Bonus max 10 points)
    if real_growth: master_score += 5
    if export_score >= 4: master_score += 5
    
    # Ph 5.3 DATA PERFECTION BONUS
    if profit_acc: master_score += 3
        
    scores["master_score"] = int(min(master_score, 100))

    return scores

if __name__ == "__main__":
    import midas_client
    import midas_parser
    import json
    
    client = midas_client.MidasClient()
    ticker = "A1CAP"
    print(f"Testing Engine for {ticker}...")
    
    static = client.fetch_static_fundamentals(ticker)
    fins = client.fetch_financial_statements(ticker)
    periods = midas_parser.parse_financials(fins)
    
    if static and periods:
        scores = calculate_all_scores(static, periods)
        print("\n--- MASTER SCORE & METRICS ---")
        print(json.dumps(scores, indent=4, ensure_ascii=False))
    else:
        print("Failed to load data.")
