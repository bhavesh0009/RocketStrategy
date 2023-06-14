from toolkit.fileutils import Fileutils
from omspy_brokers.finvasia import Finvasia
import logging

logging.basicConfig(level=logging.DEBUG)

sec_dir = "../../../"
m = Fileutils().get_lst_fm_yml(sec_dir + "profitmart.yaml")
profitmart = Finvasia(user_id=m['uid'], password=m['pwd'], pin=m['factor2'],
                      vendor_code=m['vc'], app_key=m['app_key'], imei="1234",
                      broker="profitmart")
broker = profitmart.authenticate()
token = profitmart.instrument_symbol("NSE", "SBIN-EQ")
print(token)
