import os
import pandas as pd
from datetime import datetime, time
import time
from controller.controller import Controller
import yaml
from utils.utils import Utils
import logging

class RocketScreener:
    def __init__(self):
        self.capital = 100000
        self.rocket_stocks = []
        self.broker_name = Controller.brokerName
        self.obj = Controller.brokerLogin

    def screen_stocks(self):
        self.get_start_scan_time()
        Utils.sleep_until_time(self.target_time)
        self.read_screened_stocks()
        self.process_stocks()
        self.export_rocket_stocks()
    
    def get_start_scan_time(self):
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        yaml_path = os.path.join(root_dir, 'config', 'config.yaml')
        with open(yaml_path, 'r') as yaml_file:
            config = yaml.safe_load(yaml_file)
        self.target_time = config['target_time']

    def read_screened_stocks(self):
        filename = os.path.join("data", "screened_stocks.csv")
        df = pd.read_csv(filename)
        self.screened_stocks = df.to_dict('records')

    def process_stocks(self):
        symbol_token_mapping = pd.read_csv('data/symbol_token_mapping.csv').set_index('symbol')['token'].to_dict()
        # Get the current time
        current_time = datetime.now().time()
        # Check if the current time is after 9:14:00 am
        target_time_obj = datetime.strptime(self.target_time, "%H:%M:%S").time()
        if current_time >= target_time_obj:
            for stock in self.screened_stocks:
                symbol = stock['symbol']
                flag = int(stock['flag'])
                percent_return = float(stock['percent_return'])

                token = symbol_token_mapping.get(f"{symbol}-EQ")
                ltp = self.obj.ltpData("NSE", f"{symbol}-EQ",token)
                ltp = ltp['data']['open']
                # Get the previous day's high and low (assuming you have a method to retrieve it)
                previous_day_high = stock['prev_high']
                previous_day_low = stock['prev_low']

                # Check the flag and compare LTP with the previous day's high or low
                
                if flag == 1 and ltp > previous_day_high:
                    self.rocket_stocks.append(symbol)
                elif flag == -1 and ltp < previous_day_low:
                    self.rocket_stocks.append(symbol)

    def export_rocket_stocks(self):
        current_date = datetime.now().strftime("%Y%m%d")
        filename = os.path.join("data", f"rocket_shortlisted_{current_date}.csv")
        df = pd.DataFrame({"symbol": self.rocket_stocks})
        df.to_csv(filename, index=False)