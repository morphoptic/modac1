# testAD16
import sys
import logging
from time import sleep
from modac import ad16, moData, kType
from modac.moKeys import *

from modac import moLogger
if __name__ == "__main__":
    moLogger.init()

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def doTest():
    data = []
    for repeatCount in range(100):
        ad16.update()
        ADC_Value = ad16.values()
        ADC_volts = ad16.volts()
        print("values", ADC_Value)
        kvalues = moData.getValue(keyForKType())
        for i in range(3):#len(ADC_Value)):
            print ("count %d chan %d AD16 = %ld v %lf kt: %f"%(repeatCount, i, ADC_Value[i], ADC_volts[i],kvalues[i]))
        print("moData:",moData.getValue(keyForAD16()), moData.getValue(keyForAD16Raw()), kvalues)
        sleep(1)
        
if __name__ == "__main__":
    print("MorpOptics 16Bit AD Sensor class stand alone test")
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)#, format=logFormatStr)
    logging.captureWarnings(True)
    logging.info("Logging Initialized for MO 16Bit AD  main unitTest")
    moData.init()
    ad16.init()
    kType.init()
    doTest()
    
