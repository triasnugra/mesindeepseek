class LiquidityEngine:
    def __init__(self, df):
        self.df = df
    
    def detect_setup(self, level_high, level_low, rr_ratio=2.0):
        signals = []
        if len(self.df) < 3: return signals
        
        # Cek 3 candle terakhir
        c3, c2, c1 = self.df.iloc[-3], self.df.iloc[-2], self.df.iloc[-1]
        
        # --- SETUP SHORT (Sweep High lalu Reclaim) ---
        if level_high and (c2['high'] > level_high or c3['high'] > level_high) and c1['close'] < level_high:
            entry = c1['close']
            sl = max(c2['high'], c3['high'])
            risk = sl - entry
            tp = entry - (risk * rr_ratio) # Take Profit di bawah
            
            signals.append({
                'type': 'SHORT',
                'setup': 'Sweep High + Reclaim',
                'entry_price': entry,
                'invalidation': sl,
                'take_profit': tp,
                'reason': f'Swept above {level_high:.4f} and reclaimed below it.'
            })
            
        # --- SETUP LONG (Sweep Low lalu Reclaim) ---
        elif level_low and (c2['low'] < level_low or c3['low'] < level_low) and c1['close'] > level_low:
            entry = c1['close']
            sl = min(c2['low'], c3['low'])
            risk = entry - sl
            tp = entry + (risk * rr_ratio) # Take Profit di atas
            
            signals.append({
                'type': 'LONG',
                'setup': 'Sweep Low + Reclaim',
                'entry_price': entry,
                'invalidation': sl,
                'take_profit': tp,
                'reason': f'Swept below {level_low:.4f} and reclaimed above it.'
            })
            
        return signals
