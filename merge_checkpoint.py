import json
import os

# Translation mapping from bist_scanner.py
MAPPING = {
    "pe_trailing": "fk_trailing",
    "pe_forward": "fk_forward",
    "peg_ratio": "peg",
    "pb_ratio": "pd_dd",
    "ev_ebitda": "fd_favok",
    "ev_revenue": "fd_satislar",
    "ps_ratio": "fiyat_satis",
    "roe": "ozkaynak_karliligi",
    "roa": "aktif_karlilik",
    "net_margin": "net_kar_marji",
    "operating_margin": "esas_faaliyet_marji",
    "gross_margin": "brut_kar_marji",
    "ebitda_margin": "favok_marji",
    "revenue_growth": "satis_buyumesi",
    "earnings_growth": "kar_buyumesi",
    "earnings_quarterly_growth": "ceyreklik_kar_buyumesi",
    "debt_to_equity": "borc_ozkaynak_orani",
    "current_ratio": "cari_oran",
    "quick_ratio": "asit_test_orani",
    "dividend_yield": "temettu_verimi",
    "payout_ratio": "dagitma_orani"
}

def translate_stock(stock):
    """Simple one-level translation for the main categories in the JSON."""
    new_stock = stock.copy()
    # Handle scores separately as they are often already translated or nested
    if "scores" in new_stock:
        # scores in checkpoint use English keys usually
        scores_map = {
            "piotroski_f_score": "piotroski_skoru",
            "altman_z_score": "altman_z_iflas_riski",
            "yasar_erdinc_score": "yasar_erdinc_potansiyel",
            "master_score": "master_skor",
            "real_growth": "reel_buyume_koruması",
            "export_influence": "ihracat_gucu",
            "kriz_kalkani": "kriz_kalkani", # Already TR
            "borfin_peg_score": "borfin_peg_score" # Already TR
        }
        new_scores = {}
        for k, v in new_stock["scores"].items():
            new_scores[scores_map.get(k, k)] = v
        new_stock["uzman_skorları"] = new_scores # match expected key in production
        del new_stock["scores"]
        
    return new_stock

def merge_checkpoint_to_production():
    checkpoint_file = "checkpoint_2026-03-14.json"
    production_file = "bist_all_data.json"
    
    if not os.path.exists(checkpoint_file):
        print("No checkpoint found.")
        return

    with open(checkpoint_file, 'r', encoding='utf-8') as f:
        checkpoint_data_full = json.load(f)
        checkpoint_stocks = checkpoint_data_full.get('data', [])
        
    with open(production_file, 'r', encoding='utf-8') as f:
        production_data_full = json.load(f)
        production_stocks = production_data_full.get('data', [])

    # The production stocks might have tickers in lowercase or TR keys
    # But usually 'ticker' is 'sembol' in Turkish or remains 'ticker'.
    # Let's check production keys first.
    if production_stocks:
        sample = production_stocks[0]
        ticker_key = "ticker" if "ticker" in sample else "sembol"
    else:
        ticker_key = "ticker"

    checkpoint_map = {s['ticker']: s for s in checkpoint_stocks}
    
    updated_count = 0
    for i, stock in enumerate(production_stocks):
        ticker = stock.get(ticker_key)
        if ticker in checkpoint_map:
            # For simplicity, we'll just replace the stock with a translated checkpoint version
            # though this might lose some fields if the checkpoint is incomplete.
            # But the scanner produces complete objects.
            production_stocks[i] = checkpoint_map[ticker]
            updated_count += 1
            
    production_data_full['data'] = production_stocks
    
    with open(production_file, 'w', encoding='utf-8') as f:
        json.dump(production_data_full, f, ensure_ascii=False, indent=4)
        
    print(f"✅ Merged {updated_count} hydrated stocks into production dataset.")

if __name__ == "__main__":
    merge_checkpoint_to_production()
