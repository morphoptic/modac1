# read and decimate modac csv
# for ok lines, reprocess AD24_4 from mV to C using ambient temp
import sys
this = sys.modules[__name__]
import os
import csv
from datetime import datetime, timedelta
from thermocouples_reference import thermocouples

# DoFile(filename) at the end of file

count = 0
outCount = 0
outfile = None
writer = None
inColumnNames = None
outColumnNames = None

timestampKey = 'timestamp'
dateKey = 'date'
timeKey = 'time'
tempKey = 'ambient'
adKey = 'ad16_0'
ktypeKey = 'kType_0'
kissCKey = 'kissC'
newCKey = 'newC'
mvFromC0Key = 'mvFromC0'
mvFromCKey = 'mvFromC'
newAmpGainKey = 'newAmpGain'
vFromCKey = 'vFromC'
testCKey = 'testC'
adFromCKey = 'adFromC'

lastTimeMin = 0
lastDateTime = None

__kTypeLookup = thermocouples['K']
_ampGain = 122.4 # from ad8495 spec sheet
adOffset = 0.0

def adOverGain(adValue, ampGain = _ampGain):
    return (adValue- adOffset)/ampGain

def mVToC(mV,tempRef=0):
    _mV = mV #fnMagic(mV)
    return __kTypeLookup.inverse_CmV(_mV, Tref=tempRef)

def cToMv(c, tempRef=0):
    return __kTypeLookup.emf_mVC(c, tempRef)

def adToC(adRead,tempRef=0, ag = _ampGain):
    v = adOverGain(adRead, ag)
    mv = v*1000.0
    c = mVToC(mv,tempRef)
    #print ("ad v mv c: ", adRead, v, mv, c)
    return c

def processLine (row):
    #print("processing line ",count, row)
    #Decimate no- do that in decimateCSV then merge w/kissC data
#    dtStr = row[timestampKey]
#    dt = datetime.strptime(dtStr,"%Y-%m-%d %H:%M:%S")
#    if this.lastDateTime== None :
#        this.lastDateTime = dt
#    elif dt.time().minute == this.lastDateTime.time().minute:
#        # skip same minute
#        #print("Same Minute", dt,dt.time().minute, this.lastDateTime,this.lastDateTime.time().minute)
#        return
#    this.lastDateTime = dt
#    dateStr = datetime.strftime(dt,"%Y-%m-%d")
#    timeStr = datetime.strftime(dt,"%I:%M:%S%p")
#    row[dateKey]= dateStr
#    row[timeKey]=timeStr

    
    # reprocess AD value to C using ambient temp
    ambtemp = float(row[tempKey])
    adread = float(row[adKey])
    #print("AD24_4 value read =",adread)
    newC = adToC(adread,ambtemp)
    row[newCKey] = newC
    
    # reverse calculate kissC -> expected AD value, amp
    
    kissC = float(row[kissCKey])
    mvFromC0 = cToMv(kissC)
    mvFromC = cToMv(kissC, ambtemp)
    row[mvFromC0Key] = mvFromC0
    row[mvFromCKey] = mvFromC
    vFromC = mvFromC/1000.0
    row[vFromCKey] = vFromC
    row[adFromCKey] = vFromC * _ampGain
    newAmpGain  = adread/vFromC
    row[newAmpGainKey] = newAmpGain
    testC = adToC(vFromC, ambtemp, newAmpGain)

    print("adread", vFromC, "oldAdGain", adOverGain(adread), "newAdGain", newAmpGain, adOverGain(adread,newAmpGain),testC)
    row[testCKey] = testC

    #print("outRow:", row)
    this.writer.writerow(row)
    this.outfile.flush()
    this.outCount += 1
    pass

def doFile(filename):
    base, ext = os.path.splitext(filename)
    outfilename = base+"_out.csv"
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if this.count == 0:
                # get existing headers
                inColumnNames = reader.fieldnames
                print("in  Columns are ", inColumnNames)
                # add new calculated column headers
                outColumnNames = [dateKey,timeKey]+ inColumnNames + [newCKey,mvFromC0Key, mvFromCKey,vFromCKey,adFromCKey,newAmpGainKey,testCKey]
                print("out Columns are ", outColumnNames)
                
                this.outfile = open(outfilename, 'w', newline='')
                this.writer = csv.DictWriter(this.outfile, outColumnNames)
                this.writer.writeheader()
            #print (count, row)
            processLine(row)
            this.count = this.count+1
            #if count > 500:
            #    break
    this.outfile.close()
    this.outfile = None
    print("Read %d lines wrote %d lines"%(this.count,this.outCount))
    this.count = 0
    this.outCount = 0

doFile('combined_0225.csv')