import pandas as pd

class MondayRange:
    def __init__(self, df):
        self.df = df
    
    def calculate(self):
        # Pastikan data adalah Daily untuk akurasi
        df_daily = self.df.resample('1D').agg({'high': 'max', 'low': 'min'}).dropna()
        
        # Cari hari Senin (0 = Monday)
        mondays = df_daily[df_daily.index.dayofweek == 0]
        
        if mondays.empty:
            return None, None
            
        # Ambil data Senin terakhir yang sudah selesai (bukan hari ini jika hari ini Senin)
        today = pd.Timestamp.now(tz=df_daily.index.tz).normalize()
        valid_mondays = mondays[mondays.index < today]
        
        if valid_mondays.empty:
            return None, None
            
        last_monday = valid_mondays.iloc[-1]
        return last_monday['high'], last_monday['low']
