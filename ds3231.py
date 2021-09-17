import datetime
import subprocess
import os

# DS3231 Register map
REGISTERS=[None]*(0x12+1)
REGISTERS[0x00]={"seconds":         {"bitmask":0x7F, "shift":0}}
REGISTERS[0x01]={"minutes":         {"bitmask":0x7F, "shift":0}}
REGISTERS[0x02]={"format":          {"bitmask":0x40, "shift":6},
                 "AM/PM":           {"bitmask":0x20, "shift":5},
                 "20_hours":        {"bitmask":0x3F, "shift":0},
                 "10_hours":        {"bitmask":0x1F, "shift":0}}
REGISTERS[0x03]={"day":             {"bitmask":0x07, "shift":0}}
REGISTERS[0x04]={"date":            {"bitmask":0x3F, "shift":0}}
REGISTERS[0x05]={"century":         {"bitmask":0x80, "shift":6},
                 "month":           {"bitmask":0x1F, "shift":0}}
REGISTERS[0x06]={"years":           {"bitmask":0xFF, "shift":0}}
REGISTERS[0x07]={"a1m1":            {"bitmask":0x80, "shift":7},
                 "seconds":         {"bitmask":0x7F, "shift":0}}
REGISTERS[0x08]={"a1m2":            {"bitmask":0x80, "shift":7},
                 "minutes":         {"bitmask":0x7F, "shift":0}}
REGISTERS[0x09]={"a1m3":            {"bitmask":0x80, "shift":7},
                 "format":          {"bitmask":0x40, "shift":6},
                 "AM/PM":           {"bitmask":0x20, "shift":5},
                 "20_hours":        {"bitmask":0x3F, "shift":0},
                 "10_hours":        {"bitmask":0x1F, "shift":0}}
REGISTERS[0x0A]={"a1m4":            {"bitmask":0x80, "shift":7},
                 "dy/dt":           {"bitmask":0x40, "shift":6},
                 "date":            {"bitmask":0x3F, "shift":0},
                 "day":             {"bitmask":0x0F, "shift":0}}
REGISTERS[0x0B]={"a2m2":            {"bitmask":0x80, "shift":7},
                 "minutes":         {"bitmask":0x7F, "shift":0}}
REGISTERS[0x0C]={"a2m3":            {"bitmask":0x80, "shift":7},
                 "format":          {"bitmask":0x40, "shift":6},
                 "AM/PM":           {"bitmask":0x20, "shift":5},
                 "20_hours":        {"bitmask":0x3F, "shift":0},
                 "10_hours":        {"bitmask":0x1F, "shift":0}}
REGISTERS[0x0D]={"a2m4":            {"bitmask":0x80, "shift":7},
                 "dy/dt":           {"bitmask":0x40, "shift":6},
                 "date":            {"bitmask":0x3F, "shift":0},
                 "day":             {"bitmask":0x0F, "shift":0}}
REGISTERS[0x0E]={"eosc":            {"bitmask":0x7F, "shift":0},
                 "bbsqw":           {"bitmask":0x7F, "shift":0},
                 "conv":            {"bitmask":0x7F, "shift":0},
                 "rs2":             {"bitmask":0x7F, "shift":0},
                 "rs1":             {"bitmask":0x7F, "shift":0},
                 "intcn":           {"bitmask":0x7F, "shift":0},
                 "a2ie":            {"bitmask":0x7F, "shift":0},
                 "a1ie":            {"bitmask":0x7F, "shift":0}}
REGISTERS[0x0F]={"osf":             {"bitmask":0x80, "shift":7},
                 "en32khz":         {"bitmask":0x08, "shift":3},
                 "bsy":             {"bitmask":0x04, "shift":2},
                 "a2f":             {"bitmask":0x02, "shift":1},
                 "a1f":             {"bitmask":0x01, "shift":0}}
REGISTERS[0x10]={"aging_offset":    {"bitmask":0xFF, "shift":0}}
REGISTERS[0x11]={"temp_msb":        {"bitmask":0xFF, "shift":0}}
REGISTERS[0x12]={"temp_lsb":        {"bitmask":0xC0, "shift":5}}

