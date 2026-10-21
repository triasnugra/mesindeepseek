import ccxt
import pandas as pd

class DataFetcher:
    def __init__(self, exchange_id='bybit'): # Ganti default ke bybit
        # Gunakan opsi tambahan agar tidak diblokir
        exchange_class = getattr(ccxt, exchange_id)
        self.exchange = exchange_class({
            'enableRateLimit': True, # Wajib agar tidak kena rate limit
            'options': {
                'defaultType': 'spot',
            }
        })
    
    def fetch_ohlcv(self, symbol, timeframe, limit=500):
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            if not ohlcv:
                return None
                
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            print(f"Error fetching {symbol} {timeframe}: {e}")
            return None
