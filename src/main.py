import pandas as pd
import os
import yaml
import sys
import logging
from utils.utils import Utils
from stock_scanner.stock_screener import StockScreener
from rocket_screener.rocket_screener import RocketScreener

from controller.controller import Controller


def initLoggingConfg():
  format = "%(asctime)s: %(message)s"
  logging.basicConfig( format=format, level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")

initLoggingConfg()

# Read the stock symbols from universe.csv
universe_df = pd.read_csv('data/universe.csv')
stock_symbols = universe_df['Symbol'].tolist()
stock_symbols = list(map(str.strip, stock_symbols))

# Read the threshold values from the YAML file
root_dir = os.path.dirname(os.path.dirname(__file__))
yaml_path = os.path.join(root_dir, 'config', 'config.yaml')
with open(yaml_path, 'r') as yaml_file:
    config = yaml.safe_load(yaml_file)

threshold_positive = config['threshold_positive']
threshold_negative = config['threshold_negative']
target_time = config['target_time']
controller = Controller()
controller.generate_smart_connect_object()

screener = StockScreener(stock_symbols, threshold_positive, threshold_negative)
screener.run_scan()


# Access the short-listed stocks
short_listed_stocks = screener.short_listed_stocks

# Convert short_listed_stocks to a pandas DataFrame
df = pd.DataFrame(short_listed_stocks)
short_symbols = df[df.flag==1].symbol.to_list()
long_symbols = df[df.flag==-1].symbol.to_list()
total_scans = str(df.shape[0])
if len(long_symbols) > 0:
    logging.info(f"Found following stocks for long: {long_symbols}")
if len(short_symbols) > 0:
    logging.info(f"Found following stocks for short: {short_symbols}")
if total_scans == df[df.flag==0].shape:
    logging.info(f"Scanned {total_scans} stocks but found 0 stock after scanning.")
df[~(df.flag==0)].to_csv(r"data\screened_stocks.csv", index=False)    
df.to_csv(r"data\universe_stock_with_pivots.csv")

Utils.sleep_until_time(target_time)

rs = RocketScreener()
rs.screen_stocks()

