from toolkit.fileutils import Fileutils
from omspy_brokers.finvasia import Finvasia
import logging
from pprint import pprint
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)

sec_dir = "../../../"
m = Fileutils().get_lst_fm_yml(sec_dir + "profitmart.yaml")
pmart = Finvasia(user_id=m['uid'], password=m['pwd'], pin=m['factor2'],
                 vendor_code=m['vc'], app_key=m['app_key'], imei="1234",
                 broker="profitmart")
if pmart.authenticate():
    print("success")

token = pmart.instrument_symbol("NSE", "SBIN-EQ")
resp = pmart.scriptinfo("NSE", token)
print(resp)


"""
pmart.finvasia.place_order(buy_or_sell='B', product_type='B', exchange='NSE',
                           tradingsymbol='INFY-EQ', quantity=2, discloseqty=1,
                           price_type='LMT', price=1500, trigger_price=None,
                           retention='DAY', remarks='my_order_001',
                           bookloss_price=1490, bookprofit_price=1510)
pmart.order_place(side='B', product='B', exchange='NSE',
                  symbol='INFY-EQ', quantity=2, disclosed_quantity=1,
                  order_type='LIMIT', price=1500, trigger_price=None,
                  validity='DAY', tag='rocket_leg_1',
                  bookloss_price=1490, bookprofit_price=1510)


"""
resp = pmart.orders
pprint(resp)


startdate = int(datetime(2023, 6, 10, 0, 0).timestamp())
enddate = int(datetime(2023, 6, 16, 0, 0).timestamp())
ret = pmart.finvasia.get_daily_price_series(
    exchange="NSE", tradingsymbol="PAYTM-EQ", startdate=startdate, enddate=enddate)
