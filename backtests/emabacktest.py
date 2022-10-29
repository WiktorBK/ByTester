import matplotlib.pyplot as plt
import time 
import pandas as pd
from binance.client import Client
import secrets
from ta.trend import EMAIndicator, macd_diff


client = Client()
ts = time.time() 
#####
month = 2629800
since = ts- month * 24
symbols = ['SOLUSDT','BNBUSDT', 'ETHUSDT','MATICUSDT', 'ADAUSDT']
capital_usd = 600 # per one pair
lvg = 5
fee_rate = 0.0003 # % / 100
tp_percentage = 0.1 # % / 100
sl_percentage = 0.1 # % / 100
#####

ema_window_1 = 200 # Long Term EMA
ema_window_2 = 50 # Short Term EMA


def ema_difference(df):
    ema_difference = []
    df[f'ema{ema_window_1}'] = EMAIndicator(df['Close'], ema_window_1).ema_indicator()
    df[f'ema{ema_window_2}'] = EMAIndicator(df['Close'], ema_window_2).ema_indicator()
    for i in range(len(df[f'ema{ema_window_2}'])):
        ema_difference.append(df[f'ema{ema_window_2}'][i] - df[f'ema{ema_window_1}'][i])

    return ema_difference
def macd(df):
    macd_signals = []
    df['MACD relation'] = macd_diff(df['Close'])
    for i in range(len(df['MACD relation'])):
        if df['MACD relation'][i] > 0:
                macd_signals.append('BUY')
        elif df['MACD relation'][i] < 0:
                macd_signals.append('SELL')
        else:
            macd_signals.append('No Signal')
    
            
    return macd_signals
def get_latest_data(symbol):
    try:
        data = client.futures_historical_klines(
        symbol, 
        Client.KLINE_INTERVAL_3MINUTE,
        str(since))
    except:
        print("couldn't load latest data\nretrying in 60 sec")
        time.sleep(3)
        data = client.futures_historical_klines(
        symbol, 
        Client.KLINE_INTERVAL_3MINUTE,
        str(since))       
    df = pd.DataFrame(data)
    df = df.iloc[:, 0:5]
    df.columns = ['Time', 'Open', 'High', 'Low', 'Close']
    df = df.set_index('Time')
    df.index = pd.to_datetime(df.index, unit='ms')
    df = df.astype(float)

    return df
def get_trades(ema_diff, df, macd_signals):
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
                           'open': df['Close'][i+1], 
                           'tp': take_profit, 
                           "sl": stoploss})

            # adding marks to plot
            plt.scatter(df.index[i], df['Close'][i], c = "r", marker="v")

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

            # adding marks to plot
            plt.scatter(df.index[i], df['Close'][i], c = "g", marker = "^")
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
        try:
            return {"start_date": trades[0]['time'], "end_date": trades[-1]['time'], "wins": wins, 'losses': loss, 'till_next_cross': nones, 'profit': round(profit, 3), 'minus': minus, 'plus': plus}
        except:
            return round(profit, 3)



plus = 0
minus = 0
combined = 0
for symbol in symbols:
    # combined = 0
    df = get_latest_data(symbol)
    ema_diff = ema_difference(df)
    macd_signals = macd(df)
    trades = get_trades(ema_diff, df, macd_signals)
    results = get_results(trades, df, False)
    print(symbol, results)
    plus += results['plus']
    minus += results['minus']
    # for order in results:
    #     print(order)
        # combined += order['profit']
        # if order['profit'] > 0:
        #     plus += 1
        # else:
        #     minus += 1 
    try:
        combined += results['profit']
    except:
        combined += results
print(round(combined, 3), plus, minus)  