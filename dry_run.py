import bist_scanner
import json

bist_scanner.fetch_bist_tickers = lambda: ["A1CAP", "AKBNK", "THYAO", "BIMAS", "FROTO"]

if __name__ == "__main__":
    print("Starting Dry Run...")
    bist_scanner.main() # Wait, what is the main function in bist_scanner?
    # Actually, let's just run it as a normal script but edit the file.
