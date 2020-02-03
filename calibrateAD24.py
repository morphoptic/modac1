# calibrateAD24
import sys
this = sys.modules[__name__]

import logging
from time import sleep
import datetime
import numpy as np
from modac import moLogger, ad24, moData, moCSV, enviro, kType
from modac.moKeys import *

type ="gun_"
type ="room_"
type ="kiln2027_"
#type ="ice_"
#type ="25C_"
#type ="60C_"
#type ="ifa_"
#idx of ktypes in AD24 array
kTypeAD24 = kType.kTypeIdx # [4,5,6]

if __name__ == "__main__":
    moLogger.init()
    
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

numMin = 10
numMin = 1
#numMin = 5
numSeconds = (60*numMin)
#numSeconds = 3# (60*numMin)
#sleepTime = 0.005
sleepTime = 1.0

def makeHeader():
#        ad2,ad4, ad5, ad6, ,m1.1, m1.2, m1.3,m1.4,, mv1,mv2,mv3,,
#        Kr1,Kr2,Kr3,,K0-1,K0-2,K0-3, "
    ad = ", "
    m1 = ", "
    mv = ", "
    kr = ", "
    k0 = ", "
    deviceCount = len(kTypeAD24)
    for idx in range(deviceCount):
        ad += ", ad%d"%kTypeAD24[idx]
        m1 += ", ad/g.%d"%idx
        mv += ", c.%d"%idx
        kr += ", KR.%d"%idx
        k0 += ", K0.%d"%idx
    columnHeading = "Seconds,TimeStamp,TempC" + ad + m1 + mv + kr + k0
    return columnHeading

def doTest():
    seconds = 0.00
    kTypeLog = [] # collection of primary data, one row per Sample
    data = []
    calibrate = "calibrateCSV_"
    now = datetime.datetime.now()
    nowStr = now.strftime("%Y%m%d_%H%M")
    name = calibrate + type
    outName = name+nowStr+".csv"
    outFile = open(outName, "w")
    columnHeading = makeHeader() #"Seconds,TimeStamp,TempC, "
    print(columnHeading)
    print(columnHeading,file=outFile)
    for repeatCount in range(numSeconds):
        # for each Row/timestep
        moData.updateTimestamp()
        enviro.update()
        ad24.update()
        kType.update()
        moCSV.addRow()
        moData.logData()
        #
        timestamp = moData.getValue(keyForTimeStamp())
        ADC_Value = ad24.all0to5Array()
        ADC_Raw = ad24.allRawArray()
        #get ktype from moData
        kValues = moData.getValue(keyForKType())
        print("kValues: ",kValues)
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
        line = "%10.9f, %s, %6.5f, ,"%(seconds, timestamp, enviro.degC() )
        kline = ", "
        kline0 = ", "
        m1line = ", "
        m2line = ", "
        print("enviroC", enviro.degC())
        # collect data for each type, print columns to log file as we go
        kIdx = 0
        for idxAD in kTypeAD24:
            print("idxAD", idxAD)
            #get adValue
            adValue = ADC_Value[idxAD]
            row.append(adValue)
            tcoupleAD.append(adValue)
            
            #m1 = ad/ampGain
            m1 = kType.adOverGain( adValue)
            mvog.append(m1)
            
            #m2 = (ad-ZeroOffset)/ampGain
            m2 = kType.adToC(adValue)
            mv.append(m2)
            
#            # k = inverseLoopup(m2, coldJunctionTemp)
#            k = kType.adToC(adValue,enviro.degC())
            k = kValues[kIdx]
            kIdx+=1
            
            k0 =  kType.adToC(adValue,0)
            ktype0.append(k0)
            
            #build up print line
            line = line + "%10.9f,"%adValue
            m1line = m1line + "%10.9f,"%m1
            m2line = m2line + "%10.9f,"%m2
            kline = kline + "%10.9f,"%k
            kline0 = kline0 + "%10.9f,"%k0
        # add numeric values to row array
        row += [0] +mvog
        row = row+ [0] +mv
        row = row+ [0] +kValues
        row = row+ [0] +ktype0
