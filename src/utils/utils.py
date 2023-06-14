import math
import logging
import uuid
import time
import calendar
from datetime import datetime, timedelta, date
import pytz

# from config.Config import getHolidays
# from models.Direction import Direction
#from trademgmt.TradeState import TradeState

class Utils:
    dateFormat = "%Y-%m-%d"
    timeFormat = "%H:%M:%S"
    dateTimeFormat = "%Y-%m-%d %H:%M:%S"    

    @staticmethod
    def initLoggingConfig():
        format ="%(asctime)s: %(message)s"
        logging.basicConfig(format=format, level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")

    @staticmethod
    def roundtoNSEPrice(price):
        x = round(price, 2) * 20
        y = math.ceil(x)
        return y / 20

    @staticmethod
    def isMarketOpen():
        if Utils.isTodayHoliday():
            return False
        now = datetime.now()
        marketStartTime = Utils.getMarketStartTime()
        marketEndTime = Utils.getMarketEndTime()
        return now >= marketStartTime and now <= marketEndTime

    @staticmethod
    def getMarketStartTime(dateTimeObj = None):
        return Utils.getTimeOfDay(9, 15, 0, dateTimeObj)

    @staticmethod
    def getMarketEndTime(dateTimeObj = None):
        return Utils.getTimeOfDay(15, 30, 0, dateTimeObj)

    @staticmethod
    def getTimeOfDay(hours, minutes, seconds, dateTimeObj = None):
        if dateTimeObj == None:
            dateTimeObj = datetime.now()
        dateTimeObj = dateTimeObj.replace(hour=hours, minute=minutes, second=seconds, microsecond=0)
        return dateTimeObj

    @staticmethod
    def getTimeOfToDay(hours, minutes, seconds):
        return Utils.getTimeOfDay(hours, minutes, seconds, datetime.now())

    @staticmethod
    def getTodayDateStr():
        return Utils.convertToDateStr(datetime.now())

    @staticmethod
    def convertToDateStr(datetimeObj):
        return datetimeObj.strftime(Utils.dateFormat)     

    @staticmethod
    def getEpoch(datetimeObj = None):
        # This method converts given datetimeObj to epoch seconds
        if datetimeObj == None:
            datetimeObj = datetime.now()
        epochSeconds = datetime.timestamp(datetimeObj)
        return int(epochSeconds) # converting double to long           

    @staticmethod
    def isMarketClosedForTheDay():
        # This method returns true if the current time is > marketEndTime
        # Please note this will not return true if current time is < marketStartTime on a trading day
        if Utils.isTodayHoliday():
            return True
        now = datetime.now()
        marketEndTime = Utils.getMarketEndTime()
        return now > marketEndTime

    @staticmethod
    def waitTillMarketOpens(context):
        nowEpoch = Utils.getEpoch(datetime.now())
        marketStartTimeEpoch = Utils.getEpoch(Utils.getMarketStartTime())
        waitSeconds = marketStartTimeEpoch - nowEpoch
        if waitSeconds > 0:
            logging.info("%s: Waiting for %d seconds till market opens...", context, waitSeconds)
            time.sleep(waitSeconds)

    @staticmethod
    def sleep_until_time(target_time):
        target_time = datetime.strptime(target_time, '%H:%M:%S').time()
        current_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_diff = datetime.combine(date.today(), target_time) - datetime.combine(date.today(), current_time)
        sleep_duration = time_diff.total_seconds()

        logging.info(f"Sleeping for {sleep_duration} seconds.")
        if sleep_duration > 0:
            time.sleep(sleep_duration)
        #logging.info("Target time reached. Continue with the rest of the code.")


    # @staticmethod
    # def isHoliday(datetimeObj):
    #     dayOfWeek = calendar.day_name[datetimeObj.weekday()]
    #     if dayOfWeek == 'Saturday' or dayOfWeek == 'Sunday':
    #         return True

    #     dateStr = Utils.convertToDateStr(datetimeObj)
    #     holidays = getHolidays()
    #     if (dateStr in holidays):
    #         return True
    #     else:
    #         return False

    # @staticmethod
    # def isTodayHoliday():
    #     return Utils.isHoliday(datetime.now())            