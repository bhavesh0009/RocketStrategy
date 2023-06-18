from smartapi import SmartConnect
from omspy_brokers.finvasia import Finvasia
import logging
import yaml

class Controller:
    brokerLogin = None # static variable
    brokerName = "Profitmart" # static variable

    def load_credentials(self):
        logging.info("Loading credentials.")
        with open("config/api_credentials.yaml", "r") as file:
            credentials = yaml.safe_load(file)
        # self.api_key = credentials["api_key"]
        # self.secret_key = credentials["secret_key"]
        # self.client_id = credentials["client_id"]
        # self.password = credentials["password"]
        self.uid = credentials['uid']
        self.pwd = credentials['pwd']
        self.factor2 = credentials['factor2']
        self.vc = credentials['vc']
        self.app_key = credentials['app_key']

    def generate_login_object(self):
        logging.info("Creating login object....")
        self.load_credentials()
        # obj = SmartConnect(api_key=self.api_key)
        # totp = pyotp.TOTP(s=self.secret_key)
        # data = obj.generateSession(self.client_id, self.password, totp.now())
        # # One time script to refresh NIFTY data
        # refreshToken= data['data']['refreshToken']
        # #fetch the feedtoken
        # feedToken=obj.getfeedToken()
        # #fetch User Profile
        # userProfile= obj.getProfile(refreshToken)
        pmart = Finvasia(user_id=self.uid, password=self.pwd, pin=self.factor2,
                 vendor_code=self.vc, app_key=self.app_key, imei="1234",
                 broker="profitmart")
        if pmart.authenticate():
            Controller.brokerLogin = pmart
            logging.info("Login object created successfully!!")

    def getBrokerLogin(self):
        return Controller.brokerLogin

    def getBrokerName(self):
        return Controller.brokerName