import time
import logging
from datetime import date, timedelta, datetime,  time as dt_time
from controller.controller import Controller
import pandas as pd
from tqdm import tqdm
import os
from utils.utils import Utils
import json
import urllib.parse

# import yfinance as yf


class StockScreener:
    def __init__(self, stock_symbols, threshold_positive, threshold_negative):
        self.stock_symbols = stock_symbols
        self.threshold_positive = threshold_positive
        self.threshold_negative = threshold_negative
        self.short_listed_stocks = []
        self.obj = Controller.brokerLogin
        self.broker_name = Controller.brokerName
    
    def getEpoch(self, datetimeObj = None):
        if datetimeObj == None:
            datetimeObj = datetime.now()
        epochSeconds = datetime.timestamp(datetimeObj)
        return int(epochSeconds)

    def get_symbol_to_token_mapping(self):
        logging.info("Mapping symbol to token..")
        today = date.today()
        last_run_file = "data/last_run_date.txt"
        if os.path.exists(last_run_file):
            with open(last_run_file, "r") as file:
                last_run_date_str = file.read()
                last_run_date = date.fromisoformat(last_run_date_str)
                
                if last_run_date == today:
                    logging.info("Mapping has already been run today. Skipping refresh.")
                    mapping_df = pd.read_csv("data/symbol_token_mapping.csv")
                    self.symbol_token_mapping = mapping_df
                    return        
        universe_df = pd.read_csv("data/universe.csv")
        symbol_to_token = {}
        for symbol in universe_df["Symbol"]:
            # token = self.obj.instrument_symbol("NSE", symbol + "-EQ")
            resp = self.obj.searchscrip(exchange='NSE', searchtext=symbol + "-EQ")
            token = resp['values'][0]['token']
            symbol_to_token[symbol] = token  

        # Store the symbol-to-token mapping in a file
        mapping_file = "data/symbol_token_mapping.csv"
        mapping_df = pd.DataFrame(symbol_to_token.items(), columns=["symbol", "token"])
        self.symbol_token_mapping = mapping_df
        mapping_df.to_csv(mapping_file, index=False)            
        # Update the last run date
        with open(last_run_file, "w") as file:
            file.write(str(today))        
                
        logging.info("Symbol to token mapping is refreshed.")

    def get_next_trading_day(self):
        current_time = datetime.now().time()
        if current_time.hour < 15 or (current_time.hour == 15 and current_time.minute < 31):
            return date.today().strftime('%Y_%m_%d')
        today = date.today()
        tomorrow = today + timedelta(days=1)
        holidays_df = pd.read_csv("config/holidays.csv")
        holidays = set(holidays_df["date"])
        while tomorrow.weekday() in (5, 6) or tomorrow.strftime("%Y-%m-%d") in holidays:
            tomorrow += timedelta(days=1)
        return tomorrow.strftime('%Y_%m_%d')
    
    def check_last_run(self):
        next_trading_day = self.get_next_trading_day()
        filename = f"data/screened_stocks_{next_trading_day}.csv"
        if os.path.exists(filename):
            return True
        else:
            return False

    def run_scan(self):
        if not self.check_last_run():
            logging.info("Running scan...")
            self.get_symbol_to_token_mapping()
            logging.info("Getting stock data...")
            for symbol in  tqdm(self.stock_symbols, desc="Processing", unit="symbol"):
                stock_data = self.fetch_stock_data(symbol)
                if stock_data.shape[0] == 0:
                    logging.warning(f"No data found for {symbol}.")
                else:
                    percent_return = self.calculate_percent_return(stock_data)
                    flag = self.check_flag(percent_return)
                    prev_close = stock_data['Close'].iloc[-1]
                    prev_high = stock_data['High'].iloc[-1]
                    prev_low = stock_data['Low'].iloc[-1]
                    pivot_points = self.calculate_pivot_points(stock_data)

                    stock_dict = {
                        'symbol': symbol,
                        'flag': flag,
                        'percent_return': percent_return,
                        'prev_high': prev_high,
                        'prev_low' : prev_low,
                        'prev_close' : prev_close,
                        **pivot_points
                    }
                    self.short_listed_stocks.append(stock_dict)
                    time.sleep(0.01)
            self.process_shortlisted_stocks(self.short_listed_stocks)
            logging.info("Scan completed.")
        else:
            logging.info("Shortlisted stocks are already present.")

    def process_shortlisted_stocks(self, short_listed_stocks):
        df = pd.DataFrame(short_listed_stocks)
        config = Utils.get_config()
        df = df[(df.prev_close > config['share_price_min_threshold']) & (df.prev_close < config['share_price_max_threshold'])]
        short_symbols = df[df.flag==1].symbol.to_list()
        long_symbols = df[df.flag==-1].symbol.to_list()
        total_scans = str(df.shape[0])
        if len(long_symbols) > 0:
            logging.info(f"Found following stocks for long: {long_symbols}")
        if len(short_symbols) > 0:
            logging.info(f"Found following stocks for short: {short_symbols}")
        if total_scans == df[df.flag==0].shape[0]:
            logging.info(f"Scanned {total_scans} stocks but found 0 stock after scanning.")
        next_trading_day = self.get_next_trading_day()
        df.to_csv(os.path.join("data", f"universe_stocks_{next_trading_day}.csv"), index=False)
        df[~(df.flag==0)].to_csv(os.path.join("data", f"screened_stocks_{next_trading_day}.csv"), index=False)

    def fetch_stock_data(self, symbol):
        logging.debug("Running fuction fetch_stock_data.")
        symbol_eq = symbol #+ "-EQ"  # Add "-EQ" to the symbol
        encoded_symbol = urllib.parse.quote(symbol_eq + "-EQ")
        token = self.symbol_token_mapping.loc[self.symbol_token_mapping["symbol"] == symbol_eq, "token"].values[0]
        current_time = datetime.now().time()
        end_date = date.today()
        start_date = end_date - timedelta(days=7)  # 7 days before the end date
        start_datetime = datetime.combine(start_date, dt_time.min)
        end_datetime = datetime.combine(end_date, dt_time.max)
        if current_time < dt_time(15, 31):
            end_datetime -= timedelta(days=1)  # Yesterday's date
        elif current_time >= dt_time(15, 31):
            end_datetime = datetime.combine(end_date, dt_time.max)  # Today's date        
        exchange = "NSE"
        start_datetime = self.getEpoch(start_datetime)
        end_datetime = self.getEpoch(end_datetime)
        # quote_history = self.obj.historical(exchange, str(token),start_datetime ,end_datetime)
        quote_history = self.get_history(exchange, str(token), encoded_symbol, start_datetime , end_datetime)
        logging.debug(f"Total records recieved : {len(quote_history)}")
        stock_data = self.process_history_data(quote_history)
        return stock_data

    def get_history(self, exchange, token, symbol, start_datetime, end_datetime):
        logging.debug("Running fuction get_history.")
        max_retries = 3
        retry_delay = 5
        for retry in range(max_retries):
            try:
                # logging.info(symbol)
                try:
                    quote_history = self.obj.get_daily_price_series(exchange, symbol, start_datetime, end_datetime)
                except Exception as e:             
                    logging.warning(f"Error occurred while fetching data for {symbol}: {str(e)}")    
                    quote_history = []       
                # daily_prices = api.get_daily_price_series("NSE","SBIN-EQ","1687458600","1688063399")
                # logging.debug(f"Total records recieved : {len(quote_history)}")
                if len(quote_history) == 0:
                    logging.warning(f"No data found for {symbol}")
                    time.sleep(retry_delay)
                else:
                    break  
            except Exception as e:
                logging.warning(f"Error occurred while fetching data for {symbol}: {str(e)}")
                time.sleep(retry_delay)
        return quote_history

    def process_history_data(self, quote_history):
        quote_history = [json.loads(json_str) for json_str in quote_history]
        logging.debug("Running fuction process_history_data.")
        logging.debug(f"Total records recieved : {len(quote_history)}")
        columns=['time', 'into', 'inth', 'intl', 'intc','ssboe', 'intv']
        df = pd.DataFrame(quote_history, columns=columns)
        logging.debug(f"Shape of dataframe is {df.shape}")
        df = df.drop(['ssboe'], axis=1)
        df['time'] = pd.to_datetime(df['time'])
        df = df.rename(columns={'time': 'Date', 'into': 'Open', 'inth': 'High', 'intl': 'Low', 'intc': 'Close', 'intv': 'Volume'})
        # unique_dates = df['Date'].dt.date.unique()
        # df = df.set_index('Date')
        for c in ['Open','High','Low','Close']:
            df[c] = df[c].astype('float')
        # df['Volume'] = df['Volume'].astype('int')    
        # df_daily = df.resample('D').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'})
        # df_daily = df_daily.reset_index()
        # df_daily['Date'] = pd.to_datetime(df_daily['Date'])
        # df_daily = df_daily[df_daily['Date'].dt.date.isin(unique_dates)]
        return df
         

    def calculate_percent_return(self, stock_data):
        stock_data['Prev Close'] = stock_data['Close'].shift(1)
        stock_data['% Return'] = (stock_data['Close'] - stock_data['Prev Close']) / stock_data['Prev Close'] * 100
        return round(stock_data['% Return'].iloc[-1], 2)

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
        pivot = round((prev_high + prev_low + prev_close) / 3, 2)
        res1 = round(2 * pivot - prev_low, 2)
        res2 = round(pivot + (res1 - (2 * pivot - prev_high)), 2)
        res3 = round(prev_high + 2 * (pivot - prev_low), 2)
        sup1 = round(2 * pivot - prev_high, 2)
        sup2 = round(pivot - (res1 - sup1), 2)
        sup3 = round(prev_low - 2 * (prev_high - pivot), 2)

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
