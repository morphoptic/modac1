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

channels = [chan0, chan1, chan2, chan3]

print("{:>5}\t{:>5}".format('raw', 'v'))

errCount=0
totalErrCount =0
values = [0, 0, 0, 0]
def readChans():
    i = 0
    for chan in channels:0
        try:
            values[i] = chan.value
            #log.info("{:>5}\t{:>5.3f}".format(chan.value, chan.voltage))
            if chan.value > 20000:
                raise Exception("AD16 Range Error ").with_traceback(sys.exc_info()[2])
            this.errCount =0
            i += 1
        except:
            this.errCount +=1
            this.totalErrCount +=1
            print("Error reading ad16, consec err:"+str(this.errCount)+" total:"+str(this.totalErrCount))
            log.error("Error reading ad16, consec err:"+str(this.errCount)+" total:"+str(this.totalErrCount), exc_info=True)
            break
    log.info("AD16 values: "+str(values))
i=0
while True:
    #for i in range(10):
    i+=1
    readChans()
    log.info("cycle "+str(i))
    time.sleep(0.5)
