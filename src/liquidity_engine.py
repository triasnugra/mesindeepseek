class LiquidityEngine:
    def __init__(self, df):
        self.df = df
    
    def detect_setup(self, level_high, level_low):
        signals = []
        if len(self.df) < 3: return signals
        
        # Cek 3 candle terakhir
        c3, c2, c1 = self.df.iloc[-3], self.df.iloc[-2], self.df.iloc[-1]
        
        # --- SETUP SHORT (Sweep High lalu Reclaim) ---
        # 1. Candle sebelumnya (c2) menyentuh/menembus level_high
        # 2. Candle saat ini (c1) close di BAWAH level_high (Reclaim)
        # 3. Level high harus valid
        if level_high and (c2['high'] > level_high or c3['high'] > level_high) and c1['close'] < level_high:
            signals.append({
                'type': 'SHORT',
                'setup': 'Sweep High + Reclaim (Deviation)',
                'entry_price': c1['close'],
                'invalidation': max(c2['high'], c3['high']), # SL di atas ekor sweep
                'reason': f'Price swept above {level_high:.4f} and reclaimed below it.'
            })
            
        # --- SETUP LONG (Sweep Low lalu Reclaim) ---
        # 1. Candle sebelumnya (c2) menyentuh/menembus level_low
        # 2. Candle saat ini (c1) close di ATAS level_low (Reclaim)
        elif level_low and (c2['low'] < level_low or c3['low'] < level_low) and c1['close'] > level_low:
            signals.append({
                'type': 'LONG',
                'setup': 'Sweep Low + Reclaim (Deviation)',
                'entry_price': c1['close'],
                'invalidation': min(c2['low'], c3['low']), # SL di bawah ekor sweep
                'reason': f'Price swept below {level_low:.4f} and reclaimed above it.'
            })
            
        return signals
