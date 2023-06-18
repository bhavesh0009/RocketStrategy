from toolkit.fileutils import Fileutils
from omspy_brokers.finvasia import Finvasia
import logging
import os

logging.basicConfig(level=logging.DEBUG)

# sec_dir = "../../../"

root_dir = os.path.dirname(os.path.dirname(__file__))

sec_dir = os.path.join(root_dir, 'config', 'api_credentials.yaml')
logging.info(sec_dir)
m = Fileutils().get_lst_fm_yml(sec_dir)
pmart = Finvasia(user_id=m['uid'], password=m['pwd'], pin=m['factor2'],
                 vendor_code=m['vc'], app_key=m['app_key'], imei="1234",
                 broker="profitmart")
if pmart.authenticate():
    print("success")

token = pmart.instrument_symbol("NSE", "SBIN-EQ")
resp = pmart.scriptinfo("NSE", token)
print(resp)
