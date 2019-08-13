# testAD16
import sys
import logging
from time import sleep
from modac import ad16, moData
from modac.moKeys import *

from modac import moLogger
if __name__ == "__main__":
    moLogger.init()

if __name__ == "__main__":
    moLogger.init()
    
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def doTest():
    data = []
    for repeatCount in range(60):
        ad16.update()
        ADC_Value = ad16.values()
        print("values", ADC_Value)
        for i in range(len(ADC_Value)):
            print ("%d %d ADC = %lf"%(repeatCount, i, ADC_Value[i]))
        print("moData:",moData.getValue(keyForAD16()))
        sleep(1)
        
if __name__ == "__main__":
    print("MorpOptics 16Bit AD Sensor class stand alone test")
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)#, format=logFormatStr)
    logging.captureWarnings(True)
    logging.info("Logging Initialized for MO 16Bit AD  main unitTest")
    moData.init()
    ad16.init()
    doTest()
    
