from ta.trend import EMAIndicator, SMAIndicator
from pybit.usdt_perpetual import HTTP
import pandas as pd
import secrets
from datetime import datetime
import calendar


symbols = ['SOLUSDT','BNBUSDT', 'ETHUSDT','ADAUSDT', 'MATICUSDT', 'LTCUSDT']


interval = '5'
capital_usd = 1 # per one pair
lvg = 20
fee_rate = 0.0006 # % / 100


# Strategy 
def ema_difference(df, ema_window_1, ema_window_2):
    ema_difference = []
    df[f'ema{ema_window_1}'] = EMAIndicator(df['Close'], ema_window_1).ema_indicator()
    df[f'ema{ema_window_2}'] = EMAIndicator(df['Close'], ema_window_2).ema_indicator()
    for i in range(len(df[f'ema{ema_window_2}'])):
        ema_difference.append(df[f'ema{ema_window_2}'][i] - df[f'ema{ema_window_1}'][i])

    return ema_difference
def check_for_cross(ema_difference):
    if ema_difference[-3] > 0 and ema_difference[-2] <= 0:
        return "Sell"
    elif ema_difference[-3] < 0 and ema_difference[-2] >= 0:
        return "Buy"
    else:
        return "NO SIGNAL"

# Open Bybit Session
session = HTTP(
    "https://api.bybit.com",
    api_key = secrets.apiKey_bb,
    api_secret = secrets.secret_bb,
    request_timeout= 60
)


def get_data(symbol, months): 
    now = datetime.utcnow()
    unixtime = calendar.timegm(now.utctimetuple())
    month = 2629800
    candles_200 = int(interval) * 60 * 200
    p = candles_200 / month
    p = round(p, 4)
    y = 1 / p
    x = int(y * months)
    data = session.query_kline(
            symbol= symbol, 
            interval = interval,
            **{'from':int(unixtime - month * p * x)},
            limit = 200
        )['result']
    if len(data) != 200:
        df = pd.DataFrame(data)
        df = df.iloc[:, 5:11]
        df.columns = ['Time', 'Volume', 'Open', 'High', 'Low', 'Close']
        df = df.set_index('Time')
        df.index = pd.to_datetime(df.index, unit='s')
        df = df.astype(float)

        return df
    
    else:
        x -= 1
        while x >= 1:
            since = int(unixtime - month * p * x)
            data1 = (session.query_kline(
                symbol= symbol, 
                interval = interval,
                **{'from':since},
                limit = 200
            )['result'])
            if len(data1) != 200:
                for i in data1:
                    data.append(i)
                break
            for i in data1:
                data.append(i)
            x -= 1
        # Format Data
        df = pd.DataFrame(data)
        df = df.iloc[:, 5:11]
        df.columns = ['Time', 'Volume', 'Open', 'High', 'Low', 'Close']
        df = df.set_index('Time')
        df.index = pd.to_datetime(df.index, unit='s')
        df = df.astype(float)

        return df

def get_trades(ema_diff, df, tp_percentage, sl_percentage):
    trades = []
    #iterating through entire period of given time and searching for crosses
    for i in range(198, len(ema_diff) - 1):
        if ema_diff[i] > 0 and ema_diff[i+1] <= 0:
            # calculating prices
            take_profit = float(df['Close'][i+1]) * (1 - tp_percentage)
            stoploss = float(df['Close'][i+1]) * (1 + sl_percentage)

            trades.append({'index':i+1,
                           'side': "SELL", 
                           'time':df.index[i+1], 
                           'open': df['Open'][i+1], 
                           'tp': take_profit, 
                           "sl": stoploss})

            

        elif ema_diff[i] < 0 and ema_diff[i+1] >= 0:
            # calculating prices
            take_profit = float(df['Close'][i+1]) * (1 + tp_percentage)
            stoploss = float(df['Close'][i+1]) * (1 - sl_percentage)

            trades.append({'index':i+1, 
                           'side': "BUY", 
                           'time':df.index[i+1], 
                           'open': df['Open'][i+1], 
                           'tp': take_profit, 
                           "sl": stoploss})

            

    return trades

