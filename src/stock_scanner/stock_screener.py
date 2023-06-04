import yfinance as yf
import pandas as pd
from datetime import date, timedelta, datetime, time
import time
import logging
import pytz
import yaml

class StockScreener:
    def __init__(self, stock_symbols, threshold_positive, threshold_negative):
        self.stock_symbols = stock_symbols
        self.threshold_positive = threshold_positive
        self.threshold_negative = threshold_negative
        self.short_listed_stocks = []

    @staticmethod
    def sleep_until_time(target_time):
        target_time = datetime.strptime(target_time, '%H:%M:%S').time()
        current_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_diff = datetime.combine(date.today(), target_time) - datetime.combine(date.today(), current_time)
        sleep_duration = time_diff.total_seconds()

        logging.info(f"Sleeping for {sleep_duration} seconds.")
        if sleep_duration > 0:
            time.sleep(sleep_duration)
        logging.info("Target time reached. Continue with the rest of the code.")

    def run_scan(self):
        logging.info("Running scan...")
        for symbol in self.stock_symbols:
            stock_data = self.fetch_stock_data(symbol)
            if stock_data is None:
                logging.warning("No data found for {symbol}.")

            percent_return = self.calculate_percent_return(stock_data)
            flag = self.check_flag(percent_return)
            pivot_points = self.calculate_pivot_points(stock_data)

            stock_dict = {
                'symbol': symbol,
                'flag': flag,
                'percent_return': percent_return,
                **pivot_points
            }
            self.short_listed_stocks.append(stock_dict)
            time.sleep(0.5)
        logging.info("Scan completed.")

    def run_current_day_scan(self):
        pass

    def fetch_stock_data(self, symbol):
        symbol_ns = symbol + ".NS"
        end_date = date.today() - timedelta(days=1)
        start_date = end_date - timedelta(days=7)
        stock_data = yf.download(symbol_ns, start=start_date, end=end_date)

        if stock_data.empty:
            self.logger.warning(f"No data available for stock: {symbol}")
            return None

        return stock_data

    def calculate_percent_return(self, stock_data):
        stock_data['Prev Close'] = stock_data['Close'].shift(1)
        stock_data['% Return'] = (stock_data['Close'] - stock_data['Prev Close']) / stock_data['Prev Close'] * 100
        return stock_data['% Return'].iloc[-1]

    def check_flag(self, percent_return):
        if percent_return > self.threshold_positive:
            return 1
        elif percent_return < self.threshold_negative:
            return -1
        else:
            return 0

    def calculate_pivot_points(self, stock_data):
        prev_high = stock_data['High'].iloc[-1]
        prev_low = stock_data['Low'].iloc[-1]
        prev_close = stock_data['Close'].iloc[-1]
        pivot = (prev_high + prev_low + prev_close) / 3
        res1 = 2 * pivot - prev_low
        res2 = pivot + (res1 - (2 * pivot - prev_high))
        res3 = prev_high + 2 * (pivot - prev_low)
        sup1 = 2 * pivot - prev_high
        sup2 = pivot - (res1 - sup1)
        sup3 = prev_low - 2 * (prev_high - pivot)

        pivot_points = {
            'prev_high': prev_high,
            'prev_low': prev_low,
            'PIVOT': pivot,
            'RES1': res1,
            'RES2': res2,
            'RES3': res3,
            'SUP1': sup1,
            'SUP2': sup2,
            'SUP3': sup3
        }

        return pivot_points
