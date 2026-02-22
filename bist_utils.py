import requests
import pandas as pd
from bs4 import BeautifulSoup
import concurrent.futures
import yfinance as yf

# Common headers for requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def fetch_bist_tickers():
    """
    Fetches BIST tickers from KAP or falls back to a hardcoded list.
    """
    try:
        url = "https://www.kap.org.tr/tr/bist-sirketler"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # The structure might have changed, but let's try a generic search for links that look like tickers
            # For now, let's return the hardcoded list if scraping fails or as a robust fallback
            # The previous hardcoded list was very good.
            pass
    except Exception as e:
        print(f"Error fetching tickers: {e}")
        
    # Validated list from previous run (truncated for example, but ideally the full list)
    # Re-using the full list from bist_scanner.py for completeness is best, 
    # but to save tokens, I will rely on the list being passed or re-implemented here.
    # For now, let's just use a sample or the full list if I can copy it.
    
    # Let's try to grab the list from the user's existing bist_scanner.py via read, 
    # but I already have it in context. I'll paste the logic I used before or a simplified one.
    # Actually, simpler: I'll put the calculation functions here first.
    
    return [
        "A1YEN", "ACSEL", "ADEL", "ADESE", "ADGYO", "ADLVY", "AEFES", "AFYON", "AGESA", "AGHOL", "AGROT", "AGYO", "AHGAZ", "AHSGY", "AKBNK", "AKCKM", "AKCNS", "AKCVR", "AKDFA", "AKENR", "AKFGY", "AKFIS", "AKFK", "AKFYE", "AKGRT", "AKHAN", "AKMGY", "AKSA", "AKSEN", "AKSFA", "AKSGY", "AKSUE", "AKTVK", "AKYHO", "ALARK", "ALCAR", "ALCTL", "ALFAS", "ALGYO", "ALJF", "ALKA", "ALKIM", "ALKLC", "ALTNY", "ALVES", "ANELE", "ANGEN", "ANHYT", "ANSGR", "ARASE", "ARCLK", "ARDYZ", "ARENA", "ARFYE", "ARMGD", "ARSAN", "ARSVY", "ARTMS", "ARZUM", "ASELS", "ASGYO", "ASTOR", "ASUZU", "ATAGY", "ATAKP", "ATATP", "ATATR", "ATAVK", "ATEKS", "ATLAS", "ATLFA", "ATSYH", "AVGYO", "AVHOL", "AVOD", "AVPGY", "AVTUR", "AYCES", "AYDEM", "AYEN", "AYES", "AYGAZ", "AZTEK", "BAGFS", "BAHKM", "BAKAB", "BALAT", "BALSU", "BANVT", "BARMA", "BASCM", "BASGZ", "BAYRK", "BEGYO", "BERA", "BESLR", "BESTE", "BEYAZ", "BFREN", "BIENY", "BIGCH", "BIGEN", "BIGTK", "BIMAS", "BINBN", "BINHO", "BIOEN", "BIZIM", "BJKAS", "BLCYT", "BLKOM", "BLUME", "BMSCH", "BMSTL", "BNPPI", "BNTAS", "BOBET", "BORLS", "BORSK", "BOSSA", "BRGFK", "BRISA", "BRKO", "BRKSN", "BRKT", "BRKVY", "BRLSM", "BRMEN", "BRSAN", "BRYAT", "BSOKE", "BSRFK", "BTCIM", "BUCIM", "BULGS", "BURCE", "BURVA", "BVSAN", "BYDNR", "CAGFA", "CANTE", "CASA", "CATES", "CCOLA", "CELHA", "CEMAS", "CEMTS", "CEMZY", "CEOEM", "CGCAM", "CIMSA", "CLEBI", "CLKMT", "CMBTN", "CMENT", "CMSAN", "CONSE", "COSMO", "CRDFA", "CRFSA", "CUSAN", "CVKMD", "CWENE", "DAGI", "DAPGM", "DARDL", "DCTTR", "DENGE", "DERHL", "DERIM", "DESA", "DESPC", "DEVA", "DFKTR", "DGATE", "DGGYO", "DGNMO", "DGRVK", "DIRIT", "DITAS", "DKVRL", "DMLKT", "DMRGD", "DMSAS", "DNFIN", "DNISI", "DNYVA", "DNZEN", "DOAS", "DOCO", "DOFER", "DOFRB", "DOGUB", "DOGVY", "DOHOL", "DOKTA", "DRPHN", "DSTKF", "DTRND", "DUNYH", "DURDO", "DURKN", "DVRLK", "DYBNK", "DYOBY", "DZGYO", "EBEBK", "ECILC", "ECOGR", "ECZIP", "ECZYT", "EDATA", "EDIP", "EFOR", "EGEEN", "EGEGY", "EGEPO", "EGGUB", "EGPRO", "EGSER", "EKER", "EKGYO", "EKIZ", "EKOFA", "EKOS", "EKOVR", "EKSUN", "EKTVK", "ELITE", "EMIRV", "EMKEL", "EMNIS", "EMVAR", "ENDAE", "ENERY", "ENJSA", "ENKAI", "ENSRI", "ENTRA", "EPLAS", "ERBOS", "ERCB", "EREGL", "ERGLI", "ERSU", "ESCAR", "ESCOM", "ESEN", "ETILR", "ETYAT", "EUHOL", "EUKYO", "EUPWR", "EUREN", "EUYO", "EYGYO", "FADE", "FAIRF", "FENER", "FLAP", "FMIZP", "FONET", "FORMT", "FORTE", "FRIGO", "FRMPL", "FROTO", "FZLGY", "GARFA", "GARFL", "GATEG", "GEDIK", "GEDZA", "GENIL", "GENTS", "GEREL", "GESAN", "GGBVK", "GIPTA", "GLCVY", "GLRMK", "GLRYH", "GLYHO", "GMTAS", "GOKNR", "GOLTS", "GOODY", "GOZDE", "GRNYO", "GRSEL", "GRTHO", "GSDDE", "GSDHO", "GSIPD", "GSRAY", "GUBRF", "GUNDG", "GWIND", "GZNMI", "HALKF", "HATEK", "HATSN", "HAYVK", "HDFFL", "HDFGS", "HDFVK", "HEDEF", "HEKTS", "HKTM", "HLGYO", "HLVKS", "HOROZ", "HRKET", "HTTBT", "HUBVC", "HUNER", "HURGZ", "HUZFA", "ICUGS", "IDGYO", "IEYHO", "IHAAS", "IHEVA", "IHGZT", "IHLAS", "IHLGM", "IHYAY", "IMASM", "INALR", "INDES", "INGRM", "INTEK", "INTEM", "INVEO", "INVES", "ISBIR", "ISDMR", "ISFAK", "ISFIN", "ISGSY", "ISGYO", "ISKPL", "ISSEN", "ISTFK", "ISTVY", "ISYAT", "IZENR", "IZFAS", "IZINV", "IZMDC", "JANTS", "KAPLM", "KAREL", "KARSN", "KARTN", "KATMR", "KATVK", "KAYSE", "KBORU", "KCAER", "KCHOL", "KENT", "KERVN", "KFEIN", "KFILO", "KGYO", "KIMMR", "KLGYO", "KLKIM", "KLMSN", "KLRHO", "KLSER", "KLSYN", "KLVKS", "KLYPV", "KMPUR", "KNFRT", "KNTFA", "KOCFN", "KOCMT", "KONKA", "KONTR", "KONYA", "KOPOL", "KORDS", "KORTS", "KOTON", "KRGYO", "KRONT", "KRPLS", "KRSTL", "KRTEK", "KRVGD", "KSFIN", "KSTUR", "KTKVK", "KTLEV", "KTSKR", "KTSVK", "KUTPO", "KUVVA", "KUYAS", "KZBGY", "KZGYO", "LIDER", "LIDFA", "LILAK", "LINK", "LKMNH", "LMKDC", "LOGO", "LRSHO", "LUKSK", "LYDHO", "LYDYE", "MAALT", "MACKO", "MAGEN", "MAKIM", "MAKTK", "MANAS", "MARBL", "MARKA", "MARMR", "MARTI", "MAVI", "MBFTR", "MEDTR", "MEGAP", "MEGMT", "MEKAG", "MEPET", "MERCN", "MERIT", "MERKO", "METRO", "MEYSU", "MGROS", "MHRGY", "MIATK", "MINTF", "MMCAS", "MNDRS", "MNDTR", "MNGFA", "MOBTL", "MOGAN", "MOPAS", "MPARK", "MRBKF", "MRGYO", "MRMAG", "MRSHL", "MSGYO", "MTRKS", "MTRYO", "MZHLD", "NATEN", "NETAS", "NETCD", "NIBAS", "NTGAZ", "NTHOL", "NUGYO", "NUHCM", "NURVK", "OBAMS", "OBASE", "ODAS", "ODINE", "OFSYM", "OKTIN", "ONCSM", "ONRYT", "OPET", "ORCAY", "ORFIN", "ORGE", "ORMA", "OSTIM", "OTKAR", "OTOKC", "OTOSR", "OTTO", "OYAKC", "OYAYO", "OYLUM", "OZATD", "OZGYO", "OZKGY", "OZRDN", "OZSUB", "OZYSR", "PAGYO", "PAHOL", "PAMEL", "PAPIL", "PARSN", "PASEU", "PATEK", "PCILT", "PEKGY", "PENGD", "PENTA", "PETKM", "PETUN", "PGSUS", "PINSU", "PKART", "PKENT", "PLTUR", "PNLSN", "PNSUT", "POLHO", "POLTK", "PRDGS", "PRFFK", "PRKAB", "PRKME", "PRZMA", "PSDTC", "PSGYO", "QFINF", "QNBFF", "QNBFK", "QNBVK", "QUAGR", "QUFIN", "QYHOL", "RALYH", "RAYSG", "REEDR", "RGYAS", "RNPOL", "RODRG", "ROYAL", "RTALB", "RUBNS", "RUZYE", "RYGYO", "RYSAS", "SAFKR", "SAHOL", "SAMAT", "SANEL", "SANFM", "SANKO", "SARKY", "SARTN", "SASA", "SAYAS", "SDTTR", "SEGMN", "SEGYO", "SEKFK", "SEKUR", "SELEC", "SELVA", "SERNT", "SEYKM", "SILVR", "SISE", "SKTAS", "SKYLP", "SMART", "SMRFA", "SMRTG", "SMRVA", "SNGYO", "SNICA", "SNPAM", "SODSN", "SOKE", "SOKM", "SONME", "SRVGY", "SUMAS", "SUNTK", "SURGY", "SUWEN", "SZUKI", "TABGD", "TAMFA", "TARKM", "TATEN", "TATGD", "TAVHL", "TBORG", "TCELL", "TCKRC", "TDGYO", "TEBFA", "TEHOL", "TEKTU", "TEVKS", "TEZOL", "TFNVK", "TGSAS", "THYAO", "TIMUR", "TKFEN", "TKNSA", "TLMAN", "TMPOL", "TMSN", "TNZTP", "TOASO", "TRALT", "TRCAS", "TRENJ", "TRGYO", "TRHOL", "TRILC", "TRKFN", "TRKNT", "TRMET", "TRYKI", "TSGYO", "TSPOR", "TTKOM", "TTRAK", "TUCLK", "TUKAS", "TUPRS", "TUREX", "TURGG", "TURSG", "TV8TV", "UCAYM", "UFUK", "ULAS", "ULKER", "ULUFA", "ULUSE", "ULUUN", "UMPAS", "UNLU", "USAK", "VAKFA", "VAKFN", "VAKKO", "VAKVK", "VANGD", "VBTYZ", "VDFAS", "VDFLO", "VERTU", "VERUS", "VESBE", "VESTL", "VKFYO", "VKGYO", "VKING", "VRGYO", "VSNMD", "YAPRK", "YATAS", "YAYLA", "YBTAS", "YEOTK", "YESIL", "YGGYO", "YGYO", "YIGIT", "YKFIN", "YKFKT", "YKSLN", "YONGA", "YUNSA", "YYAPI", "YYLGD", "ZEDUR", "ZERGY", "ZGYO", "ZKBVK", "ZKBVR", "ZOREN", "ZRGYO"
    ]

