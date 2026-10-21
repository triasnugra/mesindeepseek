import ccxt
import pandas as pd

class DataFetcher:
    def __init__(self, exchange_id='binance'): # Anda bisa dengan aman kembali ke 'binance' sekarang
        self.exchange_id = exchange_id
        self.exchange_class = getattr(ccxt, exchange_id)
        
        # Daftar host fallback resmi untuk menghindari blokir IP GitHub Actions
        self.binance_hosts = [
            'data-api.binance.vision',
            'api1.binance.com',
            'api2.binance.com',
            'api3.binance.com',
            'api.binance.com' # Endpoint default
        ]
        
        # Inisialisasi awal exchange
        self.exchange = self._init_exchange()

    def _init_exchange(self, hostname=None):
        config = {
            'enableRateLimit': True, # Wajib agar tidak terkena rate limit
            'options': {
                'defaultType': 'spot',
            }
        }
        # Jika ada hostname khusus (digunakan saat fallback Binance), terapkan ke config
        if hostname:
            config['hostname'] = hostname
            
        return self.exchange_class(config)

    def fetch_ohlcv(self, symbol, timeframe, limit=500):
        # Logika Fallback otomatis jika exchange adalah Binance
        if self.exchange_id == 'binance':
            for host in self.binance_hosts:
                try:
                    # Ganti endpoint API ke host alternatif
                    self.exchange = self._init_exchange(hostname=host)
                    ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                    
                    if ohlcv:
                        return self._format_dataframe(ohlcv)
                        
                except Exception as e:
                    print(f"⚠️ [Fallback] Gagal fetch dari {host} untuk {symbol} - Mencoba endpoint lain...")
                    continue # Bypass error dan coba URL selanjutnya di dalam list
                    
            print(f"❌ Error: Seluruh endpoint Binance gagal/diblokir untuk {symbol}.")
            return None
            
        # Logika normal jika menggunakan exchange lain (misal: bybit)
        else:
            try:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                if not ohlcv:
                    return None
                return self._format_dataframe(ohlcv)
            except Exception as e:
                print(f"Error fetching {symbol} {timeframe} dari {self.exchange_id}: {e}")
                return None

    def _format_dataframe(self, ohlcv):
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
