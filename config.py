SYMBOLS =  ['SOLUSDT','BNBUSDT', 'ETHUSDT','ADAUSDT', 'MATICUSDT', 'LTCUSDT']

MONTHS = 1 # for higher values the program will run slower

INTERVAL = '5'

CAPITAL_USD = 1 # per one pair
LVG = 20 
FEE_RATE = 0.0006 # % / 100


EMA1 = 200 # long term ema window
EMA2 = 50 # short term ema window

TP_PERC = 0.0125 # takeprofit percentage
SL_PERC = 0.01 # stoploss percentage



# ! Do not change !  
MONTH_SEC = 2629800 # seconds in one month
CANDLES200_SEC = int(INTERVAL) * 60 * 200 # 200 candles in seconds
PERIOD_MONTH_PERC = CANDLES200_SEC/MONTH_SEC # Percentage of 200candles period in one month
PERIODS_PER_MONTH = MONTH_SEC/CANDLES200_SEC # amount of 200candles periods in one month 
