#import bme280
#import smbus2
from time import sleep
from moBME280 import moBME280

print ("BME280 Test - humidity, pressure, temp")


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
    print(bme.timestamp,hStr, tStr, pStr)
    sleep(1)
    
