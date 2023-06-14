import logging
import yaml
from smartapi import SmartConnect
import pyotp

class Controller:
    brokerLogin = None # static variable
    brokerName = "Angel" # static variable

    def load_credentials(self):
        logging.info("Loading credentials.")
        with open("config/api_credentials.yaml", "r") as file:
            credentials = yaml.safe_load(file)
        self.api_key = credentials["api_key"]
        self.secret_key = credentials["secret_key"]
        self.client_id = credentials["client_id"]
        self.password = credentials["password"]

    def generate_smart_connect_object(self):
        logging.info("Creating login object....")
        self.load_credentials()
        obj = SmartConnect(api_key=self.api_key)
        totp = pyotp.TOTP(s=self.secret_key)
        data = obj.generateSession(self.client_id, self.password, totp.now())
        # One time script to refresh NIFTY data
        refreshToken= data['data']['refreshToken']
        #fetch the feedtoken
        feedToken=obj.getfeedToken()
        #fetch User Profile
        userProfile= obj.getProfile(refreshToken)
        Controller.brokerLogin = obj
        logging.info("Login object created successfully!!")


    def getBrokerLogin(self):
        return Controller.brokerLogin

    def getBrokerName(self):
        return Controller.brokerName