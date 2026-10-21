from .monday_range import MondayRange
from .liquidity_engine import LiquidityEngine
from .market_structure import MarketStructure

class SignalGenerator:
    def __init__(self, df_htf, df_ltf):
        self.df_htf = df_htf
        self.df_ltf = df_ltf
        
    def analyze(self):
        # 1. Hitung Monday Range
        mr = MondayRange(self.df_ltf)
        mr_high, mr_low = mr.calculate()
        
        # 2. Cek Struktur Pasar (Boxes)
        ms = MarketStructure(self.df_htf)
        support, resistance = ms.get_boxes()
        
        current_price = self.df_ltf.iloc[-1]['close']
        
        # 3. Cek No Trade Zone
        if ms.is_mid_range(current_price, support.iloc[-1], resistance.iloc[-1]):
            return {"status": "NO TRADE", "reason": "Price in middle of range (EliZ Rule)"}
            
        # 4. Cek Liquidity Sweep & Reclaim
        le = LiquidityEngine(self.df_ltf)
        
        # Kita cek sweep di area Monday Range dan Boxes
        signals = []
        if mr_high and mr_low:
            signals.extend(le.detect_sweep_and_reclaim(mr_high, mr_low))
            
        if not signals:
            return {"status": "WAIT", "reason": "No clear trigger (Sweep + Reclaim) found"}
            
        return {
            "status": "SIGNAL FOUND",
            "current_price": current_price,
            "monday_range": {"high": mr_high, "low": mr_low},
            "boxes": {"support": support.iloc[-1], "resistance": resistance.iloc[-1]},
            "signals": signals
        }
