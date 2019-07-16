# moBME280 class wrapper over Adafruit BME280 I2C temp-humidity-pressure
# err this does NOT use adafruit code, just hardware
# i think it uses Rpi.bme280  https://github.com/rm-hull/bme280
# adafruit library does not use gpioZero
# hopefully there isnt a conflict
#import gpiozero
import logging, logging.handlers
import sys
from time import sleep
#
import smbus2
import bme280

class moBME280:
    """Morphoptic class to read BME280 Temp/Humidity/Pressure Sensor"""
    _port = 1 
    _address = 0x77 # Adafruit BME280 address. Other BME280s may be different
    _bus = smbus2.SMBus(_port)
    temperature = 0
    humidity = 0
    pressure = 0
    timestamp = 0
    def __init__(self, addressP = 0x77):
        self.address = addressP
        self.calibration_params = bme280.load_calibration_params(self._bus,self._address)
        
    def read(self):
        bme280_data = bme280.sample(self._bus,self._address)
        self.timestamp = bme280_data.timestamp
        self.humidity  = bme280_data.humidity
        self.pressure  = bme280_data.pressure
        self.temperature = bme280_data.temperature
    
    def __str__(self):
        self.read()
        #return "{0}: {1} z: {2} {3}".format(self.timestamp, self.temperature, self.humidity, self.pressure)
        string= "{:.3f} %rH {:.3f}°C {:.3f} hPa".format(self.humidity, self.temperature, self.pressure)
        return string

__modacBME280 = None

def init():
    global __modacBME280
    logging.info("modac_BME280.init")
    __modacBME280 = moBME280()
    update()

def update():
    __modacBME280.read()

def temperature():
    if not isinstance(__modacBME280.temperature, float):
        logging.warn("bme280 temp is not a float")
        return 0.0
    return __modacBME280.temperature

def humidity():
    if not isinstance(__modacBME280.humidity, float):
        logging.warn("bme280 humidity is not a float")
        return 0.0
    return __modacBME280.humidity

def pressure():
    if not isinstance(__modacBME280.pressure, float):
        logging.warn("bme280 pressure is not a float")
        return 0.0
    return __modacBME280.pressure

def timestamp():
    return __modacBME280.timestamp

def timestampStr():
    return timestamp().strftime("%Y-%m-%d %H:%M:%S.%f%Z : ")

def testBME280():
    logging.info("test BME temp, pressure, humidity sensor")
    print("test BME temp, pressure, humidity sensor")
    for i in range(0,10):
        update()
        hStr = 'Humidity: %0.3f %%rH '% humidity()
        tStr = 'Temp: %0.3f °C '% temperature()
        pStr = 'Pressure: %0.3f hPa' % pressure()
        timeStr = timestamp().strftime("%Y-%m-%d %H:%M:%S.%f%Z : ")
        msg = timeStr + hStr+tStr+pStr
        #print(msg)
        logging.info(msg)
        #print("alt :", bme)
        sleep(1)

if __name__ == "__main__":
    print("MorpOptics BME280 Sensor class stand alone test")
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)#, format=logFormatStr)
    logging.captureWarnings(True)
    logging.info("Logging Initialized for MO BME280 main unitTest")
    init()
    update()
    
    #while True:
    for i in range(0,6):
        testBME280()
#        update()
#        hStr = 'Humidity: %0.3f %%rH '% humidity()
#        tStr = 'Temp: %0.3f °C '% temperature()
#        pStr = 'Pressure: %0.3f hPa' % pressure()
#        print(timestamp(),": ",hStr, tStr, pStr)
#        #print("alt :", bme)
#        sleep(1)

