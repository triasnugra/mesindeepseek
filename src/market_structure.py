class MarketStructure:
    def __init__(self, df):
        self.df = df
        
    def get_boxes(self, window=20):
        # Menggunakan rolling min/max sederhana sebagai proxy Boxes
        # Di produksi, Anda bisa menggunakan algoritma ZigZag atau Fractal
        resistance = self.df['high'].rolling(window=window).max()
        support = self.df['low'].rolling(window=window).min()
        return support, resistance

    def is_mid_range(self, current_price, support, resistance):
        # Cek apakah harga berada di tengah-tengah (No Trade Zone)
        mid = (support + resistance) / 2
        range_size = resistance - support
        
        # Jika harga berada dalam 20% dari titik tengah, anggap No Trade Zone
        if abs(current_price - mid) < (range_size * 0.2):
            return True
        return False
