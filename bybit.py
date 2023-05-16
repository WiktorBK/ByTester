from pybit import HTTP
import pandas as pd
from datetime import datetime
import calendar
import traceback
from config import *

class Bybit:
    def __init__(self):
        self.session = self.open_session()

    def open_session(self):
        try: return HTTP("https://api.bybit.com", request_timeout= 60)
        except: print(f"Couldn't open session:\n {traceback.format_exc()}")

 
        