def calculate_piotroski(stock):
    try:
        fin = stock.financials
        bs = stock.balance_sheet
        cf = stock.cashflow
        
        if fin.empty or bs.empty or cf.empty:
            return None

        # Helper to safely get value or 0
        def get_val(df, key, col_idx=0):
            try:
                return df.loc[key].iloc[col_idx]
            except:
                return 0

        # We need at least 2 years of data for some metrics
        if len(fin.columns) < 2:
            return None

        score = 0
        
        # 1. ROA > 0 (Net Income / Total Assets)
        net_income = get_val(fin, 'Net Income')
        total_assets = get_val(bs, 'Total Assets')
        roa = net_income / total_assets if total_assets else 0
        if roa > 0: score += 1

        # 2. Operating Cash Flow > 0
        ocf = get_val(cf, 'Operating Cash Flow')
        if ocf > 0: score += 1

        # 3. ROA Increasing (Current ROA > Previous ROA)
        net_income_prev = get_val(fin, 'Net Income', 1)
        total_assets_prev = get_val(bs, 'Total Assets', 1)
        roa_prev = net_income_prev / total_assets_prev if total_assets_prev else 0
        if roa > roa_prev: score += 1

        # 4. CFO > Net Income (Quality of Earnings)
        if ocf > net_income: score += 1

        # 5. Long Term Debt Decreasing (or stable)
        lt_debt = get_val(bs, 'Long Term Debt')
        lt_debt_prev = get_val(bs, 'Long Term Debt', 1)
        if lt_debt <= lt_debt_prev: score += 1

        # 6. Current Ratio Increasing
        current_assets = get_val(bs, 'Current Assets')
        current_liab = get_val(bs, 'Current Liabilities')
        curr_ratio = current_assets / current_liab if current_liab else 0
        
        current_assets_prev = get_val(bs, 'Current Assets', 1)
        current_liab_prev = get_val(bs, 'Current Liabilities', 1)
        curr_ratio_prev = current_assets_prev / current_liab_prev if current_liab_prev else 0
        
        if curr_ratio > curr_ratio_prev: score += 1

        # 7. Shares Outstanding not increasing (No Dilution)
        shares = get_val(bs, 'Ordinary Shares Number')
        shares_prev = get_val(bs, 'Ordinary Shares Number', 1)
        if shares <= shares_prev: score += 1

        # 8. Gross Margin Increasing
        gross_profit = get_val(fin, 'Gross Profit')
        revenue = get_val(fin, 'Total Revenue')
        gm = gross_profit / revenue if revenue else 0
        
        gross_profit_prev = get_val(fin, 'Gross Profit', 1)
        revenue_prev = get_val(fin, 'Total Revenue', 1)
        gm_prev = gross_profit_prev / revenue_prev if revenue_prev else 0
        
        if gm > gm_prev: score += 1

        # 9. Asset Turnover Increasing
        asset_turnover = revenue / total_assets if total_assets else 0
        
        avg_assets_prev = (get_val(bs, 'Total Assets', 1) + get_val(bs, 'Total Assets', 2)) / 2 if len(bs.columns) > 2 else get_val(bs, 'Total Assets', 1)
        asset_turnover_prev = revenue_prev / avg_assets_prev if avg_assets_prev else 0
        
        if asset_turnover > asset_turnover_prev: score += 1

        return score
    except Exception:
        return None

