from config import *
from strategy import Strategy

class Backtest:

    def calculate_takeprofit(close_price, side):
        multiplier = -1 if side=="SELL" else 1
        return float(close_price * (1 + multiplier * TP_PERC )) # multiply by -1 if side == "SELL"

    def calculate_stoploss(close_price, side):
        multiplier = -1 if side=="BUY" else 1
        return float(close_price * (1 + multiplier * SL_PERC)) # multiply by -1 if side == "BUY"
    
    @classmethod
    def get_trades(cls, df):
        trades=[]
        ema_diff = Strategy.ema_difference(df)
        #iterate through the entire period of given time and searching for crosses
        for i in range(198, len(ema_diff) - 1):
            # find longs
            if ema_diff[i] < 0 and ema_diff[i+1] >= 0:
                # calculating prices
                tp = cls.calculate_takeprofit(df['Close'][i+1], "BUY")
                sl = cls.calculate_stoploss(df['Close'][i+1], "BUY")
                trades.append({'index':i+1, 'side': "BUY", 'time':df.index[i+1], 'open': df['Open'][i+1], 'tp': tp, "sl": sl})

            # find shorts
            elif ema_diff[i] > 0 and ema_diff[i+1] <= 0:
                tp = cls.calculate_takeprofit(df['Close'][i+1], "SELL")
                sl = cls.calculate_stoploss(df['Close'][i+1], "SELL")
                trades.append({'index':i+1,'side': "SELL", 'time':df.index[i+1], 'open': df['Open'][i+1], 'tp': tp, "sl": sl})

        return trades
        

    def result(result_, side, start, ep, cp, end):
        return {'result': result_, 'side': side, 'start_date': start, 'entry_price': ep, 'close_price': cp, 'end_date': end}

    @classmethod
    def perform_order(cls, side, tp, sl, cross_idx, cross_idx_list, df):
        k = cross_idx_list.index(cross_idx)  # index of the cross inside the list of all crosses indexes
        ep = df['Close'][cross_idx]
        start = df.index[cross_idx]
        # iterating through each candle between the crosses and identifying the results
        for i in range(cross_idx+1, cross_idx_list[k+1]):
            # long
            if side == "BUY":
                if df['High'][i] >= tp: return cls.result("win", side, start, ep, tp, df.index[i])  # return win if highest point higher than takeprofit price
                elif df['Low'][i] <= sl: return cls.result("loss", side, start, ep, sl, df.index[i]) # return loss if lowest point lower than stoploss price
            # short     
            elif side == "SELL":
                if df['High'][i] >= sl: return cls.result("loss", side, start, ep, sl, df.index[i]) # return loss if highest point higher than stoploss price
                elif df['Low'][i] <= tp: return cls.result("win", side, start, ep, tp, df.index[i]) # return win if lowest point lower than takeprofit price
        # execute if trade doesn't have a result till the next cross
        else:
            cp = df['Close'][cross_idx_list[k+1]]
            end = df.index[cross_idx_list[k+1]]
            if side == "BUY":
                if cp > sl: return cls.result('none', side, start, ep, cp, end)
                else: return cls.result('loss', side, start, ep, cp, end)
            elif side == "SELL":
                if cp < sl: return cls.result('none', side, start, ep, cp, end)
                else: return cls.result('loss', side, start, ep, cp, end)
   
    def get_pnl(ep, cp, side):
        qty = (LVG * CAPITAL_USD) / ep
        bought_for = qty * ep
        sold_for = qty * cp
        # Calculate total fee amount
        fee = FEE_RATE * LVG * CAPITAL_USD * 2
        return sold_for - bought_for - fee if side=="BUY" else bought_for - sold_for - fee

    @classmethod
    def get_detailed_orders(cls, df):
        trades = cls.get_trades(df)
        orders = []
        cross_idx_list = [i['index'] for i in trades]
        for i in range(len(trades)-1):
            order = cls.perform_order(trades[i]['side'], trades[i]['tp'], trades[i]['sl'], trades[i]['index'],cross_idx_list, df)
            pnl = cls.get_pnl(order['entry_price'], order['close_price'], order['side'])
            order['qty'] = (LVG*CAPITAL_USD) / order['entry_price']
            order['pnl'] = round(pnl, 3)
            orders.append(order)
        return orders
    
    @classmethod
    def get_results(cls, df, details=False):
        trades = cls.get_detailed_orders(df)
        wins,loss,nones,plus,minus,profit=0,0,0,0,0,0
        for i in trades:
            if details: return trades 
            profit += i['pnl']
            if i['pnl'] > 0: plus += 1
            else: minus += 1
            if i['result'] == 'win': wins += 1
            elif i['result'] == 'loss': loss += 1
            else: nones += 1
   
        try: return {"start_date": trades[0]['start_date'], "end_date": trades[-1]['start_date'], "wins": wins, 'losses': loss, 'till_next_cross': nones, 'profit': round(profit, 3), 'minus': minus, 'plus': plus}
        except IndexError: return "No trades for given period"


   





