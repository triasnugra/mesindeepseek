import pandas as pd
import numpy as np
from .monday_range import MondayRange
from .liquidity_engine import LiquidityEngine
from .market_structure import MarketStructure

class SignalGenerator:
    def __init__(self, df_htf, df_ltf):
        self.df_htf = df_htf
        self.df_ltf = df_ltf
        
    def analyze(self):
        # 1. Inisialisasi nilai default (Mencegah KeyError)
        result = {
            "status": "WAIT",
            "reason": "No clear setup found.",
            "monday_range": {"high": None, "low": None},
            "boxes": {"support": None, "resistance": None},
            "signals": []
        }

        try:
            # 2. Hitung Monday Range dari data LTF (4H)
            mr = MondayRange(self.df_ltf)
            mr_high, mr_low = mr.calculate()
            
            if mr_high is None or mr_low is None:
                result["reason"] = "Monday Range data not available."
                return result
            
            result["monday_range"] = {"high": mr_high, "low": mr_low}

            # 3. Hitung Struktur Pasar (Boxes) dari data HTF (Weekly)
            ms = MarketStructure(self.df_htf)
            support_series, resistance_series = ms.get_boxes()
            
            # Ambil nilai terbaru dari box
            current_support = support_series.iloc[-1]
            current_resistance = resistance_series.iloc[-1]
            
            result["boxes"] = {
                "support": current_support, 
                "resistance": current_resistance
            }

            current_price = self.df_ltf.iloc[-1]['close']
            result["current_price"] = current_price

            # 4. Cek No Trade Zone (Middle of Range)
            # EliZ: "Jangan trade di middle of nowhere"
            if ms.is_mid_range(current_price, current_support, current_resistance):
                result["status"] = "NO TRADE"
                result["reason"] = "Price is in the middle of the range (No Trade Zone). Sitting on hands is also a position."
                return result

            # 5. Cek Liquidity Sweep & Reclaim
            le = LiquidityEngine(self.df_ltf)
            
            # Kita cek sweep di area ekstrem: Monday Range ATAU Boxes
            # Prioritas 1: Monday Range
            signals = le.detect_sweep_and_reclaim(mr_high, mr_low)
            
            # Prioritas 2: Boxes (Support/Resistance) jika tidak ada sinyal di Monday Range
            if not signals:
                signals = le.detect_sweep_and_reclaim(current_resistance, current_support)

            if signals:
                result["status"] = "SIGNAL FOUND"
                result["reason"] = f"Found {len(signals)} setup(s) based on Liquidity Sweep + Reclaim."
                result["signals"] = signals
            else:
                result["status"] = "WAIT"
                result["reason"] = "Price is at a key level, but no Sweep + Reclaim trigger yet. Wait for confirmation."

        except Exception as e:
            # Tangkap error agar mesin tidak crash
            result["status"] = "ERROR"
            result["reason"] = f"Analysis engine error: {str(e)}"

        return result