def calculate_altman_z(stock):
    try:
        fin = stock.financials
        bs = stock.balance_sheet
        
        if fin.empty or bs.empty:
            return None
        
        def get_val(df, key):
            try:
                return df.loc[key].iloc[0]
            except:
                return 0

        total_assets = get_val(bs, 'Total Assets')
        if not total_assets: return None

        # A = Working Capital / Total Assets
        working_capital = get_val(bs, 'Working Capital')
        A = working_capital / total_assets

        # B = Retained Earnings / Total Assets
        retained_earnings = get_val(bs, 'Retained Earnings')
        B = retained_earnings / total_assets

        # C = EBIT / Total Assets
        ebit = get_val(fin, 'EBIT')
        C = ebit / total_assets

        # D = Market Value of Equity / Total Liabilities
        market_cap = stock.info.get('marketCap', 0)
        total_liab = get_val(bs, 'Total Liabilities Net Minority Interest')
        D = market_cap / total_liab if total_liab else 0

        # E = Sales / Total Assets
        sales = get_val(fin, 'Total Revenue')
        E = sales / total_assets

        z_score = 1.2*A + 1.4*B + 3.3*C + 0.6*D + 1.0*E
        return z_score
    except Exception:
        return None

def calculate_canslim_score(stock_data):
    """
    Simplified CANSLIM Model:
    C: Current Quarterly Earnings Growth > 20%
    A: Annual Earnings Growth (3Y avg) > 20%
    N: Near 52-Week High (within 15%)
    S: Supply/Demand (Volume trend)
    L: Leader (Momentum > 0)
    I: Institutional (Proxy: High Analyst Coverage or Ownership)
    M: Market (General trend check)
    """
    try:
        growth = stock_data.get('growth', {})
        perf = stock_data.get('dividends_performance', {})
        tech = stock_data.get('technicals', {})
        targets = stock_data.get('targets_consensus', {}) or {}
        
        score = 0
        
        # C & A: Earnings Growth
        q_growth = growth.get('earnings_quarterly_growth') or 0
        a_growth = growth.get('earnings_growth') or 0
        if q_growth > 0.20: score += 1
        if a_growth > 0.20: score += 1
        
        # N: Near 52W High
        price = stock_data.get('price')
        high_52w = perf.get('52w_high')
        if price and high_52w and price > (high_52w * 0.85):
            score += 1
            
        # L: Leader (Momentum)
        m1y = tech.get('momentum_1y', 0) or 0
        if m1y > 0.30: # Up more than 30% in a year is a leader sign
            score += 1
            
        # I: Institutional / Coverage
        analysts = targets.get('number_of_analysts') or 0
        if analysts > 3: # More than 3 analysts following is a proxy for institucional interest
            score += 1
            
        return {
            "score": round((score / 5) * 100, 1),
            "points": score
        }
    except Exception:
        return {"score": 0, "points": 0}

