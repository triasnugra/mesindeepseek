import pandas as pd

class MondayRange:
    def __init__(self, df):
        self.df = df
    
    def calculate(self):
        # Pastikan index adalah datetime
        if not isinstance(self.df.index, pd.DatetimeIndex):
            raise ValueError("DataFrame index must be DatetimeIndex")
            
        # Filter hanya hari Senin (0 = Monday)
        monday_data = self.df[self.df.index.dayofweek == 0]
        
        if monday_data.empty:
            return None, None
            
        # Ambil High dan Low dari hari Senin terakhir
        # (Biasanya diambil dari minggu berjalan atau minggu sebelumnya)
        last_monday = monday_data.iloc[-1]
        monday_high = last_monday['high']
        monday_low = last_monday['low']
        
        return monday_high, monday_low
