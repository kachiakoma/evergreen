import BME280_read as BME
import time

def now():
    the_time=int((time.time()-18000)*1000)
    return the_time

def temp_read():
    r_ftemp=BME.current_ftemp()
    temp = [now(), r_ftemp]
    return temp

def humidity_read():
    r_humidity=BME.current_humidity()
    humid = [now(), r_humidity]
    return humid

def pressure_read():
    r_pressure=BME.current_pressure()
    pressure = [now(), r_pressure]
    return pressure


