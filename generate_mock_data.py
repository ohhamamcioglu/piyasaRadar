import json
from datetime import datetime

def generate_mock_data():
    today = datetime.now().strftime("%Y-%m-%d")
    
    mock_data = {
        "metadata": {
            "date": today,
            "scan_time": datetime.now().isoformat(),
            "strategy_performance_1y": {
                "return": 0.5170,
                "benchmark_return": 0.5128,
                "alpha": 0.0042,
                "message": "Strategy Beats Market (Cached Result)"
            },
            "note": "This is MOCK DATA for demonstration purposes due to API rate limits."
        },
        "data": [
            {
                "ticker": "THYAO",
                "name": "Turk Hava Yollari A.O.",
                "sector": "Industrials",
                "price": 310.50,
                "market_cap": 428000000000,
                "valuation": {
                    "pe_trailing": 3.45,
                    "pe_forward": 3.10,
                    "peg_ratio": 0.15,
                    "pb_ratio": 0.85,
                    "ev_ebitda": 2.10
                },
                "profitability": {
                    "roe": 0.35,
                    "net_margin": 0.18
                },
                "growth": {
                    "revenue_growth": 0.65,
                    "earnings_growth": 0.80
                },
                "solvency": {
                    "debt_to_equity": 0.80,
                    "current_ratio": 1.10
                },
                "dividends_performance": {
                    "dividend_yield": 0.0,
                    "beta": 1.10
                },
                "cash_flow": {
                    "free_cash_flow": 50000000000,
                    "price_to_free_cash_flow": 8.56
                },
                "targets_consensus": {
                    "target_mean": 450.00,
                    "recommendation": "buy"
                },
                "efficiency": {
                    "revenue_per_employee": 15000000
                },
                "scores": {
                    "piotroski_f_score": 8,
                    "altman_z_score": 2.5,
                    "super_score": 92.5
                },
                "technicals": {
                    "rsi_14": 45.5,
                    "sma_200": 280.00,
                    "price_vs_sma200": 0.108
                },
                "ai_insight": "THYAO, sektörüne göre %40 iskontolu ve güçlü finansal yapıya sahip (F-Score: 8/9). Teknik olarak yükseliş trendinde."
            },
            {
                "ticker": "EREGL",
                "name": "Eregli Demir ve Celik",
                "sector": "Basic Materials",
                "price": 55.20,
                "market_cap": 193000000000,
                "valuation": {
                    "pe_trailing": 8.20,
                    "pe_forward": 7.50,
                    "peg_ratio": 0.90,
                    "pb_ratio": 1.10,
                    "ev_ebitda": 5.40
                },
                "profitability": {
                    "roe": 0.14,
                    "net_margin": 0.10
                },
                "cash_flow": {
                    "free_cash_flow": 12000000000,
                    "price_to_free_cash_flow": 16.08
                },
                "scores": {
                    "piotroski_f_score": 6,
                    "super_score": 75.0
                },
                "technicals": {
                    "rsi_14": 65.0,
                    "sma_200": 48.00
                },
                "ai_insight": "EREGL, sektör ortalamalarıyla uyumlu. Temettü verimliliği ve nakit akışı güçlü."
            }
        ]
    }
    
    with open("mock_bist_data.json", "w", encoding='utf-8') as f:
        json.dump(mock_data, f, ensure_ascii=False, indent=4)
    print("Mock data generated: mock_bist_data.json")

if __name__ == "__main__":
    generate_mock_data()