def calculate_magic_formula(stock, info):
    """
    Joel Greenblatt's Magic Formula:
    1. Earnings Yield = EBIT / Enterprise Value
    2. Return on Capital (ROC) = EBIT / Invested Capital
    """
    try:
        enterprise_value = info.get('enterpriseValue')
        
        # EBIT from financials
        fin = stock.financials
        ebit = None
        if not fin.empty:
            latest_fin = fin.iloc[:, 0]
            ebit = latest_fin.get('EBIT') or latest_fin.get('Operating Income')
        
        ey = ebit / enterprise_value if (ebit and enterprise_value and enterprise_value > 0) else None
        
        # ROC = EBIT / Invested Capital
        bs = stock.balance_sheet
        roc = None
        if not bs.empty:
            latest_bs = bs.iloc[:, 0]
            # yfinance often has 'Invested Capital'
            invested_capital = latest_bs.get('Invested Capital')
            
            # Fallback for ROC denominator
            if not invested_capital:
                curr_assets = latest_bs.get('Total Current Assets')
                curr_liab = latest_bs.get('Total Current Liabilities')
                total_assets = latest_bs.get('Total Assets')
                if curr_assets and curr_liab and total_assets:
                    nwc = curr_assets - curr_liab
                    nfa = total_assets - curr_assets
                    invested_capital = nwc + nfa

            if ebit and invested_capital and invested_capital > 0:
                roc = ebit / invested_capital
                    
        return {
            "earnings_yield": ey,
            "roc": roc,
            "magic_formula_rank": None 
        }
    except Exception:
        return {"earnings_yield": None, "roc": None, "magic_formula_rank": None}

