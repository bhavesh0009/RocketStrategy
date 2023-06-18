import pandas as pd
import os
import yaml
import sys
import logging
from utils.utils import Utils
from stock_scanner.stock_screener import StockScreener
from super_rocket.super_rocket import SuperRocket
from strategies.strategies import RocketStrategy
from controller.controller import Controller


def initLoggingConfg():
  format = "%(asctime)s: %(message)s"
  logging.basicConfig( format=format, level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")

initLoggingConfg()

config = Utils.get_config()
threshold_positive = config['threshold_positive']
threshold_negative = config['threshold_negative']
target_time = config['target_time']
share_price_min_threshold = config['share_price_min_threshold']
share_price_max_threshold = config['share_price_max_threshold']

# Commenting following code to run on weekend.
# if Utils.isTodayHoliday():
#     logging.info("Today is a weekend or holiday. Skipping the execution of the code.")
#     sys.exit()

universe_df = pd.read_csv('data/universe.csv')
universe_df = universe_df[~(universe_df.Disabled.str.upper() =='Y')]
stock_symbols = universe_df['Symbol'].tolist()
stock_symbols = list(map(str.strip, stock_symbols))

controller = Controller()
controller.generate_login_object()

screener = StockScreener(stock_symbols, threshold_positive, threshold_negative)
screener.run_scan()

#Utils.sleep_until_time(target_time)

sr = SuperRocket()
sr.screen_stocks()

rs = RocketStrategy()
rs.run_strategy()

