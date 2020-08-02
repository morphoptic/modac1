# moBME280 class wrapper over Adafruit BME280
import bme280
import smbus2
from time import sleep

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

if __name__ == "__main__":
    print("MorpOptics BME280 Sensor class test")
    bme = moBME280()

    while True:
        bme.read()
        hStr = 'Humidity: %0.3f %%rH '% bme.humidity
        tStr = 'Temp: %0.3f °C '%bme.temperature
        pStr = 'Pressure: %0.3f hPa' % bme.pressure
        print(bme.timestamp,": ",hStr, tStr, pStr)
        #print("alt :", bme)
        sleep(1)