def perform_order(side, tp, sl, idx, indexes, df):
    idx_of_index = indexes.index(idx)
    # iterating through every candles between the crosses and identifying the results
    for i in range(idx+1, indexes[idx_of_index+1]):
        if side == "BUY":
            if df['High'][i] >= tp:
                 return {'result': "win", 'side': side, 'start_date': df.index[idx], 'open_price': df['Close'][idx], 'close_price': tp, 'end_date': df.index[i]}
       
            elif df['Low'][i] <= sl:
                 return{'result': "loss", 'side': side, 'start_date': df.index[idx], 'open_price': df['Close'][idx], 'close_price': sl, 'end_date': df.index[i]}
         
        elif side == "SELL":
            if df['High'][i] >= sl:
                 return {'result': "loss", 'side': side, 'start_date': df.index[idx], 'open_price': df['Close'][idx], 'close_price': sl, 'end_date': df.index[i]}
            
            elif df['Low'][i] <= tp:
                 return {'result': "win", 'side': side, 'start_date': df.index[idx], 'open_price': df['Close'][idx], 'close_price': tp, 'end_date': df.index[i]}
            

    # if trade doesn't have a result till the next cross - calculate pnl             
    if side == "BUY":
        open_price = df['Close'][idx]
        close_price = df['Close'][indexes[idx_of_index+1]]
        if close_price > sl:
            diff = close_price - open_price
            percentage = diff / open_price * 100
            return {'result': "none", 'side': side, 'start_date': df.index[idx], 'open_price': open_price, 'close_price': close_price, 'end_date': df.index[indexes[idx_of_index+1]]}
        else:
            return {'result': "loss", 'side': side, 'start_date': df.index[idx], 'open_price': open_price, 'close_price': sl, 'end_date': df.index[indexes[idx_of_index+1]]}
    elif side == "SELL":
        open_price = df['Close'][idx]
        close_price = df['Close'][indexes[idx_of_index+1]]
        if close_price < sl:
            diff = close_price - open_price
            percentage = (diff / open_price) * -100 
            return  {'result': "none", 'side': side, 'start_date': df.index[idx], 'open_price': open_price, 'close_price': close_price, 'end_date': df.index[indexes[idx_of_index+1]]}
        else:
            return  {'result': "loss", 'side': side, 'start_date': df.index[idx], 'open_price': open_price, 'close_price': sl, 'end_date': df.index[indexes[idx_of_index+1]]}

def get_results(trades, df, more_details = False):
    indexes = []
    details = []
    profit = 0
    wins = 0
    loss = 0
    nones = 0
    all_orders = []
    for i in trades:
        indexes.append(i['index'])
    for i in range(len(trades)-1):
         order = perform_order(trades[i]['side'], trades[i]['tp'], trades[i]['sl'], trades[i]['index'], indexes, df)
         if order['side'] == "BUY":
             diff = order['close_price'] - order['open_price']
             percentage = diff / order['open_price'] * 100
             qty = (lvg * capital_usd) / order['open_price']
             bought_for = qty * order['open_price']
             sold_for = qty * order['close_price']
             fee = fee_rate * lvg * capital_usd * 2
             result = sold_for - bought_for - fee
             order['qty'] = qty
             order['profit'] = round(result, 3)
             details.append(order)
         elif order['side'] == "SELL":
             diff = order['close_price'] - order['open_price']
             percentage = diff / order['open_price'] * 100
             qty = (lvg * capital_usd) / order['open_price']
             bought_for = qty * order['open_price']
             sold_for = qty * order['close_price']
             fee = fee_rate * lvg * capital_usd * 2
             result = bought_for - sold_for - fee
             order['qty'] = qty
             order['profit'] = round(result, 3)
             details.append(order)
    plus = 0 
    minus = 0
    if more_details:
        for i in details:
            all_orders.append(i)
        return all_orders
    else:
        for i in details:
            profit += i['profit']
            if i['profit'] > 0:
                plus += 1
            else:
                minus += 1
            if i['result'] == 'win':
                wins += 1
            elif i['result'] == 'loss':
                loss += 1
            else:
                nones += 1
        return {"start_date": trades[0]['time'], "end_date": trades[-1]['time'], "wins": wins, 'losses': loss, 'till_next_cross': nones, 'profit': round(profit, 3), 'minus': minus, 'plus': plus}



f1 = open('tps.txt')
tps = []
for i in f1.readlines():
    i = i.strip()
    i = i.split()
    i = [float(x) for x in i]
    tps.append(i)
f1.close()
f2 = open('emas.txt')
emas = []
for i in f2.readlines():
    i = i.strip()
    i = i.split()
    i = [int(x) for x in i]
    emas.append(i)
f2.close()



plus = 0
minus = 0
combined = 0
maxi = -100
best_ema = ''
best_tpsl = ''
for ema in emas:
    for tpsl in tps:
        combined = 0
        for symbol in symbols:
            df2 = get_data(symbol, months = 1)
            ema_diff = ema_difference(df2, ema[0], ema[1])
            trades = get_trades(ema_diff, df2, tpsl[0], tpsl[1])
            results = get_results(trades, df2, True)
            print( symbol)
            for order in results:
                print(order)
                combined += order['profit']
                if order['profit'] > 0:
                    plus += 1
                else:
                    minus += 1
            print(combined, plus, minus)  
