from ast import Break
import time 
import pandas as pd
from binance.client import Client
import secrets
from ta.trend import EMAIndicator, PSARIndicator, macd_diff, MACD


client = Client()
ts = time.time() 
month = 2629800
months = 0.05
since = ts- month * months
end = since + month
#####
CAPITAL_PER_PAIR = 1 # per one pair
LVG = 20
SYMBOLS = ['SOLUSDT', 'ETHUSDT','BNBUSDT','ADAUSDT', 'MATICUSDT', 'LTCUSDT']
FEE_RATE = 0.0006 # % / 100
EMA_WINDOW = 200
TP_RATIO = 2
INTERVAL = 1
#####


def get_latest_data(symbol):

    try:
        data = client.futures_historical_klines(
        symbol, 
        Client.KLINE_INTERVAL_1MINUTE,
        str(since))
    except:
        print("couldn't load latest data\nretrying in 60 sec")
        time.sleep(3)
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

def psar(df):
    psar_signals = []
    df['pSAR_down'] = PSARIndicator(df['High'], df['Low'], df['Close']).psar_down()
    df['pSAR_up'] = PSARIndicator(df['High'], df['Low'], df['Close']).psar_up()

    for i in range(len(df['pSAR_down'])):
        if pd.isna(df['pSAR_down'][i-1]) == False and pd.isna(df['pSAR_down'][i]) == True\
        or pd.isna(df['pSAR_down'][i-2]) == False and pd.isna(df['pSAR_down'][i-1]) == True\
        or pd.isna(df['pSAR_down'][i-3]) == False and pd.isna(df['pSAR_down'][i-2]) == True:
            psar_signals.append('Buy')
        elif  pd.isna(df['pSAR_down'][i-1]) == True and pd.isna(df['pSAR_down'][i]) == False\
        or pd.isna(df['pSAR_down'][i-2]) == True and pd.isna(df['pSAR_down'][i-1]) == False\
        or pd.isna(df['pSAR_down'][i-3]) == True and pd.isna(df['pSAR_down'][i-2]) == False:
            psar_signals.append('Sell')

        else:
            psar_signals.append('NO SIGNAL')

    return psar_signals

def ema(df):
    ema_signals = []
    df['Ema100'] = EMAIndicator(df['Close'], EMA_WINDOW).ema_indicator()
    for i in range(len(df['Ema100'])):
        if df['Close'][i] <= df['Ema100'][i]:
            ema_signals.append('Sell')
        elif df['Close'][i] >= df['Ema100'][i]:
            ema_signals.append('Buy')
        else:
            ema_signals.append('NO SIGNAL')
    return ema_signals

def macd(df):
    macd_signals = []

    df['MACD relation'] = macd_diff(df['Close'])
    for i in range(len(df['MACD relation'])):
        if df['MACD relation'][i] > 0 and df['MACD relation'][i-1] <= 0 \
        or df['MACD relation'][i-1] > 0 and df['MACD relation'][i-2] <= 0 \
        or df['MACD relation'][i-2] > 0 and df['MACD relation'][i-3] <= 0:
            if df['MACD relation'][i] < 5 and df['MACD relation'][i] > 0:
                macd_signals.append('Buy')
            else:
                macd_signals.append('NO SIGNAL')
        elif df['MACD relation'][i] < 0 and df['MACD relation'][i-1] >= 0 \
        or df['MACD relation'][i-1] < 0 and df['MACD relation'][i-2] >= 0 \
        or df['MACD relation'][i-2] < 0 and df['MACD relation'][i-3] >= 0: 
            if df['MACD relation'][i] > -5 and df['MACD relation'][i] < 0:
                macd_signals.append('Sell')
            else:
                macd_signals.append('NO SIGNAL')
        else:
                macd_signals.append('NO SIGNAL')
    
            
    return macd_signals

def macd_price(df):
     macd_price_signals = []
     df['macd'] = MACD(df['Close']).macd_signal()
     for i in range(len(df['macd'])):
         if df['macd'][i] > 0:
             macd_price_signals.append('Sell')
         elif df['macd'][i] < 0:
            macd_price_signals.append('Buy')
         else:
             macd_price_signals.append('NO SIGNAL')
     return macd_price_signals

def psar_price(df):
    # Returning PSAR price
    df['pSAR'] = PSARIndicator(df['High'], df['Low'], df['Close']).psar()
    return df

def get_takeprofit(entry_price, stop_loss, side):
    # Calculating takeprofit based on open price, stoploss and side

    stop_loss_percentage = abs((1 - stop_loss/entry_price))
    take_profit_percentage = stop_loss_percentage * TP_RATIO

    if side == "Buy":
        take_profit = entry_price + entry_price * take_profit_percentage
    elif side == "Sell":
        take_profit = entry_price - entry_price * take_profit_percentage

    take_profit = round(take_profit, 4)
    take_profit = float(take_profit)
    return take_profit

def get_trades(df, ema_signals, psar_signals, macd_signals, psar_prices, macd_price_signals):
    x = EMA_WINDOW - 1
    trades = []
    latest_trade = {'side': 'None'}
    exit_idx = 0
    for i in range(x, len(ema_signals)):
        if macd_signals[i] == macd_price_signals[i] == psar_signals[i]:
            stoploss = psar_prices[i]
            takeprofit = get_takeprofit(df['Close'][i], stoploss, psar_signals[i])        
            trades.append({'index':i,
                            'side': psar_signals[i],
                            'sl': stoploss,
                            'tp': takeprofit
                            }) 
    


    return trades


