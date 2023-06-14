import time
import logging
from datetime import date, timedelta, datetime
from controller.controller import Controller
import yaml
import pandas as pd
from tqdm import tqdm
# import yfinance as yf


class StockScreener:
    def __init__(self, stock_symbols, threshold_positive, threshold_negative):
        self.stock_symbols = stock_symbols
        self.threshold_positive = threshold_positive
        self.threshold_negative = threshold_negative
        self.short_listed_stocks = []
        self.obj = Controller.brokerLogin
        self.broker_name = Controller.brokerName

    def get_symbol_to_token_mapping(self):
        logging.info("Mapping symbol to token..")
        url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        df = pd.read_json(url)
        nse_symbols = df[df["exch_seg"] == "NSE"]
        symbol_token_mapping = nse_symbols[nse_symbols.symbol.str.endswith('EQ')][["symbol", "token"]]
        symbol_token_mapping.to_csv("data/symbol_token_mapping.csv", index=False)
        self.symbol_token_mapping = symbol_token_mapping
        logging.info("Symbol to token mapping is done.")

    def run_scan(self):
        logging.info("Running scan...")
        # self.load_credentials()
        # self.generate_smart_connect_object()
        self.get_symbol_to_token_mapping()
        logging.info("Getting stock data...")
        for symbol in  tqdm(self.stock_symbols, desc="Processing", unit="symbol"):
            stock_data = self.fetch_stock_data(symbol)
            #logging.info(symbol, stock_data)
            if stock_data is None:
                logging.warning(f"No data found for {symbol}.")
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
            time.sleep(0.05)
        logging.info("Scan completed.")

    def run_pre_open_scan(self):
        pass

    def fetch_stock_data(self, symbol):
        symbol_eq = symbol + "-EQ"  # Add "-EQ" to the symbol
        token = self.symbol_token_mapping.loc[self.symbol_token_mapping["symbol"] == symbol_eq, "token"].values[0]
        current_time = datetime.now().time()
        end_date = date.today()
    
        if current_time < datetime.strptime("10:15", "%H:%M").time():
            end_date -= timedelta(days=1)  # Yesterday's date
        elif current_time >= datetime.strptime("16:00", "%H:%M").time():
            end_date = date.today()  # Today's date
        start_date = end_date - timedelta(days=7)  # 7 days before the end date
        
        historical_param = {
        "exchange": "NSE",
        "symboltoken": token,
        "interval": "ONE_DAY",
        "fromdate": start_date.strftime("%Y-%m-%d") + " 00:00",
        "todate": end_date.strftime("%Y-%m-%d") + " 23:59"}
        try:
            history = self.obj.getCandleData(historical_param)['data']
        except:
            logging.warning(f"Got an error while fetching data for {symbol}")
            time.sleep(2)
        stock_data = pd.DataFrame(history)
        stock_data.columns = ['Date','Open','High','Low','Close','Volume']
        return stock_data

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
