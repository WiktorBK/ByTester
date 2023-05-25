from bybit import *
from config import *
from backtester import *

bb = Bybit()
if __name__ == "__main__":
    print(f"Testing {len(SYMBOLS)} pairs\nCapital per one pair: {CAPITAL_USD} USD\nPeriod: {MONTHS} month/s\nInterval:{INTERVAL}min\nEMAS:{EMA1}/{EMA2}")
    for symbol in SYMBOLS:

        # run backtest for each symbol
        print(symbol, Backtest.get_results(bb.get_format_data(symbol)))