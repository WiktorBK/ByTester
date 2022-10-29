from cross import *
import time
from datetime import datetime
from notifications import * 
from bybithandler import *

symbol = 'LTCUSDT'
start_time = datetime.now().strftime("%H:%M:%S")
send_email("App Started", symbol)



# Calculates affordable quantity based on capital
def get_qty(entry_price):
    qty = (lvg * capital) / entry_price
    return qty


def run(capital):
    counter = 0
    in_trade = False

    while True:
        entry_price = float(get_entry_price(symbol))
        while True:
            if entry_price != 0 and in_trade == False:
                print("order is already being executed")
                break 
            data = get_latest_data(symbol)
            ema_diff = ema_difference(data)
            signal = check_for_cross(ema_diff)
            print(symbol, signal, ema_diff[-1], counter)
            

            # Force closing the app after 1 hour
            time_now = datetime.now().strftime("%H:%M:%S")
            format = '%H:%M:%S'
            time1 = datetime.strptime(time_now, format) - \
                datetime.strptime(start_time, format)
            time1 = str(time1)
            time_split = time1.split(":")


            if time_split[1] == "05":
                send_email("App restarted", symbol)
                return None

            if signal == 'Buy':
                entry_price = data['Close'][-2]
                qty = get_qty(entry_price)
                qty = round(qty, 1)
                print(qty)
                # long  market buy - TP= takeprofitmarket sell - SL= stop market sell
                place_order(signal, symbol, qty, False)
                entry_price = float(get_entry_price(symbol))
                take_profit = round(entry_price * (1 + tp), 2)
                stoploss = round(entry_price * (1 - sl), 2)

                time.sleep(2)
                session.set_trading_stop(symbol = symbol, side = signal, stop_loss = stoploss, take_profit = take_profit)

                print(entry_price, take_profit, stoploss, qty)
                send_email('Trade was opened', symbol)
                break

            if signal == 'Sell':
                entry_price = data['Close'][-2]
                qty = get_qty(entry_price)
                qty = round(qty, 1)
                print(qty)
                # short   market sell - TP= takeprofitmarket Buy - SL= stop market buy 
                place_order(signal, symbol, qty, False)
                entry_price = float(get_entry_price(symbol))
                take_profit = round(entry_price * (1 - tp),2)
                stoploss = round(entry_price * (1 + sl),2)

                time.sleep(2)
                session.set_trading_stop(symbol = symbol, side = signal, stop_loss = stoploss, take_profit = take_profit)
     
                print(entry_price, take_profit, stoploss, qty)
                send_email('Trade was opened', symbol)
                break

            counter += 1
            time.sleep(1.5)
        
        data = get_latest_data(symbol)
        ema_diff = ema_difference(data)
        side = get_side(symbol)

        while entry_price != 0:
            data = get_latest_data(symbol)
            ema_diff = ema_difference(data)
            signal = check_for_cross(ema_diff)
            time_now = datetime.now().strftime("%H:%M:%S")
            format = '%H:%M:%S'
            time1 = datetime.strptime(time_now, format) - datetime.strptime(start_time, format)
            time1 = str(time1)
            time_split = time1.split(":")
            if time_split[1] == "05":
                send_email("App restarted", symbol)
                return None

            if signal != 'NO SIGNAL':
                if signal != side:
                    qty = (lvg * capital) / entry_price
                    qty = round(qty, 1)
                    if side == 'Sell':
                        place_order('Buy',symbol, qty, True)
                    else:
                        place_order('Sell', symbol, qty, True)
                    in_trade = True
                    break
            entry_price = float(get_entry_price(symbol))
            print(ema_diff[-1], signal)
            time.sleep(1)
        send_email('Trade was closed', symbol)


# try:
# change_leverage(lvg, symbol)
run(capital)   
# except:
#     print('Program failed')
#     send_email('Program Failed', symbol)




