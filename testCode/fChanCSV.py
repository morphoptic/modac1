# read and decimate modac csv
import sys
this = sys.modules[__name__]
import os
import csv
from datetime import datetime, timedelta
import logging, logging.handlers
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

from filteredChannel import FilteredChannel

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

chan0 = FilteredChannel(filtered=True)

filteredColumns = ["value","movAvg","slope","slopeLimit"]
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
    except ValueError as e:
        print("ValueError ",row[raw0Key], e)
        log.error(f"caught ValueError Row:{this.count} {chan0}", exc_info=True)


    row[filteredColumns[0]] = chan0.curValue()
    row[filteredColumns[1]] = chan0.avg()
    row[filteredColumns[3]] = chan0.slope
    row[filteredColumns[3]] = chan0.slopeLimit

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
                outColumnNames = [dateKey,timeKey] + inColumnNames + filteredColumns
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
