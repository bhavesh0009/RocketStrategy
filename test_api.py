from api_helper import NorenApiPy
import logging

logging.basicConfig(level=logging.DEBUG)
api = NorenApiPy()
ret = api.login(userid=uid, password=pwd, twoFA=factor2,
                vendor_code=vc, api_secret=app_key, imei=imei)
print(ret)
