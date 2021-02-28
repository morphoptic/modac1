# ad16 = test module to wrap ADS1115 16bit AD sensor on i2c
# this version uses the old Adafruit library; before CircuitPlayground
# matching original in MODAC

# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]

import time
import board
import busio
import datetime
import sys
import os
import logging, logging.handlers, traceback

#import adafruit_ads1x15.ads1015 as ADS
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c, address=0x48)

# Create single-ended input on channel 0
chan0 = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1)
chan2 = AnalogIn(ads, ADS.P2)
chan3 = AnalogIn(ads, ADS.P3)

print("{:>5}\t{:>5}".format('raw', 'v'))

errCount=0
totalErrCount =0
def readChan(chan):
    try:
        log.info("{:>5}\t{:>5.3f}".format(chan.value, chan.voltage))
        this.errCount =0
    except:
        this.errCount +=1
        this.totalErrCount +=1
        print("Error reading ad16, consec err:"+str(this.errCount)+" total:"+str(this.totalErrCount))
        log.error("Error reading ad16, consec err:"+str(this.errCount)+" total:"+str(this.totalErrCount), exc_info=True)

i=0
while True:
    #for i in range(10):
    i+=1
    readChan(chan0)
    readChan(chan1)
    readChan(chan2)
    readChan(chan3)
    log.info("cycle "+str(i))
    time.sleep(0.5)