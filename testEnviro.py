# 
# locally required for this module
import logging, logging.handlers
import sys
from time import sleep

from modac import enviro, moData

def testEnviro():
    logging.info("test modac eniro sensor: temp, pressure, humidity sensor")
    print("test BME temp, pressure, humidity sensor")
    
    for i in range(0,10):
        enviro.update()
        hStr = 'Humidity: %0.3f %%rH '% enviro.humidity()
        tStr = 'Temp: %0.3f °C '% enviro.temperature()
        pStr = 'Pressure: %0.3f hPa' % enviro.pressure()
        timeStr = enviro.timestampStr() #timestamp().strftime("%Y-%m-%d %H:%M:%S.%f%Z : ")
        msg = timeStr + hStr+tStr+pStr
        #print(msg)
        logging.info(msg)
        print("AsDict: ", enviro.asDict())
        print("asJson ", enviro.asJson())
        print("moDataDict:",moData.rawDict())
        #print("alt :", bme)
        sleep(1)

if __name__ == "__main__":
    print("MorpOptics Enviro module test")
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)#, format=logFormatStr)
    logging.captureWarnings(True)
    logging.info("Logging Initialized for MO BME280 main unitTest")
    enviro.init()
    enviro.update()
    
    #while True:
    for i in range(0,6):
        testEnviro()