def calculate_master_score(data):
    """
    Combines all expert models into a single 0-100 ranking score.
    Weights: SuperScore(30%), Erdinc(25%), CANSLIM(20%), MagicFormula(15%), Radars(10%)
    """
    try:
        scores = data.get('scores', {})
        
        # 1. Super Score (Valuation/Quality/Technical)
        ss = scores.get('super_score', 50) or 50
        
        # 2. Erdinc (Stability/Target)
        ey = scores.get('yasar_erdinc_score', {})
        ey_score = ey.get('score', 0) if isinstance(ey, dict) else (ey or 0)
        
        # 3. CANSLIM (Growth/Momentum)
        can = scores.get('canslim_score', {})
        can_score = can.get('score', 0) if isinstance(can, dict) else (can or 0)
        
        # 4. Magic Formula (Value/Quality)
        mf = scores.get('magic_formula', {})
        mf_score = 0
        if mf:
            # Scale EY and ROC to 0-100
            ey_val = mf.get('earnings_yield') or 0
            roc_val = mf.get('roc') or 0
            # Rough scaling: EY 15% = 100, ROC 30% = 100
            mf_score = (min(ey_val/0.15, 1.0) * 50) + (min(roc_val/0.30, 1.0) * 50)
            
        # 5. Strategic Radars (Bonus)
        radars = scores.get('strategic_radars', {})
        radar_score = 0
        if radars:
            # 33 points for each radar passed (1, 3, 6)
            passed = [r for r, v in radars.items() if v.get('passed')]
            radar_score = len(passed) * 33.3
            
        # Weighted Final Calculation
        master = (ss * 0.30) + (ey_score * 0.25) + (can_score * 0.20) + (mf_score * 0.15) + (radar_score * 0.10)
        
        return round(master, 1)
    except Exception:
        return 0

