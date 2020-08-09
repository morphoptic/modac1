# MODAC enviro nment sensor
# basically wrapper over BME280 I2C temp-humidity-pressure
# i think it uses Rpi.bme280  https://github.com/rm-hull/bme280
 
import sys
this = sys.modules[__name__]

import logging, logging.handlers
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

from .moKeys import *
from . import moData

# locally required for this module
import sys
from time import sleep
import json
#
import smbus2
import bme280

# module global for BME280 device
__eSensor = None

def init():
    log.info("modac_BME280.init")
    try:
        this.__eSensor = moBME280()
    except:
        log.error("cant initialize BME280")
        log.error(str( sys.exc_info()[0]))
        
    if this.__eSensor is None:
        log.error(" no Enviro sensor BME280")
        moData.update(keyForEnviro(), asDict())
        return

    #assert not this.__eSensor is None
    this.update()

def update():
    if this.__eSensor is None:
        log.error(" no BME Enviro sensor ")
        return
    this.__eSensor.read()
    # removed global timestamp from here
    #moData.update(keyForTimeStamp(), timestampStr())
    moData.update(keyForEnviro(), asDict())

def asDict():
    d = {keyForTimeStamp():timestampStr(),
         keyForHumidity():humidity(),
         keyForTemperature():degC(),
         keyForPressure():pressure()
         }
    return d

def temperature():
    if this.__eSensor is None:
        return -1
    if not isinstance(this.__eSensor.temperature, float):
        log.warn("bme280 temp is not a float")
        return 0.0
    return this.__eSensor.temperature

def degC():
    return temperature()

def degF():
    return degC()*1.8 + 32

def humidity():
    if this.__eSensor is None:
        return -1
    if not isinstance(this.__eSensor.humidity, float):
        log.warn("bme280 humidity is not a float")
        return 0.0
    return this.__eSensor.humidity

def pressure():
    if this.__eSensor is None:
        return -1
    if not isinstance(this.__eSensor.pressure, float):
        log.warn("bme280 pressure is not a float")
        return 0.0
    return this.__eSensor.pressure

def timestamp():
    return this.__eSensor.timestamp

def timestampStr():
    if this.__eSensor is None:
        return "no enviro sensor"
    return timestamp().strftime(keyForTimeFormat())

def timestampISOStr():
    return timestamp().isoformat()

def asJson():
    s = json.dumps({keyForEnviro():asDict()})
    return s

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
        string= self.timestamp.isoformat() + "{:.3f} %rH {:.3f}°C {:.3f} hPa".format(self.humidity, self.temperature, self.pressure)
        return string

def shutdown():
    this.__eSensor = None

def testBME280():
    log.info("test BME temp, pressure, humidity sensor")
    print("test BME temp, pressure, humidity sensor")
    print("Key is", key())
    
    for i in range(0,10):
        update()
        hStr = 'Humidity: %0.3f %%rH '% humidity()
        tStr = 'Temp: %0.3f °C '% temperature()
        pStr = 'Pressure: %0.3f hPa' % pressure()
        timeStr = timestampStr()
        msg = timeStr + hStr+tStr+pStr
        #print(msg)
        log.info(msg)
        print("AsDict: ", asDict())
        print("asJson ", asJson())
        #print("alt :", bme)
        sleep(1)

if __name__ == "__main__":
    print("modac.enviro has no self test")
    init()
    testBME280()
    exit(0)
  
