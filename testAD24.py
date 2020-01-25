# testAD24
import sys
import logging
from time import sleep
from modac import moLogger, ad24, moData, moCSV
from modac.moKeys import *
#moKeys

if __name__ == "__main__":
    moLogger.init()
    
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

numSeconds = 300
def doTest():
    data = []
    for repeatCount in range(numSeconds):
        moData.updateTimestamp()
        ad24.update()
        ADC_Value = ad24.all0to5Array()
        print("ad24 raw", ad24.allRawArray())
        print("ad24 ADC_Value", ADC_Value)
        for i in range(len(ADC_Value)):
            print ("%d %d ADC = %lf"%(repeatCount, i, ADC_Value[i]))
        print("asDict", ad24.asDict())
        print("moDataDict:",moData.rawDict())
        moCSV.addRow()
        sleep(1) # one sample per sec
        
    moCSV.close()
        
if __name__ == "__main__":
    print("MorpOptics 24Bit AD Sensor class stand alone test")
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)#, format=logFormatStr)
    logging.captureWarnings(True)
    logging.info("Logging Initialized for MO 24Bit AD  main unitTest")
    moData.init()
    ad24.init()
    moCSV.init("CSV_testAD24.csv")
    doTest()
    