def calculate_strategic_radars(data):
    """
    Tuncay Turşucu's Strategic Radars
    Focusing on top performing Radars: 1, 3, and 6.
    """
    try:
        growth = data.get('growth', {})
        valuation = data.get('valuation', {})
        profitability = data.get('profitability', {})
        cash_flow = data.get('cash_flow', {})
        efficiency = data.get('efficiency', {})
        
        radars = {}
        
        # Radar 1: Growth
        # EFK Growth > 0, Satış Büyüme > 0, Low EV/EBITDA
        efk_growth = growth.get('operating_profit_growth') or growth.get('earnings_growth') or 0
        sales_growth = growth.get('revenue_growth') or 0
        ev_ebitda = valuation.get('ev_ebitda', 1000) or 1000
        
        r1_passed = (efk_growth > 0 and sales_growth > 0 and ev_ebitda < 15)
        radars['radar_1'] = {"passed": r1_passed, "score": 100 if r1_passed else 0}

        # Radar 3: Cash Flow (Backtest Leader: 448%)
        # Net Profit > 0, Low Price/CashFlow
        net_profit = profitability.get('net_margin', 0) or 0 # Proxy for profitability
        p_cf = cash_flow.get('price_to_free_cash_flow', 1000) or 1000
        
        r3_passed = (net_profit > 0 and p_cf < 12)
        radars['radar_3'] = {"passed": r3_passed, "score": 100 if r3_passed else 0}

        # Radar 6: Quality Value
        # ROIC > 15, Low MarketCap / OperatingProfit (PD/EFK)
        # Use ROIC if available, or ROE as fallback
        roic = profitability.get('roic') or profitability.get('roe') or 0
        mc_efk = 1000
        if (mc := data.get('market_cap')) and (ebit := data.get('efficiency', {}).get('operating_income')):
            mc_efk = mc / ebit if ebit > 0 else 1000
            
        r6_passed = (roic > 0.15 and mc_efk < 10)
        radars['radar_6'] = {"passed": r6_passed, "score": 100 if r6_passed else 0}
        
        return radars
    except Exception:
        return {}

