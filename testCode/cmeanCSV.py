# read and decimate modac csv
import sys
this = sys.modules[__name__]
import os
import csv
from datetime import datetime, timedelta
import logging, logging.handlers
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

from cumulativeMean import MeanLimitedChannel

count = 0
outCount = 0
outfile = None
writer = None
inColumnNames = None
outColumnNames = None

timestampKey = 'timestamp'
dateKey = 'date'
timeKey = 'time'
raw0Key = 'ad16Raw_0'
raw2Key = 'ad16Raw_2'

lastTimeMin = 0
lastDateTime = None

chan0 = MeanLimitedChannel(limited=False)
chan1 = MeanLimitedChannel(limited=False)

ma0Columns = ["chan0 ma0","chan0 ma1","chan0 ma2","chan0 ma3","chan1 ma4"]
ma1Columns = ["chan1 ma0","chan1 ma1","chan1 ma2","chan1 ma3","chan1 ma4"]
ms0Columns = ["chan0 ms0","chan0 ms1","chan0 ms2","chan0 ms3","chan1 ms4"]
ms1Columns = ["chan1 ms0","chan1 ms1","chan1 ms2","chan1 ms3","chan1 ms4"]
def processLine (row):
    #print("processing line ",count, row)
    dtStr = row[timestampKey]
    dt = datetime.strptime(dtStr,"%Y-%m-%d %H:%M:%S")
    dateStr = datetime.strftime(dt,"%Y-%m-%d")
    timeStr = datetime.strftime(dt,"%I:%M:%S%p")
    row[dateKey] = dateStr
    row[timeKey] =timeStr

    try:
        chan0.addValue(row[raw0Key])
    except ValueError:
        log.error(f"caught ValueError {count} {chan0}", exc_info=True)


    if this.count >= 10:
        # add ma and ms
        i=0
        #print (i, chan0.movAvg)
        for k in ma0Columns:
            row[k] = chan0.movAvg[i]
            i+=1
        i=0
        #print (i, chan0.movSlope)
        for k in ms0Columns:
            row[k] = chan0.movSlope[i]
            i+=1
    else:
        print(count,chan0)
    #print(count, row)
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
                inColumnNames = reader.fieldnames
                print("Columns are ",inColumnNames)
                outColumnNames = [dateKey,timeKey] + inColumnNames + ma0Columns+ms0Columns
                print("out Columns are ",outColumnNames)
                this.outfile = open(outfilename, 'w', newline='')
                this.writer = csv.DictWriter(this.outfile, outColumnNames)
                this.writer.writeheader()
                this.count = this.count + 1
                continue
            #print (count, row)
            try:
                processLine(row)
            except:
                log.error("should not die of value error")
            this.count = this.count+1
            #if count > 500:
            #    break
    this.outfile.close()
    this.outfile = None
    print("Read %d lines wrote %d lines"%(this.count,this.outCount))
    this.count = 0
    this.outCount = 0

doFile('mar3-6c.csv')
