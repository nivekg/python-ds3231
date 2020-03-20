import ds3231
import smbus
import datetime
import time

if __name__=="__main__":
    bus=smbus.SMBus(1)
    rtc=ds3231.DS3231(bus)
    while True:
        a=rtc.get_datetime()
        b=datetime.datetime.now()
        print("rtc:", a)
        print("sys:", b)
        print("diff:", b-a)
        print(rtc.get_temperature())
        time.sleep(1)