#        a = np.array(tcoupleAD)
#        line = line + "%10.9f, %10.9f, %10.9f, %10.9f"%(
#                a.mean(),np.median(a), np.average(a), np.std(a))
#        b = np.array(ktype)
#        kline = kline+ "%10.9f, %10.9f, %10.9f, %10.9f"%(
#                b.mean(),np.median(b), np.average(b), np.std(b))
#        c = np.array(mv)
#        mline = mline+ "%10.9f, %10.9f, %10.9f, %10.9f"%(
#                c.mean(),np.median(c), np.average(c), np.std(c))
        # build up string lines, inserting blank columns  "," +
        line += m1line
        line += m2line
        line += kline
        line += kline0
        print(line, file=outFile)
        outFile.flush()

#        row.append(a.mean())
#        row.append(np.median(a))
#        row.append(np.average(a))
#        row.append(np.std(a))
#        if repeatCount % 10 == 0:
#        print( line)
#        print(row)
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
#    print("npA : ", npA)  
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

#    print("dataMax ", dataMax)
#    print("dataMin ", dataMin)
#    print("dataMean ", dataMean)
#    print("dataMedian ", dataMedian)
#    print("dataAverage ", dataAverage)
#    print("dataStdDev ", dataStdDev)

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
#    print("row: ",row)
    line = name+", "
    # tempC
    line = line + "%10.9f, ,"%row[1]
    for i in range(2,rowLen):
        line = line + "%10.9f, "%row[i]
    print(line, file=file)
    
def calc0_100_300():
    log.debug("CALC REF mV")
    mv = 0.0
    c = kType.mVToC(mv,0)# ,25)
    print("Temp at mv"+ str(mv) + " = " + str(c))
    log.debug("Temp at mv"+ str(mv) + " = " + str(c))
    mv = 1.0
    c = kType.mVToC(mv,0)# ,25)
    print("Temp at mv"+ str(mv) + " = " + str(c))
    log.debug("Temp at mv"+ str(mv) + " = " + str(c))
    mv =4.096
    c = kType.mVToC(mv,0)# ,25)
    print("Temp at mv"+ str(mv) + " = " + str(c))
    log.debug("Temp at mv"+ str(mv) + " = " + str(c))
    mv = 12.209
    c = kType.mVToC(mv,0)# ,25)
    print("Temp at mv"+ str(mv) + " = " + str(c))
    log.debug("Temp at mv"+ str(mv) + " = " + str(c))
    mv = 0.0/1000.0
    c = kType.mVToC(mv,0)# ,25)
    print("Temp at mv"+ str(mv) + " = " + str(c))
    log.debug("Temp at mv"+ str(mv) + " = " + str(c))
    mv = 1.0/1000.0
    c = kType.mVToC(mv,0)# ,25)
    print("Temp at mv"+ str(mv) + " = " + str(c))
    log.debug("Temp at mv"+ str(mv) + " = " + str(c))
    mv =4.096/1000.0
    c = kType.mVToC(mv,0)# ,25)
    print("Temp at mv"+ str(mv) + " = " + str(c))
    log.debug("Temp at mv"+ str(mv) + " = " + str(c))
    mv = 12.209/1000.0
    c = kType.mVToC(mv,0)# ,25)
    print("Temp at mv"+ str(mv) + " = " + str(c))
    log.debug("Temp at mv"+ str(mv) + " = " + str(c))

    #exit()
    
if __name__ == "__main__":
    #    
    print("MorpOptics 24bAD Ktype Calibration Test")
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)#, format=logFormatStr)
    logging.captureWarnings(True)
    logging.info("Logging Initialized for MO 24Bit AD  main unitTest")
    #
    calc0_100_300()
    #
    moData.init()
    enviro.init()
    print("Enviro says degC: ",enviro.degC())
    ad24.init()
    kType.init()
    #
    now = datetime.datetime.now()
    nowStr = now.strftime("%Y%m%d_%H%M")
    dataLog = "moDataLog_"+type+nowStr+".csv"
    moCSV.init(dataLog) # log what is in MoData
    #
    doTest()
    
