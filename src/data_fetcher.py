import ccxt
import pandas as pd
import time

class DataFetcher:
    def __init__(self, exchange_id='gate'):  # <-- Ubah 'gateio' menjadi 'gate'
        exchange_class = getattr(ccxt, exchange_id)
        self.exchange = exchange_class({
            'enableRateLimit': True,
            'timeout': 30000,
            'options': {
                'defaultType': 'spot',
            }
        })
    
    def fetch_ohlcv(self, symbol, timeframe, limit=500, max_retries=3):
        for attempt in range(max_retries):
            try:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                if not ohlcv:
                    print(f"[{symbol}] Empty response from {self.exchange.id}")
                    return None
                    
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                print(f"[{symbol}] Successfully fetched {len(df)} candles from {self.exchange.id}")
                return df
            except ccxt.NetworkError as e:
                print(f"[{symbol}] Network error (attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return None
            except ccxt.ExchangeError as e:
                print(f"[{symbol}] Exchange error: {e}")
                return None
            except Exception as e:
                print(f"[{symbol}] Unexpected error: {e}")
                return None
        return None
