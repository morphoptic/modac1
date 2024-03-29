# read and decimate modac csv
# for ok lines, reprocess AD16_0 from mV to C using ambient temp
import sys
this = sys.modules[__name__]
import os
import csv
from datetime import datetime, timedelta

# functions for kType thermocouple conversions
from thermocouples_reference import thermocouples
__kTypeLookup = thermocouples['K']

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
moCatZeroKey = "moCatZero"
moCwAmbKey = 'moCwithAmbient'
mvKissC0Key = 'mvKissC0'
mvKissCAmbKey = 'mvKissCAmb'
vKissC0Key = 'vKissC0'

lastTimeMin = 0
lastDateTime = None

_ampGain = 122.4 # from ad8495 spec sheet
adOffset = 0.0

def adOverGain(adValue, ampGain = _ampGain, offset = 0):
    '''divide adValue 0-5V by gain, with offset) '''
    return (adValue- offset)/ampGain

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
#    if this.lastDateTime is None :
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
    moCatZero = float(row[ktypeKey])
    row[moCatZeroKey] = moCatZero  #add a column with new name
    #print("AD24_4 value read =",adread)
    moCAmbient = adToC(adread,ambtemp)
    row[moCwAmbKey] = moCAmbient
    
    # get kissC
    kissC = float(row[kissCKey])
    # reverse calculate kissC -> expected AD value, amp
    mvKissC0 = cToMv(kissC)
    row[mvKissC0Key] = mvKissC0
    mvKissCA = cToMv(kissC, ambtemp)
    row[mvKissCAmbKey] = mvKissCA
    vKissC0 = mvKissC0/1000.0
    row[vKissC0Key] = vKissC0

    #print("outRow:", row)
    this.writer.writerow(row)
    this.outfile.flush()
    this.outCount += 1
    pass

def doFile(filename):
    base, ext = os.path.splitext(filename)
    outfilename = base+"_p2.csv"
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rowCount = 0
        for row in reader:
            if this.count == 0:
                # get existing headers
                inColumnNames = reader.fieldnames
                print("in  Columns are ", inColumnNames)
                # add new calculated column headers
                outColumnNames = inColumnNames + [moCatZeroKey, moCwAmbKey, kissCKey, mvKissC0Key, mvKissCAmbKey,vKissC0Key]
                print("out Columns are ", outColumnNames)
                
                this.outfile = open(outfilename, 'w', newline='')
                this.writer = csv.DictWriter(this.outfile, outColumnNames)
                this.writer.writeheader()
            #print (count, row)
            processLine(row)
            rowCount += 1
            this.count = this.count+1
            #if count > 500:
            #    break
    this.outfile.close()
    this.outfile = None
    print("Read %d lines wrote %d lines"%(this.count,this.outCount))
    this.count = 0
    this.outCount = 0

doFile('combined_0225.csv')