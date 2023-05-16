from config import *
from strategy import Strategy

class Backtest:

    def calculate_takeprofit(close_price, side):
        multiplier = -1 if side=="SELL" else 1
        return float(close_price * (1 + multiplier * TP_PERC )) # multiply by -1 if side == "SELL"

    def calculate_stoploss(close_price, side):
        multiplier = -1 if side=="BUY" else 1
        return float(close_price * (1 + multiplier * SL_PERC)) # multiply by -1 if side == "BUY"
    
    @classmethod
    def get_trades(cls, df):
        trades=[]
        ema_diff = Strategy.ema_difference(df)
        #iterate through the entire period of given time and searching for crosses
        for i in range(198, len(ema_diff) - 1):
            # find longs
            if ema_diff[i] < 0 and ema_diff[i+1] >= 0:
                # calculating prices
                tp = cls.calculate_takeprofit(df['Close'][i+1], "BUY")
                sl = cls.calculate_stoploss(df['Close'][i+1], "BUY")
                trades.append({'index':i+1, 'side': "BUY", 'time':df.index[i+1], 'open': df['Open'][i+1], 'tp': tp, "sl": sl})

            # find shorts
            elif ema_diff[i] > 0 and ema_diff[i+1] <= 0:
                tp = cls.calculate_takeprofit(df['Close'][i+1], "SELL")
                sl = cls.calculate_stoploss(df['Close'][i+1], "SELL")
                trades.append({'index':i+1,'side': "SELL", 'time':df.index[i+1], 'open': df['Open'][i+1], 'tp': tp, "sl": sl})

        return trades


   