class DS3231:
    def __init__(self, bus, cur_century=2000):
        self.bus=bus
        self.addr=0x68
        self.cur_century=cur_century

    def _int_to_bcd(self, val):
        return ((val/10)<<4)|(val%10)

    def _bcd_to_int(self, val):
        return ((val&0xF0)>>4)*10+(val&0x0F)

    def _int_to_twos_complement(self, val):
        return ~(val)+1

    def _twos_complement_to_int(self, val):
        if ((val&0b10000000)>>7)!=0:
	    return val-2**8
        else:
            return val

    def _decode(self, reg):
        raw_data=self.bus.read_byte_data(self.addr, reg)
        data={}
        for key in REGISTERS[reg].keys():
            data[key]=(raw_data & REGISTERS[reg][key]["bitmask"]) >> REGISTERS[reg][key]["shift"]
        return data

    def _encode(self, reg, val, key):
        raw_data=self.bus.read_byte_data(self.addr, reg)
        new_data=(raw_data & ~REGISTERS[reg][key]["bitmask"]) | (val << REGISTERS[reg][key]["shift"])
        self.bus.write_byte_data(self.addr, reg, new_data)

    def get_seconds(self):
        return self._bcd_to_int(self._decode(0x00)["seconds"])

    def set_seconds(self, val):
        self._encode(0x00, self._int_to_bcd(val), "seconds")

    def get_minutes(self):
        return self._bcd_to_int(self._decode(0x01)["minutes"])

    def set_minutes(self,val):
        self._encode(0x01, self._int_to_bcd(val), "minutes")

    def get_hours(self):
        return self._bcd_to_int(self._decode(0x02)["20_hours"])

    def set_hours(self,val):
        self._encode(0x02, self._int_to_bcd(val), "20_hours")

    def get_day(self):
        return self._bcd_to_int(self._decode(0x03)["day"])

    def set_day(self,val):
        print(val)
        self._encode(0x03, self._int_to_bcd(val), "day")

    def get_date(self):
        return self._bcd_to_int(self._decode(0x04)["date"])

    def set_date(self,val):
        self._encode(0x04, self._int_to_bcd(val), "date")

    def get_month(self):
        return self._bcd_to_int(self._decode(0x05)["month"])

    def set_month(self,val):
        self._encode(0x05, self._int_to_bcd(val), "month")

    def get_year(self):
        return self._bcd_to_int(self._decode(0x06)["years"])+self.cur_century

    def set_year(self,val):
        self._encode(0x06, self._int_to_bcd(val), "years")

    def enable_oscillator(self):
        self._encode(0x0E, 0x0, "eosc")

    def disable_oscillator(self):
        self._encode(0x0E, 0x1, "eosc")

    def enable_bbsqw(self):
        self._encode(0x0E, 0x1, "bbsqw")

    def disable_bbsqw(self):
        self._encode(0x0E, 0x0, "bbsqw")

    def get_convert_temperature(self):
        self._decode(0x0E, "conv")

    def begin_convert_temperature(self):
        self._encode(0x0E, 0x1, "conv")

    def set_sqw_freq(self,val):
        rs1=val & 0b01
        rs2=(val & 0b10) >> 1
        self._encode(0x0E, rs1, "rs1")
        self._encode(0x0E, rs2, "rs2")

    def enable_alarm2_interrupt(self):
        self._encode(0x0E, 0x1, "a2ie")

    def disable_alarm2_interrupt(self):
        self._encode(0x0E, 0x0, "a2ie")

    def enable_alarm1_interrupt(self):
        self._encode(0x0E, 0x1, "a1ie")

    def disable_alarm1_interrupt(self):
        self._encode(0x0E, 0x0, "a1ie")

    def get_oscillator_flag(self):
        return self._decode(0x0F)["osf"]

    def clear_oscillator_flag(self):
        self._encode(0x0F, 0x0, "osf")

    def get_alarm2_flag(self):
        return self._decode(0x0F)["a2f"]

    def clear_alarm2_flag(self):
        self._encode(0x0F, 0x0, "a2f")

    def get_alarm1_flag(self):
        return self._decode(0xF)["a1f"]

    def clear_alarm1_flag(self):
        self._encode(0x0F, 0x0, "a1f")

    def enable_output_32khz(self):
        self._encode(0x0F, 0x1, "en32khz")

    def disable_output_32khz(self):
        self._encode(0x0F, 0x0, "en32khz")

    def get_temperature(self):
        msb=self._twos_complement_to_int(self._decode(0x11)["temp_msb"])
        lsb=self._decode(0x12)["temp_lsb"]*0.25
        return msb+lsb

    def get_datetime(self):
        secs=self.get_seconds()
        mins=self.get_minutes()
        hrs=self.get_hours()
        date=self.get_date()
        mth=self.get_month()
        yr=self.get_year()
        return datetime.datetime(yr,mth,date,hrs,mins,secs)

    def set_datetime(self, dt):
        self.set_seconds(dt.second)
        self.set_minutes(dt.minute)
        self.set_hours(dt.hour)
        self.set_day(dt.weekday()+1)
        self.set_date(dt.day)
        self.set_month(dt.month)
        self.set_year(dt.year-self.cur_century)

    def set_system_clock_to_rtc(self):
        self.set_datetime(datetime.datetime.now())

    def get_hour_mode(self):
        return self._decode(0x02)["format"]

    def enable_24_hour_mode(self):
        self._encode(0x02, 0x0, "format")

    def enable_12_hour_mode(self):
        self._encode(0x02, 0x1, "format")

    def set_system_clock_from_rtc(self):
        devnull = open(os.devnull, 'w')
        success = subprocess.call(["sudo", "date", "-s", self.get_datetime().ctime()], stdout=devnull, stderr=devnull)
        devnull.close()
        return success
      

    def timestamp(self):
        dt = self.get_datetime()
        return (dt - datetime.datetime(1970, 1, 1, 0, 0, 0)).total_seconds()


