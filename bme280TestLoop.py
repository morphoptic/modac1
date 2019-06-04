import bme280
import smbus2
from time import sleep

print ("BME280 Test - humidity, pressure, temp")
port = 1 
address = 0x77 # Adafruit BME280 address. Other BME280s may be different
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus,address)

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
    
