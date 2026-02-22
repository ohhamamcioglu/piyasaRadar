from bs4 import BeautifulSoup
import re

def parse_kap_html(html_content):
    """
    Parses critical financial data from KAP disclosure HTML content.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    results = {}

    tags_to_find = {
        'revenue': [r'Hasılat', r'Satış Gelirleri', r'Revenue'],
        'net_profit': [r'Net Dönem (Kârı|Zararı)', r'Net Profit', r'NetProfitLoss', r'Dönem Net Kârı'],
        'equity': [r'Özkaynaklar', r'Özsermaye', r'Equity', r'Toplam Özkaynaklar'],
        'ebitda': [r'FAVÖK', r'EBITDA'],
        'total_assets': [r'Toplam Varlıklar', r'Total Assets', r'TotalAssets', r'Varlıklar Toplamı']
    }

    # First, find ALL tables and their rows to identify value columns
    # We look for rows that have labels and numeric-looking cells
    
    def clean_val(text):
        if not text: return 0.0
        # KAP uses . for thousands and , for decimals, OR just . for thousands
        # Example: "1.234.567" or "1.234,56"
        t = text.strip().replace('(', '-').replace(')', '').replace(' ', '')
        if not t or t in ['-', '.']: return 0.0
        
        # If there's a comma, it's likely the decimal separator
        if ',' in t:
            t = t.replace('.', '').replace(',', '.')
        else:
            # If no comma, dots are likely thousand separators
            t = t.replace('.', '')
        
        try:
            return float(t)
        except ValueError:
            return 0.0

    # Search for labels in rows and extract from subsequent cells
    for key, patterns in tags_to_find.items():
        found = False
        for row in soup.find_all('tr'):
            cells = row.find_all(['td', 'th'])
            if not cells: continue
            
            label_cell = cells[0].get_text(strip=True)
            for pattern in patterns:
                if re.search(pattern, label_cell, re.IGNORECASE):
                    # Found a row that matches the pattern
                    # Now extract values from subsequent cells (usually col 1 is current, col 2 is previous)
                    vals = []
                    for cell in cells[1:]:
                        val = clean_val(cell.get_text(strip=True))
                        if val != 0.0:
                            vals.append(val)
                    
                    if vals:
                        results[key] = vals[0]
                        if len(vals) > 1:
                            results[f"{key}_prev"] = vals[1]
                        found = True
                        break
            if found: break

    return results

if __name__ == "__main__":
    import requests
    # Test with the sample ID from before
    url = "https://www.kap.org.tr/tr/Bildirim/1558047"
    response = requests.get(url)
    data = parse_kap_html(response.text)
    print("Extracted Data:", data)
