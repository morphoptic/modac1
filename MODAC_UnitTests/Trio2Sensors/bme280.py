# MODAC enviro nment sensor
# basically wrapper over BME280 I2C temp-humidity-pressure
# i think it uses Rpi.bme280  https://github.com/rm-hull/bme280
 
import sys
this = sys.modules[__name__]

import logging, logging.handlers
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import smbus2
import bme280

# module global for BME280 device
__eSensor = None

def init():
    log.info("modac_BME280.init")
    try:
        this.__eSensor = moBME280()
    except:
        log.error("cant initialize BME280", exc_info=True)

    if this.__eSensor is None:
        log.error(" no Enviro sensor BME280")
        return

    #assert not this.__eSensor is None
    this.update()

def update():
    if this.__eSensor is None:
        log.error(" no BME Enviro sensor ")
        return
    else:
        try:
            this.__eSensor.read()
            log.info("BME" +str(this.__eSensor))
        except:
            log.error(" Error reading enviro values, disable device?", exc_info=True)

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
        string= self.timestamp.isoformat() + "{:.3f} %rH {:.3f}°C {:.3f} hPa".format(self.humidity, self.temperature, self.pressure)
        return string

def shutdown():
    this.__eSensor = None

