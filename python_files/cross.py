from bybithandler import *
from ta.trend import EMAIndicator
import time

ema_window_1 = 100 # Long Term EMA
ema_window_2 = 20 # Short Term EMA


def ema_difference(df):
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

