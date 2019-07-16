import bme280
import smbus2
from time import sleep

print ("BME280 Only Test - humidity, pressure, temp")
print ("using bme280 and smbus libraries")

port = 1 
address = 0x77 # Adafruit BME280 address. Other BME280s may be different
bus = smbus2.SMBus(port)

def initBme280():
    calibration_params = bme280.load_calibration_params(bus,address)

initBme280()

while True:
    bme280_data = bme280.sample(bus,address)
    humidity  = bme280_data.humidity
    pressure  = bme280_data.pressure
    ambient_temperature = bme280_data.temperature
    print(bme280_data)
    #print(data.id)
    #print(data.timestamp)
    #print(humidity, pressure, ambient_temperature)
    sleep(1)
    
