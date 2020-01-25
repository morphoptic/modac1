# recalculate Thermocouple values from csv
# use Kiln/ref degC at room & 0c to calculate expected mv
# compare with ad/ktype reported from MODAC/Calibrate
# t = thermocouple.invert(mv, envTemp)
# where mv = ad/Gain + offset in millivolts
# note the AD value is 0-5v, so shift decimal 3 (/1000)

import sys
this = sys.modules[__name__]
import logging, logging.handlers
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

from thermocouples_reference import thermocouples
import datetime, csv

################################
__csvInFile = None
__csvOutFile = None
__csvReader= None
__csvWriter = None
defaultName = "tcheck.csv"
def initCSV(filename=defaultName):
    #this.__csvInFile = open(filename, "r")
    #this.__csvReader = csv.reader(this.__csvInFile, quoting=csv.QUOTE_NONNUMERIC)
    this.__csvOutFile = open(filename, "w")
    this.__csvWriter = csv.writer(this.__csvOutFile)

def writeCSV(row):
    this.__csvWriter.writerow(row)
    this.__csvOutFile.flush()

def closeCSV():
    #this.__csvInFile.close()
    this.__csvOutFile.close()

################################
# only looking at kType thermocouples
__kTypeLookup = thermocouples['K']

kilnDegC_array = [
0.0000,
100.0000,
25.9246,
203.0000,
198.0000,
199.0000,
199.0000,
200.0000,
201.0000,
202.0000,
199.0000,
301.0000,
300.0000,
300.0000,
299.000,
]
ad0to5_array = [
0.1378,
0.4870,
0.1414,
1.3490,
1.3252,
1.3034,
1.2942,
1.2410,
1.2284,
1.2119,
1.1417,
1.7853,
1.7954,
1.7939,
1.764,
]

envDegC_array = [
24.1757,
25.2557,
25.9246,
25.7328,
25.6000,
25.6253,
25.5697,
26.2217,
25.9791,
26.1307,
26.9068,
26.4794,
25.9639,
26.9400,
26.075,
]

################################
ampGain = 144
adOffset = 0

def adOverGain(adValue):
    return (adValue- adOffset)/ampGain

def cToMV(degC,tempRef= 0):
    return __kTypeLookup.emf_mVC(degC,tempRef)

def compareCtoMV(degC, readMV, ref):
    calcMv_0 = cToMV(degC, 0)
    calcMv_ref = cToMV(degC, ref)
    mv = adOverGain(readMV*1000)
    delta0 = (mv-calcMv_0)
#    print("C: "+str(degC) + " at0: "+str(calcMv_0) + " atRef("+str(ref)+"): "
#          + str(calcMv_ref) + " = readmv("+str(readMV)+"):" +str(mv))
    row = [degC,calcMv_0,ref,calcMv_ref,readMV,mv, delta0]
#    print(row)
    writeCSV(row)
          
def mVToC(mV,tempRef=0):
    _mV = mV #fnMagic(mV)
    return __kTypeLookup.inverse_CmV(_mV, Tref=tempRef)

def adToC(adRead,tempRef=0):
    v = adOverGain(adRead)
    mv = v*1000.0
    c = mVToC(mv,tempRef)
    #print ("ad v mv c: ", adRead, v, mv, c)
    return c

#####################
def testCalc(mV,expectedC):
    c0 = mVToC(mV, 0.0)
    c25 = mVToC(mV, 25.0)
    msg = "Temp at mv"+ str(mV) + " = (0):" + str(c0) + " (25):" + str(c25) + " expected "+str(expectedC)
    print(msg)
    #log.debug(msg)
    
# inverse_CmV
def calc0_100_300():
    log.debug("CALC REF mV")
    mv = 0.0
    testCalc(mv,0.0)
    mv = 1.0
    testCalc(mv, 25.0)
    mv = 4.096
    testCalc(mv, 100.0)
    mv = 12.209
    testCalc(mv, 300.0)
    mv =     0.004037344783333*1000.0
    testCalc(mv, 98)


#####################
# the test
# for each value in kilnDegC_array
#   compute mv expected from Thermocouple
#   compare with value in ad0to5_array
#   use both 0C and envDegC_array
if __name__ == "__main__":
    print("ThermoCheck ktype values")
    calc0_100_300()
    #def compareCtoMV(degC, readMV, ref):
    initCSV()
    writeCSV(["degC", "at0", "refC", "atRef", "readAD", "ad/gain", "delta"])
    #print("degC, at0, ref, atRef, readMV, ad/gain, delta")
    for i in range(len(kilnDegC_array)):
        compareCtoMV(kilnDegC_array[i],ad0to5_array[i],envDegC_array[i])