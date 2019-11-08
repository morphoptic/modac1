# calibrateAD24
import sys
this = sys.modules[__name__]

import logging
from time import sleep
import datetime
import numpy as np
from modac import moLogger, ad24, moData, moCSV, enviro, kType
from modac.moKeys import *

#idx of ktypes in AD24 array
kTypeAD24 = [4,5,6]
kTypeLog = []#[[0,0,0]]

if __name__ == "__main__":
    moLogger.init()
    
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

numMin = 1
numSeconds = (60*numMin)
sleepTime = 1
def doTest():
    data = []
    name = "calibrateCSV_"
    now = datetime.datetime.now()
    nowStr = now.strftime("%Y%m%d_%H%M%S")
    outName = name+nowStr+".csv"
    outFile = open(outName, "w")
    print("Count,TimeStamp,TempC, TC1, TC2, TC3, Avg,Mean,Median, StdDev,mv1,mv2,mv3,mvAvg,mvMean,mvMedian, mvStdDev,K1,K2,K3,TAvg,TMean,TMedian, TStdDev, ",
        file=outFile)
    for repeatCount in range(numSeconds):
        moData.updateTimestamp()
        ad24.update()
        enviro.update()
        timestamp = moData.getValue(keyForTimeStamp())
        ADC_Value = ad24.all0to5Array()
        row = [repeatCount, enviro.degC()]
        line = "%d, %s, %6.5f, "%(repeatCount,timestamp,enviro.degC() )
        tcoupleAD = []
        ktype = []
        mv = []
        idx = 0
        kline = ", "
        mline = ", "
        for idxAD in kTypeAD24:
            tcoupleAD.append(ADC_Value[idxAD])
            k = kType.mVToC(ADC_Value[idxAD],enviro.degC())
            ktype.append(k)
            m = kType.fnMagic(ADC_Value[idxAD])
            mv.append(m)
            row.append(ADC_Value[idxAD])
            line = line + "%10.9f,"%ADC_Value[idxAD]
            kline = kline + "%10.9f,"%k
            mline = mline + "%10.9f,"%m
        a = np.array(tcoupleAD)
        line = line + "%10.9f, %10.9f, %10.9f, %10.9f"%(
                a.mean(),np.median(a), np.average(a), np.std(a))
        b = np.array(ktype)
        kline = kline+ "%10.9f, %10.9f, %10.9f, %10.9f"%(
                b.mean(),np.median(b), np.average(b), np.std(b))
        c = np.array(mv)
        mline = mline+ "%10.9f, %10.9f, %10.9f, %10.9f"%(
                c.mean(),np.median(c), np.average(c), np.std(c))
        line += mline
        line += kline
        print(line, file=outFile)

        row.append(a.mean())
        row.append(np.median(a))
        row.append(np.average(a))
        row.append(np.std(a))
        if repeatCount % 10 == 0:
            print(repeatCount)
        kTypeLog.append(row)

        sleep(sleepTime) # one sample per sec
        
    print("TCouple log has %d entries", len(this.kTypeLog))
#    print("kTypeLog: ", this.kTypeLog)
    
    #p = kTypeLog.pop(0)
#    print("\n pop ",p)
#    print("kTypeLog: ", this.kTypeLog)

    npA = np.array(kTypeLog)
    print("npA : ", npA)  
#    this.kTypeLog = npA.tolist()
#    print("kTypeLog: ", this.kTypeLog)
    
#    np.savetxt("calibrate.csv",npA,delimiter=",")
    
    dataMax = npA.max(axis=0)
    printRow("dataMax",dataMax,outFile)
    
    dataMin = npA.min(axis=0)
    printRow("dataMin",dataMin,outFile)
    
    dataMean = np.mean(npA, axis=0)
    printRow("dataMean",dataMean,outFile)
    
    dataMedian = np.median(npA, axis=0)
    printRow("dataMedian",dataMedian,outFile)
    
    dataAverage = np.average(npA, axis=0)
    printRow("dataAverage",dataAverage,outFile)
    
    dataStdDev = np.std(npA, axis=0)
    printRow("dataStdDev",dataStdDev,outFile)

    print("dataMax ", dataMax)
    print("dataMin ", dataMin)
    print("dataMean ", dataMean)
    print("dataMedian ", dataMedian)
    print("dataAverage ", dataAverage)
    print("dataStdDev ", dataStdDev)

    npB = npA
    npB = np.vstack([npB,dataMax])
    npB = np.vstack([npB,dataMin])
    npB = np.vstack([npB,dataMean])
    npB = np.vstack([npB,dataMedian])
    npB = np.vstack([npB,dataAverage])
#    print("npB",npB)
    
    np.savetxt("calibrate_2.csv",npB,fmt="%10.8f",delimiter=",",header="count,temp,a,b,c,mean,median,avg,stdDev")
    print("Count,TempC, TC1, TC2, TC3, Avg,Mean,Median, StdDev", file=outFile)
#    print("saved data")

def printRow(name,row,file):
    rowLen=len(row)
    line = name+", "
    for i in range(1,rowLen):
        line = line + "%10.9f, "%row[i]
    print(line, file=file)
    
if __name__ == "__main__":
    #    
    print("MorpOptics 24bAD Ktype Calibration Test")
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)#, format=logFormatStr)
    logging.captureWarnings(True)
    logging.info("Logging Initialized for MO 24Bit AD  main unitTest")
    #
    moData.init()
    enviro.init()
    print("Enviro says degC: ",enviro.degC())
    ad24.init()
    kType.init()
    #
    doTest()
    
