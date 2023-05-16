from ta.trend import EMAIndicator

from config import *


class Strategy:

    def ema_difference(df):
        ema_difference = []
        df[f'ema{EMA1}'] = EMAIndicator(df['Close'], EMA1).ema_indicator()
        df[f'ema{EMA2}'] = EMAIndicator(df['Close'], EMA2).ema_indicator()
        
        # Calculate difference between two emas and append to a list
        for i in range(len(df[f'ema{EMA2}'])):
            ema_difference.append(df[f'ema{EMA2}'][i] - df[f'ema{EMA1}'][i])

        return ema_difference

        
        