import datetime
import subprocess

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
        return subprocess.call(["sudo", "date", "-s", self.get_datetime().ctime()])

    def timestamp(self):
        dt = self.get_datetime()
        return (dt - datetime.datetime(1970, 1, 1, 0, 0, 0)).total_seconds()
