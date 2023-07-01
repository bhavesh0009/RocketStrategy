import os
import logging
import pandas as pd
from utils.utils import Utils
import sys
from math import floor,ceil
import threading
import time
from datetime import datetime, timedelta,  time as dt_time

from controller.controller import Controller

class RocketStrategy:
    def __init__(self):
        self.config = Utils.get_config()
        self.obj = Controller.brokerLogin
        self.norenObj = Controller.norenLogin

    def run_strategy(self):
        self.read_rocket_stocks()
        self.calculate_capital_per_stock()
        logging.info(f"Sleeping till {self.config['order_execution_time']}")
        Utils.sleep_until_time(self.config['order_execution_time'])
        self.execute_strategy_for_symbols()
    
    def execute_strategy(self, stock_data, capital_per_stock):
        symbol = stock_data['Stock']
        signal = stock_data['Signal']
        symbol_token_mapping = pd.read_csv('data/symbol_token_mapping.csv').set_index('symbol')['token'].to_dict()
        token = symbol_token_mapping.get(symbol)
        # resp = self.obj.scriptinfo("NSE", str(token))
        # ltp = float(resp['lp'])
        resp = self.obj.get_quotes("NSE",str(token))
        ltp = float(resp['lp'])
        total_quantity = floor(capital_per_stock / ltp, 0)
        # hardcoding quantity as 1 for testing purpose.
        # quantity = 1
        self.read_screened_shares()
        df = self.screened_stocks
        buffer_entry = self.config['buffer_entry']
        buffer_trigger = self.config['buffer_trigger']
        stop_loss = self.config['stop_loss']
        target1 = self.config['target1']
        target2 = self.config['target2']
        target3 = self.config['target3']
        target1_quantity = ceil(total_quantity * self.config['target1_quantity_pct'])
        target2_quantity = ceil((total_quantity - target1_quantity) * (self.config['target2_rem_quantity_pct']))
        target3_quantity = total_quantity - target1_quantity - target2_quantity

        if signal == 'buy':
            entry_price = df[df.symbol == symbol]['prev_low'].values[0]
            trigger_price = entry_price + buffer_trigger
            order_price = round((entry_price * (1 + buffer_entry))/0.05) * 0.05
            order_price = max(order_price, trigger_price + 0.5)
            stop_loss_price = order_price * (1 - stop_loss)
            target1_price = order_price * (1 + target1)
            target2_price = order_price * (1 + target2)
            target3_price = order_price * (1 + target3)
            opposite_trans_type = self.norenObj.TRANSACTION_TYPE_SELL
            logging.info(f"Placing buy order for {symbol} {total_quantity} quantity with trigger price {trigger_price} and order price {order_price}.")
            # entry_order_id = self.obj.order_place(side="B", product="I",
            #       exchange="NSE", symbol=symbol, 
            #       quantity=total_quantity, order_type="SL-L",
            #       validity='DAY', 
            #       price=order_price, 
            #       trigger_price=trigger_price
            #       )
            entry_order_id = self.obj.place_order(buy_or_sell="B", product_type="I",
                exchange="NSE", tradingsymbol=symbol + "-EQ", 
                quantity=total_quantity, price_type="SL-LMT",
                retention='DAY', 
                price=order_price, 
                trigger_price=trigger_price
                )            
            logging.info(f"Buy order placed. Order id is {entry_order_id}")
        elif  signal == 'sell':
            entry_price = df[df.symbol == symbol]['prev_high'].values[0]
            trigger_price = entry_price - buffer_trigger
            order_price = round((entry_price * (1 - buffer_entry))/0.05) * 0.05
            order_price = min(order_price, trigger_price - 0.5)
            stop_loss_price = order_price * (1 + stop_loss)
            target1_price = order_price * (1 - target1)
            target2_price = order_price * (1 - target2)
            target3_price = order_price * (1 - target3)
            opposite_trans_type = self.norenObj.TRANSACTION_TYPE_BUY
            logging.info(f"placing sell order with trigger price {trigger_price} and order price {order_price}.")
            # entry_order_id = self.obj.order_place(side="S", product="I",
            #       exchange="NSE", symbol=symbol, 
            #       quantity=total_quantity, order_type="SL-L",
            #       validity='DAY', 
            #       price=order_price, trigger_price=trigger_price
            #       )
            entry_order_id = self.obj.place_order(buy_or_sell="S", product_type="I",
                exchange="NSE", tradingsymbol=symbol + "-EQ", 
                quantity=total_quantity, price_type="SL-LMT",
                retention='DAY', 
                price=order_price, 
                trigger_price=trigger_price
                )                 
            logging.info(f"Sell order placed. Order id is {entry_order_id}")

        while True:
            orders = pd.DataFrame(self.obj.orders)
            entry_order_status = orders[orders.order_id==entry_order_id]['status'].values[0]
            if entry_order_status == "REJECTED":
                rejection_reason = orders[orders.order_id==entry_order_id]['rejreason']
                logging.info(f"Order rejected with reason : {rejection_reason}. Exiting the code")
                sys.exit()
            elif entry_order_status == "EXECUTED":
                oco_order_id1 = self.norenObj.place_gtt_oco_mkt_order(
                        symbol + "EQ",
                        "NSE",
                        target1_price,
                        stop_loss_price,
                        opposite_trans_type,
                        self.norenObj.PRODUCT_TYPE_INTRADAY,
                        target1_quantity,
                    )         
                oco_order_id2 = self.norenObj.place_gtt_oco_mkt_order(
                        symbol + "EQ",
                        "NSE",
                        target2_price,
                        stop_loss_price,
                        opposite_trans_type,
                        self.norenObj.PRODUCT_TYPE_INTRADAY,
                        target2_quantity,
                    )         
                oco_order_id3 = self.norenObj.place_gtt_oco_mkt_order(
                        symbol + "EQ",
                        "NSE",
                        target3_price,
                        stop_loss_price,
                        opposite_trans_type,
                        self.norenObj.PRODUCT_TYPE_INTRADAY,
                        target3_quantity,
                    )         
                break
            else:
                time.sleep(5)
        # Keep checking order status for target 2 order, if executed than trail stop-loss of oco_order_id3
        while True:
            logging.info("Checking for target2 hit.")
            orders = pd.DataFrame(self.obj.orders)
            target2_order_status = orders[orders.order_id==oco_order_id2]['status'].values[0]
            if target2_order_status == "REJECTED":
                rejection_reason = orders[orders.order_id==oco_order_id2]['rejreason']
                logging.info(f"Order rejected with reason : {rejection_reason}. Exiting the code")
            elif entry_order_status == "EXECUTED":
                alert_id = self.norenObj.modify_gtt_oco_mkt_order(
                            symbol + "EQ",
                            "NSE",
                            oco_order_id3,
                            target3_price,
                            order_price,
                            opposite_trans_type,
                            self.norenObj.PRODUCT_TYPE_INTRADAY,
                            target3_quantity
                        )
            else:
                time.sleep(5)



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
        today = datetime.today().strftime("%Y_%m_%d")
        filename = os.path.join("data", f"screened_stocks_{today}.csv")
        self.screened_stocks = pd.read_csv(filename)
        # return self.screened_stocks
        # self.screened_stocks = df.to_dict('records')

    def calculate_capital_per_stock(self):
        self.num_stocks = len(self.rocket_stocks)
        self.capital_per_stock = round(self.config['capital'] / self.num_stocks, 0)
        logging.info(f"Allocation capital Rs.{self.capital_per_stock} to each stock")

    def execute_strategy_for_symbols(self):
        threads = []
        for stock_data in self.rocket_stocks:
            thread = threading.Thread(target=self.execute_strategy, args=(stock_data, self.capital_per_stock))
            thread.start()
            threads.append(thread)

        # Wait for all threads to complete
        for thread in threads:
            thread.join()        
