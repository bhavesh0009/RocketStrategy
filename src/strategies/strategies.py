import os
import logging
import pandas as pd
from utils.utils import Utils
import sys

from controller.controller import Controller

class RocketStrategy:
    def __init__(self):
        self.config = Utils.get_config()
        self.obj = Controller.brokerLogin
        # self.rocket_stocks = self.read_rocket_stocks()

    def run_strategy(self):
        self.read_rocket_stocks()
        self.calculate_capital_per_stock()
        logging.info(f"Sleeping till {order_execution_time}")
        Utils.sleep_until_time(self.config['order_execution_time'])
        self.execute_strategy_for_symbols()
    
    def execute_strategy(self, stock_data, capital_per_stock):
        symbol = stock_data['Stock']
        signal = stock_data['Signal']
        ltp = get_ltp()
        quantity = floor(capital_per_stock / ltp, 0)
        self.read_screened_shares()
        df = self.screened_stocks
        buffer_entry = config['buffer_entry']
        buffer_trigger = config['buffer_trigger']

        if stock_data['Signal'] == 'buy':
            entry_price = df[df.symbol == symbol]['prev_low']
            trigger_price = entry_price + buffer_trigger
            order_price = round((entry_price * (1 + buffer_entry))/0.05) * 0.05
            if order_price < trigger_price:
                order_price = trigger_price + 0.05
            self.obj.order_place()
            logging.info("placing buy order with trigger price {trigger_price} and order price {order_price}.")
        elif stock_data['Signal'] == 'sell':
            entry_price = df[df.symbol == symbol]['prev_high']
            trigger_price = entry_price - buffer_trigger
            order_price = round((entry_price * (1 - buffer_entry))/0.05) * 0.05
            if order_price > trigger_price:
                order_price = trigger_price - 0.05
            logging.info("placing sell order with trigger price {trigger_price} and order price {order_price}.")

    def read_rocket_stocks(self):
        today_date = pd.Timestamp.now().strftime('%Y%m%d')
        file_path = os.path.join('data', f'rocket_shortlisted_{today_date}.csv')
        if os.path.isfile(file_path):
            df = pd.read_csv(file_path)
            if df.shape[0] == 0:
                logging.info("No stocks for Rocket Strategy. Exiting the code.")
                sys.exit()
            else:
                self.rocket_stocks = df.to_dict('records')

    def read_screened_shares(self):
        #today = datetime.today().strftime("%Y_%m_%d")
        today = '2023_06_19' # Hardcoding to test on weekend.
        filename = os.path.join("data", f"screened_stocks_{today}.csv")
        self.screened_stocks = pd.read_csv(filename)
        # return self.screened_stocks
        # self.screened_stocks = df.to_dict('records')

    def calculate_capital_per_stock(self):
        self.num_stocks = len(self.rocket_stocks)
        self.capital_per_stock = round(self.config['capital'] / num_stocks, 0)

    def execute_strategy_for_symbols(self):
        threads = []
        for stock_data in self.rocket_stocks:
            thread = threading.Thread(target=self.execute_strategy, args=(stock_data, self.capital_per_stock))
            thread.start()
            threads.append(thread)

        # Wait for all threads to complete
        for thread in threads:
            thread.join()        
