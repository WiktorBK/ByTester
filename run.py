from bybit import *
from config import *
from backtester import *

bb = Bybit()
if __name__ == "__main__":
    for symbol in SYMBOLS:

        # run backtest for each symbol
        print(symbol, Backtest.get_results(bb.get_format_data(symbol)))