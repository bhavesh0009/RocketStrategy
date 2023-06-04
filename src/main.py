import pandas as pd
from stock_scanner.stock_screener import StockScreener
import os
import yaml
import sys
import logging

def initLoggingConfg():
  format = "%(asctime)s: %(message)s"
  logging.basicConfig( format=format, level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")

# Redirect stdout to null device to suppress yfinance output
sys.stdout = open(os.devnull, "w")

initLoggingConfg()

# Read the stock symbols from universe.csv
universe_df = pd.read_csv('data/universe.csv')
stock_symbols = universe_df['Symbol'].tolist()

# Read the threshold values from the YAML file
root_dir = os.path.dirname(os.path.dirname(__file__))
yaml_path = os.path.join(root_dir, 'config', 'config.yaml')
with open(yaml_path, 'r') as yaml_file:
    config = yaml.safe_load(yaml_file)

threshold_positive = config['threshold_positive']
threshold_negative = config['threshold_negative']
target_time = config['target_time']

# Create an instance of StockScreener and run the scan
screener = StockScreener(stock_symbols, threshold_positive, threshold_negative)
screener.run_scan()

# Access the short-listed stocks
short_listed_stocks = screener.short_listed_stocks

# Convert short_listed_stocks to a pandas DataFrame
df = pd.DataFrame(short_listed_stocks)
long_symbols = df[df.flag==1].symbol.to_list()
short_symbols = df[df.flag==-1].symbol.to_list()
total_scans = str(df.shape[0])
if len(long_symbols) > 0:
    logging.info(f"Found following stocks for long: {long_symbols}")
elif len(short_symbols) > 0:
    logging.info(f"Found following stocks for short: {short_symbols}")
else:
    logging.info(f"Scanned {total_scans} stocks but found 0 stock after scanning.")

screener.sleep_until_time(target_time)