import os
import pandas as pd
from datetime import datetime, timedelta,  time as dt_time
import time
from controller.controller import Controller
import yaml
from utils.utils import Utils
import logging

class SuperRocket:
    def __init__(self):
        self.rocket_stocks = {}
        self.broker_name = Controller.brokerName
        self.obj = Controller.brokerLogin

    def screen_stocks(self):
        self.get_start_scan_time()
        self.read_screened_stocks()
        Utils.sleep_until_time(self.target_time)
        self.process_stocks()
        self.export_rocket_stocks()
    
    def get_start_scan_time(self):
        config = Utils.get_config()
        self.target_time = config['target_time']

    def read_screened_stocks(self):
        now = datetime.now()
        # cutoff_time = datetime.combine(now.date(), dt_time(15, 30))
        # logging.info(now)
        # logging.info(cutoff_time)
        # if now < cutoff_time:
        #     date_str = (now - timedelta(days=1)).strftime("%Y_%m_%d")
        # else:
        date_str = now.strftime("%Y_%m_%d")        
        filename = os.path.join("data", f"screened_stocks_{date_str}.csv")
        df = pd.read_csv(filename)
        self.screened_stocks = df.to_dict('records')

    def process_stocks(self):
        symbol_token_mapping = pd.read_csv('data/symbol_token_mapping.csv').set_index('symbol')['token'].to_dict()
        # Check if the current time is after 9:14:00 am
        current_time = datetime.now().time()
        target_time_obj = datetime.strptime(self.target_time, "%H:%M:%S").time()
        if current_time >= target_time_obj:
            for stock in self.screened_stocks:
                symbol = stock['symbol']
                flag = int(stock['flag'])
                # percent_return = float(stock['percent_return'])
                token = str(symbol_token_mapping.get(symbol))
                # resp = self.obj.scriptinfo("NSE", token)
                resp = self.obj.get_quotes("NSE",token)
                logging.info(resp)
                ltp = float(resp['o'])
                previous_day_high = stock['prev_high']
                previous_day_low = stock['prev_low']
                if flag == 1 and ltp > previous_day_high:
                    self.rocket_stocks[symbol] = "sell"
                elif flag == -1 and ltp < previous_day_low:
                    self.rocket_stocks[symbol] = "buy"

    def export_rocket_stocks(self):
        current_date = datetime.now().strftime("%Y%m%d")
        filename = os.path.join("data", f"rocket_shortlisted_{current_date}.csv")
        df = pd.DataFrame.from_dict(self.rocket_stocks, orient='index', columns=['Signal'])
        df.reset_index(inplace=True)
        df.columns = ['Stock', 'Signal']
        # df = pd.DataFrame({"symbol": self.rocket_stocks})
        df.to_csv(filename, index=False)