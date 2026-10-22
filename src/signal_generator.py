from .monday_range import MondayRange
from .market_structure import MarketStructure
from .liquidity_engine import LiquidityEngine

class SignalGenerator:
    def __init__(self, df_htf, df_ltf):
        self.df_htf = df_htf
        self.df_ltf = df_ltf
        
    def analyze(self):
        # 1. Default response (Mencegah KeyError)
        result = {
            "status": "WAIT",
            "reason": "Menunggu setup...",
            "current_price": self.df_ltf.iloc[-1]['close'],
            "monday_range": {"high": None, "low": None},
            "boxes": {"support": None, "resistance": None},
            "signals": []
        }

        try:
            current_price = result["current_price"]

            # 2. Ambil Level Kunci
            mr = MondayRange(self.df_ltf)
            mr_high, mr_low = mr.calculate()
            
            ms = MarketStructure(self.df_htf)
            box_sup, box_res = ms.get_boxes()
            
            result["monday_range"] = {"high": mr_high, "low": mr_low}
            result["boxes"] = {"support": box_sup, "resistance": box_res}

            if mr_high is None or box_sup is None:
                result["reason"] = "Data history tidak cukup untuk menghitung level."
                return result

            # 3. Cek No Trade Zone
            zone_status, zone_reason = ms.check_zone(current_price, box_sup, box_res)
            if zone_status == "NO TRADE":
                result["status"] = "NO TRADE"
                result["reason"] = zone_reason
                return result

            # 4. Cek Kedekatan (Proximity Check) - Maksimal 2.5% jarak
            le = LiquidityEngine(self.df_ltf)
            signals = []
            
            # Cek apakah harga sedang di area Monday Range
            near_mr_high = mr_high and abs(current_price - mr_high) / mr_high <= 0.025
            near_mr_low = mr_low and abs(current_price - mr_low) / mr_low <= 0.025
            
            # Cek apakah harga sedang di area Boxes Weekly
            near_box_res = abs(current_price - box_res) / box_res <= 0.025
            near_box_sup = abs(current_price - box_sup) / box_sup <= 0.025

            # 5. Cari Trigger Sweep + Reclaim
            if near_mr_high or near_box_res:
                signals.extend(le.detect_setup(mr_high, None))
                if not signals: signals.extend(le.detect_setup(box_res, None))
                     
            if near_mr_low or near_box_sup:
                signals.extend(le.detect_setup(None, mr_low))
                if not signals: signals.extend(le.detect_setup(None, box_sup))

            # 6. Hasil Akhir
            if signals:
                result["status"] = "SIGNAL FOUND"
                result["reason"] = "Setup valid terdeteksi (Sweep + Reclaim)!"
                result["signals"] = signals
            else:
                result["status"] = "WAIT"
                if near_mr_high or near_mr_low or near_box_res or near_box_sup:
                    result["reason"] = "Harga di level kunci, TAPI belum ada Deviation + Reclaim. Jangan entry dulu."
                else:
                    result["reason"] = "Harga jauh dari level kunci (Monday Range / Boxes). Jangan chase harga."

        except Exception as e:
            result["status"] = "ERROR"
            result["reason"] = f"Engine Error: {str(e)}"

        return result
