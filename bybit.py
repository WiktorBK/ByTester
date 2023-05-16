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

    def current_time(self):
         now = datetime.utcnow()
         return calendar.timegm(now.utctimetuple()) # current timestamp

    def query_data(self, since, symbol):
        # query data from bybit api
        try: return self.session.query_kline(
                symbol= symbol, 
                interval = INTERVAL,
                **{'from':int(since)},
                limit = 200)['result']
        except: print(f"Couldn't query data:\n {traceback.format_exc()}")

    def get_data(self, months, symbol):

        '''
            Bybit limit is 200 candles of past data per request

            this funcion divides data periods to match bybit's limits
        '''
        unixtime = self.current_time()
        total = int(PERIODS_PER_MONTH * months)  # total amount of 200 candles periods in given value (months)
        since = unixtime - MONTH_SEC * total * PERIOD_MONTH_PERC
        data = self.query_data(since, symbol) # get first 200 candles (total of x)

        if len(data) != 200: return data
    
        total -= 1  # decrement x by 
        while total >= 1:
            since = int(unixtime - MONTH_SEC * total * PERIOD_MONTH_PERC)
            data_ = self.query_data(since, symbol)
            for i in data_: data.append(i)
            total -= 1
        return data
        
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

