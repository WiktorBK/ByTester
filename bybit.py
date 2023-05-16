from pybit import HTTP
import pandas as pd
from datetime import datetime
import calendar
import traceback
from config import *

class Bybit:
    def __init__(self):
        self.session = self.open_session()

    def open_session(self):
        try: return HTTP("https://api.bybit.com", request_timeout= 60)
        except: print(f"Couldn't open session:\n {traceback.format_exc()}")

    def get_format_data(self, symbol):
            data = self.get_data(MONTHS, symbol)
            if data==[]: print("Data period is too small")
            try:
                df = pd.DataFrame(data)
                df = df.iloc[:, 5:11]
                df.columns = ['Time', 'Open', 'High', 'Low', 'Close' , 'Volume']
                df = df.set_index('Time')
                df.index = pd.to_datetime(df.index, unit='s')
                df = df.astype(float)
                return df
            except: print(f"Couldn't format data:\n {traceback.format_exc()}")




