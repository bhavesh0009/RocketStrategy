from api_helper import NorenApiPy
import logging

logging.basicConfig(level=logging.DEBUG)
api = NorenApiPy()
uid = "35660003"
pwd = "Ret2213@"
factor2 = "AJLPD7024M"
vc = "35660003"
app_key = "pn39GKbQH3quTF8MQNQb395s4G6Dy8yN"
imei = "1234"
ret = api.login(userid=uid, password=pwd, twoFA=factor2,
                vendor_code=vc, api_secret=app_key, imei=imei)
print(ret)
