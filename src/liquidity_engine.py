import pandas as pd
import numpy as np

class LiquidityEngine:
    def __init__(self, df):
        self.df = df
    
    def detect_sweep_and_reclaim(self, level_high, level_low, lookback=5):
        """
        Mendeteksi setup EliZ:
        1. Harga menembus level (Sweep/Deviation)
        2. Harga kembali masuk ke dalam range (Reclaim)
        """
        signals = []
        
        for i in range(lookback, len(self.df)):
            current = self.df.iloc[i]
            prev = self.df.iloc[i-lookback:i]
            
            # --- SETUP SHORT (Sweep High lalu Reclaim) ---
            # Cek apakah ada candle yang high-nya menembus level_high
            swept_high = prev['high'].max() > level_high
            # Cek apakah harga saat ini sudah kembali di bawah level_high (Reclaim)
            reclaimed_high = current['close'] < level_high
            
            if swept_high and reclaimed_high:
                signals.append({
                    'timestamp': current.name,
                    'type': 'SHORT',
                    'setup': 'Sweep High + Reclaim',
                    'entry_price': current['close'],
                    'invalidation': prev['high'].max(), # Stop loss di atas sweep
                    'reason': f'Swept {level_high} and reclaimed'
                })
            
            # --- SETUP LONG (Sweep Low lalu Reclaim) ---
            # Cek apakah ada candle yang low-nya menembus level_low
            swept_low = prev['low'].min() < level_low
            # Cek apakah harga saat ini sudah kembali di atas level_low (Reclaim)
            reclaimed_low = current['close'] > level_low
            
            if swept_low and reclaimed_low:
                signals.append({
                    'timestamp': current.name,
                    'type': 'LONG',
                    'setup': 'Sweep Low + Reclaim',
                    'entry_price': current['close'],
                    'invalidation': prev['low'].min(), # Stop loss di bawah sweep
                    'reason': f'Swept {level_low} and reclaimed'
                })
                
        return signals
