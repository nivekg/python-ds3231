import ds3231
import subprocess
import smbus
import datetime
import time

if __name__=="__main__":
    bus=smbus.SMBus(1)
    rtc=ds3231.DS3231(bus)
   
    print("--get-seconds", subprocess.check_output(["python",  "ds3231.py",  "--i2c-bus", "1", "--get-seconds"])[:-1])
    print("--get-minutes", subprocess.check_output(["python",  "ds3231.py",  "--i2c-bus", "1", "--get-minutes"])[:-1])
    print("--get-hours", subprocess.check_output(["python",  "ds3231.py",  "--i2c-bus", "1", "--get-hours"])[:-1])
    print("--get-day", subprocess.check_output(["python",  "ds3231.py",  "--i2c-bus", "1", "--get-day"])[:-1])
    print("--get-date", subprocess.check_output(["python",  "ds3231.py",  "--i2c-bus", "1", "--get-date"])[:-1])
    print("--get-month", subprocess.check_output(["python",  "ds3231.py",  "--i2c-bus", "1", "--get-month"])[:-1])
    print("--get-year", subprocess.check_output(["python",  "ds3231.py",  "--i2c-bus", "1", "--get-year"])[:-1])
    print("--get-temperature", subprocess.check_output(["python",  "ds3231.py",  "--i2c-bus", "1", "--get-temperature"])[:-1])
    print("--get-ctime", subprocess.check_output(["python",  "ds3231.py",  "--i2c-bus", "1", "--get-ctime"])[:-1])
    print("--set-datetime", subprocess.check_output(["python",  "ds3231.py",  "--i2c-bus", "1", "--set-datetime", "%y-%m-%d %H:%M:%S; 21-05-10 14:55:30"])[:-1])
    print("--get-ctime", subprocess.check_output(["python",  "ds3231.py",  "--i2c-bus", "1", "--get-ctime"])[:-1])
