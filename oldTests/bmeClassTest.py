import bme280
import smbus2
from time import sleep
import moBME280

print ("BME280 Test - humidity, pressure, temp")

class moBME280: 
    _port = 1 
    _address = 0x77 # Adafruit BME280 address. Other BME280s may be different
    _bus = smbus2.SMBus(_port)
    temperature = 0
    humidity = 0
    pressure = 0
    timestamp = 0
    def init(self, addressP = 0x77):
        self.address = addressP
        self.calibration_params = bme280.load_calibration_params(self._bus,self._address)
        
    def read(self):
        bme280_data = bme280.sample(self._bus,self._address)
        self.timestamp = bme280_data.timestamp
        self.humidity  = bme280_data.humidity
        self.pressure  = bme280_data.pressure
        self.temperature = bme280_data.temperature


bme = moBME280()
bme.init()

while True:
    bme.read()
    humidity  = bme.humidity
    pressure  = bme.pressure
    ambient_temperature = bme.temperature
    hStr = 'Humidity:  %0.3f %%rH '% bme.humidity
    tStr = 'Temp:      %0.3f °C '%bme.temperature
    pStr = 'Pressure:  %0.3f hPa' % bme.pressure
    #print(bme.humidity, bme.pressure, bme.temperature)
    print(hStr, tStr, pStr)
    sleep(1)
    
