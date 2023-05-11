import calendar
from datetime import datetime
import json
import time
from pybit.usdt_perpetual import HTTP
import secrets
import pandas as pd

now = datetime.utcnow()
unixtime = calendar.timegm(now.utctimetuple())
since = unixtime - 2629800 * 0.0227
since = int(since)
####
capital = 1 # per one pair
lvg = 20
sl = 0.0175
tp = 0.035
####

# Opening bybit session
session = HTTP(
    "https://api.bybit.com",
    api_key = secrets.apiKey_bb,
    api_secret = secrets.secret_bb,
    request_timeout= 60
)



def get_latest_data(symbol): 
    # Get Data
    try:
        data = session.query_kline(
        symbol= symbol, 
        interval = '5',
        **{'from':since},
        limit = 200
        )['result']
    except:
        print("Lost Connection")
        print("Reconnecting...")
        time.sleep(3)
        data = session.query_kline(
            symbol= symbol, 
            interval = '3',
            **{'from':since}
        )['result']

    # Format Data
    df = pd.DataFrame(data)
    df = df.iloc[:, 5:11]
    df.columns = ['Time', 'Volume', 'Open', 'High', 'Low', 'Close']
    df = df.set_index('Time')
    df.index = pd.to_datetime(df.index, unit='ms')
    df = df.astype(float)

    return df

def place_order(side, symbol, qty, reduce_only):
    if reduce_only == False:
        session.place_active_order(
            symbol=symbol,
            side=side,
            order_type="Market",
            qty=qty,
            time_in_force="GoodTillCancel",
            reduce_only=reduce_only,
            close_on_trigger=False
            )
    else:
        session.place_active_order(
            symbol=symbol,
            side=side,
            order_type="Market",
            qty=qty,
            time_in_force="GoodTillCancel",
            reduce_only=reduce_only,
            close_on_trigger = False
            )

def get_correct_index(list):
    leng = len(list)
    for i in range(leng):
        ep = list[i]['entry_price'] 
        if ep != 0:
            return i

def get_entry_price(symbol):
    x = get_correct_index(session.my_position(symbol=symbol)['result'])
    if x == None:
            entry_price = 0
    else:
            entry_price = session.my_position(symbol=symbol)['result'][x]['entry_price']


    return entry_price
    
def change_leverage(lvg, symbol):
    session.set_leverage(
    symbol = symbol,
    buy_leverage = lvg,
    sell_leverage = lvg 
    )

def get_side(symbol):
    x = get_correct_index(session.my_position(symbol=symbol)['result'])
    if x == None:
            return 'No position found'
    else:
            side = session.my_position(symbol=symbol)['result'][x]['side']
            return side

