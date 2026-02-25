import re

def map_sector(raw_sector):
    """
    Maps long descriptive sector strings or company descriptions to standard categorical sectors.
    Works for both BIST (Turkish) and US (English) inputs.
    """
    if not raw_sector or not isinstance(raw_sector, str):
        return "Diğer"
    
    s = raw_sector.lower()
    
    # Define mapping rules (Ordered by specificity)
    # Each tuple is (List of keywords to match, Standard Category Name)
    mappings = [
        # Finance
        (["banka", "bankacilik", "banking"], "Bankacılık"),
        (["sigorta", "reasürans", "insurance"], "Sigorta"),
        (["yatirim", "gyo", "reit", "holding", "finansal", "financial", "asset management", "portföy"], "Finans / Holding"),
        
        # Technology / Service
        (["yazilim", "teknoloji", "bilgisayar", "bilişim", "data", "software", "tech", "semiconductors", "it services"], "Teknoloji"),
        (["telekom", "haberleşme", "iletişim", "telecom"], "Telekomünikasyon"),
        (["ulaştirma", "havacilik", "havacılık", "havayolu", "lojistik", "airlines", "transport", "logistics", "shipping", "taşima", "taşıma", "hava yolu", "depolama"], "Ulaştırma / Lojistik"),
        (["perakende", "mağaza", "market", "ticaret", "retail", "consumer defensive", "e-commerce", "giyim perakende", "mağazacılık"], "Perakende / Ticaret"),
        (["sağlik", "hastane", "medikal", "healthcare", "biotechnology", "medical", "sağlık"], "Sağlık"),
        (["turizm", "otel", "konaklama", "seyahat", "travel", "leisure", "hotel"], "Turizm"),
        (["medya", "yayin", "gazete", "tv", "media", "entertainment", "social", "yayincilik", "yayıncılık"], "Medya"),
        
        # Energy / Utilities
        (["enerji", "elektrik", "solar", "yenilenebilir", "energy", "utilities", "oil", "gas", "electricity", "petrol", "akaryakit", "akaryakıt"], "Enerji / Altyapı"),
        
        # Industry / Manufacturing
        (["otomotiv", "yedek parça", "lastik", "traktör", "auto"], "Otomotiv"),
        (["demir", "çelik", "metal", "maden", "steel", "mining", "aluminum", "madencilik"], "Metal / Madencilik"),
        (["kimya", "boya", "plastik", "gübre", "ilaç", "chemical", "pharmaceutical", "petrokimya"], "Kimya / İlaç"),
        (["çimento", "seramik", "tuğla", "mermer", "inşaat", "construction", "cement", "building", "real estate", "mimarlik", "mimarlık"], "İnşaat / Çimento"),
        (["tekstil", "giyim", "deri", "konfeksiyon", "apparel", "luxury", "footwear", "iplik", "dokuma"], "Tekstil / Giyim"),
        (["dayanikli", "beyaz eşya", "ev aletleri", "home furnishing", "appliances", "mobilya"], "Dayanıklı Tüketim"),
        
        # Consumer / Agriculture
        (["gida", "içecek", "tarim", "hayvancilik", "un", "şeker", "et", "beverages", "food", "agriculture", "gıda", "tarım", "hayvancılık"], "Gıda / Tarım"),
    ]
    
    for keywords, category in mappings:
        for kw in keywords:
            if kw in s:
                return category
                
    return "Sanayi / Diğer"

def clean_numeric(val):
    if val is None:
        return 0.0
    try:
        if isinstance(val, (int, float)):
            return float(val)
        # Handle string formatting
        val = str(val).replace(',', '.').replace('%', '').replace('$', '').replace('₺', '').strip()
        # Handle multiple dots like 1.234.567.89
        if val.count('.') > 1:
            val = val.replace('.', '', val.count('.') - 1)
        return float(val)
    except:
        return 0.0

def hybrid_merge(dest, source):
    """
    Recursively merges source into dest. 
    Only overwrites if dest[k] is None but source[k] has a value.
    """
    for k, v in source.items():
        if k in dest:
            if isinstance(v, dict) and isinstance(dest[k], dict):
                hybrid_merge(dest[k], v)
            elif dest[k] is None or dest[k] == 0:
                dest[k] = v
        else:
            dest[k] = v
    return dest