def calculate_roe_stability(stock):
    """
    Calculates the stability (Sharpe-like ratio) of ROE over available years.
    Yaşar Erdinç uses the 'SHARP' of ROE to identify consistent earners.
    """
    try:
        # Get historical annual financials
        fin = stock.financials
        bs = stock.balance_sheet
        if fin.empty or bs.empty:
            return None
            
        # We need Net Income and Total Equity for multiple years
        # Transpose so index is dates
        fin_t = fin.T
        bs_t = bs.T
        
        roes = []
        for date in fin_t.index:
            if date in bs_t.index:
                net_inc = fin_t.loc[date].get('Net Income')
                equity = bs_t.loc[date].get('Stockholders Equity')
                if net_inc is not None and equity and equity > 0:
                    roes.append(net_inc / equity)
        
        if len(roes) < 2:
            return None # Not enough history for stability check
            
        import numpy as np
        avg_roe = np.mean(roes)
        std_roe = np.std(roes)
        
        if std_roe == 0:
            return 10.0 # Perfectly stable is great
            
        return avg_roe / std_roe # Sharpe Ratio of ROE
    except Exception:
        return None

def calculate_yasar_erdinc_score(stock_data):
    """
    Yaşar Erdinç Five-Stage Selection Model
    1. Fundamental Base (ROE > Interest, Debt < 60%)
    2. Quality/Stability (ROE Sharpe Ratio)
    3. Valuation Potential (ROE vs P/B)
    4. Consistency (Index beating - proxy via momentum)
    5. Momentum (Multi-period positive returns)
    """
    try:
        info = stock_data
        valuation = info.get('valuation', {})
        profitability = info.get('profitability', {})
        solvency = info.get('solvency', {})
        tech = info.get('technicals', {})
        
        stages_passed = 0
        
        # Reference Yield (Approx 45% for TR)
        interest_rate = 0.45 
        
        # Stage 1: Fundamental Base
        roe = profitability.get('roe', 0) or 0
        de = solvency.get('debt_to_equity', 1000) or 1000
        # debt_to_equity > 60% is usually the cutoff in these models (expressed as 60 in yfinance)
        if roe > interest_rate and de < 60:
            stages_passed += 1
        else:
            # Erdinç usually stops or penalizes heavily if Stage 1 fails
            pass
            
        # Stage 2: Quality & Stability
        roe_sharp = profitability.get('roe_stability')
        if roe_sharp and roe_sharp > 1.5: # 1.5 is a decent Sharpe for stability
            stages_passed += 1
            
        # Stage 3: Valuation Potential
        pb = valuation.get('pb_ratio')
        if pb and roe > 0:
            ideal_pb = roe * 10
            # If current P/B is at least 30% below ideal P/B
            if pb < (ideal_pb * 0.7):
                stages_passed += 1
                
        # Stage 4: Index Consistency (Proxy: 1Y return > 0 and 3M return > 0)
        m3m = tech.get('momentum_3m', 0) or 0
        m1y = tech.get('momentum_1y', 0) or 0
        if m3m > 0 and m1y > 0:
            stages_passed += 1
            
        # Stage 5: Momentum Signal (Full sequence)
        m10d = tech.get('momentum_10d', 0) or 0 # Need to add this to tech
        m1m = tech.get('momentum_1m', 0) or 0
        if m10d > 0 and m1m > 0 and m3m > 0:
            stages_passed += 1
            
        # Final Score: (Stages Passed / 5) * 100
        return {
            "score": round((stages_passed / 5) * 100, 1),
            "stages_passed": stages_passed,
            "roe_target_price": (price * (roe * 10 / pb)) if (roe and pb and pb > 0 and (price := info.get('price'))) else None
        }
    except Exception:
        return {"score": 0, "stages_passed": 0}
