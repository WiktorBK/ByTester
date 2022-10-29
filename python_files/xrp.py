from cross import *
from binancehandler import *
import time
import datetime

capital = 1
symbol = 'XRPUSDT'
lvg = 20
sl = 0.1
tp = 0.1
change_leverage(lvg, symbol)

def get_qty(entry_price):
    qty = (lvg * capital) / entry_price
    return qty

def run():
    while True:
        entry_price = float(get_entry_price(symbol))
        if entry_price != 0:
            print("order is already being executed")
            break                                                                                                                 
        data = get_latest_data(symbol)
        ema_diff = ema_difference(data)
        signal = check_for_cross(ema_diff)
        now = datetime.datetime.now()
        print(symbol, signal, ema_diff[-1])
        if signal == "BUY":
            entry_price = data['Close'][-2]
            qty = get_qty(entry_price)
            print('order')
            # short   market sell - TP= takeprofitmarket Buy - SL= stop market buy 
            # long  market buy - TP= takeprofitmarket sell - SL= stop market sell
            place_order(signal, 'MARKET', symbol, qty, 0)
            entry_price = float(get_entry_price(symbol))
            take_profit = entry_price * (1 + tp)
            stoploss = entry_price * (1 - sl)
            place_order('SELL', 'TAKE_PROFIT_MARKET', symbol, qty, take_profit)
            place_order('SELL', 'STOP_MARKET', symbol, qty, stoploss)
            print(entry_price, take_profit, stoploss, qty)
            break
        if signal == 'SELL':
            entry_price = data['Close'][-2]
            qty = get_qty(entry_price)
            print('order')
            # short   market sell - TP= takeprofitmarket Buy - SL= stop market buy 
            # long  market buy - TP= takeprofitmarket sell - SL= stop market sell
            place_order(signal, 'MARKET', symbol, qty, 0)
            entry_price = float(get_entry_price(symbol))
            take_profit = entry_price * (1 - tp)
            stoploss = entry_price * (1 + sl)
            place_order('BUY', 'TAKE_PROFIT_MARKET', symbol, qty, take_profit)
            place_order('BUY', 'STOP_MARKET', symbol, qty, stoploss)
            print(entry_price, take_profit, stoploss, qty)
            break
        time.sleep(2)
    
        while entry_price != 0:
            entry_price = get_entry_price(symbol)
            print(entry_price)
            time.sleep(1)
run()




