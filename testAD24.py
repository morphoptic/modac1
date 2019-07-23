# testAD24
import sys
import logging
from time import sleep
from modac import ad24, moData

def doTest():
    data = []
    for repeatCount in range(60):
        ad24.update()
        ADC_Value = ad24.all0to5Array()
        print(ad24.allRawArray())
        print(ADC_Value)
        for i in range(len(ADC_Value)):
            print ("%d %d ADC = %lf"%(repeatCount, i, ADC_Value[i]))
        print("asDict", ad24.asDict())
        print("moDataDict:",moData.rawDict())
        
if __name__ == "__main__":
    print("MorpOptics 24Bit AD Sensor class stand alone test")
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)#, format=logFormatStr)
    logging.captureWarnings(True)
    logging.info("Logging Initialized for MO 24Bit AD  main unitTest")
    moData.init()
    ad24.init()
    doTest()
    
