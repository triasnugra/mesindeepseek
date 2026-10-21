import yaml
from src.data_fetcher import DataFetcher
from src.signal_generator import SignalGenerator

def load_config():
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)

def main():
    config = load_config()
    fetcher = DataFetcher(config['exchange'])
    
    print("=== ELIZ-STYLE CRYPTO ANALYZER ===")
    print("Mengikuti Prinsip: Monday Range, Liquidity Sweep, Deviation, Reclaim\n")
    
    for symbol in config['symbols']:
        print(f"--- Analyzing {symbol} ---")
        
        # Ambil Data
        df_htf = fetcher.fetch_ohlcv(symbol, config['timeframes']['htf'], limit=200) # Weekly
        df_ltf = fetcher.fetch_ohlcv(symbol, config['timeframes']['ltf'], limit=200) # H4
        
        if df_htf is None or df_ltf is None:
            continue
            
        # Analisis
        analyzer = SignalGenerator(df_htf, df_ltf)
        result = analyzer.analyze()
        
        # Print Hasil
        if result['status'] == "NO TRADE":
            print(f"  Status: ⛔ NO TRADE")
            print(f"  Alasan: {result['reason']} (Sitting on hands is also a position)")
        
        elif result['status'] == "WAIT":
            print(f"  Status: ⏳ WAIT")
            print(f"  Alasan: {result['reason']}")
            if 'monday_range' in result:
                print(f"  Monday Range: High {result['monday_range']['high']} / Low {result['monday_range']['low']}")
        
        elif result['status'] == "SIGNAL FOUND":
            print(f"  Status: ✅ SETUP DITEMUKAN!")
            for sig in result['signals']:
                print(f"  Tipe: {sig['type']} | Setup: {sig['setup']}")
                print(f"  Entry: {sig['entry_price']}")
                print(f"  Invalidation (SL): {sig['invalidation']}")
                print(f"  Reason: {sig['reason']}")
                print(f"  *Ingat: Risk Management 1-2% per trade!*")
        print("\n")

if __name__ == "__main__":
    main()
