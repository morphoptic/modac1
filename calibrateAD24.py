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
kTypeAD24 = kType.kTypeIdx # [4,5,6]

if __name__ == "__main__":
    moLogger.init()
    
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

numMin = 1
#numMin = 5
numSeconds = (60*numMin)
#sleepTime = 0.005
sleepTime = 1.0

def doTest():
    seconds = 0.00
    kTypeLog = [] # collection of primary data, one row per Sample
    data = []
    name = "calibrateCSV_"
    now = datetime.datetime.now()
    nowStr = now.strftime("%Y%m%d_%H%M")
    outName = name+nowStr+".csv"
    outFile = open(outName, "w")
    columnHeading = "Seconds,TimeStamp,TempC, ad4, ad5, ad6, ,m1.1, m1.2, m1.3,, mv1,mv2,mv3,,Kr1,Kr2,Kr3,,K0-1,K0-2,K0-3, "
    print(columnHeading)
    print(columnHeading,file=outFile)
    for repeatCount in range(numSeconds):
        # for each Row/timestep
        moData.updateTimestamp()
        enviro.update()
        ad24.update()
        kType.init()
        moCSV.addRow()
        moData.logData()
        #
        timestamp = moData.getValue(keyForTimeStamp())
        ADC_Value = ad24.all0to5Array()
        ADC_Raw = ad24.allRawArray()
        # row provides columns for kTypeLog
        row = [seconds, enviro.degC()]
        rowMoG =[0]
        rowMv = [0]
        rowK = [0]
        # row accumulators
        tcoupleAD = [] # 0-5V from ADC
        mvog = [] #mV / ampGain
        mv = []  #
        ktype = [] # kType.mVToC( ,roomTemp)
        ktype0 = [] # kType.mVToC( , 0c)
        idx = 0
        # print strings
        line = "%10.9f, %s, %6.5f, "%(seconds,timestamp, enviro.degC() )
        kline = ", "
        kline0 = ", "
        m1line = ", "
        m2line = ", "
        # collect data for each type, print columns to log file as we go
        for idxAD in kTypeAD24:
            #get adValue
            adValue = ADC_Value[idxAD]
            row.append(adValue)
            tcoupleAD.append(adValue)
            #m1 = ad/ampGain
            m1 = kType.mvOverGain( adValue)
            mvog.append(m1)
            #m2 = (ad-ZeroOffset)/ampGain
            m2 = kType.fnMagic(adValue)
            mv.append(m2)
            # k = inverseLoopup(m2, coldJunctionTemp)
            k = kType.mVToC(adValue,enviro.degC())
            ktype.append(k)
            k0 =  kType.mVToC(adValue,0)
            ktype0.append(k0)
            #build up print line
            line = line + "%10.9f,"%adValue
            m1line = m1line + "%10.9f,"%m1
            m2line = m2line + "%10.9f,"%m2
            kline = kline + "%10.9f,"%k
            kline0 = kline0 + "%10.9f,"%k0
        row += mvog
        row = row+mv
        row = row+ktype
        row = row+ktype0
#        a = np.array(tcoupleAD)
#        line = line + "%10.9f, %10.9f, %10.9f, %10.9f"%(
#                a.mean(),np.median(a), np.average(a), np.std(a))
#        b = np.array(ktype)
#        kline = kline+ "%10.9f, %10.9f, %10.9f, %10.9f"%(
#                b.mean(),np.median(b), np.average(b), np.std(b))
#        c = np.array(mv)
#        mline = mline+ "%10.9f, %10.9f, %10.9f, %10.9f"%(
#                c.mean(),np.median(c), np.average(c), np.std(c))
        line += m1line
        line += m2line
        line += kline
        line += kline0
        print(line, file=outFile)

#        row.append(a.mean())
#        row.append(np.median(a))
#        row.append(np.average(a))
#        row.append(np.std(a))
#        if repeatCount % 10 == 0:
        print( line)
        print(row)
        kTypeLog.append(row)

        sleep(sleepTime) # one sample per sec
        seconds+=sleepTime
        
    print(columnHeading,file=outFile)
    #using values saved in kTypeLog Array
    print("TCouple log has %d entries"%len(kTypeLog))
    summarizeColumns(kTypeLog, outFile)
    
def summarizeColumns(kTypeLog, outFile):
    # summarize columns
    
    npA = np.array(kTypeLog)
    print("npA : ", npA)  
#    this.kTypeLog = npA.tolist()
#    print("kTypeLog: ", this.kTypeLog)
    
#    np.savetxt("calibrate.csv",npA,delimiter=",")
    
    dataMax = npA.max(axis=0)
    printRow(",dataMax",dataMax,outFile)
    
    dataMin = npA.min(axis=0)
    printRow(",dataMin",dataMin,outFile)
    
    dataMean = np.mean(npA, axis=0)
    printRow(",dataMean",dataMean,outFile)
    
    dataMedian = np.median(npA, axis=0)
    printRow(",dataMedian",dataMedian,outFile)
    
    dataAverage = np.average(npA, axis=0)
    printRow(",dataAverage",dataAverage,outFile)
    
    dataStdDev = np.std(npA, axis=0)
    printRow(",dataStdDev",dataStdDev,outFile)

    print("dataMax ", dataMax)
    print("dataMin ", dataMin)
    print("dataMean ", dataMean)
    print("dataMedian ", dataMedian)
    print("dataAverage ", dataAverage)
    print("dataStdDev ", dataStdDev)

#    npB = npA
#    npB = np.vstack([npB,dataMax])
#    npB = np.vstack([npB,dataMin])
#    npB = np.vstack([npB,dataMean])
#    npB = np.vstack([npB,dataMedian])
#    npB = np.vstack([npB,dataAverage])
##    print("npB",npB)
#    
#    np.savetxt("calibrate_2.csv",npB,  fmt="%10.8f",delimiter=",",
#               header="count,temp,a,b,c,mean,median,avg,stdDev")
#    print("Count,TempC, TC1, TC2, TC3, Avg,Mean,Median, StdDev", file=outFile)
    print("saved data")

def printRow(name,row,file):
    rowLen=len(row)
    print("row: ",row)
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
    now = datetime.datetime.now()
    nowStr = now.strftime("%Y%m%d_%H%M")
    csvLog = "moDataLog_"+nowStr+".csv"
    moCSV.init(csvLog)
    #
    doTest()
    
