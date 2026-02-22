import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

class MidasClient:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
        }
        self.base_url = "https://www.getmidas.com"

    def _parse_turkish_number(self, val_str):
        if not val_str or val_str.strip() == '-' or val_str.strip() == '':
            return None
        try:
            val_str = val_str.replace('+', '').replace('%', '').replace('₺', '').replace('$', '').strip()
            # In Turkey: 1.234.567,89 -> remove dots, replace comma with dot
            if ',' in val_str and '.' in val_str:
                val_str = val_str.replace('.', '').replace(',', '.')
            elif ',' in val_str:
                val_str = val_str.replace(',', '.')
            elif '.' in val_str and val_str.count('.') > 1:
                val_str = val_str.replace('.', '')
            return float(val_str)
        except ValueError:
            return None

    def fetch_static_fundamentals(self, ticker):
        """Fetches F/K, PD/DD, Market Cap, etc. from HTML DOM."""
        url = f"{self.base_url}/canli-borsa/{ticker.lower()}-hisse/"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                print(f"Failed to fetch {ticker} HTML: Status {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            data = {"ticker": ticker, "price": None}
            
            # Extract Data Blocks
            data_blocks = soup.select('.data')
            for block in data_blocks:
                title_elem = block.select_one('.title')
                val_elem = block.select_one('.val')
                if title_elem and val_elem:
                    title = title_elem.text.strip()
                    val = val_elem.text.strip()
                    
                    if "Son İşlem Fiyatı" in title: data['price'] = self._parse_turkish_number(val)
                    elif "F/K" in title: data['pe_trailing'] = self._parse_turkish_number(val)
                    elif "PD/DD" in title: data['pb_ratio'] = self._parse_turkish_number(val)
                    elif "Piyasa Değeri" in title: data['market_cap'] = self._parse_turkish_number(val)
                    elif "Halka Açıklık" in title: data['public_float'] = self._parse_turkish_number(val)
                    elif "Günlük Hacim (Lot)" in title: data['volume'] = self._parse_turkish_number(val)
                    elif "Temettü Verimi" in title: data['dividend_yield'] = self._parse_turkish_number(val)

            # Extract 5Y historical close prices from canvas data-val
            data['history_5y'] = []
            canvas_elem = soup.find('canvas', id='line-chart')
            if canvas_elem and canvas_elem.has_attr('data-val'):
                try:
                    data['history_5y'] = json.loads(canvas_elem['data-val'])
                except Exception as e:
                    print(f"Error parsing chart data: {e}")
            # Extract Company Profile Info
            data["profile"] = {}
            profile_selectors = {
                "CEO": "ceo",
                "Kuruluş Tarihi": "founded_date",
                "Halka Arz Tarihi": "ipo_date",
                "Sektör": "sector",
                "Çalışan Sayısı": "employees",
                "Merkez": "headquarters",
                "Adres": "address"
            }
            detail_lists = soup.select('.detail-list')
            for dl in detail_lists:
                t = dl.select_one('.title')
                v = dl.select_one('.val')
                if t and v:
                    tt = t.text.strip()
                    for tr_label, en_label in profile_selectors.items():
                        if tr_label == tt:
                            data["profile"][en_label] = v.text.strip()
            
            # Extract Shareholder Text (Ortaklık Yapısı / Hakkında)
            # Just grab the paragraph texts from the summary block to provide a general description
            about_section = soup.find('h2', string=lambda s: s and "Hakkında" in s)
            if about_section:
                desc_texts = []
                for sibling in about_section.find_next_siblings():
                    if sibling.name == 'p':
                        desc_texts.append(sibling.text.strip())
                    elif sibling.name in ['h2', 'div']:
                        break
                if desc_texts:
                    data["profile"]["description"] = " ".join(desc_texts)
            
            return data
            
        except Exception as e:
            print(f"Error fetching fundamental HTML for {ticker}: {e}")
            return None

    def fetch_historical_chart_data(self, code, time_period="1Y"):
        """
        Fetches historical price data from Midas hidden API.
        code: A1CAP, USDTRY, EURTRY, GAUTRY, XU100
        time_period: 1G, 1H, 1A, 3A, 1Y, 5Y
        """
        url = f"{self.base_url}/wp-json/midas-api/v1/midas_stock_time"
        params = {"code": code, "time": time_period}
        try:
            r = requests.get(url, headers=self.headers, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, str): data = json.loads(data)
                return data.get("data", [])
        except Exception as e:
            print(f"Error fetching historical chart data for {code}: {e}")
        return []

    def fetch_financial_statements(self, ticker):
        """Fetches Balance Sheet (Bilanço), Income Statement (Gelir Tablosu), and Cash Flow (Nakit)."""
        # First, dynamically get available periods for this stock
        html_url = f"{self.base_url}/canli-borsa/{ticker.lower()}-hisse/bilanco/"
        try:
            r = requests.get(html_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            selects = soup.find_all('select')
            periods = []
            for s in selects:
                opts = s.find_all('option')
                if len(opts) > 5:
                    # Filter out 'Konsolide Olmayan' if 'Konsolide Olan' exists, but for simplicity
                    # just collect unique prefixes like '2024-09'
                    raw_periods = [opt.get('value') for opt in opts if opt.get('value')]
                    # Maintain order (newest first usually) and uniqueness
                    seen = set()
                    for p in raw_periods:
                        if p not in seen:
                            seen.add(p)
                            periods.append(p)
                    break
        except Exception as e:
            print(f"Error fetching periods for {ticker}: {e}")
            periods = []
            
        if not periods:
            # Fallback
            periods = ["2024-12", "2024-9", "2024-6", "2024-3", "2023-12", "2023-9", "2023-6", "2023-3"]
            
        financials = {"balance_sheet": [], "income_statement": [], "cash_flow_statement": []}
        
        # We fetch up to 8 periods (in chunks of 4)
        for chunk_idx in range(0, min(8, len(periods)), 4):
            chunk = periods[chunk_idx:chunk_idx+4]
            # Pad chunk with None if < 4
            while len(chunk) < 4:
                chunk.append("2000-1")
                
            bs_url = f"{self.base_url}/wp-json/midas-api/v1/midas_bilnaco_date"
            params = {
                "code": ticker,
                "date1": chunk[0], "date2": chunk[1], "date3": chunk[2], "date4": chunk[3],
                "consildated1": 1, "consildated2": 1, "consildated3": 1, "consildated4": 1,
                "bilanco": "true"
            }
            
            headers = self.headers.copy()
            headers["Referer"] = html_url
            
            try:
                # Fetch Balance Sheet
                response = requests.get(bs_url, params=params, headers=headers, timeout=10)
                if response.status_code == 200:
                    raw_data = response.json()
                    data = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
                    if "bilanco" in data and data["bilanco"]:
                        financials["balance_sheet"].extend(data["bilanco"])

                # Income Statement & Cash Flow
                if "bilanco" in params:
                    del params["bilanco"]
                    
                response = requests.get(bs_url, params=params, headers=headers, timeout=10)
                if response.status_code == 200:
                    raw_data = response.json()
                    data = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
                    if "gelir-table" in data and data["gelir-table"]:
                         financials["income_statement"].extend(data["gelir-table"])
                    if "nakit" in data and data["nakit"]:
                         financials["cash_flow_statement"].extend(data["nakit"])

            except Exception as e:
                print(f"Error fetching chunk {chunk} for {ticker}: {e}")

        return financials

if __name__ == "__main__":
    client = MidasClient()
    
    print("Testing Fundamental Static HTML Extraction...")
    fund = client.fetch_static_fundamentals("A1CAP")
    print(json.dumps(fund, indent=4, ensure_ascii=False))
    
    print("\nTesting Financial JSON API Extraction...")
    fins = client.fetch_financial_statements("A1CAP")
    if fins and len(fins['balance_sheet']) > 0:
        latest_bs = fins['balance_sheet'][0]
        latest_is = fins['income_statement'][0]
        
        print(f"Found {len(fins['balance_sheet'])} periods. Latest period has {len(latest_bs)} Balance Sheet items. First 5:")
        for item in latest_bs[:5]:
            print(f"  - {item['description']}: {item['value']}")
            
        print(f"\nLatest period has {len(latest_is)} Income Statement items. First 5:")
        for item in latest_is[:5]:
            print(f"  - {item['description']}: {item['value']}")
