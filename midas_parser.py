def parse_financials(financials):
    """
    Takes the raw financials dictionary from midas_client.fetch_financial_statements
    and returns a standardized English dictionary for the expert valuation models.
    """
    if not financials:
        return None
        
    def find_value(statement_data, target_desc):
        for item in statement_data:
            desc = item.get("description", "").strip()
            # Try exact match first
            if desc.upper() == target_desc.upper():
                return item.get("value", 0)
        # Try partial match if exact fails
        for item in statement_data:
            desc = item.get("description", "").strip()
            if target_desc.upper() in desc.upper():
                return item.get("value", 0)
                
        return 0

    bs_periods = financials.get("balance_sheet", [])
    is_periods = financials.get("income_statement", [])
    cf_periods = financials.get("cash_flow_statement", [])

    # Find max periods available
    num_periods = max(len(bs_periods), len(is_periods), len(cf_periods))
    
    parsed_periods = []
    
    for i in range(num_periods):
        bs = bs_periods[i] if i < len(bs_periods) else []
        is_data = is_periods[i] if i < len(is_periods) else []
        cf = cf_periods[i] if i < len(cf_periods) else []
        
        parsed = {}
        
        # --- Balance Sheet (Bilanço) ---
        parsed["total_assets"] = find_value(bs, "TOPLAM VARLIKLAR")
        parsed["current_assets"] = find_value(bs, "DÖNEN VARLIKLAR")
        parsed["total_liabilities"] = find_value(bs, "TOPLAM YÜKÜMLÜLÜKLER")
        parsed["current_liabilities"] = find_value(bs, "KISA VADELİ YÜKÜMLÜLÜKLER")
        
        # Long Term Debt
        ltd = find_value(bs, "Uzun Vadeli Borçlanmalar")
        parsed["long_term_debt"] = ltd if ltd != 0 else find_value(bs, "UZUN VADELİ YÜKÜMLÜLÜKLER")
        
        # Equity
        equity = find_value(bs, "ANA ORTAKLIĞA AİT ÖZKAYNAKLAR")
        parsed["total_equity"] = equity if equity != 0 else find_value(bs, "Ö Z K A Y N A K L A R")
        
        # Retained Earnings
        parsed["retained_earnings"] = find_value(bs, "Geçmiş Yıllar Karları/Zararları")
        
        # --- Income Statement (Gelir Tablosu) ---
        parsed["revenue"] = find_value(is_data, "Hasılat")
        parsed["gross_profit"] = find_value(is_data, "Brüt Kar")
        parsed["operating_income"] = find_value(is_data, "Esas Faaliyet")
        
        # EBITDA Calculation: Operating Income + Depreciation (Amortisman)
        depreciation = find_value(cf, "Amortisman ve İtfa Giderleri İle İlgili Düzeltmeler")
        parsed["ebitda"] = parsed["operating_income"] + depreciation
        
        ni = find_value(is_data, "Net Dönem Kar")
        parsed["net_income"] = ni if ni != 0 else find_value(is_data, "Dönem Kar")
        
        # Margins (Standardized)
        parsed["gross_margin"] = (parsed["gross_profit"] / parsed["revenue"]) if parsed["revenue"] else 0
        parsed["operating_margin"] = (parsed["operating_income"] / parsed["revenue"]) if parsed["revenue"] else 0
        parsed["net_margin"] = (parsed["net_income"] / parsed["revenue"]) if parsed["revenue"] else 0
        parsed["ebitda_margin"] = (parsed["ebitda"] / parsed["revenue"]) if parsed["revenue"] else 0
        
        # --- Solvency ---
        parsed["current_ratio"] = (parsed["current_assets"] / parsed["current_liabilities"]) if parsed["current_liabilities"] else 0
        parsed["debt_to_equity"] = (parsed["total_liabilities"] / parsed["total_equity"]) if parsed["total_equity"] else 0

        # --- Cash Flow Statement (Nakit Akım) ---
        parsed["operating_cash_flow"] = find_value(cf, "İŞLETME FAALİYETLERİNDEN NAKİT AKIŞLARI")

        parsed_periods.append(parsed)

    # Calculate Growth (Sequential and Annual)
    for i in range(len(parsed_periods)):
        p = parsed_periods[i]
        # Sequential Growth (vs previous quarter reported)
        if i + 1 < len(parsed_periods):
            prev = parsed_periods[i+1]
            p["revenue_growth_qoq"] = (p["revenue"] / prev["revenue"] - 1) if prev["revenue"] else 0
            p["net_income_growth_qoq"] = (p["net_income"] / prev["net_income"] - 1) if prev["net_income"] else 0
        else:
            p["revenue_growth_qoq"] = 0
            p["net_income_growth_qoq"] = 0

        # Annual Growth (vs same quarter last year)
        if i + 4 < len(parsed_periods):
            p4 = parsed_periods[i+4]
            p["revenue_growth_yoy"] = (p["revenue"] / p4["revenue"] - 1) if p4["revenue"] else 0
            p["net_income_growth_yoy"] = (p["net_income"] / p4["net_income"] - 1) if p4["net_income"] else 0
        else:
            p["revenue_growth_yoy"] = 0
            p["net_income_growth_yoy"] = 0

    return parsed_periods

if __name__ == "__main__":
    import midas_client
    import json
    client = midas_client.MidasClient()
    fins = client.fetch_financial_statements("A1CAP")
    parsed = parse_financials(fins)
    print(json.dumps(parsed, indent=4, ensure_ascii=False))
