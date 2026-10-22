class MarketStructure:
    def __init__(self, df):
        self.df = df
        
    def get_boxes(self, lookback_weeks=52):
        # Ambil lookback 1 tahun (52 minggu) untuk menentukan Boxes makro
        recent_data = self.df.tail(lookback_weeks)
        resistance = recent_data['high'].max()
        support = recent_data['low'].min()
        return support, resistance

    def check_zone(self, current_price, support, resistance):
        range_size = resistance - support
        if range_size <= 0:
            return "NO TRADE", "Invalid Range"

        # Middle of Range (No Trade Zone) = 30% area tengah
        mid_lower = support + (range_size * 0.35)
        mid_upper = support + (range_size * 0.65)
        
        if mid_lower <= current_price <= mid_upper:
            return "NO TRADE", f"Harga di middle of range ({mid_lower:.2f} - {mid_upper:.2f}). Sitting on hands is also a position."
            
        return "TRADEABLE", "Harga di area ekstrem."