def perform_order(side, tp, sl, idx, indexes, df, trade, trades):
    idx_of_index = indexes.index(idx) 
    correct_entry = False 
    hit = False
    i = idx+1
    while correct_entry == False or hit == False:  
        if side == "Buy":
            if df['High'][i] >= tp:
                trade['exit_idx'] = i 
                return trade     
            elif df['Low'][i] <= sl:
                trade['exit_idx'] = i      
                return trade
        
        elif side == "Sell":
            if df['High'][i] >= sl:
                trade['exit_idx'] = i      
                return trade
            
            elif df['Low'][i] <= tp:
                trade['exit_idx'] = i      
                return trade  
        if i in indexes:
            iidx = indexes.index(i)            
            if side != trades[iidx]['side']:
                trade['exit_idx'] = i
                return trade

        i+=1
            

    # if trade doesn't have a result till the next trade  

    if side == "Buy":
        open_price = df['Close'][idx]
        close_price = df['Close'][indexes[idx_of_index+1]]
        if close_price > sl:
                 trade['exit_idx'] = indexes[idx_of_index+1] 
                 return trade
        else:
                 trade['exit_idx'] = indexes[idx_of_index+1]   
                 return trade
    elif side == "Sell":
        open_price = df['Close'][idx]
        close_price = df['Close'][indexes[idx_of_index+1]]
        if close_price < sl:
                 trade['exit_idx'] = indexes[idx_of_index+1]    
                 return trade
        else:
                 trade['exit_idx'] = indexes[idx_of_index+1]     
                 return trade


def get_results(trades, more_details = False):
    indexes = []
    results = []
    for i in trades:
            indexes.append(i['index'])
    for i in range(len(trades)-1):
        trade = perform_order(trades[i]['side'], trades[i]['tp'], trades[i]['sl'], trades[i]['index'], indexes, df)
        if trade['side'] == "Buy":
                qty = (LVG * CAPITAL_PER_PAIR) / trade['open_price']
                bought_for = qty * trade['open_price']
                sold_for = qty * trade['close_price']
                fee = FEE_RATE * LVG * CAPITAL_PER_PAIR * 2
                result = sold_for - bought_for - fee
                trade['qty'] = qty
                trade['profit'] = round(result, 3)
                results.append(trade)
        elif trade['side'] == "Sell":
                qty = (LVG * CAPITAL_PER_PAIR) / trade['open_price']
                bought_for = qty * trade['open_price']
                sold_for = qty * trade['close_price']
                fee = FEE_RATE * LVG * CAPITAL_PER_PAIR * 2
                result = bought_for - sold_for - fee
                trade['qty'] = qty
                trade['profit'] = round(result, 3)
                results.append(trade)
    all_orders = []
    profit = 0
    wins = 0
    loss = 0
    nones = 0
    if more_details:
        for i in results:
            all_orders.append(i)
        return all_orders
    else:
        for i in results:
            profit += i['profit']
            if i['result'] == 'WIN':
                wins += 1
            elif i['result'] == 'LOSS':
                loss += 1
            else:
                nones += 1
        return {"start_date": trades[0]['time'], "end_date": results[-1]['end_date'], "wins": wins, 'losses': loss, "till_next_trade": nones, 'profit': round(profit, 3)}


df = psar_price(get_latest_data('ETHUSDT'))
ema_signals = ema(df)
psar_signals = psar(df)
macd_signals = macd(df)
macd_price_signals = macd_price(df)
trades = get_trades(df, ema_signals, psar_signals, macd_signals, df['pSAR'], macd_price_signals)
indexes = []
for i in trades:
        indexes.append(i['index'])
for trade in trades:
    print(perform_order(trade['side'], trade['tp'], trade['sl'], trade['index'], indexes, df, trade, trades))

# f1 = open(r'C:\Users\admin\Desktop\Inf\pythonProjects\KrakenCross\txtfiles\emas.txt')
# emas = []
# for i in f1.readlines():
#     emas.append(int(i.strip()))
# f1.close()
# f2 = open(r'C:\Users\admin\Desktop\Inf\pythonProjects\KrakenCross\txtfiles\tps.txt')
# tps = []
# for i in f2.readlines():
#     tps.append(float(i.strip()))
# f2.close()


# result_list = []
# combined = 0
# for symbol in SYMBOLS:
#     df = psar_price(get_latest_data(symbol))
#     ema_signals = ema(df)
#     psar_signals = psar(df)
#     macd_signals = macd(df)
#     macd_price_signals = macd_price(df)
#     trades = get_trades(df, ema_signals, psar_signals, macd_signals, df['pSAR'], macd_price_signals)
#     results = get_results(trades)
#     print(symbol, results)
#     result_list.append([symbol,results])
#     combined += results['profit']
# f = open('results.txt', 'a')
# f.write(f'\n\nPeriod: {months} month/s, Interval: {INTERVAL}, Ema Window: {EMA_WINDOW}, TP Ratio: {TP_RATIO}, Capital: {CAPITAL_PER_PAIR* len(SYMBOLS)}\n')
# for i in result_list:
#     f.write(f"{i[0]} {i[1]}\n")
# f.write(str(combined))
# f.close()