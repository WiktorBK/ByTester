import pandas as pd
from binance.client import Client
import secrets
import time
import datetime

client = Client(secrets.apiKey, secrets.secretKey, {"timeout": 30})
ts = time.time() 
since = ts - 2629800 * 0.01

####
capital = 2 # per one pair
lvg = 20
sl = 0.0175
tp = 0.035
####

def get_latest_data(symbol):
    try:
        data = client.futures_historical_klines(
        symbol, 
        Client.KLINE_INTERVAL_1MINUTE,
        str(since))
    except:
        print("couldn't load latest data\nretrying in 60 sec")
        time.sleep(2)
        data = client.futures_historical_klines(
        "ETHUSDT", 
        Client.KLINE_INTERVAL_1MINUTE,
        str(since))
        
    df = pd.DataFrame(data)
    df = df.iloc[:, 0:5]
    df.columns = ['Time', 'Open', 'High', 'Low', 'Close']
    df = df.set_index('Time')
    df.index = pd.to_datetime(df.index, unit='ms')
    df = df.astype(float)

    return df

def place_order(side, order_type, symbol, qty, stop_price):
    # order_type - MARKET / STOP_MARKET / TAKE_PROFIT_MARKET
    # side - BUY / SELL
    if order_type == 'MARKET':
        client.futures_create_order(
        symbol = symbol, 
        side = side, 
        type = order_type,
        quantity = qty)
        print(f"order has been placed\n{symbol}\n{side}\n{order_type}\n{datetime.datetime.now()}")
    else:
        client.futures_create_order(
        symbol = symbol, 
        side = side, 
        type = order_type,
        quantity = qty,
        stopPrice = stop_price,
        closePosition = True)
    
def get_entry_price(symbol):
    entry_price = client.futures_position_information(
        symbol=symbol
        )[0]['entryPrice']
    
    return entry_price

def change_leverage(lvg, symbol):
    client.futures_change_leverage(
        leverage=str(lvg),
        symbol = symbol)    

def cancel_open_orders(symbol):
    client.futures_cancel_all_open_orders(symbol = symbol)

