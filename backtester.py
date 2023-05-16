from config import *
from strategy import Strategy


class Backtest:

    def calculate_takeprofit(close_price, side):
        multiplier = -1 if side=="SELL" else 1
        return float(close_price * (1 + multiplier * TP_PERC )) # multiply by -1 if side == "SELL"

    def calculate_stoploss(close_price, side):
        multiplier = -1 if side=="BUY" else 1
        return float(close_price * (1 + multiplier * SL_PERC)) # multiply by -1 if side == "BUY"
    