if __name__ == "__main__":
    import smbus
    import argparse
    import ds3231

    parser = argparse.ArgumentParser(description = "Utility used to interact with the DS3231 RTC from Maximum Integrated")
    parser.add_argument("--i2c-bus", type=int, help = "i2c bus that the DS3231 is connected too")
    parser.add_argument("--get-seconds", action="store_true", help = "Returns the seconds RTC timekeeping register")
    parser.add_argument("--set-seconds", type=int, help = "Sets the seconds RTC timekeeping register")
    parser.add_argument("--get-minutes", action="store_true", help = "Returns the minutes RTC timekeeping register")
    parser.add_argument("--set-minutes", type=int, help = "Sets the minutes RTC timekeeping register")
    parser.add_argument("--get-hours", action="store_true", help = "Returns the hours RTC timekeeping register")
    parser.add_argument("--set-hours", type=int, help = "Sets the hours RTC timekeeping register")
    parser.add_argument("--get-day", action="store_true", help = "Returns the day RTC timekeeping register")
    parser.add_argument("--set-day", type=int, help = "Sets the day RTC timekeeping register. Sunday equals 1")
    parser.add_argument("--get-date", action="store_true", help = "Returns the date RTC timekeeping register")
    parser.add_argument("--set-date", type=int, help = "Sets the date RTC timekeeping register")
    parser.add_argument("--get-month", action="store_true", help = "Returns the month RTC timekeeping register")
    parser.add_argument("--set-month", type=int, help = "Sets the month RTC timekeeping register")
    parser.add_argument("--get-year", action="store_true", help = "Returns the year RTC timekeeping register")
    parser.add_argument("--set-year", type=int, help = "Sets the year RTC timekeeping register. Only the last two digits for the year [0-99]")
    parser.add_argument("--set-datetime", type=str, help = "Sets the RTC timekeeping registers based on the supplied time format. eg. \"%H:%M:%S 12:30:15\"")
    parser.add_argument("--get-ctime", action="store_true")
    parser.add_argument("--enable-oscillator", action="store_true", help = "")
    parser.add_argument("--disable-oscillator", action="store_true", help = "")
    parser.add_argument("--enable-bbsqw", action="store_true", help = "")
    parser.add_argument("--disable-bbsqw", action="store_true", help = "")
    parser.add_argument("--begin-temperature-conversion", action="store_true", help = "")
    parser.add_argument("--get-temperature-conversion-flag", action="store_true", help = "")
    parser.add_argument("--get-temperature", action="store_true", help = "")
    parser.add_argument("--set-sqw-freq", type=int, help = "")
    parser.add_argument("--get-oscillator-flag", action="store_true", help = "")
    parser.add_argument("--clear-oscillator-flag", action="store_true", help = "")
    parser.add_argument("--enable-alarm1-interrupt", action="store_true", help = "")
    parser.add_argument("--disable-alarm1-interrupt", action="store_true", help = "")
    parser.add_argument("--get-alarm1-flag", action="store_true", help = "")
    parser.add_argument("--clear-alarm1-flag", action="store_true", help = "")
    parser.add_argument("--enable-alarm2-interrupt", action="store_true", help = "")
    parser.add_argument("--disable-alarm2-interrupt", action="store_true", help = "")
    parser.add_argument("--get-alarm2-flag", action="store_true", help = "")
    parser.add_argument("--clear-alarm2-flag", action="store_true", help = "")
    parser.add_argument("--enable-32khz-output", action="store_true", help = "")
    parser.add_argument("--disable-32khz-output", action="store_true", help = "")
    parser.add_argument("--set-system-clock-to-rtc", action="store_true", help = "")
    parser.add_argument("--get-hour-mode", action="store_true", help = "")
    parser.add_argument("--enable-24-hour-mode", action="store_true", help = "")
    parser.add_argument("--enable-12-hour-mode", action="store_true", help = "")
    parser.add_argument("--set-system-clock-from-rtc", action="store_true", help = "")
    parser.add_argument("--timestamp", action="store_true", help = "Return the DS3231 timekeeping registers as a unix timestamp")
    args = parser.parse_args()

    rtc = None

    try:
        if args.i2c_bus != None:
            bus = smbus.SMBus(args.i2c_bus)
            rtc = ds3231.DS3231(bus)
        else:
            print("Please specify the i2c bus the RTC is connected too.")
            exit(1)

        if args.get_seconds:
            print(rtc.get_seconds())

        if args.set_seconds != None:
            if args.set_seconds >=0 and args.set_seconds <= 60:
                rtc.set_seconds(args.set_seconds)
            else:
                print("Seconds need to be in the range 0 to 60")
                exit(1)

        if args.get_minutes:
            print(rtc.get_minutes())

        if args.set_minutes != None:
            if args.set_minutes >= 0 and args.set_minutes <= 60:
                rtc.set_minutes(args.set_minutes)
            else:
                print("Minutes need to be in the range 0 to 60")
                exit(1)

        if args.get_hours:
            print(rtc.get_hours())

        if args.set_hours != None:
            if args.set_hours >= 0 and args.set_hours <= 24:
                rtc.set_hours(args.set_hours)
            else:
                print("Hours need to be in the range 0 to 24")
                exit(1)

        if args.get_day:
            print(rtc.get_day())

        if args.set_day != None:
            if args.set_day >= 1 and args.set_day <= 7:
                rtc.set_day(args.set_day)
            else:
                print("Day need to be in the range 1 to 7. Sunday starts at 1")
                exit(1)

        if args.get_date:
            print(rtc.get_date())

        if args.set_date != None:
            if args.set_date >= 1 and args.set_date <= 31:
                rtc.set_date(args.set_date)
            else:
                print("Date needs to be in the range 1 to 31")
                exit(1)

        if args.get_month:
            print(rtc.get_month())

        if args.set_month != None:
            if args.set_month >= 1 and args.set_month <= 12:
                rtc.set_month(args.set_month)
            else:
                print("Month needs to be in the range 1 to 12")
                exit(1)

        if args.get_year:
            print(rtc.get_year())

        if args.set_year != None:
            if args.set_year >= 0 and args.set_year <= 99:
                rtc.set_year(args.set_year)
            else:
                print("Year needs to be in the range 0 to 99. Only the last two digits are required")
                exit(1)

        if args.set_datetime != None:
            format, date = args.set_datetime.split("; ")
            rtc.set_datetime(datetime.datetime.strptime(date, format))

        if args.get_ctime:
           print(rtc.get_datetime().ctime())

        if args.enable_oscillator:
            rtc.enable_oscilator()

        if args.disable_oscillator:
            rtc.disable_oscilator()

        if args.enable_bbsqw:
            rtc.enable_bbsqw()

        if args.disable_bbsqw:
            rtc.disable_bbsqw()

        if args.begin_temperature_conversion:
            print(rtc.begin_temperature_conversion())

        if args.get_temperature_conversion_flag:
            print(rtc.get_temperature_conversion_flag())

        if args.get_temperature:
            print(rtc.get_temperature())

        if args.set_sqw_freq != None:
            if args.set_sqw_freq in [0, 1, 2, 3]:
                rtc.set_sqw_freq(args.set_sqw_freq)

        if args.get_oscillator_flag:
            print(rtc.get_oscillator_flag())

        if args.clear_oscillator_flag:
            rtc.clear_oscillator_flag()

        if args.enable_alarm1_interrupt:
            rtc.enable_alarm1_interrupt()

        if args.disable_alarm1_interrupt:
            rtc.disable_alarm1_interrupt()

        if args.get_alarm1_flag:
            print(rtc.get_alarm1_flag())

        if args.clear_alarm1_flag:
            rtc.clear_alarm1_flag()

        if args.enable_alarm2_interrupt:
            rtc.enable_alarm2_interrupt()

        if args.disable_alarm2_interrupt:
            rtc.disable_alarm2_interrupt()

        if args.get_alarm2_flag:
            print(rtc.get_alarm2_flag())

        if args.clear_alarm2_flag:
            rtc.clear_alarm2_flag()

        if args.enable_32khz_output:
            rtc.enable_32khz_output()

        if args.disable_32khz_output:
            rtc.disable_32khz_output()

        if args.set_system_clock_to_rtc:
            rtc.set_system_clock_to_rtc()

        if args.get_hour_mode:
            print(rtc.get_hour_mode())

        if args.enable_24_hour_mode:
            rtc.enable_24_hour_mode()

        if args.enable_12_hour_mode:
            rtc.enable_12_hour_mode()

        if args.set_system_clock_from_rtc:
            rtc.set_system_clock_from_rtc()

        if args.timestamp:
            print(int(rtc.timestamp()))

    except Exception as e:
        print(e.message)
        exit(1)
